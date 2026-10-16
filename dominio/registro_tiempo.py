from datetime import date

from dominio.validaciones import validar_fecha, validar_horas, validar_id, validar_rut


class RegistroTiempo:
    """Parte de la composición ◆ con Empleado: pertenece a un empleado y muere con él."""

    def __init__(self, empleado_rut, proyecto_id, horas, fecha: date, id=None):
        self._id = id                                  # lo asigna la base (autoincremento)
        self._empleado_rut = validar_rut(empleado_rut)
        self.proyecto_id = proyecto_id
        self.horas = horas
        self.fecha = fecha

    @property
    def id(self):
        return self._id

    @property
    def empleado_rut(self):
        # Solo lectura: por la composición, un registro no cambia de empleado.
        return self._empleado_rut

    @property
    def proyecto_id(self):
        return self._proyecto_id

    @proyecto_id.setter
    def proyecto_id(self, valor):
        self._proyecto_id = validar_id(valor, "proyecto_id")

    @property
    def horas(self):
        return self._horas

    @horas.setter
    def horas(self, valor):
        self._horas = validar_horas(valor)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        self._fecha = validar_fecha(valor, "fecha")

    def __str__(self):
        return (f"[{self.id}] {self.fecha:%d-%m-%Y} · empleado {self.empleado_rut} · "
                f"proyecto {self.proyecto_id} · {self.horas} h")

    def __repr__(self):
        return (f"RegistroTiempo(id={self.id}, empleado_rut={self.empleado_rut!r}, "
                f"proyecto_id={self.proyecto_id}, horas={self.horas}, fecha={self.fecha})")
