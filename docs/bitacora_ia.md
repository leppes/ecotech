# Bitácora de uso de IA

Cada uso de IA se documenta con: qué se le pidió (**prompt**), qué respondió y
qué **decidió el equipo** — acepto / modifico / descarto — con criterio técnico.

## Auditoría del código (las tres revisiones de la C09)

| Revisión | Cómo se revisó | Resultado |
|---|---|---|
| ¿Las consultas están parametrizadas? | Búsqueda en `infraestructura/` de `" +`, `' +`, `f"SELECT`, `f"INSERT`, `f"UPDATE`, `f"DELETE`, `%s" %`, `.format(` y `execute(f`; prueba de inyección con `' OR '1'='1` en `main.py` | Las 12 pruebas de inyección devuelven `[]`, `None` o `False`. La primera búsqueda dio «sin coincidencias», pero tenía un hueco: no detectó `execute(_SELECT_BASE + " WHERE e.rut = ?", ...)`, que la propia IA había escrito en `EmpleadoRepositorio.obtener` (ver registro del 2026-10-21). |
| ¿Captura demasiado? | Búsqueda de `except Exception`, `except:` y `except sqlite3.Error` | Sin coincidencias. Antes, `conexion.py` capturaba `sqlite3.Error` completo y un RUT duplicado salía como "No se pudo operar sobre la base"; se cambió por capturas específicas. |
| ¿Usa librerías que existen? | `requirements.txt` revisado en PyPI e instalado en un entorno limpio | `python-dotenv` existe (pypi.org/project/python-dotenv). `sqlite3` es de la biblioteca estándar. |

## Registro

### 2026-10-16 · Claude Code · Aplicar la C09 (excepciones y transacciones) al repositorio

**Prompt:** «este es mi trabajo la clase es el contexto hay que aplicarlo al
repositorio», adjuntando la guía de la Evaluación Formativa UA2 y la presentación
de la clase 9 (Excepciones y transacciones).

**Respuesta (resumen de lo que propuso):**

1. Excepciones propias en `dominio/excepciones.py` y traducción de
   `sqlite3.IntegrityError` en cada repositorio (`RutDuplicado`, `NombreDuplicado`,
   `ReferenciaInexistente`, `EntidadEnUso`).
2. `obtener_conexion()` con `with conn:` (commit/rollback) y captura solo de
   `OperationalError` → `ErrorDeConexion`.
3. Encapsulamiento con `@property` y validación en los setters, incluyendo el
   dígito verificador del RUT.
4. `probar_conexion()` como prueba de conexión al inicio de `main.py`.
5. Demostración del rollback al guardar y al actualizar un empleado.
6. `requirements.txt`, `.env.example` y README actualizados.

**Decisión del equipo:** *(completar por el equipo: acepto / modifico / descarto
para cada punto, con el criterio técnico)*

Puntos que conviene evaluar antes de decidir:

- Para saber qué regla violó un `IntegrityError` se lee el mensaje de SQLite
  (`"UNIQUE constraint failed"`, `"FOREIGN KEY constraint failed"`). En
  Python 3.11+ existe `e.sqlite_errorname`, más robusto pero no disponible en
  versiones anteriores.
- `guardar()` de Departamento, Proyecto y RegistroTiempo ahora **devuelve un
  objeto nuevo** con el id asignado por la base (el `id` pasó a ser de solo
  lectura), en vez de modificar el objeto recibido.
- La validación del dígito verificador obliga a usar RUT reales en las pruebas
  (por eso cambió `12345678-9` por `12345678-5` en `main.py`).

### 2026-10-16 · Claude Code · Interfaz de usuario según la rúbrica

**Prompt:** «que mas falta», y después las imágenes de los criterios de
calificación de la rúbrica UA2.

**Respuesta (resumen de lo que propuso):**

1. Una aplicación con menú por consola (`app.py`, `interfaz/`), porque el
   criterio 2.1.4.G.14 pide validar entradas del usuario y `main.py` es solo una demo.
2. `pedir()` vuelve a preguntar hasta recibir un dato válido; los errores del
   dominio y de la base se informan y se vuelve al menú; Ctrl+C sale ordenadamente.
3. Las reglas de sueldo y horas pasaron a `validaciones.py` para que el dominio
   y el menú usen la misma.
4. Un solo `MenuCatalogo` para departamentos y proyectos; `__str__` en el dominio.
5. `DB_MOTOR` ahora se valida (antes se ignoraba).
6. `docs/criterios.md`: dónde está la evidencia de cada criterio.

**Decisión del equipo:** *(completar por el equipo)*

Puntos que conviene evaluar antes de decidir:

- Un error que solo detecta la base (RUT repetido, departamento inexistente)
  aparece después de llenar todo el formulario, y hay que empezar de nuevo.
  Se podría consultar antes, pero igual habría que capturar el error de la base,
  porque entre la consulta y el guardado otro usuario puede cambiar los datos.
- Al actualizar un empleado, Enter conserva el departamento; no hay forma de
  dejarlo «sin departamento» desde el menú.

### 2026-10-21 · Claude Code · Revisión contra la guía de la ES2 y la plantilla del informe

**Prompt:** «esta es la evaluación, revisa mi código y ve qué falta y si está
bien», adjuntando la guía de la ES2 y la plantilla del informe.

