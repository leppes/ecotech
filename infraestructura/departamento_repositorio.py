import sqlite3

from dominio.departamento import Departamento
from dominio.excepciones import EntidadEnUso, NombreDuplicado
from infraestructura.conexion import obtener_conexion


class DepartamentoRepositorio:

    def _fila_a_departamento(self, fila):
        return Departamento(id=fila[0], nombre=fila[1])

    def guardar(self, departamento):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "INSERT INTO departamento (nombre) VALUES (?)",
                    (departamento.nombre,),
                )
                nuevo_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise NombreDuplicado(f"Ya existe un departamento llamado {departamento.nombre}")
        return Departamento(departamento.nombre, nuevo_id)

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT id, nombre FROM departamento WHERE id = ?", (id,)
            ).fetchone()
        if fila is None:
            return None
        return self._fila_a_departamento(fila)

    def listar(self, nombre_contiene=None):
        sql = "SELECT id, nombre FROM departamento"
        params = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        sql += " ORDER BY nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        lista = []
        for fila in filas:
            lista.append(self._fila_a_departamento(fila))
        return lista

    def actualizar(self, departamento):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "UPDATE departamento SET nombre = ? WHERE id = ?",
                    (departamento.nombre, departamento.id),
                )
                filas = cur.rowcount
        except sqlite3.IntegrityError:
            raise NombreDuplicado(f"Ya existe un departamento llamado {departamento.nombre}")
        return filas

    def eliminar(self, id):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM departamento WHERE id = ?", (id,))
                borrados = cur.rowcount
        except sqlite3.IntegrityError:
            raise EntidadEnUso(f"El departamento {id} tiene empleados asignados")
        return borrados > 0
