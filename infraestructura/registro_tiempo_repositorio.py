import sqlite3
from datetime import date

from dominio.excepciones import ReferenciaInexistente
from dominio.registro_tiempo import RegistroTiempo
from infraestructura.conexion import obtener_conexion


class RegistroTiempoRepositorio:

    def _fila_a_registro(self, fila):
        return RegistroTiempo(
            id=fila[0],
            empleado_rut=fila[1],
            proyecto_id=fila[2],
            horas=fila[3],
            fecha=date.fromisoformat(fila[4]),
        )

    def guardar(self, registro):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    """INSERT INTO registro_tiempo (empleado_rut, proyecto_id, horas, fecha)
                       VALUES (?, ?, ?, ?)""",
                    (registro.empleado_rut, registro.proyecto_id,
                     registro.horas, registro.fecha.isoformat()),
                )
                nuevo_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise ReferenciaInexistente(
                f"El empleado {registro.empleado_rut} o el proyecto {registro.proyecto_id} no existe")
        return RegistroTiempo(registro.empleado_rut, registro.proyecto_id,
                              registro.horas, registro.fecha, nuevo_id)

    def obtener(self, id):
        with obtener_conexion() as conn:
            fila = conn.execute(
                """SELECT id, empleado_rut, proyecto_id, horas, fecha
                   FROM registro_tiempo WHERE id = ?""",
                (id,),
            ).fetchone()
        if fila is None:
            return None
        return self._fila_a_registro(fila)

    def listar(self, empleado_rut=None, desde=None, hasta=None):
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
            sql += " WHERE " + " AND ".join(condiciones)
        sql += " ORDER BY fecha"
        with obtener_conexion() as conn:
            filas = conn.execute(sql, params).fetchall()
        lista = []
        for fila in filas:
            lista.append(self._fila_a_registro(fila))
        return lista

    def actualizar(self, registro):
        try:
            with obtener_conexion() as conn:
                cur = conn.execute(
                    """UPDATE registro_tiempo SET proyecto_id = ?, horas = ?, fecha = ?
                       WHERE id = ?""",
                    (registro.proyecto_id, registro.horas, registro.fecha.isoformat(), registro.id),
                )
                filas = cur.rowcount
        except sqlite3.IntegrityError:
            raise ReferenciaInexistente(f"El proyecto {registro.proyecto_id} no existe")
        return filas

    def eliminar(self, id):
        with obtener_conexion() as conn:
            cur = conn.execute("DELETE FROM registro_tiempo WHERE id = ?", (id,))
            borrados = cur.rowcount
        return borrados > 0
