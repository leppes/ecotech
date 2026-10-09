class Persona:
    def __init__(self, rut, nombre):
        self.rut = rut
        self.nombre = nombre

    def __repr__(self):
        return f"Persona(rut={self.rut!r}, nombre={self.nombre!r})"
