# infraestructura/conexion.py
import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()


class ErrorDeConexion(Exception):
    """La base de datos no está configurada, no está disponible o no respondió."""


@contextmanager
def obtener_conexion():
    """Una conexión = una transacción: o pasa todo lo del bloque, o no pasa nada.

    - Si el bloque termina bien, `with conn` hace commit.
    - Si salta cualquier excepción, `with conn` hace rollback y la deja subir.

    Solo se traduce OperationalError (la base no responde, está bloqueada o le
    falta una tabla). IntegrityError NO se captura aquí: sube al repositorio,
    que es quien sabe convertirlo en RutDuplicado, EntidadEnUso, etc.
    """
    ruta = os.environ.get("DB_NOMBRE")
    if not ruta:
        raise ErrorDeConexion("Falta la variable DB_NOMBRE. ¿Copiaste el .env.example a .env?")
    try:
        conn = sqlite3.connect(ruta)
    except sqlite3.OperationalError as e:
        raise ErrorDeConexion(f"No se pudo abrir la base {ruta!r}: {e}") from e
    try:
        conn.execute("PRAGMA foreign_keys = ON")   # SQLite las ignora si no se activan
        with conn:
            yield conn
    except sqlite3.OperationalError as e:
        raise ErrorDeConexion(f"La base no pudo completar la operación: {e}") from e
    finally:
        conn.close()


def probar_conexion():
    """Prueba de conexión: abre la base, le pide la versión del motor y
    confirma que las llaves foráneas quedaron activas."""
    with obtener_conexion() as conn:
        version = conn.execute("SELECT sqlite_version()").fetchone()[0]
        llaves_foraneas = conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    return version, llaves_foraneas


# SQLite informa qué regla se violó en el mensaje del IntegrityError.
def es_duplicado(error):
    """UNIQUE o PRIMARY KEY repetida."""
    return str(error).startswith("UNIQUE constraint failed")


def es_llave_foranea(error):
    """FOREIGN KEY: se apunta a algo que no existe, o se borra algo que está en uso."""
    return str(error).startswith("FOREIGN KEY constraint failed")
