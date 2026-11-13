---
name: entregar
description: Entrega un archivo en una tarea de Aula Virtual tras verificaciones y confirmación explícita del estudiante.
argument-hint: "[actividad] [archivo]"
disable-model-invocation: true
allowed-tools: Bash(python3 tools/aula.py tarea *) Bash(python3 tools/aula.py grupo *) Bash(pdftotext *) Read Glob Grep Edit
---

# Entregar en Aula Virtual: `$ARGUMENTS`

Entregar es una acción **visible para el docente y, si es grupal, para todo el grupo**. Una nueva entrega reemplaza la anterior del grupo.

## 1. Identificar

- Actividad: por argumento o por el espacio de trabajo actual. Lee la ficha (curso, `canvas_id`, formatos, "Notas del curso": p. ej. tareas duplicadas donde hay que subir en ambas).
- Archivo: en `mi-trabajo/<curso>/<actividad>/entregable/`. Si hay varios, pregunta cuál.

## 2. Verificar (todo, antes de preguntar)

- `python3 tools/aula.py tarea <curso_id> <canvas_id>`: estado actual, fecha de vencimiento, formatos aceptados.
- Extensión permitida y tamaño razonable.
- Contenido (`pdftotext -layout` o Read): están todas las preguntas, la **declaración de IA** y, si es grupal, los **nombres de todos los integrantes** según `python3 tools/aula.py grupo <curso_id>`.
- Si el estado ya es "entregada" (en grupales significa que alguien del grupo ya entregó): muestra fecha y archivo entregado (salen en `tarea`) y advierte que se reemplazará para todos.
- Si está vencida: avisa que quedará marcada como atrasada.

Si algo falla, detente y dilo. No entregues "para no perder la fecha" sin que el estudiante lo decida.

## 3. Confirmar

Muestra un resumen de 5 líneas (tarea, id, archivo, estado actual y qué cambiará, advertencias) y pregunta literalmente: **"¿Confirmas que entregue este archivo?"**. Solo un "sí" explícito del estudiante en este turno cuenta como confirmación.

## 4. Entregar y verificar

```
python3 tools/aula.py entregar <curso_id> <canvas_id> "<ruta del archivo>" --confirmar [--comentario "..."]
```

Claude Code pedirá además aprobar el comando (regla `ask` del repo): es la segunda confirmación, a propósito.

Después: `python3 tools/aula.py tarea <curso_id> <canvas_id>` para comprobar el estado "entregada", y actualiza el `README.md` del espacio de trabajo (estado `entregada`, fecha, intento, archivo). Si la ficha indica que la misma entrega va en otra tarea (duplicadas), recuérdalo y repite el proceso con su id.
