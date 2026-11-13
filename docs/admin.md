# Guía del admin

El admin (Edwin Veloz) mantiene la parte versionada: `cursos/`, `tools/`, `docs/`, `plantillas/`, `.claude/`. Los compañeros hacen `git pull` y nunca editan esas carpetas (si ven un error, lo reportan).

## Agregar o actualizar un curso

1. `python3 tools/aula.py cursos`: lista cursos activos y cuáles ya tienen carpeta.
2. En Claude Code: `/sync-curso <id> --slug <carpeta>` (curso nuevo) o `/sync-curso <id>` (actualizar). Genera:
   - `cursos/<slug>/CLAUDE.md`: bloque generado (datos, tabla de actividades, módulos) + secciones curadas.
   - `cursos/<slug>/actividades/*.md`: una ficha por tarea (formato en `docs/ficha-actividad.md`).
   - `cursos/<slug>/materiales.md`: lecturas y archivos con sus ids (sin descargar).
   - `cursos/<slug>/paginas.md`: cronograma, políticas y demás páginas del curso.
   - Registro en `cursos/cursos.json`.
3. Curar fuera de las marcas `aula:inicio/fin`: **Fechas clave**, **Conceptos clave por sesión**, **Notas del curso** y las notas de cada ficha nueva.
4. Actualizar la tabla "Cursos" del `CLAUDE.md` raíz.
5. Commit y push: `sync(<slug>): <qué cambió>`.

Cuándo sincronizar: después de cada clase (los docentes publican tareas nuevas) y cuando cambie una fecha. Re-sincronizar es seguro: solo reescribe lo generado.

## Qué nunca va al repo

PDFs y demás material del curso (copyright; se descargan bajo demanda), `.env`, `mi-trabajo/`, `CLAUDE.local.md`, nombres de grupos o integrantes (dependen de cada estudiante y se consultan en vivo). El `.gitignore` ya lo cubre; revisa `git status` antes de cada commit.

## Compartir con compañeros

- Repositorio **privado**: https://github.com/edwin06111998/mba-espae. Invita a los compañeros con permiso de lectura: `gh api -X PUT repos/edwin06111998/mba-espae/collaborators/<usuario> -f permission=pull` (o desde Settings → Collaborators). Ellos reciben cursos nuevos pidiéndole a Claude "actualiza el repo".
- Onboarding: solo deben clonar, abrir Claude Code en la carpeta y escribir "hola"; el hook detecta que falta configuración y Claude ejecuta `/configurar`.
- Sistema de diseño: el repo no fija ninguno. Cada estudiante registra el suyo en su `CLAUDE.local.md` con `/configurar`; no agregues referencias a sistemas de diseño personales en archivos versionados.
- Versionado: un commit por sincronización; etiqueta (`git tag`) al cerrar cada curso, p. ej. `liderazgo-cerrado`.

## Mantener el CLI

`tools/aula.py` usa solo la librería estándar (Python 3.9+). Si Canvas cambia o hace falta un endpoint nuevo: agrégalo como subcomando de solo lectura; las acciones que escriben en Aula Virtual llevan `--confirmar` y una regla `ask` en `.claude/settings.json`.
