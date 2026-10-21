import os
from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.excepciones import (DatoInvalido, EntidadEnUso, NombreDuplicado,
                                 ReferenciaInexistente, RutDuplicado)
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import ErrorDeConexion, probar_conexion
from infraestructura.esquema import crear_tablas, vaciar_tablas
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.registro_tiempo_repositorio import RegistroTiempoRepositorio

PAYLOAD = "' OR '1'='1"
BASE_DEMO = "ecotech_demo.db"


def titulo(texto):
    print(f"\n=== {texto} ===")


def mostrar(texto, lista):
    print(texto, "->", [str(x) for x in lista])


def debe_fallar(descripcion, operacion, excepcion):
    try:
        operacion()
        print(f"✘ Se aceptó: {descripcion}")
    except excepcion as e:
        print(f"✔ {type(e).__name__} <- {descripcion}: {e}")


def demo():
    titulo("Prueba de conexión")
    version, llaves_foraneas = probar_conexion()
    print(f"✔ Conectado a SQLite {version} con la librería estándar sqlite3")
    if llaves_foraneas:
        print("✔ Llaves foráneas activas: True")
    else:
        print("✘ Llaves foráneas activas: False")

    crear_tablas()
    vaciar_tablas()

    repo_dep = DepartamentoRepositorio()
    repo_pro = ProyectoRepositorio()
    repo_emp = EmpleadoRepositorio()
    repo_reg = RegistroTiempoRepositorio()

    titulo("Departamento: CRUD")
    ti = repo_dep.guardar(Departamento("Tecnología"))
    rrhh = repo_dep.guardar(Departamento("Recursos Humanos"))
    print("guardar  ->", ti, "|", rrhh)
    print("obtener  ->", repo_dep.obtener(ti.id))
    mostrar("listar  ", repo_dep.listar())
    rrhh.nombre = "Personas"
    print("actualizar filas ->", repo_dep.actualizar(rrhh))
    mostrar("listar('Pers')", repo_dep.listar(nombre_contiene="Pers"))

    titulo("Proyecto: CRUD")
    web = repo_pro.guardar(Proyecto("Sitio web"))
    app = repo_pro.guardar(Proyecto("App móvil"))
    print("obtener  ->", repo_pro.obtener(web.id))
    mostrar("listar  ", repo_pro.listar())
    app.nombre = "App móvil v2"
    print("actualizar filas ->", repo_pro.actualizar(app))

    titulo("Empleado: CRUD")
    ana = Empleado("12345678-5", "Ana Rojas", date(2024, 3, 1), 950_000, ti.id)
    luis = Empleado("11.111.111-1", "Luis Pérez", date(2023, 7, 15), 800_000, ti.id)
    repo_emp.guardar(ana)
    repo_emp.guardar(luis)
    print("obtener  ->", repo_emp.obtener("12345678-5"))
    print("RUT normalizado ->", luis.rut)
    print("listar() ->", len(repo_emp.listar()), "empleados")
    print("listar('Ana') ->", len(repo_emp.listar(nombre_contiene="Ana")), "empleado(s)")
    ana.sueldo_base = 1_050_000
    print("actualizar filas ->", repo_emp.actualizar(ana))
    print("sueldo nuevo ->", repo_emp.obtener("12345678-5").sueldo_base)
    print("obtener inexistente ->", repo_emp.obtener("99999999-9"))

    titulo("RegistroTiempo: CRUD")
    r1 = repo_reg.guardar(RegistroTiempo(ana.rut, web.id, 8, date(2026, 10, 1)))
    r2 = repo_reg.guardar(RegistroTiempo(ana.rut, app.id, 7.5, date(2026, 10, 2)))
    repo_reg.guardar(RegistroTiempo(luis.rut, web.id, 9, date(2026, 10, 1)))
    print("obtener  ->", repo_reg.obtener(r1.id))
    print("listar de Ana ->", len(repo_reg.listar(empleado_rut=ana.rut)), "registros")
    print("listar rango 02-10 a 31-10 ->",
          len(repo_reg.listar(desde=date(2026, 10, 2), hasta=date(2026, 10, 31))), "registro(s)")
    r2.horas = 6
    print("actualizar filas ->", repo_reg.actualizar(r2))
    print("eliminar r2 ->", repo_reg.eliminar(r2.id))

    titulo("Encapsulamiento: los objetos rechazan datos inválidos")
    debe_fallar("RUT con dígito verificador incorrecto",
                lambda: Empleado("12345678-9", "Pedro Díaz", date(2024, 1, 2), 900_000), DatoInvalido)
    debe_fallar("31 horas en un día",
                lambda: RegistroTiempo(luis.rut, web.id, 31, date(2026, 10, 5)), DatoInvalido)
    debe_fallar("departamento sin nombre", lambda: Departamento("   "), DatoInvalido)
    try:
        luis.sueldo_base = -1
        print("✘ Se aceptó un sueldo negativo")
    except DatoInvalido as e:
        print(f"✔ DatoInvalido <- sueldo negativo: {e}")
    try:
        luis.rut = "22222222-2"
        print("✘ Se pudo cambiar el RUT")
    except AttributeError:
        print("✔ AttributeError <- el RUT es de solo lectura")
    print("sueldo de Luis sigue en ->", luis.sueldo_base)

    titulo("Errores de la base traducidos al dominio")
    debe_fallar("guardar dos veces el mismo RUT", lambda: repo_emp.guardar(ana), RutDuplicado)
    debe_fallar("departamento con nombre repetido",
                lambda: repo_dep.guardar(Departamento("Tecnología")), NombreDuplicado)
    debe_fallar("horas en un proyecto que no existe",
                lambda: repo_reg.guardar(RegistroTiempo(luis.rut, 9999, 8, date(2026, 10, 3))),
                ReferenciaInexistente)

    titulo("Transacción: persona + empleado, todo o nada")
    eva = Empleado("22222222-2", "Eva Soto", date(2025, 1, 6), 700_000, departamento_id=9999)
    debe_fallar("guardar empleado en un departamento que no existe",
                lambda: repo_emp.guardar(eva), ReferenciaInexistente)
    eva.departamento_id = ti.id
    try:
        repo_emp.guardar(eva)
        print("✔ Rollback de guardar: no quedó una persona huérfana, el mismo RUT se guardó después")
    except RutDuplicado:
        print("✘ Quedó una persona huérfana: el INSERT de persona no se deshizo")

    eva.nombre = "Eva Soto Pérez"
    eva.departamento_id = 9999
    debe_fallar("actualizar con departamento inexistente",
                lambda: repo_emp.actualizar(eva), ReferenciaInexistente)
    nombre_en_base = repo_emp.obtener(eva.rut).nombre
    if nombre_en_base == "Eva Soto":
        print(f"✔ Rollback de actualizar: el nombre en la base sigue siendo '{nombre_en_base}'")
    else:
        print(f"✘ Rollback de actualizar: el nombre cambió a '{nombre_en_base}'")

    titulo("Decisión: cascada de registro_tiempo")
    print("registros de Ana antes  ->", len(repo_reg.listar(empleado_rut=ana.rut)))
    print("eliminar Ana ->", repo_emp.eliminar(ana.rut))
    print("registros de Ana después ->", len(repo_reg.listar(empleado_rut=ana.rut)))
    print("eliminar Ana otra vez ->", repo_emp.eliminar(ana.rut))

    titulo("Decisión: no se borra lo que todavía se usa")
    debe_fallar("borrar un departamento con empleados", lambda: repo_dep.eliminar(ti.id), EntidadEnUso)
    debe_fallar("borrar un proyecto con horas registradas", lambda: repo_pro.eliminar(web.id), EntidadEnUso)
    print("eliminar departamento vacío ->", repo_dep.eliminar(rrhh.id))
    print("eliminar proyecto sin registros ->", repo_pro.eliminar(app.id))

    titulo(f"Prueba de inyección con {PAYLOAD!r}")
    pruebas = {
        "empleado.listar":       repo_emp.listar(nombre_contiene=PAYLOAD),
        "empleado.obtener":      repo_emp.obtener(PAYLOAD),
        "empleado.eliminar":     repo_emp.eliminar(PAYLOAD),
        "departamento.listar":   repo_dep.listar(nombre_contiene=PAYLOAD),
        "departamento.obtener":  repo_dep.obtener(PAYLOAD),
        "departamento.eliminar": repo_dep.eliminar(PAYLOAD),
        "proyecto.listar":       repo_pro.listar(nombre_contiene=PAYLOAD),
        "proyecto.obtener":      repo_pro.obtener(PAYLOAD),
        "proyecto.eliminar":     repo_pro.eliminar(PAYLOAD),
        "registro.listar":       repo_reg.listar(empleado_rut=PAYLOAD),
        "registro.obtener":      repo_reg.obtener(PAYLOAD),
        "registro.eliminar":     repo_reg.eliminar(PAYLOAD),
    }
    for metodo, resultado in pruebas.items():
        if resultado in ([], None, False):
            print(f"✔ {metodo:24} -> {resultado!r}")
        else:
            print(f"✘ {metodo:24} -> {resultado!r}")

    print("\nEmpleados que siguen en la base ->", len(repo_emp.listar()))


if __name__ == "__main__":
    os.environ["DB_NOMBRE"] = BASE_DEMO
    try:
        demo()
    except ErrorDeConexion as e:
        print(f"Error de conexión: {e}")
