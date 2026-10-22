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
```

`main.py` hace la prueba de conexión, crea las tablas si no existen y abre el menú.
Para crear las tablas sin abrir el menú:
`python -c "from repositorio.conexion import inicializar_bd; inicializar_bd()"`.

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
ecotech/
├── dominio/                     # Clases del negocio (POO, sin SQL)
│   ├── __init__.py
│   ├── persona.py
│   ├── empleado.py              # Empleado hereda de Persona
│   ├── departamento.py
│   ├── proyecto.py
│   ├── registro_tiempo.py
│   ├── validaciones.py          # Reglas compartidas (RUT, sueldo, horas, fechas)
│   └── excepciones.py           # Excepciones propias del dominio
├── repositorio/                 # Persistencia: lo único que habla con la base
│   ├── __init__.py
│   ├── conexion.py              # Conexión con .env, commit/rollback, inicializar_bd()
│   ├── empleado_repo.py         # CRUD parametrizado y mapper fila -> objeto
│   ├── departamento_repo.py
│   ├── proyecto_repo.py
│   └── registro_tiempo_repo.py
├── datos/
│   └── schema.sql               # CREATE TABLE con llaves foráneas
├── .env.example                 # Variables de entorno (sin credenciales)
├── .gitignore                   # Excluye .env, .venv, __pycache__, *.db y *.log
├── requirements.txt             # python-dotenv
├── main.py                      # Menú por consola: valida lo que escribe el usuario
└── README.md
```

## Decisiones de diseño (C08)

| Decisión | Opciones | La nuestra |
|---|---|---|
| ¿Se borra de verdad? | DELETE real · marcar `activo = 0` | **DELETE real**. Al eliminar un empleado se borra su fila en `persona` y, por cascada, la de `empleado`. |
| ¿Qué pasa con los hijos? | Cascada · impedir el borrado · dejarlos huérfanos | **Cascada** para `registro_tiempo` (composición ◆ con empleado). **Impedir el borrado** (`ON DELETE RESTRICT`) de un `departamento` con empleados o de un `proyecto` con registros: el repositorio lo informa con `EntidadEnUso`. |
| ¿Quién asigna el id? | La base (autoincremento) · el programa | **El programa** para `persona`/`empleado` (el RUT es la llave natural). **La base** para `departamento`, `proyecto` y `registro_tiempo`: `guardar()` devuelve el objeto con el id asignado. |

## Esquema (C07) — `datos/schema.sql`

- El **RUT es TEXT** (como número pierde el dígito verificador y los ceros).
- Las **fechas son DATE** (se guardan en formato ISO `AAAA-MM-DD`, así se filtra por rango).
- **NOT NULL** en los atributos obligatorios.
- La relación **N:M empleado ↔ proyecto** se resuelve con la tabla intermedia `registro_tiempo`.
- La **composición ◆** se tradujo en `ON DELETE CASCADE`.
- Es **repetible**: `CREATE TABLE IF NOT EXISTS`, corre dos veces seguidas sin error.
- `PRAGMA foreign_keys = ON` se activa en cada conexión; sin eso SQLite ignora las llaves foráneas.

## Seguridad: prueba de inyección

En el menú, **Empleados → Listar / buscar por nombre** con el texto `' OR '1'='1`
no devuelve resultados: el valor se trata como texto, nunca como parte del SQL.
Ninguna consulta se arma concatenando valores: los filtros solo agregan **texto fijo**
con su `?`, y los valores van siempre en la lista de parámetros.
