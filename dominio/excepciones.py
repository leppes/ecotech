class ErrorDeDominio(Exception):
    pass


class DatoInvalido(ErrorDeDominio, ValueError):
    pass


class RutDuplicado(ErrorDeDominio):
    pass


class NombreDuplicado(ErrorDeDominio):
    pass


class ReferenciaInexistente(ErrorDeDominio):
    pass


class EntidadEnUso(ErrorDeDominio):
    pass