**Respuesta (resumen de lo que propuso):**

1. La plantilla exige ejecutar desde `main.py`: el menú pasó de `app.py` a
   `main.py`, y la demo de `main.py` a `demo.py`, con su propia base para no
   borrar los datos de la aplicación.
2. Copiar `.env.example` sin editarlo hacía fallar el programa (variables
   vacías). Ahora trae `DB_MOTOR=sqlite` y `DB_NOMBRE=ecotech.db`, que no son secretos.
3. `Menu` pasó a ser clase abstracta (`ABC`) y el dominio tiene tipos.
4. Revisó el historial de Git: no hay `.env`, bases de datos ni contraseñas.
5. **Hallazgo en código generado por la propia IA (sesión del 2026-10-16):**
   `EmpleadoRepositorio.obtener` tenía `conn.execute(_SELECT_BASE + " WHERE e.rut = ?", (rut,))`.
   No era inyectable (une dos textos fijos y el RUT va como parámetro), pero
   había un `+` dentro de `execute(...)`, que la escala castiga con 0 y nota
   topada al 60%. La búsqueda de la primera sesión no lo detectó porque buscaba
   `" +` y aquí el `+` va después de un nombre de variable. Se cambió por
   `sql = _SELECT_BASE + " WHERE e.rut = ?"` y `conn.execute(sql, (rut,))`,
   el mismo patrón que usan los `listar` del equipo.

**Decisión del equipo:** *(completar por el equipo)*

### 2026-10-21 · Claude Code · Corrección de mensajes de error y simplificación del código

**Pedido:** corregir los mensajes de error que mostraban detalles internos y
simplificar el código al nivel del curso (2.º semestre), sin comentarios.

**Respuesta (resumen de lo que hizo):**

1. **Seguridad (fuga de información):** `ErrorDeConexion` incluía la ruta del
   archivo de la base y el mensaje de SQLite, y el menú se los mostraba al usuario.
   Ahora el usuario ve un mensaje genérico («No se pudo completar la operación en la
   base de datos») y el detalle se guarda con `logging` en `ecotech.log`, que está
   en `.gitignore`. Probado bloqueando la base: el usuario ve el mensaje genérico y
   el log dice `database is locked`.
2. **Transacción explícita:** `with conn:` se cambió por `conn.commit()` y
   `conn.rollback()` dentro de `obtener_conexion()`, igual que en la clase 9.
3. **Menos excepciones:** `RutInvalido`, `SueldoInvalido` y `HorasInvalidas` se
   juntaron en una sola, `DatoInvalido`.
4. **Código más simple:** validación del RUT sin expresiones regulares (`split` e
   `isdigit`); se quitaron `es_duplicado()` y `es_llave_foranea()` (el repositorio
   revisa `"UNIQUE" in str(e)` donde hace falta); ciclos `for` en vez de listas por
   comprensión; sin `Optional`, `@staticmethod` ni `__repr__`.
5. Se borraron los comentarios y docstrings de los archivos `.py`.

Se volvieron a correr todas las pruebas: `demo.py` sin ✘, la sesión de menú con
entradas inválidas sin errores, y la prueba de romper la transacción a propósito
sigue marcando ✘.

**Decisión del equipo:** *(completar por el equipo)*

### 2026-10-22 · Claude Code · Dejar solo lo que pide la evaluación

**Pedido:** dejar en el repositorio solo lo que pide la evaluación y dejar todo listo
para la entrega.

**Respuesta (resumen de lo que hizo):** se eliminó `docs/criterios.md` (guía de
estudio que la evaluación no pide) y el README se acortó a una guía de ejecución
rápida, como describe la plantilla del informe. Las explicaciones técnicas quedan
en el informe.

**Decisión del equipo:** *(completar por el equipo)*

## Fragmentos generados con IA (criterio I.19)

Generados con Claude Code en las sesiones del 2026-10-16 y del 2026-10-21. El
2026-10-21 se reescribieron en versión simplificada todos los archivos `.py` de la
tabla:

| Archivo | Qué se generó |
|---|---|
| `dominio/excepciones.py`, `dominio/validaciones.py` | Archivos completos |
| `dominio/persona.py`, `empleado.py`, `departamento.py`, `proyecto.py`, `registro_tiempo.py` | Propiedades con validación, `__str__` y los tipos del constructor. Los `__init__` son del equipo, adaptados |
| `infraestructura/conexion.py` | `commit()`/`rollback()`, captura de `OperationalError` con mensaje genérico y `logging`, `probar_conexion()`, validación de `DB_MOTOR` |
| `infraestructura/*_repositorio.py` | Los bloques `try/except sqlite3.IntegrityError`. Las consultas SQL y los mappers son del equipo (C08) |
| `interfaz/`, `main.py` (con `logging`) | Archivos completos |
| `demo.py` (antes `main.py`) | Secciones «Prueba de conexión», «Encapsulamiento», «Errores de la base», «Transacción», la función `debe_fallar` y el uso de una base propia |
| `requirements.txt`, `.env.example` | Archivos completos |
| `README.md` | Guía de ejecución, configuración y estructura. Las secciones de decisiones de diseño (C08), esquema (C07) y seguridad son del equipo |

*(El equipo debe agregar aquí cualquier otro uso de IA, por ejemplo en la C07 y la C08.)*
