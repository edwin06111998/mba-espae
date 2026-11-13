---
name: actividad
description: Abre o retoma una actividad del MBA. Ubica su ficha, consulta el estado en vivo en Aula Virtual, crea el espacio de trabajo personal en mi-trabajo/, descarga y lee los materiales, y propone un plan alineado a la rúbrica. Úsalo cuando el estudiante quiera empezar, continuar o entender una tarea, caso o actividad.
argument-hint: "<código, nombre o id de la actividad>"
allowed-tools: Bash(python3 tools/aula.py *) Bash(mkdir -p mi-trabajo/*) Bash(cp -R plantillas/*) Bash(pdftotext *) Read Write Edit Glob Grep
---

# Abrir o retomar una actividad: `$ARGUMENTS`

## 1. Ubicar la ficha

Busca en `cursos/*/actividades/*.md` por código (`codigo: "6.1"`), id (`canvas_id: 39890`) o palabras del título. Si hay más de una coincidencia (p. ej. tareas duplicadas en Canvas), lee la sección "Notas del curso" de ambas y pregunta solo si las notas no lo resuelven. Si el curso aún no tiene carpeta, trabaja directo con `python3 tools/aula.py tarea <curso> <id>` y avisa que la ficha falta (el admin la genera con `/sync-curso`).

Lee: la ficha completa, el `CLAUDE.md` del curso (fechas, **conceptos clave**, notas del curso) y `docs/ficha-actividad.md` si dudas del formato.

## 2. Estado en vivo

- `python3 tools/aula.py tarea <curso_id> <canvas_id>`: estado de entrega, fecha, formatos aceptados.
- Si es grupal: `python3 tools/aula.py grupo <curso_id>` para los integrantes reales del grupo de este estudiante.

## 3. Espacio de trabajo

Ruta: `mi-trabajo/<carpeta-del-curso>/<nombre-de-la-ficha-sin-.md>/`.

- Si no existe: `mkdir -p` de la ruta y `cp -R plantillas/actividad/. <ruta>/`. Luego completa el encabezado del `README.md` (ficha, id, vence, modalidad, integrantes, estado `en curso`).
- Si existe: lee su `README.md` y retoma desde "Siguiente paso". No sobrescribas nada.

## 4. Materiales

- Descarga los "Materiales enlazados" de la ficha: `python3 tools/aula.py descargar <curso_id> <id> ...` (quedan en `mi-trabajo/<curso>/_material/`, compartidos entre actividades del curso).
- Para PDFs largos genera texto buscable: `pdftotext -layout "<pdf>" "<pdf>.txt"` (si no existe `pdftotext`, lee el PDF con Read por rangos de páginas).
- Si la actividad se apoya en lecturas o slides de una sesión, búscalas en `materiales.md` del curso y descarga solo las pertinentes (prioriza las marcadas ➡️ y las slides del profesor).
- Lee el caso completo antes de opinar. Anota en `notas/caso.md` los hechos clave con su página: protagonistas, cronología, cifras, citas textuales, decisión pendiente.

## 5. Plan alineado a la rúbrica

Escribe en el `README.md` del espacio de trabajo:

- **Qué se entrega exactamente** (formato, extensión, PDF, declaración de IA, nombres).
- **Mapa pregunta → criterio de rúbrica → peso**. Lo de mayor peso recibe más profundidad.
- **Marcos del curso aplicables** a cada pregunta (de "Conceptos clave" y de las lecturas).
- **Reparto** (si es grupal): qué hace el estudiante y qué falta del equipo. Recuerda que el equipo debe validar conclusiones.

Muestra el plan al estudiante en ≤ 15 líneas y pregúntale cómo quiere avanzar: borrador completo para revisar, pregunta por pregunta, o solo estructura y él redacta. No redactes el entregable final sin ese acuerdo.

## 6. Mientras se trabaja

- Borradores en `borradores/` (Markdown). Una sección por pregunta, en el orden del enunciado.
- Cada afirmación sobre el caso cita página; cada concepto, su fuente (APA 7). No inventes.
- Actualiza "Bitácora" y "Siguiente paso" del `README.md` al cerrar cada bloque de trabajo.
- Siguientes pasos naturales: `/revisar` → `/presentacion` → `/declaracion-ia` → `/entregar`.
