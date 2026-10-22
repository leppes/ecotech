from datetime import date

from dominio.excepciones import DatoInvalido


def validar_texto(valor, campo):
    if not isinstance(valor, str) or valor.strip() == "":
        raise DatoInvalido(f"El {campo} no puede estar vacío")
    return valor.strip()


def validar_fecha(valor, campo):
    if not isinstance(valor, date):
        raise DatoInvalido(f"La {campo} debe ser una fecha")
    return valor


def validar_id(valor, campo):
    if not isinstance(valor, int) or valor <= 0:
        raise DatoInvalido(f"El {campo} debe ser un número mayor que 0")
    return valor


def validar_sueldo(valor):
    if not isinstance(valor, int) or valor < 0:
        raise DatoInvalido("El sueldo debe ser un número entero mayor o igual a 0")
    return valor


def validar_dias(valor):
    if not isinstance(valor, int) or valor < 0 or valor > 30:
        raise DatoInvalido("Los días trabajados deben estar entre 0 y 30")
    return valor


def validar_horas(valor):
    if not isinstance(valor, (int, float)) or valor <= 0 or valor > 24:
        raise DatoInvalido("Las horas deben ser mayores que 0 y como máximo 24")
    return valor


def calcular_dv(numero):
    suma = 0
    factor = 2
    for digito in reversed(numero):
        suma = suma + int(digito) * factor
        factor = factor + 1
        if factor > 7:
            factor = 2
    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar_rut(rut):
    if not isinstance(rut, str):
        raise DatoInvalido("El RUT debe ser texto")
    rut = rut.strip().replace(".", "").upper()
    if rut.count("-") != 1:
        raise DatoInvalido("El RUT debe tener el formato 12345678-5")
    numero, dv = rut.split("-")
    if not numero.isdigit() or len(numero) < 7 or len(numero) > 8 or len(dv) != 1:
        raise DatoInvalido("El RUT debe tener el formato 12345678-5")
    if calcular_dv(numero) != dv:
        raise DatoInvalido("El dígito verificador del RUT no es correcto")
    return rut
