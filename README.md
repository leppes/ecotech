# EcoTech Solutions — Sistema de Gestión Interna (UA2)

Implementación en Python del modelo UML de EcoTech, con persistencia en SQLite
mediante el **patrón Repositorio**: CRUD parametrizado de **Empleado**,
**Departamento**, **Proyecto** y **RegistroTiempo**, con encapsulamiento,
excepciones propias del dominio y transacciones (C07, C08 y C09).

## Cómo ejecutar

```powershell
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # (Mac/Linux: cp) y completar DB_MOTOR=sqlite, DB_NOMBRE=ecotech.db
python app.py                     # la aplicación: menú por consola
python main.py                    # la demo automática con todas las comprobaciones
```

`app.py` es la **aplicación**: hace la prueba de conexión, crea las tablas si no
existen y abre un menú por consola con el CRUD de empleados, departamentos,
proyectos y registro de horas.

`main.py` es la **demo**: hace la prueba de conexión, crea las tablas (si no existen), vacía los
datos, recorre el CRUD de las cuatro entidades, muestra cómo los objetos rechazan
datos inválidos, cómo se traducen los errores de la base, comprueba el rollback de
las transacciones y las decisiones de borrado, y corre la prueba de inyección.
Cada comprobación imprime ✔ o ✘.

## Configuración (.env)

| Variable | Ejemplo | Uso |
|---|---|---|
| `DB_MOTOR` | `sqlite` | Motor de base de datos |
| `DB_NOMBRE` | `ecotech.db` | Archivo de la base |
| `DB_HOST`, `DB_USUARIO`, `DB_PASSWORD` | *(vacío en SQLite)* | Para MySQL / PostgreSQL |

- `.env` **no se versiona** (está en `.gitignore`). Comprobar con `git status`.
- `.env.example` **sí se versiona**: es la documentación de qué hay que configurar.
- Sin `.env`, el programa falla al arrancar con un mensaje claro. Lo mismo si
  `DB_MOTOR` dice otro motor que no sea `sqlite`.

## Paso 1 — Del UML al código

| Elemento del modelo | En el código |
|---|---|
| Clase `Persona` | `dominio/persona.py` |
| Clase `Empleado` | `dominio/empleado.py` |
| Clase `Departamento` | `dominio/departamento.py` |
| Clase `Proyecto` | `dominio/proyecto.py` |
| Clase `RegistroTiempo` | `dominio/registro_tiempo.py` |
| **Herencia** Empleado → Persona | `class Empleado(Persona)` con `super().__init__(rut, nombre)` |
| **Asociación** Departamento 1 — * Empleado | `Empleado.departamento_id` · FK `ON DELETE RESTRICT` |
| **N:M** Empleado ↔ Proyecto | Se resuelve con `RegistroTiempo` (`empleado_rut` + `proyecto_id`) |
| **Composición ◆** Empleado — RegistroTiempo | `RegistroTiempo.empleado_rut` es de solo lectura (un registro no cambia de dueño) · FK `ON DELETE CASCADE` |

## Paso 2 — Encapsulamiento y reutilización

- Todos los atributos son **internos** (prefijo `_`, la convención de Python para
  «no se toca desde afuera»: `_rut`, `_nombre`, `_sueldo_base`, ...) y se acceden con `@property`. Los **setters validan** y lanzan un error del dominio si
  el dato no sirve, así un objeto nunca queda en un estado inválido.
- **Solo lectura**: `rut` (llave natural), `id` (lo asigna la base) y
  `RegistroTiempo.empleado_rut` (composición). Intentar cambiarlos lanza `AttributeError`.
- Reglas que se validan: RUT con formato `12345678-5` y **dígito verificador**
  (acepta puntos y la k minúscula, y lo guarda normalizado), nombres no vacíos,
  fechas de tipo `date`, sueldo entero `>= 0`, horas entre 0 (excluido) y 24.
- **Reutilización**:
  - `Empleado` hereda de `Persona` el RUT y el nombre **con sus validaciones**.
  - `dominio/validaciones.py` reúne las validaciones que usan varias clases
    (`validar_texto`, `validar_fecha`, `validar_id`, `validar_rut`): se escriben una vez.
  - Cada repositorio tiene **una sola función de mapeo** (`_fila_a_...`), y
    `EmpleadoRepositorio` usa el mismo `_SELECT_BASE` en `obtener` y `listar`.
  - `Empleado.__str__` reutiliza el de `Persona` con `super().__str__()`.
  - En la interfaz, todos los menús heredan de `Menu` (el ciclo y el manejo de
    errores se escriben una vez), y **un solo `MenuCatalogo`** sirve para
    departamentos y proyectos, que tienen la misma forma (id + nombre).

