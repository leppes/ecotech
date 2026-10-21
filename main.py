import logging

from infraestructura.conexion import ErrorDeConexion, probar_conexion
from infraestructura.esquema import crear_tablas
from interfaz.menu import MenuPrincipal


def main():
    logging.basicConfig(filename="ecotech.log", level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        version, _ = probar_conexion()
        crear_tablas()
    except ErrorDeConexion as e:
        print(f"No se pudo iniciar la aplicación: {e}")
        return
    print(f"Conectado a SQLite {version}")
    try:
        MenuPrincipal().mostrar()
    except (KeyboardInterrupt, EOFError):
        print()
    print("Hasta luego.")


if __name__ == "__main__":
    main()
