import logging
from abc import ABC, abstractmethod
from datetime import date, datetime

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import ErrorDeDominio
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.validaciones import validar_horas, validar_rut, validar_sueldo
from repositorio.conexion import ErrorDeConexion, inicializar_bd, probar_conexion
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio
from repositorio.registro_tiempo_repo import RegistroTiempoRepositorio


def pedir(mensaje, convertir=str, actual=None, opcional=False):
    if actual is not None:
        if isinstance(actual, date):
            mensaje = f"{mensaje} [{actual.strftime('%d-%m-%Y')}]"
        else:
            mensaje = f"{mensaje} [{actual}]"
    while True:
        texto = input(f"{mensaje}: ").strip()
        if texto == "":
            if actual is not None:
                return actual
            if opcional:
                return None
            print("  ✘ Este dato es obligatorio.")
            continue
        try:
            return convertir(texto)
        except ValueError as e:
            print(f"  ✘ {e}")


def confirmar(mensaje):
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        print("  ✘ Responde s o n.")


def mostrar_lista(elementos):
    if len(elementos) == 0:
        print("  (sin resultados)")
    for elemento in elementos:
        print(f"  {elemento}")


def a_entero(texto):
    try:
        return int(texto.replace(".", ""))
    except ValueError:
        raise ValueError(f"'{texto}' no es un número entero")


def a_decimal(texto):
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ValueError(f"'{texto}' no es un número")


