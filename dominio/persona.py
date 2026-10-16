from dominio.validaciones import validar_rut, validar_texto


class Persona:
    def __init__(self, rut, nombre):
        self._rut = validar_rut(rut)
        self.nombre = nombre          # pasa por el setter, que valida

    @property
    def rut(self):
        # Solo lectura: es la llave natural, no cambia una vez creada la persona.
        return self._rut

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "nombre")

    def __str__(self):
        return f"{self.rut} · {self.nombre}"

    def __repr__(self):
        return f"Persona(rut={self.rut!r}, nombre={self.nombre!r})"
