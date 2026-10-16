import sqlite3

from dominio.departamento import Departamento
from dominio.excepciones import EntidadEnUso, NombreDuplicado
from infraestructura.conexion import es_duplicado, es_llave_foranea, obtener_conexion


class DepartamentoRepositorio:

    @staticmethod
    def _fila_a_departamento(fila):
        return Departamento(id=fila[0], nombre=fila[1])

    def guardar(self, departamento):
        """Devuelve el departamento con el id que le asignó la base."""
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "INSERT INTO departamento (nombre) VALUES (?)",
                    (departamento.nombre,),
                )
        except sqlite3.IntegrityError as e:
            if es_duplicado(e):
                raise NombreDuplicado(f"Ya existe un departamento llamado {departamento.nombre!r}") from e
            raise
        return Departamento(departamento.nombre, id=cur.lastrowid)

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT id, nombre FROM departamento WHERE id = ?", (id,)
            ).fetchone()
        return self._fila_a_departamento(fila) if fila else None

    def listar(self, nombre_contiene=None):
        sql = "SELECT id, nombre FROM departamento"
        params = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        sql += " ORDER BY nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        return [self._fila_a_departamento(f) for f in filas]

    def actualizar(self, departamento):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "UPDATE departamento SET nombre = ? WHERE id = ?",
                    (departamento.nombre, departamento.id),
                )
        except sqlite3.IntegrityError as e:
            if es_duplicado(e):
                raise NombreDuplicado(f"Ya existe un departamento llamado {departamento.nombre!r}") from e
            raise
        return cur.rowcount

    def eliminar(self, id):
        # ON DELETE RESTRICT: si el departamento tiene empleados, la base lo rechaza.
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM departamento WHERE id = ?", (id,))
        except sqlite3.IntegrityError as e:
            if es_llave_foranea(e):
                raise EntidadEnUso(f"El departamento {id} tiene empleados: reasígnalos antes de borrarlo") from e
            raise
        return cur.rowcount > 0
