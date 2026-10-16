"""Errores del negocio de EcoTech.

Hablan el idioma del dominio: la capa de arriba (main, una futura interfaz)
los captura sin necesitar saber qué motor de base de datos hay abajo.
"""


class ErrorDeDominio(Exception):
    """Base de todos los errores del negocio."""


# ---------- Datos con formato inválido: los detecta la propia clase ----------
# Heredan de ValueError porque eso son: un valor con formato incorrecto.

class DatoInvalido(ErrorDeDominio, ValueError):
    """Un dato no cumple el formato esperado."""


class RutInvalido(DatoInvalido):
    """El RUT no tiene el formato 12345678-5 o su dígito verificador no corresponde."""


class SueldoInvalido(DatoInvalido):
    """El sueldo base no es un entero mayor o igual a 0."""


class HorasInvalidas(DatoInvalido):
    """Las horas de un registro no están entre 0 (excluido) y 24."""


# ---------- Reglas que dependen de lo que ya hay en la base ----------
# Las lanza el repositorio al traducir un sqlite3.IntegrityError.

class RutDuplicado(ErrorDeDominio):
    """Ya existe una persona con ese RUT."""


class NombreDuplicado(ErrorDeDominio):
    """Ya existe un departamento o un proyecto con ese nombre."""


class ReferenciaInexistente(ErrorDeDominio):
    """Se apunta a un departamento, proyecto o empleado que no existe."""


class EntidadEnUso(ErrorDeDominio):
    """No se puede borrar algo que todavía usan otros registros."""