def a_fecha(texto):
    try:
        return datetime.strptime(texto, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError(f"'{texto}' no es una fecha válida, usa el formato DD-MM-AAAA")


def a_sueldo(texto):
    return validar_sueldo(a_entero(texto))


def a_horas(texto):
    return validar_horas(a_decimal(texto))


class Menu(ABC):
    titulo = "Menú"
    salida = "Volver"

    @abstractmethod
    def opciones(self):
        pass

    def mostrar(self):
        opciones = self.opciones()
        while True:
            print(f"\n=== {self.titulo} ===")
            for numero, (texto, _) in enumerate(opciones, start=1):
                print(f"{numero}. {texto}")
            print(f"0. {self.salida}")
            eleccion = input("Opción: ").strip()
            if eleccion == "0":
                return
            if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
                self._ejecutar(opciones[int(eleccion) - 1][1])
            else:
                print(f"  ✘ Opción no válida: escribe un número del 0 al {len(opciones)}.")

    def _ejecutar(self, accion):
        try:
            accion()
        except ErrorDeDominio as e:
            print(f"  ✘ {e}")
        except ErrorDeConexion as e:
            print(f"  ✘ {e}")


class MenuCatalogo(Menu):
    def __init__(self, titulo, clase, repositorio):
        self.titulo = titulo
        self._clase = clase
        self._repo = repositorio

    def opciones(self):
        return [("Registrar", self.registrar),
                ("Listar / buscar por nombre", self.listar),
                ("Cambiar nombre", self.actualizar),
                ("Eliminar", self.eliminar)]

    def registrar(self):
        nuevo = self._repo.guardar(self._clase(pedir("Nombre")))
        print(f"  ✔ Guardado: {nuevo}")

    def listar(self):
        filtro = pedir("Buscar (Enter para ver todos)", opcional=True)
        mostrar_lista(self._repo.listar(nombre_contiene=filtro))

    def actualizar(self):
        entidad = self._repo.obtener(pedir("Id", a_entero))
        if entidad is None:
            print("  ✘ No existe ese id.")
            return
        entidad.nombre = pedir("Nombre", actual=entidad.nombre)
        self._repo.actualizar(entidad)
        print(f"  ✔ Actualizado: {entidad}")

    def eliminar(self):
        id_ = pedir("Id", a_entero)
        if not confirmar(f"¿Eliminar el id {id_}?"):
            return
        print("  ✔ Eliminado." if self._repo.eliminar(id_) else "  ✘ No existe ese id.")


class MenuEmpleados(Menu):
    titulo = "Empleados"

    def __init__(self, repo_empleados, repo_departamentos):
        self._repo = repo_empleados
        self._repo_dep = repo_departamentos

    def opciones(self):
        return [("Registrar", self.registrar),
                ("Listar / buscar por nombre", self.listar),
                ("Actualizar", self.actualizar),
                ("Eliminar", self.eliminar)]

    def _mostrar_departamentos(self):
        print("Departamentos disponibles:")
        mostrar_lista(self._repo_dep.listar())

    def registrar(self):
        rut = pedir("RUT (12345678-5)", validar_rut)
        nombre = pedir("Nombre")
        fecha_ingreso = pedir("Fecha de ingreso (DD-MM-AAAA)", a_fecha)
        sueldo_base = pedir("Sueldo base", a_sueldo)
        self._mostrar_departamentos()
        departamento_id = pedir("Id del departamento (Enter si no tiene)", a_entero, opcional=True)
        empleado = Empleado(rut, nombre, fecha_ingreso, sueldo_base, departamento_id)
        self._repo.guardar(empleado)
        print(f"  ✔ Guardado: {empleado}")

    def listar(self):
        filtro = pedir("Buscar (Enter para ver todos)", opcional=True)
        mostrar_lista(self._repo.listar(nombre_contiene=filtro))

    def actualizar(self):
        empleado = self._repo.obtener(pedir("RUT", validar_rut))
        if empleado is None:
            print("  ✘ No hay un empleado con ese RUT.")
            return
        print("Enter conserva el valor entre corchetes.")
        empleado.nombre = pedir("Nombre", actual=empleado.nombre)
        empleado.fecha_ingreso = pedir("Fecha de ingreso", a_fecha, actual=empleado.fecha_ingreso)
        empleado.sueldo_base = pedir("Sueldo base", a_sueldo, actual=empleado.sueldo_base)
        self._mostrar_departamentos()
        empleado.departamento_id = pedir("Id del departamento", a_entero,
                                         actual=empleado.departamento_id, opcional=True)
        self._repo.actualizar(empleado)
        print(f"  ✔ Actualizado: {empleado}")

    def eliminar(self):
        rut = pedir("RUT", validar_rut)
        if not confirmar(f"¿Eliminar a {rut}? También se borran sus registros de horas"):
            return
        print("  ✔ Eliminado." if self._repo.eliminar(rut) else "  ✘ No hay un empleado con ese RUT.")


class MenuRegistros(Menu):
    titulo = "Registro de horas"

    def __init__(self, repo_registros, repo_proyectos):
        self._repo = repo_registros
        self._repo_pro = repo_proyectos

    def opciones(self):
        return [("Registrar horas", self.registrar),
                ("Listar (por empleado y/o fechas)", self.listar),
                ("Actualizar", self.actualizar),
                ("Eliminar", self.eliminar)]

    def _mostrar_proyectos(self):
        print("Proyectos disponibles:")
        mostrar_lista(self._repo_pro.listar())

    def registrar(self):
        rut = pedir("RUT del empleado", validar_rut)
        self._mostrar_proyectos()
        proyecto_id = pedir("Id del proyecto", a_entero)
        horas = pedir("Horas", a_horas)
        fecha = pedir("Fecha (DD-MM-AAAA)", a_fecha)
        nuevo = self._repo.guardar(RegistroTiempo(rut, proyecto_id, horas, fecha))
        print(f"  ✔ Guardado: {nuevo}")

    def listar(self):
        print("Enter deja el filtro vacío.")
        rut = pedir("RUT del empleado", validar_rut, opcional=True)
        desde = pedir("Desde (DD-MM-AAAA)", a_fecha, opcional=True)
        hasta = pedir("Hasta (DD-MM-AAAA)", a_fecha, opcional=True)
        mostrar_lista(self._repo.listar(empleado_rut=rut, desde=desde, hasta=hasta))

    def actualizar(self):
        registro = self._repo.obtener(pedir("Id del registro", a_entero))
        if registro is None:
            print("  ✘ No existe ese registro.")
            return
        print("Enter conserva el valor entre corchetes.")
        self._mostrar_proyectos()
        registro.proyecto_id = pedir("Id del proyecto", a_entero, actual=registro.proyecto_id)
        registro.horas = pedir("Horas", a_horas, actual=registro.horas)
        registro.fecha = pedir("Fecha", a_fecha, actual=registro.fecha)
        self._repo.actualizar(registro)
        print(f"  ✔ Actualizado: {registro}")

    def eliminar(self):
        id_ = pedir("Id del registro", a_entero)
        if not confirmar(f"¿Eliminar el registro {id_}?"):
            return
        print("  ✔ Eliminado." if self._repo.eliminar(id_) else "  ✘ No existe ese registro.")


class MenuPrincipal(Menu):
    titulo = "EcoTech Solutions · Gestión interna"
    salida = "Salir"

    def __init__(self):
        repo_dep = DepartamentoRepositorio()
        repo_pro = ProyectoRepositorio()
        self._submenus = [
            MenuEmpleados(EmpleadoRepositorio(), repo_dep),
            MenuCatalogo("Departamentos", Departamento, repo_dep),
            MenuCatalogo("Proyectos", Proyecto, repo_pro),
            MenuRegistros(RegistroTiempoRepositorio(), repo_pro),
        ]

    def opciones(self):
        return [(submenu.titulo, submenu.mostrar) for submenu in self._submenus]


def main():
    logging.basicConfig(filename="ecotech.log", level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        version, _ = probar_conexion()
        inicializar_bd()
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
