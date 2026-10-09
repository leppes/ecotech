class Proyecto:
    def __init__(self, nombre, id=None):
        self.id = id          # lo asigna la base (autoincremento)
        self.nombre = nombre

    def __repr__(self):
        return f"Proyecto(id={self.id}, nombre={self.nombre!r})"
