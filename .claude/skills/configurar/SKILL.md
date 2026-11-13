---
name: configurar
description: Configuración guiada del repo para un estudiante nuevo o para renovar el token. Conecta su Aula Virtual (token personal, sin que pase por el chat) y registra su sistema de diseño para presentaciones. Úsalo cuando el contexto de inicio diga CONFIGURACIÓN PENDIENTE, cuando el token falle o venza, o cuando el estudiante quiera cambiar su sistema de diseño.
allowed-tools: Bash(python3 tools/aula.py *) Bash(python tools/aula.py *) Bash(python3 --version) Bash(python --version) Bash(open https://postgradosvirtual.espol.edu.ec/*) Read Write Edit Artifact
---

# Configuración guiada

El estudiante puede no ser técnico: no le hables de Python, `.env`, variables de entorno ni terminal. Pasos cortos, uno a la vez, en tono amable. Toma ~2 minutos.

## 0. Requisito silencioso

Ejecuta `python3 --version` (si falla, `python --version`; desde ahí usa ese comando en lugar de `python3`). Si ninguno existe, explícale cómo instalarlo y detente hasta que esté:
- macOS: aceptar la ventana "Instalar herramientas de línea de comandos" que aparece al intentarlo, o descargar Python desde python.org.
- Windows: instalador de python.org marcando "Add python.exe to PATH"; luego reabrir Claude Code.

## 1. Token de Aula Virtual

Explícale en 2 líneas: el token es una llave personal para que Claude consulte sus tareas y materiales; se guarda solo en su computadora y nunca debe pegarse en el chat.

Ofrece abrir la página (en macOS: `open https://postgradosvirtual.espol.edu.ec/profile/settings`) y dale estos pasos:

1. Inicia sesión en Aula Virtual si te lo pide. Estás en **Cuenta → Configuración**.
2. Baja hasta **Integraciones aprobadas** y pulsa **+ Nuevo token de acceso**.
3. Propósito: `Claude Code MBA`. Fecha de expiración: el fin del semestre (o déjala vacía si lo permite).
4. Pulsa **Generar token** y **copia** el texto largo que aparece (solo se muestra una vez).
5. Escríbeme **"listo"** (no pegues el token aquí).

Cuando diga "listo": `python3 tools/aula.py configurar --portapapeles`. El token se lee del portapapeles, se verifica contra Aula Virtual y se guarda; nunca aparece en la conversación.

- Si falla la lectura del portapapeles o el token no es válido: `python3 tools/aula.py configurar` (abre una ventana para pegarlo) y pídele que lo pegue ahí.
- Si el estudiante pega el token en el chat por error: no lo uses; recomiéndale borrarlo en Aula Virtual (ícono de papelera junto al token) y generar otro.
- Si el botón "+ Nuevo token de acceso" no aparece: la institución lo deshabilitó; avísale que el repo funciona igual con las fichas y materiales versionados, pero sin datos en vivo, y que lo consulte con el admin.

## 2. Sistema de diseño para presentaciones

Cada estudiante usa **su propio** sistema de diseño de Claude (artifact de tipo Design System en claude.ai).

1. Lista los que puede abrir: Artifact `list` con `type: "Design System"`. Muéstrale solo los nombres.
2. Pregúntale cuál usar para sus presentaciones del MBA. Opciones: uno de la lista, "ninguno por ahora" o "créame uno" (en ese caso, crea uno sobrio y académico con el tipo Design System: Artifact `quickstart` con `intent: "other"`).
3. Si la herramienta Artifact no está disponible, pregúntale el nombre exacto tal como aparece en claude.ai.

## 3. Guardar su perfil local

- Si no existe `CLAUDE.local.md` en la raíz, créalo copiando `plantillas/perfil-local.md`.
- Reemplaza `{{SISTEMA_DE_DISENO}}` por `<nombre exacto> — <url del artifact>` o por `ninguno (Claude elige un estilo sobrio y académico)`.
- Si ya existía, cambia solo esa línea.

Este archivo es personal (git lo ignora) y Claude Code lo carga en cada sesión.

## 4. Cierre

- `python3 tools/aula.py contexto --refrescar` y muéstrale en 3–5 líneas: su nombre, sus cursos, sus grupos y lo más urgente.
- Dile qué puede pedir a partir de ahora, en lenguaje natural: "¿qué tengo pendiente?", "ayúdame con la actividad 6.1", "hazme la presentación", "entrega mi PDF", "actualiza el repo".
