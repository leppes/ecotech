from dominio.validaciones import validar_rut, validar_texto


class Persona:
    def __init__(self, rut: str, nombre: str):
        self._rut = validar_rut(rut)
        self.nombre = nombre

    @property
    def rut(self):
        return self._rut

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "nombre")

    def __str__(self):
        return f"{self.rut} - {self.nombre}"
