---
name: declaracion-ia
description: Redacta la declaración de uso de inteligencia artificial generativa que exigen las actividades del MBA (qué partes se apoyaron en IA, plataforma y enlaces a las conversaciones) y prepara la evidencia de la sesión de Claude Code. Úsalo antes de cerrar cualquier entregable.
argument-hint: "[actividad]"
allowed-tools: Read Write Edit Glob Grep Artifact
---

# Declaración de uso de IA: `$ARGUMENTS`

Los cursos permiten IA generativa **solo si se declara de forma transparente**. Un entregable sin declaración no se entrega.

## 1. Formato

- Si la ficha de la actividad trae su propio formato de declaración (p. ej. "Uso de inteligencia artificial generativa"), úsalo literal.
- Si no, usa `plantillas/declaracion-ia.md`.

## 2. Contenido: honesto y específico

Reconstruye, a partir de esta sesión y de la "Bitácora" del `README.md` del espacio de trabajo, qué hizo Claude realmente: lectura y resumen del caso, estructura de respuestas, redacción de borradores, revisión contra rúbrica, diseño de diapositivas, búsqueda de conceptos. Y qué hizo el estudiante o el equipo: decisiones, validación de conclusiones, ejemplos propios, discusión. No minimices ni exageres el aporte de la IA.

Plataforma: "Claude (Anthropic), mediante Claude Code". Si se usaron otras, inclúyelas.

## 3. Evidencia (enlace a la conversación)

Las sesiones locales de Claude Code no generan un enlace público por sí solas. Opciones, de más a menos recomendada:

1. **Exportar y publicar.** El estudiante ejecuta `/export mi-trabajo/<curso>/<actividad>/ia/sesion-AAAA-MM-DD.txt`. Luego, con su permiso, publica ese texto como Artifact (página simple, título `Conversación IA · <código actividad>`) y el estudiante lo comparte con enlace desde claude.ai. Antes de publicar, revisa que el texto no tenga datos personales de terceros.
2. **Sesión en la nube.** Si la actividad se trabajó en claude.ai/code, usar Compartir → Público en esa sesión.

En ambos casos, el estudiante **debe abrir el enlace en una ventana de incógnito** para comprobar que se ve sin iniciar sesión, como exigen los cursos. No afirmes que el enlace es público si no se comprobó.

## 4. Dónde va

- Diapositivas: última diapositiva del deck.
- Documento: sección final, después de referencias.
- Guarda el texto en `mi-trabajo/<curso>/<actividad>/ia/declaracion.md` y registra los enlaces en el `README.md` del espacio de trabajo.
