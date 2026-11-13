# MBA ESPAE · Centro de trabajo con Claude Code

Espacio de trabajo para la Maestría en Administración de Empresas (ESPAE · ESPOL, Cohorte 1). Abres Claude Code en esta carpeta y te ayuda con tus cursos: qué tienes pendiente, analizar los casos con los conceptos del curso, armar la presentación y entregarla en Aula Virtual. Tu trabajo queda solo en tu computadora.

## Empezar (una sola vez)

1. **Acepta la invitación** al repositorio que te llegó de GitHub.
2. **Descarga el repositorio.** Lo más fácil es [GitHub Desktop](https://desktop.github.com): *File → Clone repository → mba-espae*. Si usas terminal: `git clone https://github.com/edwin06111998/mba-espae.git`.
3. **Abre Claude Code en esa carpeta.** Puede ser con la app de escritorio (abrir carpeta) o con la terminal (`cd mba-espae` y luego `claude`). Si pregunta si confías en la carpeta, responde que sí.
4. **Escribe "hola".** Claude te guía en la configuración. Solo te pedirá dos cosas:
   - **Tu token de Aula Virtual.** Es una llave personal que generas en Aula Virtual → Cuenta → Configuración → Integraciones aprobadas → *+ Nuevo token de acceso*. Claude te abre la página y te explica cada paso. El token **no se pega en el chat**: lo copias y Claude lo guarda directo en tu computadora.
   - **El nombre de tu sistema de diseño** de Claude, para tus presentaciones. Si no tienes uno, puedes omitirlo o pedir que te cree uno.

No necesitas saber programación ni tocar ningún archivo.

> Uso responsable: la política de Canvas restringe usar tokens personales en aplicaciones. El admin está confirmando con la coordinación del MBA que el uso está permitido. Consultar tareas y materiales es el uso de menor riesgo.

## Uso diario

Pídelo en lenguaje natural, por ejemplo:

- "¿Qué tengo pendiente?"
- "Ayúdame con la actividad 6.1"
- "Revisa mi borrador contra la rúbrica"
- "Hazme la presentación"
- "Entrega mi PDF"
- "Actualiza el repo"

O usa los atajos:

| Atajo | Qué hace |
|---|---|
| `/pendientes` | Qué vence, qué está atrasado y por dónde empezar |
| `/actividad 6.1` | Abre la actividad: lee el caso, prepara tu carpeta y propone un plan según la rúbrica |
| `/revisar` | Evalúa tu borrador contra la rúbrica (puntaje estimado y qué falta) |
| `/presentacion` | Genera las diapositivas con tu sistema de diseño, listas para PDF |
| `/declaracion-ia` | Arma la declaración de uso de IA que exigen los cursos |
| `/entregar` | Sube tu PDF a Aula Virtual. Siempre te pide confirmación antes |
| `/configurar` | Repite la configuración (token vencido, cambiar sistema de diseño) |

## Dónde queda tu trabajo

Todo lo tuyo se guarda en la carpeta `mi-trabajo/`, una subcarpeta por curso y por actividad: borradores, PDFs descargados y entregables. Esa carpeta **nunca se sube** al repositorio; respáldala por tu cuenta si quieres (iCloud, Drive…).

## Reglas

- La IA se declara siempre (`/declaracion-ia`), y el equipo valida las conclusiones antes de entregar.
- Si ves un error en la información de un curso, avísale al admin en lugar de editarla.

Admin: Edwin Veloz. Mantenimiento y detalles técnicos: `docs/admin.md` y `docs/aula-virtual.md`.
