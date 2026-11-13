# MBA ESPAE — Centro de trabajo

Repositorio compartido por estudiantes de la **Maestría en Administración de Empresas (ESPAE · ESPOL), Cohorte 1**. Aquí se hacen las actividades de todos los cursos con Claude Code, conectado a Aula Virtual (Canvas). Cada persona clona el repo y trabaja en local con **su propio token**.

Al iniciar la sesión, un hook te inyecta quién es el estudiante, sus grupos y sus pendientes (`tools/aula.py contexto`).

**Primera vez:** si el contexto de inicio dice `CONFIGURACIÓN PENDIENTE` o "Aula Virtual no disponible", tu primera respuesta es ofrecer `/configurar` (token personal + sistema de diseño, ~2 minutos). El estudiante puede no ser técnico: nunca le pidas editar archivos, usar la terminal ni entender Python o variables de entorno; tú ejecutas todo. Si `python3` no existe en su sistema (Windows), usa `python`.

**Actualizar:** si el estudiante pide actualizar el repo o traer cursos nuevos, ejecuta `git pull` (su carpeta `mi-trabajo/` no se toca) y resume qué cursos o fichas llegaron.

## Qué está versionado y qué no

| Ruta | Qué es | Git |
|---|---|---|
| `cursos/<curso>/CLAUDE.md` | Contexto del curso: actividades, módulos, fechas, conceptos, notas del admin | versionado (admin) |
| `cursos/<curso>/actividades/*.md` | **Ficha** de cada actividad (enunciado, rúbrica, materiales). Formato: `docs/ficha-actividad.md` | versionado (admin) |
| `cursos/<curso>/materiales.md`, `paginas.md` | Índice de lecturas con ids de archivo; páginas del curso (cronograma, políticas) | versionado (admin) |
| `cursos/cursos.json` | Registro de cursos (id Canvas ↔ carpeta) | versionado (admin) |
| `tools/aula.py` | CLI de Aula Virtual (solo stdlib) | versionado |
| `docs/` | Referencia: API, ficha, presentaciones, admin | versionado |
| `plantillas/` | Plantillas: espacio de trabajo, declaración de IA, perfil local | versionado |
| `mi-trabajo/` | **Todo lo personal**: borradores, material descargado, entregables | ignorado |
| `.env`, `CLAUDE.local.md` | Token y perfil personal (sistema de diseño, preferencias); los crea `/configurar` | ignorado |

Nunca escribas trabajo personal fuera de `mi-trabajo/`. Nunca modifiques `cursos/` salvo que el estudiante sea el admin y lo pida (ver `docs/admin.md`).

## Cursos

| Curso | Carpeta | Id Canvas |
|---|---|---|
| Liderazgo Ético y Gestión de Personas | `cursos/liderazgo-etico-gestion-personas/` | 5121 |
| Mercadeo e Investigación de Mercados | _pendiente de sincronizar_ | 5122 |
| Decisiones Financieras para la Gerencia | _pendiente de sincronizar_ | 5123 |

Antes de trabajar en un curso, lee su `CLAUDE.md` y la ficha de la actividad. La fuente de verdad del estado personal (entregado, nota, grupo) es siempre la API, nunca el repo.

## Aula Virtual: siempre a través de `tools/aula.py`

Ejecuta siempre desde la raíz con la ruta relativa `python3 tools/aula.py …`; los permisos del repo dependen de esa forma exacta.

```
python3 tools/aula.py yo                         # usuario, cursos y grupos con integrantes
python3 tools/aula.py pendientes [--curso X] [--dias N]
python3 tools/aula.py tareas <curso>             # todas las tareas con mi estado
python3 tools/aula.py tarea <curso> <id>         # enunciado, rúbrica y mi estado en vivo
python3 tools/aula.py modulos <curso>            # estructura con ids de archivos
python3 tools/aula.py descargar <curso> <id>...  # → mi-trabajo/<curso>/_material/
python3 tools/aula.py pagina <curso> <slug>
python3 tools/aula.py notas|anuncios|grupo <curso>
python3 tools/aula.py api <ruta> [clave=valor ...]   # GET de solo lectura a cualquier endpoint
python3 tools/aula.py entregar <curso> <id> <archivo>... [--comentario T] --confirmar   # ESCRIBE
```

