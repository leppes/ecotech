"""Menús de la aplicación. No saben SQL: usan los repositorios y el dominio."""
from abc import ABC, abstractmethod

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import ErrorDeDominio
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.validaciones import validar_horas, validar_rut, validar_sueldo
from infraestructura.conexion import ErrorDeConexion
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.registro_tiempo_repositorio import RegistroTiempoRepositorio
from interfaz.consola import a_decimal, a_entero, a_fecha, confirmar, mostrar_lista, pedir


# Convertidores que además aplican la regla del dominio: si el dato no la
# cumple, se vuelve a preguntar solo ese campo y no se pierde el formulario.
def a_sueldo(texto):
    return validar_sueldo(a_entero(texto))


def a_horas(texto):
    return validar_horas(a_decimal(texto))


class Menu(ABC):
    """Base de todos los menús: muestra las opciones y ejecuta la elegida.

    Cada submenú solo define su `titulo` y sus `opciones()`; el ciclo y el
    manejo de errores se escriben una sola vez aquí.
    """
    titulo = "Menú"
    salida = "Volver"

    @abstractmethod
    def opciones(self):
        """Lista de (texto, método). Cada submenú está obligado a definirla:
        Menu es abstracta y no se puede instanciar directamente."""

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

    @staticmethod
    def _ejecutar(accion):
        # Un error del negocio o de la base se informa y se vuelve al menú:
        # el programa no se cae. Cualquier otro error es un bug y se deja subir.
        try:
            accion()
        except ErrorDeDominio as e:
            print(f"  ✘ {e}")
        except ErrorDeConexion as e:
            print(f"  ✘ Problema con la base de datos: {e}")


class MenuCatalogo(Menu):
    """Departamentos y proyectos se manejan igual (id + nombre): un solo menú
    para los dos, que recibe la clase y el repositorio con que trabaja."""

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
