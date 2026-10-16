from dominio.validaciones import validar_texto


class Proyecto:
    def __init__(self, nombre, id=None):
        self._id = id            # lo asigna la base (autoincremento)
        self.nombre = nombre     # pasa por el setter, que valida

    @property
    def id(self):
        # Solo lectura: el id lo decide la base, no el programa.
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "nombre del proyecto")

    def __repr__(self):
        return f"Proyecto(id={self.id}, nombre={self.nombre!r})"