`<curso>` acepta el id, la carpeta o parte del nombre. Para endpoints que el CLI no cubre, usa `api` y consulta `docs/aula-virtual.md`.

Reglas duras:
- **Nunca** leas, imprimas ni pidas el token. No uses `curl` con el token; no abras `.env`.
- **Entregar o comentar en Aula Virtual exige confirmación explícita del estudiante en el chat**, después de mostrarle qué archivo, en qué tarea y si reemplaza una entrega del grupo. Usa el skill `/entregar`.
- Las horas de Canvas vienen en UTC; muéstralas siempre en hora de Ecuador (UTC−5). El CLI ya lo hace.

## Flujo de una actividad

0. `/configurar`: solo la primera vez (o si el token vence).
1. `/pendientes`: qué vence y en qué estado está.
2. `/actividad <nombre o código>`: crea `mi-trabajo/<curso>/<ficha>/` desde la plantilla, descarga los materiales, lee el caso y propone un plan alineado a la rúbrica.
3. Análisis y borradores en `mi-trabajo/<curso>/<ficha>/borradores/`. Fundamenta en hechos del caso y en los conceptos del curso (sección "Conceptos clave" del `CLAUDE.md` del curso).
4. `/revisar`: el subagente `revisor-rubrica` evalúa el borrador contra la rúbrica de la ficha.
5. `/presentacion`: deck con el sistema de diseño (ver abajo); exportado a PDF en `entregable/`.
6. `/declaracion-ia`: arma la declaración de uso de IA que exigen los cursos.
7. `/entregar`: sube el PDF a Aula Virtual, con confirmación.

## Reglas académicas

- **Uso de IA declarado.** Los cursos permiten IA generativa solo si se declara: qué partes se apoyaron en IA, qué plataforma y enlace a las conversaciones. Todo entregable lleva su declaración (`/declaracion-ia`); nunca entregues sin ella.
- **El estudiante decide.** Claude analiza, estructura y redacta borradores; el estudiante y su equipo validan las conclusiones. En trabajos grupales, recuerda que el equipo debe revisar antes de entregar.
- **Fundamenta todo.** Cada afirmación sobre el caso cita el hecho del caso (página/sección). Cada marco teórico cita su fuente (APA 7). No inventes datos, citas ni referencias; si falta información, dilo.
- **Responde exactamente lo que pide la actividad**, en el orden de las preguntas, cuidando el peso de cada criterio de la rúbrica.
- **Integrantes**: los entregables grupales llevan los nombres de todos los integrantes del grupo según Aula Virtual (`python3 tools/aula.py grupo <curso>`), no según el repo.
- Idioma: español neutro académico, ortografía completa. Los compañeros del repo pueden estar en grupos distintos: nunca mezcles trabajo de un grupo con otro.

## Presentaciones

Toda presentación se hace con el skill `/presentacion`: Artifact de tipo Slides con el **sistema de diseño personal del estudiante**, el que figura en `CLAUDE.local.md` → `Sistema de diseño:`. Si ahí dice `{{SISTEMA_DE_DISENO}}` o el archivo no existe, completa primero `/configurar`. Nunca uses otro sistema de diseño. Se aplica la adaptación académica de `docs/presentaciones.md`: solo lo visual, sin logos ni copy comercial.

## Admin

El admin (Edwin Veloz) sincroniza cursos nuevos y cura el contexto con `/sync-curso` (`docs/admin.md`). Si el estudiante no es el admin y detecta un error en `cursos/`, propón el cambio en vez de editarlo.
