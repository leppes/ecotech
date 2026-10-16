# Bitácora de uso de IA

Cada uso de IA se documenta con: qué se le pidió (**prompt**), qué respondió y
qué **decidió el equipo** — acepto / modifico / descarto — con criterio técnico.

## Auditoría del código (las tres revisiones de la C09)

| Revisión | Cómo se revisó | Resultado |
|---|---|---|
| ¿Las consultas están parametrizadas? | Búsqueda en `infraestructura/` de `" +`, `' +`, `f"SELECT`, `f"INSERT`, `f"UPDATE`, `f"DELETE`, `%s" %`, `.format(` y `execute(f`; prueba de inyección con `' OR '1'='1` en `main.py` | Sin coincidencias. Las 12 pruebas de inyección devuelven `[]`, `None` o `False`. |
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
