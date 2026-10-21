import sqlite3

from dominio.proyecto import Proyecto
from dominio.excepciones import EntidadEnUso, NombreDuplicado
from infraestructura.conexion import obtener_conexion


class ProyectoRepositorio:

    def _fila_a_proyecto(self, fila):
        return Proyecto(id=fila[0], nombre=fila[1])

    def guardar(self, proyecto):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "INSERT INTO proyecto (nombre) VALUES (?)",
                    (proyecto.nombre,),
                )
                nuevo_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise NombreDuplicado(f"Ya existe un proyecto llamado {proyecto.nombre}")
        return Proyecto(proyecto.nombre, nuevo_id)

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT id, nombre FROM proyecto WHERE id = ?", (id,)
            ).fetchone()
        if fila is None:
            return None
        return self._fila_a_proyecto(fila)

    def listar(self, nombre_contiene=None):
        sql = "SELECT id, nombre FROM proyecto"
        params = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        sql += " ORDER BY nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        lista = []
        for fila in filas:
            lista.append(self._fila_a_proyecto(fila))
        return lista

    def actualizar(self, proyecto):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "UPDATE proyecto SET nombre = ? WHERE id = ?",
                    (proyecto.nombre, proyecto.id),
                )
                filas = cur.rowcount
        except sqlite3.IntegrityError:
            raise NombreDuplicado(f"Ya existe un proyecto llamado {proyecto.nombre}")
        return filas

    def eliminar(self, id):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM proyecto WHERE id = ?", (id,))
                borrados = cur.rowcount
        except sqlite3.IntegrityError:
            raise EntidadEnUso(f"El proyecto {id} tiene horas registradas, no se puede eliminar")
        return borrados > 0
