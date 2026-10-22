import sqlite3
from datetime import date

from dominio.empleado import Empleado
from dominio.excepciones import ReferenciaInexistente, RutDuplicado
from repositorio.conexion import obtener_conexion

SELECT_EMPLEADO = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.departamento_id
                     FROM empleado e JOIN persona p ON p.rut = e.rut"""


class EmpleadoRepositorio:

    def _fila_a_empleado(self, fila):
        return Empleado(
            rut=fila[0],
            nombre=fila[1],
            fecha_ingreso=date.fromisoformat(fila[2]),
            sueldo_base=fila[3],
            departamento_id=fila[4],
        )

    def guardar(self, empleado):
        try:
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
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise RutDuplicado(f"Ya existe una persona con RUT {empleado.rut}")
            raise ReferenciaInexistente(f"El departamento {empleado.departamento_id} no existe")
        return empleado

    def obtener(self, rut):
        sql = SELECT_EMPLEADO + " WHERE e.rut = ?"
        with obtener_conexion() as conn:
            fila = conn.execute(sql, (rut,)).fetchone()
        if fila is None:
            return None
        return self._fila_a_empleado(fila)

    def listar(self, nombre_contiene=None):
        sql = SELECT_EMPLEADO
        params = []
        if nombre_contiene:
            sql += " WHERE p.nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        sql += " ORDER BY p.nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        lista = []
        for fila in filas:
            lista.append(self._fila_a_empleado(fila))
        return lista

    def actualizar(self, empleado):
        try:
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
                filas = cur.rowcount
        except sqlite3.IntegrityError:
            raise ReferenciaInexistente(f"El departamento {empleado.departamento_id} no existe")
        return filas

    def eliminar(self, rut):
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM persona WHERE rut = ?", (rut,))
            borrados = cur.rowcount
        return borrados > 0
