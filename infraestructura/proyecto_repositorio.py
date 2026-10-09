from dominio.proyecto import Proyecto
from infraestructura.conexion import obtener_conexion


class ProyectoRepositorio:

    @staticmethod
    def _fila_a_proyecto(fila):
        return Proyecto(id=fila[0], nombre=fila[1])

    def guardar(self, proyecto):
        with obtener_conexion() as conn:
            cur = conn.execute(
                "INSERT INTO proyecto (nombre) VALUES (?)",
                (proyecto.nombre,),
            )
        proyecto.id = cur.lastrowid   # el id lo asignó la base
        return proyecto

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
        with obtener_conexion() as conn:
            cur = conn.execute(
                "UPDATE proyecto SET nombre = ? WHERE id = ?",
                (proyecto.nombre, proyecto.id),
            )
        return cur.rowcount

    def eliminar(self, id):
        # ON DELETE RESTRICT: si el proyecto tiene registros de tiempo,
        # la base lo rechaza y se lanza ErrorDeConexion.
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM proyecto WHERE id = ?", (id,))
        return cur.rowcount > 0
