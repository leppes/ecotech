from datetime import date


class RegistroTiempo:
    def __init__(self, empleado_rut, proyecto_id, horas, fecha: date, id=None):
        self.id = id          # lo asigna la base (autoincremento)
        self.empleado_rut = empleado_rut
        self.proyecto_id = proyecto_id
        self.horas = horas
        self.fecha = fecha

    def __repr__(self):
        return (f"RegistroTiempo(id={self.id}, empleado_rut={self.empleado_rut!r}, "
                f"proyecto_id={self.proyecto_id}, horas={self.horas}, fecha={self.fecha})")
