from dominio.validaciones import validar_texto


class Proyecto:
    def __init__(self, nombre: str, id: int = None):
        self._id = id
        self.nombre = nombre

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "nombre del proyecto")

    def __str__(self):
        return f"[{self.id}] {self.nombre}"
