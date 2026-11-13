# Aula Virtual (Canvas LMS): conexión y referencia

Aula Virtual de posgrados ESPOL es una instancia de **Canvas LMS** (`https://postgradosvirtual.espol.edu.ec`). Referencia oficial de la API: https://developerdocs.instructure.com/services/canvas

## Configurar el token (cada estudiante, una vez)

Lo hace Claude con `/configurar` (se ofrece solo en la primera sesión):

1. El estudiante genera el token en Aula Virtual → **Cuenta → Configuración → Integraciones aprobadas → + Nuevo token de acceso** (página `/profile/settings`) y lo **copia**.
2. Claude ejecuta `python3 tools/aula.py configurar --portapapeles`: lee el token del portapapeles, lo verifica contra `users/self` y lo guarda en `.env` (permisos 600). Alternativa sin portapapeles: `python3 tools/aula.py configurar` abre un diálogo del sistema con campo oculto.
3. El token nunca pasa por la conversación ni por la salida de los comandos.

El token da acceso a **toda la cuenta** de Aula Virtual: es personal, no se comparte y no se sube al repo (`.env` está en `.gitignore` y Claude Code tiene prohibido leerlo). Para revocarlo: misma pantalla, ícono de borrar. Si se filtra (p. ej. se pegó en un chat), revocarlo y generar otro.

## Por qué un CLI propio y no un MCP

Se evaluaron tres opciones (noviembre 2026):

| Opción | Veredicto |
|---|---|
| **MCP oficial de Instructure** (OAuth, en fase experimental) | Requiere que ESPOL lo active con una developer key y apunta a Canvas alojado por Instructure; además **no permite entregar tareas** a estudiantes. No disponible para nosotros hoy. |
| **MCP comunitarios** (`vishalsachdev/canvas-mcp`, `bruchris/canvas-lms-mcp`, `DMontgomery40/mcp-canvas-lms`…) | Código de terceros con acceso total a la cuenta y dependencias npm/PyPI. El más maduro (vishalsachdev) **rechaza entregas grupales**, que son la mayoría en el MBA. |
| **CLI propio `tools/aula.py`** (elegido) | ~1.000 líneas auditables, cero dependencias, el token nunca sale de la máquina ni aparece en la conversación, entregas grupales con aviso y doble confirmación (bandera `--confirmar` + regla `ask` de Claude Code, que pregunta incluso en modo auto). |

Claude no necesita leer la documentación de la API en cada sesión: el CLI cubre los casos de uso y `aula.py api <ruta>` permite cualquier GET de la referencia oficial.

## Política de uso

La política de API de Instructure (agosto 2025) prohíbe conectar sus APIs mediante MCP u otras tecnologías no aprobadas, y su guía para estudiantes desaconseja generar tokens para insertarlos en aplicaciones. ESPOL parece alojar su propia instancia, así que lo que rige en la práctica es la normativa de ESPOL. **Antes de automatizar entregas, confirma con la coordinación del MBA o TI de ESPOL que el uso de tokens personales está permitido.** Mientras tanto, el uso de lectura (consultar tareas, descargar material) es el de menor riesgo. Ver `README.md`.

## Referencia del CLI

| Comando | Endpoint(s) |
|---|---|
| `yo` | `GET users/self`, `courses?enrollment_state=active`, `users/self/groups`, `groups/:id/users` |
| `pendientes`, `tareas`, `contexto` | `GET courses/:id/assignments?include[]=submission&order_by=due_at` |
| `tarea` | `GET courses/:id/assignments/:id?include[]=submission` |
| `modulos` | `GET courses/:id/modules?include[]=items` |
| `pagina` | `GET courses/:id/pages/:slug` |
| `descargar` | `GET courses/:id/files/:id` → `url` firmada (sin token) |
| `notas` | `GET courses/:id/enrollments?user_id=self` + submissions |
| `anuncios` | `GET announcements?context_codes[]=course_:id` |
| `api <ruta>` | cualquier GET (solo lectura) |
| `entregar` | 3 pasos: `POST …/assignments/:id/submissions/self/files` → POST multipart a `upload_url` (sin token) → confirmar `Location`; luego `POST …/assignments/:id/submissions` con `submission[submission_type]=online_upload` y `submission[file_ids][]` |
| `comentar` | `PUT …/assignments/:id/submissions/self` con `comment[text_comment]` |
| `sync` (admin) | course + modules + assignments + pages + files (solo metadatos) |

## Comportamiento de Canvas que importa

- **Tareas grupales** (`group_category_id` presente): la entrega de **un** miembro cuenta para todo el grupo y se replica a cada integrante. Si tu estado dice "sin entregar", nadie del grupo ha entregado. Una reentrega crea un nuevo intento para todos.
- **Fechas**: la API devuelve UTC (`2026-11-13T04:59:59Z` = jueves 12/11 23:59 en Ecuador).
- **Paginación**: header `Link` con `rel="next"`; el CLI la sigue.
- **Rate limit**: por token; con peticiones secuenciales casi nunca se alcanza. El CLI reintenta los GET ante 429 y **nunca** reintenta un POST.
- **401 en algunos endpoints** (lista de archivos del curso, usuarios, rúbricas): el docente no los habilitó para estudiantes; los archivos sí se descargan por id desde módulos o enunciados.
