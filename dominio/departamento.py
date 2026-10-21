from typing import Optional

from dominio.validaciones import validar_texto


class Departamento:
    def __init__(self, nombre: str, id: Optional[int] = None):
        self._id = id            # lo asigna la base (autoincremento)
        self.nombre = nombre     # pasa por el setter, que valida

    @property
    def id(self) -> Optional[int]:
        # Solo lectura: el id lo decide la base, no el programa.
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "nombre del departamento")

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre}"

    def __repr__(self):
        return f"Departamento(id={self.id}, nombre={self.nombre!r})"
