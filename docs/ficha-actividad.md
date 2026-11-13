# Formato estándar de la ficha de actividad

Cada tarea de Aula Virtual tiene una ficha en `cursos/<curso>/actividades/<nombre>.md`. La genera `python3 tools/aula.py sync <curso_id>` y la cura el admin. Es la **única fuente de contexto versionada** de una actividad; el estado personal (entregado, nota) se consulta en vivo con el CLI.

## Nombre del archivo

`<código>-<tema>.md`: código de la actividad si existe (`6.1`), tema en kebab-case sin tildes (máx. 45 caracteres), sin prefijos genéricos ("Análisis de caso", "Curso LinkedIn Learning"). Si dos tareas generan el mismo nombre (duplicadas en Canvas), la segunda lleva `-<canvas_id>`.

Los registros de asistencia no tienen ficha: solo aparecen en la tabla de actividades del `CLAUDE.md` del curso.

## Estructura

```markdown
---
canvas_id: 39890                 # id de la tarea en Canvas (clave para el CLI)
curso_id: 5121
codigo: "6.1"
titulo: "<nombre completo en Canvas>"
modalidad: "grupal"              # grupal | individual (según group_category_id)
entrega: "online_upload"         # tipos de entrega de Canvas
formatos: "pdf"                  # extensiones permitidas, o "cualquiera"
vence: "2026-11-12 23:59 (hora Ecuador)"
puntos: 100
modulo: "<módulo de Canvas donde está la tarea>"
url: "<enlace a la tarea en Aula Virtual>"
---

# <título>

<!-- aula:inicio … -->            ← GENERADO: se reescribe en cada sync
## Enunciado (Aula Virtual)       instrucciones convertidas de HTML a Markdown
## Rúbrica (Aula Virtual)         solo si el docente adjuntó una rúbrica de Canvas
## Materiales enlazados           archivos citados en el enunciado + comando para descargarlos
<!-- aula:fin -->

## Notas del curso                ← CURADO: nunca se sobrescribe
```

## Reglas

- El frontmatter y el bloque entre `aula:inicio` y `aula:fin` son del generador: no se editan a mano.
- Todo lo curado va **fuera** de las marcas, en "Notas del curso": duplicados, contradicciones del enunciado, aclaraciones del docente en clase, criterios no escritos.
- Muchas rúbricas vienen dentro del enunciado (tablas de criterios con puntos) y no como rúbrica de Canvas: Claude debe buscarlas en el enunciado.
- `[archivo:<id>]` en el enunciado es un archivo de Canvas: `python3 tools/aula.py descargar <curso_id> <id>`.
