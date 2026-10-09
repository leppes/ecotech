# EcoTech — Laboratorios C07 y C08

Persistencia en SQLite con el **patrón Repositorio**: CRUD parametrizado de
**Empleado**, **Departamento**, **Proyecto** y **RegistroTiempo**.

## Cómo ejecutar

```powershell
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # y completar DB_MOTOR=sqlite, DB_NOMBRE=ecotech.db
python main.py
```

`main.py` crea las tablas (si no existen), vacía los datos, recorre el CRUD de las
cuatro entidades, comprueba las decisiones de borrado y corre la prueba de inyección.

## Configuración (.env)

| Variable | Ejemplo | Uso |
|---|---|---|
| `DB_MOTOR` | `sqlite` | Motor de base de datos |
| `DB_NOMBRE` | `ecotech.db` | Archivo de la base |
| `DB_HOST`, `DB_USUARIO`, `DB_PASSWORD` | *(vacío en SQLite)* | Para MySQL / PostgreSQL |

- `.env` **no se versiona** (está en `.gitignore`). Comprobar con `git status`.
- `.env.example` **sí se versiona**: es la documentación de qué hay que configurar.
- Sin `.env`, el programa falla al arrancar con un mensaje claro.

## Decisiones de diseño (C08)

| Decisión | Opciones | La nuestra |
|---|---|---|
| ¿Se borra de verdad? | DELETE real · marcar `activo = 0` | **DELETE real**. Al eliminar un empleado se borra su fila en `persona` y, por cascada, la de `empleado`. |
| ¿Qué pasa con los hijos? | Cascada · impedir el borrado · dejarlos huérfanos | **Cascada** para `registro_tiempo` (composición ◆ con empleado). **Impedir el borrado** (`ON DELETE RESTRICT`) de un `departamento` con empleados o de un `proyecto` con registros. |
| ¿Quién asigna el id? | La base (autoincremento) · el programa | **El programa** para `persona`/`empleado` (el RUT es la llave natural). **La base** para `departamento`, `proyecto` y `registro_tiempo`. |

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
  persona.py
  empleado.py                    # Empleado hereda de Persona
  departamento.py
  proyecto.py
  registro_tiempo.py
infraestructura/                 # Lo único que habla con la base.
  conexion.py                    # obtener_conexion() lee del .env · ErrorDeConexion
  esquema.py                     # crear_tablas() · vaciar_tablas()
  empleado_repositorio.py
  departamento_repositorio.py
  proyecto_repositorio.py
  registro_tiempo_repositorio.py
main.py                          # Demo del ciclo completo + prueba de inyección
.env.example                     # Variables a configurar (sin valores)
requirements.txt
```

Cada repositorio tiene **una sola función de mapeo** (`_fila_a_...`) que convierte
una fila de la base en un objeto del dominio.

## Seguridad: prueba de inyección

Todos los métodos que reciben datos se probaron con el payload `' OR '1'='1`:
devuelven `[]`, `None` o `False`, nunca la tabla completa ni un error de SQL.

Se buscaron en `infraestructura/` los patrones `" +`, `' +`, `f"SELECT`, `f"INSERT`,
`f"UPDATE`, `f"DELETE` y `%s" %`: no aparece ninguno dentro de un `execute`.
Los filtros dinámicos solo agregan **texto fijo** con su `?`; los valores van siempre
en la lista de parámetros.