## Paso 3 — Conexión a la base de datos

- Librería oficial: **`sqlite3`**, de la biblioteca estándar de Python (no se instala).
- `python-dotenv` lee el `.env`, así las credenciales quedan fuera del código.
- `infraestructura/conexion.py`:
  - `obtener_conexion()` abre la conexión, activa `PRAGMA foreign_keys = ON` y la cierra siempre (`finally`).
  - `probar_conexion()` es la **prueba de conexión**: consulta `sqlite_version()` y
    confirma que las llaves foráneas quedaron activas. Es lo primero que corre `main.py`:

```
=== Prueba de conexión ===
✔ Conectado a SQLite 3.45.1 con la librería estándar sqlite3
✔ Llaves foráneas activas: True
```

## Manejo de errores (C09)

Se captura **lo específico**; nunca `except Exception` ni `except: pass`. Lo que
una capa no sabe manejar, lo deja subir.

| Error de origen | Dónde se captura | Se convierte en | Cuándo |
|---|---|---|---|
| Dato con formato inválido | setter de la clase | `RutInvalido`, `SueldoInvalido`, `HorasInvalidas`, `DatoInvalido` | RUT mal escrito, sueldo negativo, 31 horas, nombre vacío |
| `sqlite3.IntegrityError` (UNIQUE) | repositorio | `RutDuplicado`, `NombreDuplicado` | Mismo RUT dos veces, nombre de departamento/proyecto repetido |
| `sqlite3.IntegrityError` (FOREIGN KEY) al guardar | repositorio | `ReferenciaInexistente` | Departamento o proyecto que no existe |
| `sqlite3.IntegrityError` (FOREIGN KEY) al borrar | repositorio | `EntidadEnUso` | Departamento con empleados, proyecto con horas |
| `sqlite3.OperationalError` | `obtener_conexion()` | `ErrorDeConexion` | La base no abre, está bloqueada o no responde |

- Las excepciones del dominio están en `dominio/excepciones.py`. Todas heredan de
  `ErrorDeDominio`, y las de datos inválidos además de `ValueError`.
- La traducción se hace con `raise ... from e`: el mensaje habla el idioma del
  negocio, pero el error original de SQLite queda encadenado para depurar.
- `main.py` no importa `sqlite3`: captura errores del dominio sin saber qué motor hay abajo.
- Un `IntegrityError` que el repositorio no sabe traducir (p. ej. un `CHECK`) **no
  se esconde**: se relanza con `raise`, porque significa que hay un bug.

## Validación de las entradas del usuario (`interfaz/`)

El programa **no se cae** por lo que escriba el usuario:

| Qué escribe mal | Qué pasa |
|---|---|
| Opción de menú que no existe | «Opción no válida» y se muestra el menú otra vez |
| Texto donde va un número, fecha que no existe (31-02), RUT mal escrito | Se vuelve a preguntar **solo ese campo** |
| Sueldo negativo, más de 24 horas | Igual: el menú usa la misma regla del dominio (`validar_sueldo`, `validar_horas`) |
| Campo obligatorio vacío | «Este dato es obligatorio» y se repite |
| RUT o nombre repetido, departamento o proyecto que no existe, borrar algo en uso | Se informa el error del dominio y se vuelve al menú |
| La base se bloquea o no responde | «Problema con la base de datos» y se vuelve al menú |
| Ctrl+C | Se sale con «Hasta luego», sin traza de error |

Las validaciones están en dos capas: `interfaz/consola.py` convierte el texto al
tipo de Python (entero, fecha DD-MM-AAAA, decimal con coma), y el dominio aplica
las reglas del negocio. Así, aunque alguien use las clases sin pasar por el menú,
los datos se siguen validando.

## Transacciones (C09): todo o nada

`obtener_conexion()` es una transacción: dentro usa `with conn:`, que hace
**commit** si el bloque termina bien y **rollback** si salta una excepción.

