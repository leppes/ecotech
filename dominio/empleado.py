from datetime import date

from dominio.persona import Persona
from dominio.validaciones import validar_dias, validar_fecha, validar_id, validar_sueldo


class Empleado(Persona):
    def __init__(self, rut: str, nombre: str, fecha_ingreso: date, sueldo_base: int,
                 departamento_id: int = None):
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.departamento_id = departamento_id

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        self._fecha_ingreso = validar_fecha(valor, "fecha de ingreso")

    @property
    def sueldo_base(self):
        return self._sueldo_base

    @sueldo_base.setter
    def sueldo_base(self, valor):
        self._sueldo_base = validar_sueldo(valor)

    @property
    def departamento_id(self):
        return self._departamento_id

    @departamento_id.setter
    def departamento_id(self, valor):
        if valor is None:
            self._departamento_id = None
        else:
            self._departamento_id = validar_id(valor, "id del departamento")

    def antiguedad(self):
        hoy = date.today()
        anios = hoy.year - self.fecha_ingreso.year
        if (hoy.month, hoy.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day):
            anios = anios - 1
        return anios

    def calcular_sueldo_proporcional(self, dias_trabajados):
        dias = validar_dias(dias_trabajados)
        return round(self.sueldo_base * dias / 30)

    def __str__(self):
        texto = super().__str__()
        texto += f" - ingreso {self.fecha_ingreso.strftime('%d-%m-%Y')}"
        texto += f" - sueldo ${self.sueldo_base}"
        if self.departamento_id is not None:
            texto += f" - departamento {self.departamento_id}"
        return texto
