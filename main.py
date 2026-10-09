from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import ErrorDeConexion
from infraestructura.esquema import crear_tablas, vaciar_tablas
from infraestructura.departamento_repositorio import DepartamentoRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.registro_tiempo_repositorio import RegistroTiempoRepositorio

PAYLOAD = "' OR '1'='1"


def titulo(texto):
    print(f"\n=== {texto} ===")


def demo():
    crear_tablas()     # repetible: IF NOT EXISTS
    vaciar_tablas()    # la demo parte siempre sin datos

    repo_dep = DepartamentoRepositorio()
    repo_pro = ProyectoRepositorio()
    repo_emp = EmpleadoRepositorio()
    repo_reg = RegistroTiempoRepositorio()

    # ---------------- DEPARTAMENTO ----------------
    titulo("Departamento: CRUD")
    ti = repo_dep.guardar(Departamento("Tecnología"))
    rrhh = repo_dep.guardar(Departamento("Recursos Humanos"))
    print("guardar  ->", ti, rrhh)
    print("obtener  ->", repo_dep.obtener(ti.id))
    print("listar   ->", repo_dep.listar())
    rrhh.nombre = "Personas"
    print("actualizar filas ->", repo_dep.actualizar(rrhh))
    print("listar('Pers') ->", repo_dep.listar(nombre_contiene="Pers"))

    # ---------------- PROYECTO ----------------
    titulo("Proyecto: CRUD")
    web = repo_pro.guardar(Proyecto("Sitio web"))
    app = repo_pro.guardar(Proyecto("App móvil"))
    print("obtener  ->", repo_pro.obtener(web.id))
    print("listar   ->", repo_pro.listar())
    app.nombre = "App móvil v2"
    print("actualizar filas ->", repo_pro.actualizar(app))

    # ---------------- EMPLEADO ----------------
    titulo("Empleado: CRUD")
    ana = Empleado("12345678-9", "Ana Rojas", date(2024, 3, 1), 950_000, ti.id)
    luis = Empleado("11111111-1", "Luis Pérez", date(2023, 7, 15), 800_000, ti.id)
    repo_emp.guardar(ana)
    repo_emp.guardar(luis)
    print("obtener  ->", repo_emp.obtener("12345678-9"))
    print("listar() ->", len(repo_emp.listar()), "empleados")
    print("listar('Ana') ->", len(repo_emp.listar(nombre_contiene="Ana")), "empleado(s)")
    ana.sueldo_base = 1_050_000
    print("actualizar filas ->", repo_emp.actualizar(ana))
    print("sueldo nuevo ->", repo_emp.obtener("12345678-9").sueldo_base)
    print("obtener inexistente ->", repo_emp.obtener("99999999-9"))

    titulo("RUT duplicado (llave primaria)")
    try:
        repo_emp.guardar(ana)
        print("✘ Se guardó dos veces el mismo RUT")
    except ErrorDeConexion as e:
        print("✔ Aviso en vez de caerse:", e)

    # ---------------- REGISTRO_TIEMPO ----------------
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

    # ---------------- DECISIONES DE BORRADO ----------------
    titulo("Decisión: cascada de registro_tiempo")
    print("registros de Ana antes  ->", len(repo_reg.listar(empleado_rut=ana.rut)))
    print("eliminar Ana ->", repo_emp.eliminar("12345678-9"))
    print("registros de Ana después ->", len(repo_reg.listar(empleado_rut=ana.rut)))
    print("eliminar Ana otra vez ->", repo_emp.eliminar("12345678-9"))

    titulo("Decisión: no se borra lo que todavía se usa")
    for nombre, repo, id_ in [("departamento con empleados", repo_dep, ti.id),
                              ("proyecto con registros", repo_pro, web.id)]:
        try:
            repo.eliminar(id_)
            print(f"✘ Se borró un {nombre}")
        except ErrorDeConexion as e:
            print(f"✔ Borrado de {nombre} impedido:", e)
    print("eliminar departamento vacío ->", repo_dep.eliminar(rrhh.id))
    print("eliminar proyecto sin registros ->", repo_pro.eliminar(app.id))

    # ---------------- PRUEBA DE INYECCIÓN ----------------
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
        ok = resultado in ([], None, False)
        print(f"{'✔' if ok else '✘'} {metodo:24} -> {resultado!r}")

    print("\nEmpleados que siguen en la base ->", len(repo_emp.listar()))


if __name__ == "__main__":
    try:
        demo()
    except ErrorDeConexion as e:
        print(f"Error: {e}")
