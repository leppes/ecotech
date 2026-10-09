from datetime import date

from dominio.empleado import Empleado
from infraestructura.conexion import obtener_conexion

# Mismo orden de columnas en TODAS las lecturas -> el mapper siempre calza.
_SELECT_BASE = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.departamento_id
                  FROM empleado e JOIN persona p ON p.rut = e.rut"""


class EmpleadoRepositorio:

    @staticmethod
    def _fila_a_empleado(fila):
        return Empleado(
            rut=fila[0],
            nombre=fila[1],
            fecha_ingreso=date.fromisoformat(fila[2]),
            sueldo_base=fila[3],
            departamento_id=fila[4],
        )

    # ---------- CREATE ----------
    def guardar(self, empleado):
        # Las dos inserciones van en la misma conexión = misma transacción.
        # Si la segunda falla, se deshace también la primera.
        with obtener_conexion() as conn:
            conn.execute(
                "INSERT INTO persona (rut, nombre) VALUES (?, ?)",
                (empleado.rut, empleado.nombre),
            )
            conn.execute(
                """INSERT INTO empleado (rut, fecha_ingreso, sueldo_base, departamento_id)
                   VALUES (?, ?, ?, ?)""",
                (empleado.rut, empleado.fecha_ingreso.isoformat(),
                 empleado.sueldo_base, empleado.departamento_id),
            )
        return empleado

    # ---------- READ ----------
    def obtener(self, rut):
        with obtener_conexion() as conn:
            fila = conn.execute(
                """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.departamento_id
                   FROM empleado e JOIN persona p ON p.rut = e.rut
                   WHERE e.rut = ?""",
                (rut,),
            ).fetchone()
        return self._fila_a_empleado(fila) if fila else None

    def listar(self, nombre_contiene=None):
        sql = _SELECT_BASE
        params = []
        if nombre_contiene:
            sql += " WHERE p.nombre LIKE ?"          # texto fijo
            params.append(f"%{nombre_contiene}%")    # el valor va aparte
        sql += " ORDER BY p.nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        return [self._fila_a_empleado(f) for f in filas]

    # ---------- UPDATE ----------
    def actualizar(self, empleado):
        with obtener_conexion() as conn:
            conn.execute(
                "UPDATE persona SET nombre = ? WHERE rut = ?",
                (empleado.nombre, empleado.rut),
            )
            cur = conn.execute(
                """UPDATE empleado
                   SET fecha_ingreso = ?, sueldo_base = ?, departamento_id = ?
                   WHERE rut = ?""",
                (empleado.fecha_ingreso.isoformat(), empleado.sueldo_base,
                 empleado.departamento_id, empleado.rut),
            )
        return cur.rowcount

    # ---------- DELETE ----------
    def eliminar(self, rut):
        # Borrado físico. Se borra la persona y, por ON DELETE CASCADE,
        # se van su fila en empleado y todos sus registro_tiempo.
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM persona WHERE rut = ?", (rut,))
        return cur.rowcount > 0
