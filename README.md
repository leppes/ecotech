# EcoTech Solutions — Sistema de Gestión de Empleados

Aplicación de consola en Python que gestiona empleados, departamentos, proyectos y
registro de horas, con persistencia en SQLite mediante el **patrón Repositorio**.

Equipo: Miguel Fuentealba (líder de proyecto), Benjamín Leppe y Gonzalo Bustos ·
TI3021 Programación Orientada a Objeto Seguro · ES2.

## Cómo ejecutar

```powershell
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # (Mac/Linux: cp) — con SQLite funciona sin editarlo
python main.py                    # la aplicación: menú por consola
python demo.py                    # demo automática: prueba cada regla y marca ✔ o ✘
```

`main.py` hace la prueba de conexión, crea las tablas si no existen y abre el menú.
`demo.py` usa su propia base (`ecotech_demo.db`) para no borrar los datos del menú.

## Configuración (.env)

| Variable | Ejemplo | Uso |
|---|---|---|
| `DB_MOTOR` | `sqlite` | Motor de base de datos |
| `DB_NOMBRE` | `ecotech.db` | Archivo de la base |
| `DB_HOST`, `DB_USUARIO`, `DB_PASSWORD` | *(vacío en SQLite)* | Para MySQL / PostgreSQL |

- `.env` **no se versiona** (está en `.gitignore`); `.env.example` sí, como modelo.
- Si la base falla, el usuario ve un mensaje genérico y el detalle técnico queda en
  `ecotech.log` (también ignorado por Git).

## Estructura

```
db/
  01_esquema.sql                 # CREATE TABLE con llaves foráneas y ON DELETE
dominio/                         # Clases del negocio. No saben SQL.
  persona.py
  empleado.py                    # Empleado hereda de Persona
  departamento.py
  proyecto.py
  registro_tiempo.py
  validaciones.py                # Reglas compartidas (RUT, sueldo, horas, fechas)
  excepciones.py                 # Excepciones propias del dominio
infraestructura/                 # Lo único que habla con la base.
  conexion.py                    # Conexión, commit/rollback y prueba de conexión
  esquema.py                     # crear_tablas() · vaciar_tablas()
  empleado_repositorio.py        # CRUD parametrizado de cada entidad
  departamento_repositorio.py
  proyecto_repositorio.py
  registro_tiempo_repositorio.py
interfaz/                        # Lo único que habla con el usuario.
  consola.py                     # Lee y valida lo que escribe el usuario
  menu.py                        # Menús del CRUD
docs/
  bitacora_ia.md                 # Bitácora de uso crítico de IA
main.py                          # La aplicación
demo.py                          # Demo automática y prueba de inyección
.env.example                     # Variables a configurar (sin credenciales)
requirements.txt
```

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

## Seguridad: prueba de inyección

Todos los métodos que reciben datos se probaron con el payload `' OR '1'='1`:
devuelven `[]`, `None` o `False`, nunca la tabla completa ni un error de SQL.
Ninguna consulta se arma concatenando valores: los filtros solo agregan **texto fijo**
con su `?`, y los valores van siempre en la lista de parámetros.
