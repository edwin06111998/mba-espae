# Presentaciones del MBA

Las presentaciones se generan con Claude Code como **Artifact de tipo Slides** usando el **sistema de diseño personal de cada estudiante** (un artifact de tipo Design System en su cuenta de claude.ai). Skill: `/presentacion`.

## Qué sistema de diseño se usa

- Cada estudiante declara el suyo en `CLAUDE.local.md` (personal, no versionado), línea `Sistema de diseño: <nombre> — <url>`. Lo registra `/configurar`.
- El repo **no** fija ninguno: nunca uses el sistema de diseño de otra persona ni uno distinto al declarado.
- Si la línea dice `{{SISTEMA_DE_DISENO}}` o no existe `CLAUDE.local.md`: ejecuta `/configurar` (paso 2) antes de diseñar.
- Si dice "ninguno": usa el estilo por defecto del tipo Slides con una paleta sobria (fondo claro, un color de acento, una sola familia tipográfica sans-serif).

## Adaptación académica (siempre, con cualquier sistema de diseño)

Del sistema de diseño se toma **lo visual**: paleta, tipografía, radios, espaciado, estilo de íconos. Lo que sea de marca comercial no aplica:

- **Sin logos ni nombres de empresas o productos** del estudiante. La portada lleva curso, actividad y equipo.
- Sin llamados a la acción, precios ni lenguaje de venta. Tono académico: tercera persona o primera del plural.
- Sin emoji. Un solo color de énfasis por diapositiva para la idea central.

## Estructura del deck para análisis de caso

1. **Portada**: curso, código y título de la actividad, equipo y **nombres de todos los integrantes**, docente, fecha.
2. **El caso en una diapositiva**: protagonista, dilema, decisión pendiente.
3. **Una sección por pregunta, en el orden del enunciado.** Título = la respuesta en una frase (no la pregunta). Cuerpo = 2–4 argumentos con evidencia del caso (pág.) y el concepto del curso que la sostiene.
4. Para preguntas de opciones o alternativas: tabla de ventajas / riesgos por opción y la **recomendación** destacada.
5. **Conclusión / recomendación final** (si la actividad la pide).
6. **Referencias** en APA 7.
7. **Declaración de uso de IA** (última diapositiva, formato de la ficha o `plantillas/declaracion-ia.md`).

Reglas de contenido: una idea por diapositiva; ≤ 40 palabras de cuerpo; datos con fuente; nada de relleno ni frases genéricas; gráficos o tablas solo si aclaran.

## Exportar

El PDF se descarga desde la página del artifact y se guarda en `mi-trabajo/<curso>/<actividad>/entregable/<código>_<Tema>_<Grupo-o-Apellido>.pdf`. Después: `/revisar` y `/entregar`.
