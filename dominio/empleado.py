from datetime import date

from dominio.persona import Persona


class Empleado(Persona):
    def __init__(self, rut, nombre, fecha_ingreso: date, sueldo_base, departamento_id=None):
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.departamento_id = departamento_id

    def __repr__(self):
        return (f"Empleado(rut={self.rut!r}, nombre={self.nombre!r}, "
                f"fecha_ingreso={self.fecha_ingreso}, sueldo_base={self.sueldo_base}, "
                f"departamento_id={self.departamento_id})")
