from datetime import date
from typing import Optional

from dominio.persona import Persona
from dominio.validaciones import validar_fecha, validar_id, validar_sueldo


class Empleado(Persona):
    """Empleado ES una Persona: hereda rut y nombre con sus validaciones."""

    def __init__(self, rut: str, nombre: str, fecha_ingreso: date, sueldo_base: int,
                 departamento_id: Optional[int] = None):
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.departamento_id = departamento_id

    @property
    def fecha_ingreso(self) -> date:
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        self._fecha_ingreso = validar_fecha(valor, "fecha_ingreso")

    @property
    def sueldo_base(self) -> int:
        return self._sueldo_base

    @sueldo_base.setter
    def sueldo_base(self, valor):
        self._sueldo_base = validar_sueldo(valor)

    @property
    def departamento_id(self) -> Optional[int]:
        return self._departamento_id

    @departamento_id.setter
    def departamento_id(self, valor):
        # Opcional: un empleado puede no tener departamento asignado todavía.
        self._departamento_id = None if valor is None else validar_id(valor, "departamento_id")

    def __str__(self) -> str:
        # Reutiliza cómo se muestra una Persona y le agrega lo propio del empleado.
        sueldo = f"{self.sueldo_base:,}".replace(",", ".")
        return (f"{super().__str__()} · ingreso {self.fecha_ingreso:%d-%m-%Y} · "
                f"sueldo ${sueldo} · departamento {self.departamento_id or '-'}")

    def __repr__(self):
        return (f"Empleado(rut={self.rut!r}, nombre={self.nombre!r}, "
                f"fecha_ingreso={self.fecha_ingreso}, sueldo_base={self.sueldo_base}, "
                f"departamento_id={self.departamento_id})")