La operación que lo necesita es **guardar un empleado**: son dos escrituras que
dependen entre sí (`INSERT INTO persona` + `INSERT INTO empleado`). Si la segunda
falla, sin transacción quedaría una persona huérfana. Lo mismo al **actualizar**
(`UPDATE persona` + `UPDATE empleado`). `main.py` lo comprueba:

- Guarda un empleado con un departamento que no existe → `ReferenciaInexistente`.
  Luego guarda el mismo RUT con un departamento válido: si la persona hubiera
  quedado huérfana, saltaría `RutDuplicado`.
- Cambia el nombre (UPDATE válido) y el departamento a uno inexistente (UPDATE que
  falla) → el nombre en la base sigue siendo el original.

## Decisiones de diseño (C08)

| Decisión | Opciones | La nuestra |
|---|---|---|
| ¿Se borra de verdad? | DELETE real · marcar `activo = 0` | **DELETE real**. Al eliminar un empleado se borra su fila en `persona` y, por cascada, la de `empleado`. |
| ¿Qué pasa con los hijos? | Cascada · impedir el borrado · dejarlos huérfanos | **Cascada** para `registro_tiempo` (composición ◆ con empleado). **Impedir el borrado** (`ON DELETE RESTRICT`) de un `departamento` con empleados o de un `proyecto` con registros: el repositorio lo informa con `EntidadEnUso`. |
| ¿Quién asigna el id? | La base (autoincremento) · el programa | **El programa** para `persona`/`empleado` (el RUT es la llave natural). **La base** para `departamento`, `proyecto` y `registro_tiempo`: `guardar()` devuelve el objeto con el id asignado. |

## Esquema (C07) — `db/01_esquema.sql`

- El **RUT es TEXT** (como número pierde el dígito verificador y los ceros).
- Las **fechas son DATE** (se guardan en formato ISO `AAAA-MM-DD`, así se filtra por rango).
- **NOT NULL** en los atributos obligatorios.
- La relación **N:M empleado ↔ proyecto** se resuelve con la tabla intermedia `registro_tiempo`.
- La **composición ◆** se tradujo en `ON DELETE CASCADE`.
- Es **repetible**: `CREATE TABLE IF NOT EXISTS`, corre dos veces seguidas sin error.
- `PRAGMA foreign_keys = ON` se activa en cada conexión; sin eso SQLite ignora las llaves foráneas.

## Estructura

```
db/
  01_esquema.sql                 # CREATE TABLE con llaves foráneas y ON DELETE
dominio/                         # Clases del negocio. No saben SQL.
  excepciones.py                 # ErrorDeDominio y sus subclases
  validaciones.py                # Validaciones compartidas (RUT, texto, fecha, id)
  persona.py
  empleado.py                    # Empleado hereda de Persona
  departamento.py
  proyecto.py
  registro_tiempo.py
interfaz/                        # Lo único que habla con el usuario.
  consola.py                     # pedir() pregunta hasta recibir un dato válido
  menu.py                        # Menu (base) y sus submenús
infraestructura/                 # Lo único que habla con la base.
  conexion.py                    # obtener_conexion() · probar_conexion() · ErrorDeConexion
  esquema.py                     # crear_tablas() · vaciar_tablas()
  empleado_repositorio.py        # Traducen IntegrityError a errores del dominio
  departamento_repositorio.py
  proyecto_repositorio.py
  registro_tiempo_repositorio.py
docs/
  bitacora_ia.md                 # Uso de IA: prompt, respuesta y decisión
  criterios.md                   # Dónde está la evidencia de cada criterio de la rúbrica
app.py                           # La aplicación (menú por consola)
main.py                          # Demo del ciclo completo + prueba de inyección
.env.example                     # Variables a configurar (sin valores)
requirements.txt
```

## Seguridad: prueba de inyección

Todos los métodos que reciben datos se probaron con el payload `' OR '1'='1`:
devuelven `[]`, `None` o `False`, nunca la tabla completa ni un error de SQL.

Se buscaron en `infraestructura/` los patrones `" +`, `' +`, `f"SELECT`, `f"INSERT`,
`f"UPDATE`, `f"DELETE`, `%s" %` y `.format(`: no aparece ninguno dentro de un `execute`.
Los filtros dinámicos solo agregan **texto fijo** con su `?`; los valores van siempre
en la lista de parámetros.
