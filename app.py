"""Aplicación de EcoTech: menú por consola para el CRUD.

(La demo automática con todas las comprobaciones sigue en main.py.)
"""
from infraestructura.conexion import ErrorDeConexion, probar_conexion
from infraestructura.esquema import crear_tablas
from interfaz.menu import MenuPrincipal


def iniciar():
    try:
        version, _ = probar_conexion()
        crear_tablas()
    except ErrorDeConexion as e:
        print(f"No se pudo iniciar la aplicación: {e}")
        return
    print(f"Conectado a SQLite {version}.")
    try:
        MenuPrincipal().mostrar()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o fin de la entrada: se sale ordenadamente, sin traza de error.
        print()
    print("Hasta luego.")


if __name__ == "__main__":
    iniciar()
