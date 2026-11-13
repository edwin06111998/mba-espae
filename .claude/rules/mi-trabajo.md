---
paths:
  - "mi-trabajo/**"
---

# Convenciones de `mi-trabajo/` (personal, ignorado por git)

```
mi-trabajo/
├── .cache/                         # caché del CLI (no tocar)
└── <carpeta-del-curso>/            # mismo nombre que en cursos/
    ├── _material/                  # descargas de Aula Virtual (+ .txt de pdftotext), compartidas por el curso
    └── <nombre-de-la-ficha>/       # una carpeta por actividad, mismo nombre que la ficha sin .md
        ├── README.md               # estado, plan, bitácora, siguiente paso (plantilla: plantillas/actividad/)
        ├── notas/                  # caso.md (hechos con página), lecturas.md, apuntes de clase
        ├── borradores/             # respuestas en Markdown, una sección por pregunta
        ├── entregable/             # SOLO lo que se sube: <código>_<Tema>_<Grupo-o-Apellido>.pdf
        └── ia/                     # declaracion.md, export de la sesión, enlaces
```

- Una actividad = una carpeta; nunca mezclar actividades ni grupos.
- Nombres de archivo sin espacios ni tildes; versiones como `respuestas-v2.md`, no `final-final.md`.
- Al cerrar cada bloque de trabajo, actualiza "Bitácora" y "Siguiente paso" del `README.md` y su campo `estado`.
- El material descargado tiene copyright: no se copia fuera de `mi-trabajo/` ni se versiona.
