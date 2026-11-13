---
name: pendientes
description: Muestra las tareas pendientes del estudiante en Aula Virtual (vencidas y próximas), priorizadas, con su ficha y su espacio de trabajo. Úsalo cuando pregunten qué hay que entregar, qué vence, cómo van, o al empezar a trabajar.
argument-hint: "[curso] [días]"
allowed-tools: Bash(python3 tools/aula.py *) Read Glob Grep
---

# Pendientes

Estado en vivo (no uses la caché del inicio de sesión):

!`python3 tools/aula.py pendientes --dias 21`

Argumentos: `$ARGUMENTS` (si traen un curso o un número de días, vuelve a consultar con `--curso` / `--dias`).

## Qué hacer con esto

1. Agrupa en: **vencidas**, **vencen en ≤ 48 h**, **esta semana**, **después**. Hora de Ecuador.
2. Para cada una, ubica su ficha buscando `canvas_id: <id>` en `cursos/*/actividades/*.md` y si ya existe espacio de trabajo en `mi-trabajo/<curso>/<ficha>/` (lee su `README.md` para el estado).
3. Señala lo que cambia la prioridad:
   - Grupal sin entregar = **nadie del grupo ha entregado** (Canvas replica la entrega grupal a todos).
   - Tareas duplicadas o con notas del admin en la sección "Notas del curso" de la ficha.
   - Vencidas: Canvas suele seguir aceptando entregas atrasadas (quedan marcadas). Confírmalo con `python3 tools/aula.py tarea <curso> <id>` y no prometas que se aceptará.
4. Cierra con UNA recomendación concreta de por dónde empezar y el comando: `/actividad <código o nombre>`.

Formato: tabla corta por grupo de urgencia (vence · actividad · modalidad · ficha · estado del espacio de trabajo). Sin relleno.
