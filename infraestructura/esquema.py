from pathlib import Path

from infraestructura.conexion import obtener_conexion

RUTA_ESQUEMA = Path(__file__).resolve().parent.parent / "db" / "01_esquema.sql"


def crear_tablas():
    """Ejecuta db/01_esquema.sql. Se puede correr las veces que sea (IF NOT EXISTS)."""
    with obtener_conexion() as conn:
        conn.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))


def vaciar_tablas():
    """Borra los datos (no las tablas) para que la demo parta limpia cada vez."""
    with obtener_conexion() as conn:
        conn.execute("DELETE FROM registro_tiempo")
        conn.execute("DELETE FROM empleado")
        conn.execute("DELETE FROM persona")
        conn.execute("DELETE FROM proyecto")
        conn.execute("DELETE FROM departamento")
