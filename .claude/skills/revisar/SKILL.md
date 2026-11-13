---
name: revisar
description: Evalúa un borrador o entregable contra la rúbrica de su actividad usando el subagente revisor-rubrica, y devuelve puntaje estimado por criterio, brechas y mejoras priorizadas. Úsalo antes de hacer la presentación o antes de entregar.
argument-hint: "[ruta del borrador o actividad]"
allowed-tools: Read Glob Grep Agent
---

# Revisar contra la rúbrica: `$ARGUMENTS`

1. Identifica el espacio de trabajo (`mi-trabajo/<curso>/<actividad>/`): por el argumento, por el directorio en el que se viene trabajando o preguntando. Lee su `README.md` para saber cuál es la ficha.
2. Identifica qué revisar: el borrador más reciente de `borradores/` o el PDF/HTML de `entregable/` si el argumento lo indica.
3. Lanza el subagente **revisor-rubrica** con: ruta de la ficha, ruta del `CLAUDE.md` del curso, ruta(s) del borrador, modalidad (individual/grupal) y si debe incluir declaración de IA y nombres de integrantes.
4. Presenta su resultado tal cual (tabla por criterio + 3–5 mejoras priorizadas por puntos en juego). No reescribas el borrador por iniciativa propia: pregunta qué mejoras aplicar.
5. Registra en la "Bitácora" del `README.md` del espacio de trabajo el puntaje estimado y las mejoras pendientes.
