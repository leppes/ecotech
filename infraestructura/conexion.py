import logging
import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()


class ErrorDeConexion(Exception):
    pass


@contextmanager
def obtener_conexion():
    if os.getenv("DB_MOTOR", "sqlite") != "sqlite":
        raise ErrorDeConexion("Este programa solo funciona con DB_MOTOR=sqlite")
    ruta = os.getenv("DB_NOMBRE")
    if not ruta:
        raise ErrorDeConexion("Falta DB_NOMBRE en el archivo .env (copia .env.example a .env)")
    try:
        conn = sqlite3.connect(ruta)
        conn.execute("PRAGMA foreign_keys = ON")
    except sqlite3.OperationalError as e:
        logging.error("No se pudo abrir la base %s: %s", ruta, e)
        raise ErrorDeConexion("No se pudo conectar a la base de datos")
    try:
        yield conn
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    except sqlite3.OperationalError as e:
        conn.rollback()
        logging.error("Error de SQLite: %s", e)
        raise ErrorDeConexion("No se pudo completar la operación en la base de datos")
    finally:
        conn.close()


def probar_conexion():
    with obtener_conexion() as conn:
        version = conn.execute("SELECT sqlite_version()").fetchone()[0]
        activas = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    return version, activas == 1
