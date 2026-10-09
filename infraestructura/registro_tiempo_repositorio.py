from datetime import date

from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import obtener_conexion


class RegistroTiempoRepositorio:

    @staticmethod
    def _fila_a_registro(fila):
        return RegistroTiempo(
            id=fila[0],
            empleado_rut=fila[1],
            proyecto_id=fila[2],
            horas=fila[3],
            fecha=date.fromisoformat(fila[4]),
        )

    def guardar(self, registro):
        with obtener_conexion() as conn:
            cur = conn.execute(
                """INSERT INTO registro_tiempo (empleado_rut, proyecto_id, horas, fecha)
                   VALUES (?, ?, ?, ?)""",
                (registro.empleado_rut, registro.proyecto_id,
                 registro.horas, registro.fecha.isoformat()),
            )
        registro.id = cur.lastrowid
        return registro

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                """SELECT id, empleado_rut, proyecto_id, horas, fecha
                   FROM registro_tiempo WHERE id = ?""",
                (id,),
            ).fetchone()
        return self._fila_a_registro(fila) if fila else None

    def listar(self, empleado_rut=None, desde=None, hasta=None):
        """Filtros opcionales. Cada filtro agrega TEXTO FIJO con su ?,
        y el valor va a la lista de parámetros. Nunca se concatena el valor."""
        sql = "SELECT id, empleado_rut, proyecto_id, horas, fecha FROM registro_tiempo"
        condiciones = []
        params = []
        if empleado_rut:
            condiciones.append("empleado_rut = ?")
            params.append(empleado_rut)
        if desde:
            condiciones.append("fecha >= ?")
            params.append(desde.isoformat())
        if hasta:
            condiciones.append("fecha <= ?")
            params.append(hasta.isoformat())
        if condiciones:
            sql += " WHERE "
            sql += " AND ".join(condiciones)   # une textos fijos, no valores
        sql += " ORDER BY fecha"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        return [self._fila_a_registro(f) for f in filas]

    def actualizar(self, registro):
        with obtener_conexion() as conn:
            cur = conn.execute(
                """UPDATE registro_tiempo SET proyecto_id = ?, horas = ?, fecha = ?
                   WHERE id = ?""",
                (registro.proyecto_id, registro.horas, registro.fecha.isoformat(), registro.id),
            )
        return cur.rowcount

    def eliminar(self, id):
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM registro_tiempo WHERE id = ?", (id,))
        return cur.rowcount > 0
