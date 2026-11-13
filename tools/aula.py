#!/usr/bin/env python3
"""CLI de Aula Virtual (Canvas LMS) para el repositorio MBA ESPAE.

Solo usa la librería estándar de Python (3.9+). Lee la configuración de
`.env` en la raíz del repo (CANVAS_BASE_URL, CANVAS_TOKEN) o de variables
de entorno. Nunca imprime el token.

Uso rápido (desde la raíz del repo):
    python3 tools/aula.py configurar      # primera vez: guarda tu token
    python3 tools/aula.py yo
    python3 tools/aula.py pendientes
    python3 tools/aula.py tarea <curso> <id_tarea>
    python3 tools/aula.py --help

Las acciones que escriben en Aula Virtual (entregar, comentar) exigen
`--confirmar`; sin esa bandera solo muestran lo que harían.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import mimetypes
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURSOS_JSON = ROOT / "cursos" / "cursos.json"
TRABAJO = ROOT / "mi-trabajo"
CACHE = TRABAJO / ".cache"

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("America/Guayaquil")
except Exception:  # Windows sin tzdata: Ecuador no tiene horario de verano
    TZ = dt.timezone(dt.timedelta(hours=-5))

DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


class AulaError(Exception):
    pass


# ───────────────────────── configuración y HTTP ─────────────────────────


def load_env() -> dict:
    cfg = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("CANVAS_BASE_URL", "CANVAS_TOKEN"):
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    if not cfg.get("CANVAS_TOKEN"):
        raise AulaError(
            "Aula Virtual no está configurado en este repo: abre Claude Code aquí y escribe /configurar "
            "(o ejecuta: python3 tools/aula.py configurar)."
        )
    cfg.setdefault("CANVAS_BASE_URL", "https://postgradosvirtual.espol.edu.ec")
    cfg["CANVAS_BASE_URL"] = cfg["CANVAS_BASE_URL"].rstrip("/")
    return cfg


class Canvas:
    def __init__(self) -> None:
        cfg = load_env()
        self.base = cfg["CANVAS_BASE_URL"]
        self.api = f"{self.base}/api/v1"
        self._token = cfg["CANVAS_TOKEN"]

    def _url(self, path: str, params: dict | list | None = None) -> str:
        url = path if path.startswith("http") else f"{self.api}/{path.lstrip('/')}"
        if params:
            sep = "&" if "?" in url else "?"
            url += sep + urllib.parse.urlencode(params, doseq=True)
        return url

    def _request(self, method: str, url: str, data: bytes | None = None, headers: dict | None = None, auth: bool = True):
        h = {"Accept": "application/json"}
        if auth:
            h["Authorization"] = f"Bearer {self._token}"
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        for intento in range(3):
            try:
                return urllib.request.urlopen(req, timeout=60)
            except urllib.error.HTTPError as e:
                limitado = e.code == 429 or (e.code == 403 and "Rate Limit" in (e.read() or b"").decode("utf-8", "ignore"))
                if limitado and method == "GET" and intento < 2:  # nunca reintentar POST (entregas no idempotentes)
                    time.sleep(2 * (intento + 1))
                    continue
                msg = {401: "sin permiso (token inválido, vencido o el docente no habilitó esta sección)",
                       404: "no encontrado (o no visible para estudiantes)"}.get(e.code, e.reason)
                raise AulaError(f"HTTP {e.code} en {method} {url.split('?')[0].replace(self.base, '')}: {msg}") from None
            except urllib.error.URLError as e:
                raise AulaError(f"No se pudo conectar a {self.base}: {e.reason}") from None
        raise AulaError("Rate limit de Canvas: intenta de nuevo en unos segundos")

    def get(self, path: str, params: dict | list | None = None, paginate: bool = True):
        url = self._url(path, params)
        out = []
        while url:
            r = self._request("GET", url)
            data = json.load(r)
            if not isinstance(data, list) or not paginate:
                return data
            out.extend(data)
            m = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("Link", "") or "")
            url = m.group(1) if m else None
        return out

    def post(self, path: str, fields: list, auth: bool = True):
        body = urllib.parse.urlencode(fields).encode()
        r = self._request("POST", self._url(path), body, {"Content-Type": "application/x-www-form-urlencoded"}, auth)
        return json.load(r)

    def download(self, url: str, dest: Path) -> None:
        # Las URLs de descarga de Canvas ya vienen firmadas (verifier); urllib sigue el redirect a S3.
        r = self._request("GET", url, auth=False)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)

    def upload_file(self, init_path: str, file: Path) -> dict:
        """Flujo de 3 pasos de Canvas: pedir slot → subir multipart → confirmar."""
        size = file.stat().st_size
        ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        slot = self.post(init_path, [("name", file.name), ("size", str(size)), ("content_type", ctype)])
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in slot.get("upload_params", {}).items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{slot.get("file_param", "file")}"; '
            f'filename="{file.name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
        )
        body = b"".join(parts) + file.read_bytes() + f"\r\n--{boundary}--\r\n".encode()

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        upload_url = urllib.parse.urljoin(self.base + "/", slot["upload_url"])  # Canvas autoalojado puede darla relativa
        opener = urllib.request.build_opener(NoRedirect)
        # Al almacenamiento no se le envía el token: la petición ya va firmada con upload_params.
        req = urllib.request.Request(upload_url, data=body, method="POST",
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})

        def confirmar(location: str) -> dict:
            loc = urllib.parse.urljoin(upload_url, location)
            mismo_origen = urllib.parse.urlparse(loc).netloc == urllib.parse.urlparse(self.base).netloc
            return json.load(self._request("GET", loc, auth=mismo_origen))

        try:
            r = opener.open(req, timeout=300)
            if r.status == 201 and r.headers.get("Location"):
                return confirmar(r.headers["Location"])
            return json.load(r)  # 200/201 con el objeto File en el cuerpo
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                return confirmar(e.headers["Location"])
            raise AulaError(f"Falló la subida del archivo: HTTP {e.code}") from None


# ───────────────────────── utilidades ─────────────────────────


def local_dt(iso: str | None) -> dt.datetime | None:
    if not iso:
        return None
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ)


def fmt_fecha(iso: str | None, con_dia: bool = True) -> str:
    d = local_dt(iso)
    if not d:
        return "sin fecha"
    s = d.strftime("%Y-%m-%d %H:%M")
    return f"{DIAS[d.weekday()]} {s}" if con_dia else s


def slugify(s: str, max_len: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    if len(s) > max_len:  # cortar en límite de palabra
        s = s[:max_len + 1].rsplit("-", 1)[0]
    return s.rstrip("-")


# Prefijos de nombre de tarea que no aportan al nombre de la ficha
_PREFIJOS_TAREA = re.compile(
    r"^(actividad\s+\d+(\.\d+)?\s*[|>]\s*)?((tarea|actividad)\s+(individual|grupal)\s*[|>]\s*)?"
    r"(an[aá]lisis( y (discusi[oó]n|resoluci[oó]n))?( de| del)? caso:?\s*|discusi[oó]n del caso\s*|"
    r"curso linkedin learning:\s*|complemento formativo:\s*|completar\s+)?",
    re.I,
)


def nombre_ficha(nombre_tarea: str) -> str:
    cod = _codigo_actividad(nombre_tarea)
    resto = _PREFIJOS_TAREA.sub("", nombre_tarea.strip()).strip(" «»\"'")
    return (f"{cod}-" if cod else "") + slugify(resto, 45)


def cursos_registrados() -> list:
    if CURSOS_JSON.exists():
        return json.loads(CURSOS_JSON.read_text(encoding="utf-8"))
    return []


def resolver_curso(ref: str) -> int:
    """Acepta id numérico, slug de carpeta o parte del nombre del curso."""
    if str(ref).isdigit():
        return int(ref)
    ref_l = ref.lower()
    for c in cursos_registrados():
        if ref_l in (c["slug"], str(c["id"])) or ref_l in c["nombre"].lower():
            return int(c["id"])
    raise AulaError(f"Curso '{ref}' no está en cursos/cursos.json; usa el id numérico (python3 tools/aula.py cursos)")


def estado_entrega(sub: dict | None) -> str:
    if not sub:
        return "—"
    st = sub.get("workflow_state")
    if sub.get("excused"):
        return "excusada"
    if st == "graded":
        return f"calificada ({sub.get('score')})"
    if st in ("submitted", "pending_review"):
        return "entregada" + (" (atrasada)" if sub.get("late") else "")
    if sub.get("missing"):
        return "FALTANTE"
    return "sin entregar"


def modalidad(a: dict) -> str:
    return "grupal" if a.get("group_category_id") else "individual"


# ───────────────────────── HTML → Markdown ─────────────────────────


class _Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, dict(attrs or []), [], parent


class _TreeBuilder(HTMLParser):
    VOID = {"br", "img", "hr", "input", "meta", "link", "col", "source", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = _Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in self.VOID:
            self.cur = n

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


BLOCK = {"p", "div", "section", "article", "header", "footer", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
         "ul", "ol", "li", "table", "tr", "hr", "pre", "figure"}


def _text(n) -> str:
    if isinstance(n, str):
        return n
    return "".join(_text(c) for c in n.children)


def _clean_inline(s: str) -> str:
    s = re.sub(r"[ \t\r\f\v ]+", " ", s)
    s = re.sub(r"\*\*\s*\*\*", "", s)
    return s.strip()


class HtmlToMd:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    def convert(self, raw: str | None) -> str:
        if not raw:
            return ""
        tb = _TreeBuilder()
        tb.feed(raw)
        md = self.block(tb.root)
        md = re.sub(r"[ \t]+\n", "\n", md)
        md = re.sub(r"[ \t]+([.,;:)\]?!])", r"\1", md)  # sin espacio antes de puntuación
        md = re.sub(r"([(¿¡\[])[ \t]+", r"\1", md)
        md = re.sub(r"\bPASO (\d+)(?=\S)", r"PASO \1 · ", md)
        md = re.sub(r"\n{3,}", "\n\n", md)
        return md.strip()

    # inline -----------------------------------------------------------
    def inline(self, n) -> str:
        if isinstance(n, str):
            return n.replace("\n", " ")
        t = n.tag
        if t == "br":
            return "\n"
        if t == "img":
            alt = n.attrs.get("alt", "").strip()
            return f"[imagen: {alt}]" if alt and not alt.lower().startswith(("blob", "image")) else ""
        if t in ("script", "style"):
            return ""
        inner = "".join(self.inline(c) for c in n.children)
        if t in ("strong", "b"):
            s = inner.strip()
            return f" **{s}** " if s else inner
        if t in ("em", "i"):
            s = inner.strip()
            return f" *{s}* " if s else inner
        if t == "a":
            href = n.attrs.get("href", "")
            label = _clean_inline(inner) or href
            m = re.search(r"/files/(\d+)", href)
            if m:
                name = n.attrs.get("title") or label
                return f"{label} [archivo:{m.group(1)}]" if name else f"[archivo:{m.group(1)}]"
            if href.startswith("/"):
                href = self.base_url + href
            if href and href != label:
                return f"[{label}]({href})"
            return label
        if t in BLOCK:  # bloque dentro de inline (p.ej. div dentro de td)
            return "\n" + self.block(n) + "\n"
        return inner

    # block ------------------------------------------------------------
    def block(self, n) -> str:
        out, buf = [], []

        def flush():
            if buf:
                s = "\n".join(_clean_inline(x) for x in "".join(buf).split("\n"))
                s = s.strip()
                if s:
                    out.append(s)
                buf.clear()

        for c in n.children:
            if isinstance(c, str) or c.tag not in BLOCK:
                buf.append(self.inline(c))
                continue
            flush()
            t = c.tag
            if t in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = max(3, int(t[1]) + 1)  # dentro de una ficha los títulos arrancan en ###
                txt = _clean_inline(_text(c))
                if txt:
                    out.append("#" * min(level, 6) + " " + txt)
            elif t in ("ul", "ol"):
                items = []
                for i, li in enumerate([x for x in c.children if not isinstance(x, str) and x.tag == "li"], 1):
                    body = self.block(li).replace("\n", "\n   ")
                    items.append(f"{i}. {body}" if t == "ol" else f"- {body}")
                if items:
                    out.append("\n".join(items))
            elif t == "table":
                out.append(self.table(c))
            elif t == "hr":
                out.append("---")
            elif t == "blockquote":
                out.append("\n".join("> " + x for x in self.block(c).splitlines()))
            elif t == "pre":
                out.append("```\n" + _text(c).strip() + "\n```")
            else:
                s = self.block(c)
                if s:
                    out.append(s)
        flush()
        return "\n\n".join(x for x in out if x.strip())

    def _rows(self, table) -> list:
        rows = []

        def walk(n):
            for c in n.children:
                if isinstance(c, str):
                    continue
                if c.tag == "tr":
                    rows.append([x for x in c.children if not isinstance(x, str) and x.tag in ("td", "th")])
                elif c.tag in ("thead", "tbody", "tfoot"):
                    walk(c)

        walk(table)
        return rows

    def table(self, t) -> str:
        rows = [r for r in self._rows(t) if r]
        if not rows:
            return ""
        cell_md = [[self.block(c).strip() for c in r] for r in rows]
        nested = any(c.tag == "table" for r in rows for cell in r for c in _iter(cell))
        ncols = max(len(r) for r in rows)

        def plano(s: str) -> str:
            return s.replace("**", "").strip()

        # filas de "insignia" (1 | Título, O1 | Opción): título en negrita → encabezado; si no → ítem numerado
        if ncols == 2 and all(len(r) == 2 and 0 < len(plano(r[0])) <= 3 for r in cell_md):
            out = []
            for a, b in cell_md:
                a = plano(a)
                if re.fullmatch(r"\*\*[^*]+\*\*", b.strip()):
                    out.append(f"### {a}. {plano(b)}" if a.isdigit() else f"### {a} · {plano(b)}")
                else:
                    out.append(f"**{a}.** {b}" if a.isdigit() else f"**{a}** · {b}")
            return "\n\n".join(out)
        es_fila_nota = [len(r) == 1 and int(r[0].attrs.get("colspan", 1)) >= ncols for r in rows]
        datos = [md for md, nota in zip(cell_md, es_fila_nota) if not nota]
        es_datos = (not nested and ncols >= 3 and len(datos) >= 3
                    and all(len(x) <= 160 and "\n\n" not in x for r in datos for x in r))
        if es_datos:
            lines, notas, pend = [], [], {}
            for r, md, nota in zip(rows, cell_md, es_fila_nota):
                if nota:
                    notas.append(md[0])
                    continue
                vals, ci = [], 0
                for col in range(ncols):
                    if pend.get(col, 0) > 0:
                        pend[col] -= 1
                        vals.append("〃")
                        continue
                    if ci < len(r):
                        span = int(r[ci].attrs.get("rowspan", 1))
                        if span > 1:
                            pend[col] = span - 1
                        vals.append(md[ci].replace("\n", " ").replace("|", "/"))
                        ci += 1
                    else:
                        vals.append("")
                lines.append("| " + " | ".join(re.sub(r"\*\*(.*?)\*\*", r"\1", v) if not lines else v for v in vals) + " |")
                if len(lines) == 1:
                    lines.append("|" + "---|" * ncols)
            return "\n".join(lines) + ("\n\n" + "\n\n".join(notas) if notas else "")
        # tabla de maquetación: cada fila como texto
        out = []
        for md in cell_md:
            md = [x for x in md if x]
            if not md:
                continue
            if all(len(x) <= 80 and "\n" not in x for x in md) and len(md) > 1:
                out.append(" · ".join(md))
            else:
                out.append("\n\n".join(md))
        return "\n\n".join(out)


def _iter(n):
    for c in n.children:
        if not isinstance(c, str):
            yield c
            yield from _iter(c)


# ───────────────────────── comandos de lectura ─────────────────────────


def cmd_yo(cv: Canvas, args) -> None:
    me = cv.get("users/self")
    print(f"Usuario: {me['name']} (id {me['id']})")
    cursos = cv.get("courses", {"enrollment_state": "active", "per_page": 100})
    grupos = cv.get("users/self/groups", {"per_page": 100})
    print("\nCursos activos:")
    for c in cursos:
        print(f"  {c['id']}  {c.get('course_code', '')}  {c.get('name', '')}")
        for g in [g for g in grupos if g.get("course_id") == c["id"]]:
            miembros = cv.get(f"groups/{g['id']}/users", {"per_page": 100})
            print(f"      grupo «{g['name']}» (id {g['id']}): {', '.join(u['name'] for u in miembros)}")


def cmd_cursos(cv: Canvas, args) -> None:
    reg = {c["id"]: c for c in cursos_registrados()}
    for c in cv.get("courses", {"enrollment_state": "active", "per_page": 100}):
        r = reg.get(c["id"])
        print(f"{c['id']}  {c.get('course_code', ''):22}  {c.get('name', '')}"
              + (f"  → cursos/{r['slug']}/" if r else "  (sin carpeta en el repo)"))


def _asignaciones(cv: Canvas, cid: int) -> list:
    return cv.get(f"courses/{cid}/assignments", {"include[]": ["submission"], "per_page": 100, "order_by": "due_at"})


def cmd_pendientes(cv: Canvas, args) -> None:
    ids = [resolver_curso(args.curso)] if args.curso else [c["id"] for c in cv.get("courses", {"enrollment_state": "active", "per_page": 100})]
    nombres = {c["id"]: c["name"] for c in cursos_registrados()}
    ahora = dt.datetime.now(TZ)
    limite = ahora + dt.timedelta(days=args.dias)
    filas = []
    for cid in ids:
        for a in _asignaciones(cv, cid):
            sub = a.get("submission") or {}
            if "none" in a.get("submission_types", []) or "not_graded" in a.get("submission_types", []):
                continue
            if sub.get("workflow_state") in ("submitted", "graded", "pending_review") or sub.get("excused"):
                continue
            due = local_dt(a.get("due_at"))
            if due and due > limite:
                continue
            filas.append((due or limite, cid, a, sub))
    if not filas:
        print(f"Nada pendiente en los próximos {args.dias} días.")
        return
    for due, cid, a, sub in sorted(filas, key=lambda x: x[0]):
        vencida = due < ahora
        etiqueta = "VENCIDA " if vencida else ""
        print(f"{etiqueta}{fmt_fecha(a.get('due_at'))}  [{cid} {nombres.get(cid, '')[:28]}]  "
              f"{a['name']}  ({modalidad(a)}, {a.get('points_possible')} pts, id {a['id']})")


def cmd_tareas(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    for a in _asignaciones(cv, cid):
        print(f"{a['id']}  {fmt_fecha(a.get('due_at'))}  {estado_entrega(a.get('submission')):22}  "
              f"{modalidad(a):10}  {a['name']}")


def cmd_tarea(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    a = cv.get(f"courses/{cid}/assignments/{args.tarea}",
               {"include[]": ["submission"]}, paginate=False)
    sub = a.get("submission") or {}
    print(f"# {a['name']}\n")
    print(f"- Vence: {fmt_fecha(a.get('due_at'))} (hora Ecuador) | Puntos: {a.get('points_possible')} | {modalidad(a)}")
    print(f"- Entrega: {', '.join(a.get('submission_types', []))}"
          + (f" | formatos: {', '.join(a['allowed_extensions'])}" if a.get("allowed_extensions") else ""))
    print(f"- Mi estado: {estado_entrega(sub)}" + (f" — {fmt_fecha(sub.get('submitted_at'))}" if sub.get("submitted_at") else ""))
    if sub.get("attachments"):
        for f in sub["attachments"]:
            print(f"  - archivo entregado: {f.get('display_name')} (id {f.get('id')})")
    print(f"- URL: {a.get('html_url')}\n")
    print(HtmlToMd(cv.base).convert(a.get("description")))
    if a.get("rubric"):
        print("\n## Rúbrica\n")
        print(rubrica_md(a["rubric"]))


def rubrica_md(rubric: list) -> str:
    lines = ["| Criterio | Pts | Niveles |", "|---|---|---|"]
    for r in rubric:
        niveles = "; ".join(f"{x.get('description', '')} ({x.get('points')})" for x in r.get("ratings", []))
        desc = (r.get("description") or "") + (f" — {r['long_description']}" if r.get("long_description") else "")
        lines.append(f"| {desc.replace('|', '/')} | {r.get('points')} | {niveles.replace('|', '/')} |")
    return "\n".join(lines)


def cmd_modulos(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    for m in cv.get(f"courses/{cid}/modules", {"include[]": ["items"], "per_page": 100}):
        print(f"\n## {m['position']}. {m['name']}")
        for i in m.get("items", []):
            ind = "  " * i.get("indent", 0)
            t = i["type"]
            if t == "SubHeader":
                print(f"{ind}**{i['title']}**")
            elif t == "File":
                print(f"{ind}- [archivo:{i.get('content_id')}] {i['title']}")
            elif t == "ExternalUrl":
                print(f"{ind}- [enlace] {i['title']} → {i.get('external_url')}")
            elif t == "Assignment":
                print(f"{ind}- [tarea:{i.get('content_id')}] {i['title']}")
            elif t == "Page":
                print(f"{ind}- [página:{i.get('page_url')}] {i['title']}")
            else:
                print(f"{ind}- [{t}] {i['title']}")


def cmd_pagina(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    p = cv.get(f"courses/{cid}/pages/{args.pagina}", paginate=False)
    print(f"# {p.get('title')}\n")
    print(HtmlToMd(cv.base).convert(p.get("body")))


def _dest_material(cid: int) -> Path:
    slug = next((c["slug"] for c in cursos_registrados() if int(c["id"]) == cid), str(cid))
    return TRABAJO / slug / "_material"


def cmd_descargar(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    destino = Path(args.dest) if args.dest else _dest_material(cid)
    for fid in args.archivos:
        try:
            f = cv.get(f"courses/{cid}/files/{fid}", paginate=False)
        except AulaError:
            f = cv.get(f"files/{fid}", paginate=False)
        dest = destino / f["display_name"]
        if dest.exists() and dest.stat().st_size == f.get("size") and not args.forzar:
            print(f"ya existe: {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest}")
            continue
        cv.download(f["url"], dest)
        print(f"descargado: {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest} ({f.get('size', 0) // 1024} KB)")


def cmd_notas(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    enr = cv.get(f"courses/{cid}/enrollments", {"user_id": "self"})
    for e in enr:
        g = e.get("grades") or {}
        print(f"Nota actual: {g.get('current_score')} | Nota final: {g.get('final_score')}")
    for a in _asignaciones(cv, cid):
        sub = a.get("submission") or {}
        if sub.get("score") is not None:
            print(f"  {sub.get('score'):>6} / {a.get('points_possible')}  {a['name']}")


def cmd_anuncios(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    for an in cv.get("announcements", {"context_codes[]": f"course_{cid}", "per_page": 20}):
        print(f"\n## {an['title']} — {fmt_fecha(an.get('posted_at'))} ({(an.get('author') or {}).get('display_name', '')})\n")
        print(HtmlToMd(cv.base).convert(an.get("message")))


def cmd_grupo(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    for g in cv.get("users/self/groups", {"per_page": 100}):
        if g.get("course_id") == cid:
            miembros = cv.get(f"groups/{g['id']}/users", {"per_page": 100})
            print(f"«{g['name']}» (id {g['id']}): {', '.join(u['name'] for u in miembros)}")


def cmd_api(cv: Canvas, args) -> None:
    params = [tuple(p.split("=", 1)) for p in args.params]
    print(json.dumps(cv.get(args.ruta, params or None), ensure_ascii=False, indent=1))


PERFIL_LOCAL = ROOT / "CLAUDE.local.md"
PLACEHOLDER_DISENO = "{{SISTEMA_DE_DISENO}}"


def _token_configurado() -> bool:
    try:
        load_env()
        return True
    except AulaError:
        return False


def _diseno_configurado() -> bool:
    return PERFIL_LOCAL.exists() and PLACEHOLDER_DISENO not in PERFIL_LOCAL.read_text(encoding="utf-8")


def cmd_contexto(cv: Canvas | None, args) -> None:
    """Contexto breve para el hook SessionStart: quién soy, grupos y próximas entregas (con caché)."""
    if not _token_configurado():
        print("CONFIGURACIÓN PENDIENTE: este estudiante todavía no conectó su Aula Virtual a este repo.\n"
              "En tu primera respuesta, antes de cualquier otra cosa, salúdalo, explícale en una frase qué es este "
              "repo y ofrece hacer la configuración guiada con el skill /configurar (toma 2 minutos: solo necesita "
              "su token de Aula Virtual y, opcionalmente, el nombre de su sistema de diseño).")
        return
    if not _diseno_configurado():
        print("Pendiente opcional: el estudiante no ha indicado su sistema de diseño para presentaciones "
              "(CLAUDE.local.md). Si pide una presentación, complétalo antes con /configurar.")
    cache = CACHE / "contexto.txt"
    if cache.exists() and time.time() - cache.stat().st_mtime < args.ttl * 60 and not args.refrescar:
        print(cache.read_text(encoding="utf-8"))
        return
    try:
        cv = cv or Canvas()
        me = cv.get("users/self")
        reg = {int(c["id"]): c for c in cursos_registrados()}
        cursos = cv.get("courses", {"enrollment_state": "active", "per_page": 100})
        grupos = cv.get("users/self/groups", {"per_page": 100})
        ahora = dt.datetime.now(TZ)
        lines = [f"Aula Virtual — estudiante: {me['name']} (hoy {DIAS[ahora.weekday()]} {ahora:%Y-%m-%d %H:%M}, hora Ecuador)"]
        pend = []
        for c in cursos:
            slug = reg.get(c["id"], {}).get("slug")
            lines.append(f"- Curso {c['id']} {c.get('name')}" + (f" → cursos/{slug}/" if slug else " (sin carpeta en el repo)"))
            for g in [g for g in grupos if g.get("course_id") == c["id"]]:
                miembros = cv.get(f"groups/{g['id']}/users", {"per_page": 100})
                lines.append(f"    grupo «{g['name']}»: {', '.join(u['name'] for u in miembros)}")
            for a in _asignaciones(cv, c["id"]):
                sub = a.get("submission") or {}
                if set(a.get("submission_types", [])) & {"none", "not_graded"}:
                    continue
                if sub.get("workflow_state") in ("submitted", "graded", "pending_review") or sub.get("excused"):
                    continue
                due = local_dt(a.get("due_at"))
                if due and due < ahora + dt.timedelta(days=10):
                    pend.append((due, c["id"], a))
        if pend:
            lines.append("Pendientes sin entregar (vencidas y próximos 10 días):")
            for due, cid, a in sorted(pend, key=lambda x: x[0]):
                tag = "VENCIDA " if due < ahora else ""
                lines.append(f"  {tag}{fmt_fecha(a.get('due_at'))}  [{cid}] {a['name']} ({modalidad(a)}, id {a['id']})")
        else:
            lines.append("Sin pendientes en los próximos 10 días.")
        txt = "\n".join(lines)
        CACHE.mkdir(parents=True, exist_ok=True)
        cache.write_text(txt, encoding="utf-8")
        print(txt)
    except AulaError as e:
        print(f"Aula Virtual no disponible: {e}. Si el token venció o fue revocado, ofrece /configurar.")


# ───────────────────────── configuración guiada ─────────────────────────


def _pedir_token(args) -> str:
    """Obtiene el token sin que pase por la conversación: diálogo oculto del sistema o portapapeles."""
    if args.portapapeles:
        cmds = {"darwin": ["pbpaste"], "win32": ["powershell", "-NoProfile", "-Command", "Get-Clipboard"]}
        cmd = cmds.get(sys.platform, ["xclip", "-selection", "clipboard", "-o"])
        import subprocess
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            raise AulaError("No se pudo leer el portapapeles en este sistema") from None
    if sys.platform == "darwin":
        import subprocess
        script = [
            "-e", "activate",
            "-e", 'display dialog "Pega tu token de Aula Virtual (no se mostrará en el chat):" default answer "" '
                  'with hidden answer with title "MBA ESPAE · Configuración" buttons {"Cancelar", "Guardar"} '
                  'default button "Guardar" cancel button "Cancelar" giving up after 600',
            "-e", "text returned of result",
        ]
        r = subprocess.run(["osascript", *script], capture_output=True, text=True)
        if r.returncode != 0:
            raise AulaError("Configuración cancelada en el diálogo")
        return r.stdout.strip()
    try:
        import tkinter
        from tkinter import simpledialog

        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        tok = simpledialog.askstring("MBA ESPAE · Configuración", "Pega tu token de Aula Virtual:", show="*", parent=root)
        root.destroy()
        if not tok:
            raise AulaError("Configuración cancelada en el diálogo")
        return tok.strip()
    except ImportError:
        raise AulaError("Este sistema no puede mostrar el diálogo: copia el token y usa --portapapeles") from None


def cmd_configurar(args) -> None:
    token = re.sub(r"\s+", "", _pedir_token(args))
    if not token or len(token) < 20:
        raise AulaError("Eso no parece un token de Aula Virtual (está vacío o es muy corto)")
    base = "https://postgradosvirtual.espol.edu.ec"
    req = urllib.request.Request(f"{base}/api/v1/users/self", headers={"Authorization": f"Bearer {token}"})
    try:
        me = json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        raise AulaError(f"Aula Virtual rechazó el token (HTTP {e.code}). Genera uno nuevo y vuelve a intentar") from None
    except urllib.error.URLError as e:
        raise AulaError(f"No se pudo conectar a Aula Virtual: {e.reason}") from None
    env = ROOT / ".env"
    env.write_text(f"CANVAS_BASE_URL={base}\nCANVAS_TOKEN={token}\n", encoding="utf-8")
    try:
        os.chmod(env, 0o600)
    except OSError:
        pass
    (CACHE / "contexto.txt").unlink(missing_ok=True)
    print(f"Token guardado y verificado. Aula Virtual te reconoce como: {me['name']} (id {me['id']}).")


# ───────────────────────── comandos de escritura ─────────────────────────


def _grupo_ya_entrego(a: dict) -> bool:
    sub = a.get("submission") or {}
    return sub.get("workflow_state") in ("submitted", "graded", "pending_review")


def cmd_entregar(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    a = cv.get(f"courses/{cid}/assignments/{args.tarea}", {"include[]": ["submission"]}, paginate=False)
    archivos = [Path(p).expanduser().resolve() for p in args.archivos]
    for f in archivos:
        if not f.is_file():
            raise AulaError(f"No existe el archivo {f}")
        ext = f.suffix.lstrip(".").lower()
        if a.get("allowed_extensions") and ext not in [e.lower() for e in a["allowed_extensions"]]:
            raise AulaError(f"{f.name}: la tarea solo acepta {', '.join(a['allowed_extensions'])}")
    if "online_upload" not in a.get("submission_types", []):
        raise AulaError(f"La tarea no acepta archivos (tipos: {', '.join(a.get('submission_types', []))})")
    print(f"Tarea: {a['name']} (id {a['id']}, {modalidad(a)})")
    print(f"Vence: {fmt_fecha(a.get('due_at'))}  | Estado actual: {estado_entrega(a.get('submission'))}")
    print("Archivos: " + ", ".join(f"{f.name} ({f.stat().st_size // 1024} KB)" for f in archivos))
    if args.comentario:
        print(f"Comentario: {args.comentario}")
    if modalidad(a) == "grupal" and _grupo_ya_entrego(a):
        print("ATENCIÓN: tu grupo ya tiene una entrega; una nueva la reemplaza para todo el grupo.")
    if not args.confirmar:
        print("\nSimulación: no se envió nada. Repite con --confirmar para entregar.")
        return
    ids = []
    for f in archivos:
        up = cv.upload_file(f"courses/{cid}/assignments/{a['id']}/submissions/self/files", f)
        ids.append(str(up["id"]))
        print(f"subido: {f.name} (archivo {up['id']})")
    fields = [("submission[submission_type]", "online_upload")] + [("submission[file_ids][]", i) for i in ids]
    if args.comentario:
        fields.append(("comment[text_comment]", args.comentario))
    s = cv.post(f"courses/{cid}/assignments/{a['id']}/submissions", fields)
    (CACHE / "contexto.txt").unlink(missing_ok=True)  # el resumen de inicio de sesión queda desactualizado
    print(f"ENTREGADA: intento {s.get('attempt')} — {fmt_fecha(s.get('submitted_at'))}")


def cmd_comentar(cv: Canvas, args) -> None:
    cid = resolver_curso(args.curso)
    a = cv.get(f"courses/{cid}/assignments/{args.tarea}", paginate=False)
    print(f"Tarea: {a['name']}\nComentario: {args.texto}")
    if not args.confirmar:
        print("\nSimulación: no se envió nada. Repite con --confirmar para publicar el comentario.")
        return
    cv._request("PUT", cv._url(f"courses/{cid}/assignments/{a['id']}/submissions/self"),
                urllib.parse.urlencode([("comment[text_comment]", args.texto)]).encode(),
                {"Content-Type": "application/x-www-form-urlencoded"})
    print("Comentario publicado.")


# ───────────────────────── sincronización del repo (admin) ─────────────────────────

GEN_INI, GEN_FIN = "<!-- aula:inicio — generado por tools/aula.py sync; no editar a mano -->", "<!-- aula:fin -->"


def _reemplazar_generado(path: Path, generado: str, plantilla_manual: str) -> None:
    """Escribe el bloque generado y conserva lo que esté fuera de las marcas."""
    bloque = f"{GEN_INI}\n{generado.strip()}\n{GEN_FIN}"
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        if GEN_INI in txt and GEN_FIN in txt:
            ini, fin = txt.index(GEN_INI), txt.index(GEN_FIN) + len(GEN_FIN)
            nuevo = txt[:ini] + bloque + txt[fin:]
            if nuevo != txt:
                path.write_text(nuevo, encoding="utf-8")
            return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plantilla_manual.replace("{{GENERADO}}", bloque), encoding="utf-8")


def _codigo_actividad(nombre: str) -> str | None:
    m = re.search(r"Actividad\s+(\d+(?:\.\d+)?)", nombre, re.I)
    return m.group(1) if m else None


def _archivos_en_html(raw: str | None) -> list:
    return sorted(set(re.findall(r"/files/(\d+)", raw or "")), key=int)


def cmd_sync(cv: Canvas, args) -> None:
    cid = int(args.curso_id)
    curso = cv.get(f"courses/{cid}", {"include[]": ["syllabus_body", "teachers", "term"]}, paginate=False)
    reg = cursos_registrados()
    entrada = next((c for c in reg if int(c["id"]) == cid), None)
    slug = args.slug or (entrada or {}).get("slug") or slugify(re.sub(r"^MBA\d*\s*\|\s*", "", curso["name"]))
    base = ROOT / "cursos" / slug
    conv = HtmlToMd(cv.base)
    hoy = dt.datetime.now(TZ).strftime("%Y-%m-%d")

    modulos = cv.get(f"courses/{cid}/modules", {"include[]": ["items", "content_details"], "per_page": 100})
    asign = cv.get(f"courses/{cid}/assignments", {"per_page": 100, "order_by": "due_at"})
    modulo_de = {i.get("content_id"): m["name"] for m in modulos for i in m.get("items", []) if i["type"] == "Assignment"}

    # nombres de archivos enlazados en enunciados (con un GET por archivo)
    nombres_archivo: dict = {}

    def nombre_archivo(fid: str) -> str:
        if fid not in nombres_archivo:
            try:
                f = cv.get(f"courses/{cid}/files/{fid}", paginate=False)
                nombres_archivo[fid] = f"{f['display_name']} ({f.get('size', 0) // 1024} KB)"
            except AulaError:
                nombres_archivo[fid] = "(sin acceso)"
        return nombres_archivo[fid]

    # ── fichas de actividades
    fichas = []
    usados = set()
    for a in asign:
        tipos = a.get("submission_types", [])
        if tipos == ["none"]:  # registros de asistencia: van solo al índice
            fichas.append((a, None))
            continue
        cod = _codigo_actividad(a["name"])
        nombre = nombre_ficha(a["name"])
        if nombre in usados:
            nombre += f"-{a['id']}"
        usados.add(nombre)
        archivo = base / "actividades" / f"{nombre}.md"
        adj = _archivos_en_html(a.get("description"))
        fm = {
            "canvas_id": a["id"],
            "curso_id": cid,
            "codigo": cod or "",
            "titulo": a["name"],
            "modalidad": modalidad(a),
            "entrega": ", ".join(tipos),
            "formatos": ", ".join(a.get("allowed_extensions") or []) or "cualquiera",
            "vence": fmt_fecha(a.get("due_at"), con_dia=False) + " (hora Ecuador)" if a.get("due_at") else "sin fecha",
            "puntos": int(a["points_possible"]) if a.get("points_possible") is not None else None,
            "modulo": modulo_de.get(a["id"], ""),
            "url": a.get("html_url"),
        }
        partes = [f"## Enunciado (Aula Virtual)\n\n{conv.convert(a.get('description')) or '_El docente no publicó instrucciones._'}"]
        if a.get("rubric"):
            partes.append("## Rúbrica (Aula Virtual)\n\n" + rubrica_md(a["rubric"]))
        if adj:
            partes.append("## Materiales enlazados\n\n" + "\n".join(
                f"- {nombre_archivo(f)} — `python3 tools/aula.py descargar {cid} {f}`" for f in adj))
        partes.append(f"_Sincronizado: {hoy}._")
        frontmatter = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()) + "\n---\n"
        plantilla = (frontmatter + f"\n# {a['name']}\n\n{{{{GENERADO}}}}\n\n"
                     "## Notas del curso\n\n"
                     "<!-- Curado por el admin: aclaraciones del docente, trampas, criterios no escritos. "
                     "Lo que esté fuera de las marcas aula:inicio/fin no se sobrescribe. -->\n")
        # el frontmatter también se regenera: va dentro de un archivo cuyo encabezado se reescribe
        if archivo.exists():
            txt = archivo.read_text(encoding="utf-8")
            if txt.startswith("---\n"):
                txt = frontmatter + txt.split("\n---\n", 1)[1]
                archivo.write_text(txt, encoding="utf-8")
        _reemplazar_generado(archivo, "\n\n".join(partes), plantilla)
        fichas.append((a, archivo))

    # ── materiales por módulo
    mat = [f"# Materiales — {curso['name']}\n",
           "Índice generado desde los módulos de Aula Virtual. Los archivos NO se versionan: "
           f"se descargan bajo demanda a `mi-trabajo/{slug}/_material/` con `python3 tools/aula.py descargar {cid} <id> [<id> ...]`.\n",
           "➡️ = lectura sugerida por el docente.\n"]
    for m in modulos:
        mat.append(f"\n## {m['position']}. {m['name']}\n")
        for i in m.get("items", []):
            ind = "  " * max(0, i.get("indent", 0) - 1)
            t = i["type"]
            if t == "SubHeader":
                mat.append(f"\n**{i['title'].strip()}**\n")
            elif t == "File":
                mat.append(f"{ind}- {i['title'].strip()} — archivo `{i.get('content_id')}`")
            elif t == "ExternalUrl":
                mat.append(f"{ind}- {i['title'].strip()} — {i.get('external_url')}")
            elif t == "Page":
                mat.append(f"{ind}- Página: {i['title'].strip()} — `python3 tools/aula.py pagina {cid} {i.get('page_url')}`")
            elif t == "Assignment":
                mat.append(f"{ind}- Tarea: {i['title'].strip()} (id {i.get('content_id')})")
    (base).mkdir(parents=True, exist_ok=True)
    (base / "materiales.md").write_text("\n".join(mat).strip() + f"\n\n_Sincronizado: {hoy}._\n", encoding="utf-8")

    # ── páginas informativas del curso (cronograma, políticas, etc.) → paginas.md
    pags = [f"# Páginas informativas — {curso['name']}\n",
            "Copia de las páginas del curso en Aula Virtual (cronograma, políticas, soporte...). Generado; no editar.\n"]
    if curso.get("syllabus_body"):
        pags.append("## Programa del curso (syllabus)\n\n" + conv.convert(curso["syllabus_body"]))
    for m in modulos:
        for i in m.get("items", []):
            if i["type"] == "Page":
                p = cv.get(f"courses/{cid}/pages/{i['page_url']}", paginate=False)
                cuerpo = conv.convert(p.get("body"))
                cuerpo = re.sub(r"^(#{1,5}) ", r"#\1 ", cuerpo, flags=re.M)
                pags.append(f"## {i['title'].strip()}\n\n{cuerpo or '_(vacía)_'}")
    (base / "paginas.md").write_text("\n\n".join(pags).strip() + f"\n\n_Sincronizado: {hoy}._\n", encoding="utf-8")

    # ── bloque generado del CLAUDE.md del curso
    docentes = ", ".join(t["display_name"].title() for t in curso.get("teachers", []))
    gen = ["## Datos de Aula Virtual\n",
           f"- Curso: **{curso['name']}** — código `{curso.get('course_code')}`, id Canvas `{cid}`",
           f"- Docentes: {docentes}",
           f"- Programa: {(curso.get('term') or {}).get('name', '')}",
           f"- URL: {cv.base}/courses/{cid}",
           f"- Sincronizado: {hoy}\n",
           "### Actividades\n",
           f"Mi estado en cada una (personal, no se versiona): `python3 tools/aula.py tareas {cid}`.\n",
           "| Vence (Ecuador) | Actividad | Modalidad | Pts | Ficha |", "|---|---|---|---|---|"]
    for a, f in sorted(fichas, key=lambda x: x[0].get("due_at") or "9999"):
        ficha = f"[{f.stem}](actividades/{f.name})" if f else "— (asistencia)"
        nombre_tabla = re.sub(r"^(Actividad\s+[\d.]+)\s*\|\s*(Tarea|Actividad)\s+(individual|grupal)\s*[>|]\s*",
                              r"\1 · ", a["name"].strip(), flags=re.I).replace("|", "/")
        pts = a.get("points_possible")
        gen.append(f"| {fmt_fecha(a.get('due_at'))} | {nombre_tabla} | {modalidad(a)} | "
                   f"{int(pts) if pts is not None else '—'} | {ficha} |")
    gen.append("\n### Módulos\n")
    gen += [f"{m['position']}. {m['name'].strip()}" for m in modulos]
    gen.append("\nLecturas y archivos con sus ids: [materiales.md](materiales.md). "
               "Cronograma, políticas y demás páginas del curso: [paginas.md](paginas.md).")
    plantilla_curso = (
        f"# {curso['name']}\n\n"
        "Contexto del curso para Claude Code. El bloque entre las marcas `aula:` lo regenera el admin con "
        "`/sync-curso`; todo lo demás es curado a mano y se conserva.\n\n"
        "## Cómo trabajar este curso\n\n"
        "- Empieza siempre por la ficha de la actividad en `actividades/` (formato estándar, ver `docs/ficha-actividad.md`).\n"
        "- Lecturas y archivos: `materiales.md`; se descargan bajo demanda a `mi-trabajo/`, nunca se versionan.\n"
        f"- Trabajo personal: `mi-trabajo/{slug}/<nombre-de-la-ficha>/` (ignorado por git).\n\n"
        "{{GENERADO}}\n\n"
        "## Fechas clave\n\n<!-- Curado: sesiones, evaluación final, requisitos de aprobación. -->\n\n"
        "## Conceptos clave por sesión\n\n<!-- Curado: marcos teóricos que el docente espera ver aplicados. -->\n\n"
        "## Notas del curso\n\n<!-- Curado: criterios del docente, preferencias de formato, avisos dados en clase. -->\n"
    )
    _reemplazar_generado(base / "CLAUDE.md", "\n".join(gen), plantilla_curso)

    # ── registro
    if not entrada:
        reg.append({"id": cid, "slug": slug, "nombre": curso["name"], "codigo": curso.get("course_code")})
        CURSOS_JSON.parent.mkdir(parents=True, exist_ok=True)
        CURSOS_JSON.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n = len([f for _, f in fichas if f])
    print(f"Sincronizado cursos/{slug}/: CLAUDE.md, materiales.md y {n} fichas en actividades/")


# ───────────────────────── CLI ─────────────────────────


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="aula", description="CLI de Aula Virtual (Canvas) para el repo MBA ESPAE")
    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("yo", help="usuario, cursos activos y grupos con integrantes")
    sp.add_parser("cursos", help="cursos activos y si tienen carpeta en el repo")
    x = sp.add_parser("pendientes", help="tareas sin entregar (vencidas y próximas)")
    x.add_argument("--curso")
    x.add_argument("--dias", type=int, default=21)
    x = sp.add_parser("tareas", help="todas las tareas de un curso con mi estado")
    x.add_argument("curso")
    x = sp.add_parser("tarea", help="enunciado completo, rúbrica y mi estado de una tarea")
    x.add_argument("curso")
    x.add_argument("tarea", type=int)
    x = sp.add_parser("modulos", help="estructura de módulos con ids de archivos y tareas")
    x.add_argument("curso")
    x = sp.add_parser("pagina", help="contenido de una página del curso")
    x.add_argument("curso")
    x.add_argument("pagina")
    x = sp.add_parser("descargar", help="descarga archivos por id a mi-trabajo/<curso>/_material/")
    x.add_argument("curso")
    x.add_argument("archivos", nargs="+")
    x.add_argument("--dest")
    x.add_argument("--forzar", action="store_true")
    x = sp.add_parser("notas", help="calificaciones publicadas")
    x.add_argument("curso")
    x = sp.add_parser("anuncios", help="anuncios del curso")
    x.add_argument("curso")
    x = sp.add_parser("grupo", help="mis grupos en un curso con integrantes")
    x.add_argument("curso")
    x = sp.add_parser("api", help="GET de solo lectura a cualquier endpoint (escape hatch)")
    x.add_argument("ruta", help="p.ej. courses/5121/discussion_topics")
    x.add_argument("params", nargs="*", help="clave=valor")
    x = sp.add_parser("configurar", help="guarda y verifica tu token (diálogo oculto, no pasa por el chat)")
    x.add_argument("--portapapeles", action="store_true", help="leer el token del portapapeles en vez del diálogo")
    x = sp.add_parser("contexto", help="resumen breve para el hook de inicio de sesión")
    x.add_argument("--ttl", type=int, default=60, help="minutos de caché")
    x.add_argument("--refrescar", action="store_true")
    x = sp.add_parser("entregar", help="ESCRIBE: entrega archivos en una tarea (requiere --confirmar)")
    x.add_argument("curso")
    x.add_argument("tarea", type=int)
    x.add_argument("archivos", nargs="+")
    x.add_argument("--comentario")
    x.add_argument("--confirmar", action="store_true")
    x = sp.add_parser("comentar", help="ESCRIBE: comentario en mi entrega (requiere --confirmar)")
    x.add_argument("curso")
    x.add_argument("tarea", type=int)
    x.add_argument("texto")
    x.add_argument("--confirmar", action="store_true")
    x = sp.add_parser("sync", help="ADMIN: regenera cursos/<slug>/ desde Aula Virtual")
    x.add_argument("curso_id")
    x.add_argument("--slug")

    args = p.parse_args(argv)
    handlers = {
        "yo": cmd_yo, "cursos": cmd_cursos, "pendientes": cmd_pendientes, "tareas": cmd_tareas,
        "tarea": cmd_tarea, "modulos": cmd_modulos, "pagina": cmd_pagina, "descargar": cmd_descargar,
        "notas": cmd_notas, "anuncios": cmd_anuncios, "grupo": cmd_grupo, "api": cmd_api,
        "entregar": cmd_entregar, "comentar": cmd_comentar, "sync": cmd_sync,
    }
    try:
        if args.cmd == "contexto":
            cmd_contexto(None, args)
            return 0
        if args.cmd == "configurar":
            cmd_configurar(args)
            return 0
        handlers[args.cmd](Canvas(), args)
        return 0
    except AulaError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
