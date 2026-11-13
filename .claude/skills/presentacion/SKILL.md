---
name: presentacion
description: Genera la presentación (deck de diapositivas) de una actividad del MBA como Artifact de tipo Slides con el sistema de diseño personal del estudiante, adaptado a uso académico, y la deja lista para exportar a PDF y entregar. Úsalo cuando la actividad pida diapositivas, exposición o presentación.
argument-hint: "[actividad]"
allowed-tools: Read Write Edit Glob Grep Artifact Bash(python3 tools/aula.py *)
---

# Presentación: `$ARGUMENTS`

Lee primero `docs/presentaciones.md` (sistema de diseño, adaptación académica, estructura del deck). Es obligatorio.

## 1. Insumos

- Espacio de trabajo `mi-trabajo/<curso>/<actividad>/`: `README.md` (plan, integrantes) y el borrador final de `borradores/`.
- Ficha de la actividad: qué exige la presentación (preguntas en orden, declaración de IA en la última diapositiva, nombres de integrantes, formato PDF).
- Integrantes reales: `python3 tools/aula.py grupo <curso>` si es grupal.

Si el borrador no está validado por el estudiante, detente y pídeselo: la presentación sintetiza un contenido ya decidido, no lo inventa.

## 2. Sistema de diseño del estudiante

1. Lee la línea `Sistema de diseño:` de `CLAUDE.local.md`. Si falta o dice `{{SISTEMA_DE_DISENO}}`, ejecuta el paso 2 de `/configurar` y vuelve.
2. Si es un nombre: lista los design systems (Artifact `list` con `type: "Design System"`), toma el que coincide (o su url si está registrada) y léelo (`read` de `project/README.md`). Si ya no aparece, díselo y pregunta si elegir otro.
3. Si es "ninguno": estilo sobrio por defecto (ver `docs/presentaciones.md`).
4. Aplica siempre la **adaptación académica**: sin logos ni marcas, sin copy comercial, tono académico.

## 3. Crear el deck

- Artifact `quickstart` con `intent: "slides"` y sigue sus instrucciones (tipo Slides, 16:9), usando el sistema de diseño del paso 2.
- Título del artifact: `<código> · <tema corto> — <grupo o apellido>`.
- Estructura: la de `docs/presentaciones.md` (portada → una sección por pregunta en el orden del enunciado → recomendación/conclusión → referencias → declaración de IA).
- Densidad: una idea por diapositiva; máximo ~40 palabras de cuerpo; el detalle va a las notas del presentador si el tipo lo permite.
- Guarda la URL del artifact en el `README.md` del espacio de trabajo (sección "Entregable").

## 4. Exportar y dejar listo para entregar

- El estudiante descarga el PDF desde la página del artifact (opción de descarga a PDF) y lo guarda en `mi-trabajo/<curso>/<actividad>/entregable/` con el nombre `<código>_<Tema>_<Grupo-o-Apellido>.pdf` (sin espacios ni tildes). Si no sabe dónde quedó la descarga, búscala en su carpeta de Descargas y muévela tú.
- Verifica el PDF guardado: número de diapositivas, que la última sea la declaración de IA y que estén todos los integrantes (`pdftotext` o Read).
- Siguiente paso: `/revisar entregable` y luego `/entregar`.

## Si no hay herramienta Artifact

Genera `entregable/presentacion.html` (16:9, una `<section>` por diapositiva, `@page { size: 1280px 720px }`) con los colores y la tipografía del sistema de diseño del estudiante (o el estilo sobrio por defecto), y expórtala a PDF con Chrome sin interfaz:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer --print-to-pdf="<ruta>.pdf" "<ruta>/presentacion.html"
```
