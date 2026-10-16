from datetime import date

from dominio.excepciones import SueldoInvalido
from dominio.persona import Persona
from dominio.validaciones import validar_fecha, validar_id


class Empleado(Persona):
    """Empleado ES una Persona: hereda rut y nombre con sus validaciones."""

    def __init__(self, rut, nombre, fecha_ingreso: date, sueldo_base, departamento_id=None):
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.departamento_id = departamento_id

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        self._fecha_ingreso = validar_fecha(valor, "fecha_ingreso")

    @property
    def sueldo_base(self):
        return self._sueldo_base

    @sueldo_base.setter
    def sueldo_base(self, valor):
        if not isinstance(valor, int) or valor < 0:
            raise SueldoInvalido(f"El sueldo base debe ser un entero mayor o igual a 0, no {valor!r}")
        self._sueldo_base = valor

    @property
    def departamento_id(self):
        return self._departamento_id

    @departamento_id.setter
    def departamento_id(self, valor):
        # Opcional: un empleado puede no tener departamento asignado todavía.
        self._departamento_id = None if valor is None else validar_id(valor, "departamento_id")

    def __repr__(self):
        return (f"Empleado(rut={self.rut!r}, nombre={self.nombre!r}, "
                f"fecha_ingreso={self.fecha_ingreso}, sueldo_base={self.sueldo_base}, "
                f"departamento_id={self.departamento_id})")
