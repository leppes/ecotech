import sqlite3

from dominio.excepciones import EntidadEnUso, NombreDuplicado
from dominio.proyecto import Proyecto
from infraestructura.conexion import es_duplicado, es_llave_foranea, obtener_conexion


class ProyectoRepositorio:

    @staticmethod
    def _fila_a_proyecto(fila):
        return Proyecto(id=fila[0], nombre=fila[1])

    def guardar(self, proyecto):
        """Devuelve el proyecto con el id que le asignó la base."""
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "INSERT INTO proyecto (nombre) VALUES (?)",
                    (proyecto.nombre,),
                )
        except sqlite3.IntegrityError as e:
            if es_duplicado(e):
                raise NombreDuplicado(f"Ya existe un proyecto llamado {proyecto.nombre!r}") from e
            raise
        return Proyecto(proyecto.nombre, id=cur.lastrowid)

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT id, nombre FROM proyecto WHERE id = ?", (id,)
            ).fetchone()
        return self._fila_a_proyecto(fila) if fila else None

    def listar(self, nombre_contiene=None):
        sql = "SELECT id, nombre FROM proyecto"
        params = []
        if nombre_contiene:
            sql += " WHERE nombre LIKE ?"
            params.append(f"%{nombre_contiene}%")
        sql += " ORDER BY nombre"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        return [self._fila_a_proyecto(f) for f in filas]

    def actualizar(self, proyecto):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    "UPDATE proyecto SET nombre = ? WHERE id = ?",
                    (proyecto.nombre, proyecto.id),
                )
        except sqlite3.IntegrityError as e:
            if es_duplicado(e):
                raise NombreDuplicado(f"Ya existe un proyecto llamado {proyecto.nombre!r}") from e
            raise
        return cur.rowcount

    def eliminar(self, id):
        # ON DELETE RESTRICT: si el proyecto tiene registros de tiempo, la base lo rechaza.
        try:
            with obtener_conexion() as conn:
                cur = conn.execute("DELETE FROM proyecto WHERE id = ?", (id,))
        except sqlite3.IntegrityError as e:
            if es_llave_foranea(e):
                raise EntidadEnUso(f"El proyecto {id} tiene horas registradas: no se puede borrar") from e
            raise
        return cur.rowcount > 0
