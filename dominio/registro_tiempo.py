from datetime import date

from dominio.validaciones import validar_fecha, validar_horas, validar_id, validar_rut


class RegistroTiempo:
    def __init__(self, empleado_rut: str, proyecto_id: int, horas: float, fecha: date,
                 id: int = None):
        self._id = id
        self._empleado_rut = validar_rut(empleado_rut)
        self.proyecto_id = proyecto_id
        self.horas = horas
        self.fecha = fecha

    @property
    def id(self):
        return self._id

    @property
    def empleado_rut(self):
        return self._empleado_rut

    @property
    def proyecto_id(self):
        return self._proyecto_id

    @proyecto_id.setter
    def proyecto_id(self, valor):
        self._proyecto_id = validar_id(valor, "id del proyecto")

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
        fecha = self.fecha.strftime("%d-%m-%Y")
        return (f"[{self.id}] {fecha} - empleado {self.empleado_rut} - "
                f"proyecto {self.proyecto_id} - {self.horas} horas")
