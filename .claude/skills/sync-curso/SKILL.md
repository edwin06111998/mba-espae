---
name: sync-curso
description: ADMIN. Sincroniza un curso de Aula Virtual al repo (CLAUDE.md del curso, fichas de actividades, materiales y páginas) y cura su contexto.
argument-hint: "<id del curso> [--slug carpeta]"
disable-model-invocation: true
allowed-tools: Bash(python3 tools/aula.py *) Bash(git status *) Bash(git diff *) Read Write Edit Glob Grep
---

# Sincronizar curso: `$ARGUMENTS`

Solo el admin del repo mantiene `cursos/`. Lee `docs/admin.md` antes de empezar.

## 1. Sincronizar

- Sin argumento: `python3 tools/aula.py cursos` y pregunta cuál.
- Curso nuevo: elige un slug corto en kebab-case sin tildes (p. ej. `mercadeo-investigacion-mercados`) y ejecuta `python3 tools/aula.py sync <id> --slug <slug>`.
- Curso existente: `python3 tools/aula.py sync <id>` (respeta lo curado fuera de las marcas `aula:inicio/fin`).
- Revisa `git status` y `git diff --stat cursos/`: fichas nuevas, cambios de enunciado o de fechas. Resume los cambios relevantes para los compañeros.

## 2. Curar (lo que el generador no sabe)

En `cursos/<slug>/CLAUDE.md`, fuera de las marcas:

- **Fechas clave**: sesiones, evaluación final y requisitos de aprobación, resumidos desde `paginas.md`.
- **Conceptos clave por sesión**: para cada sesión, los marcos teóricos que el docente espera ver aplicados, con su autor y año. Fuente: títulos de lecturas en `materiales.md` y, para precisión, las slides del profesor (descárgalas con `python3 tools/aula.py descargar` a `mi-trabajo/` y léelas; nunca las copies al repo). Una línea por concepto: nombre, idea central, cuándo aplicarlo.
- **Notas del curso**: criterios del docente, formatos preferidos, avisos de clase que el admin te cuente.

En cada ficha nueva, sección "Notas del curso": duplicados, enunciados incompletos (p. ej. "[completar fecha]"), diferencias entre versiones, qué cuenta para la nota.

## 3. Registrar

- Actualiza la tabla "Cursos" del `CLAUDE.md` raíz.
- Propón el commit (no lo hagas sin que el admin lo pida): `sync(<slug>): <qué cambió>`. Nunca incluyas `mi-trabajo/`, PDFs ni `.env`.
