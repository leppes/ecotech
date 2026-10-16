"""Validaciones que comparten varias clases del dominio.

Se escriben una sola vez y las reutilizan Persona, Empleado, Departamento,
Proyecto y RegistroTiempo en sus setters, y el menú al leer del teclado.
"""
import re
from datetime import date

from dominio.excepciones import DatoInvalido, HorasInvalidas, RutInvalido, SueldoInvalido

_FORMATO_RUT = re.compile(r"^(\d{7,8})-([\dK])$")


def validar_texto(valor, campo):
    """Texto obligatorio. Devuelve el texto sin espacios sobrantes."""
    if not isinstance(valor, str) or not valor.strip():
        raise DatoInvalido(f"El campo {campo} es obligatorio y debe ser texto, no {valor!r}")
    return valor.strip()


def validar_fecha(valor, campo):
    if not isinstance(valor, date):
        raise DatoInvalido(f"El campo {campo} debe ser una fecha (date), no {valor!r}")
    return valor


def validar_id(valor, campo):
    """Llave asignada por la base: entero positivo."""
    if not isinstance(valor, int) or valor <= 0:
        raise DatoInvalido(f"El campo {campo} debe ser un entero positivo, no {valor!r}")
    return valor


def validar_sueldo(valor):
    if not isinstance(valor, int) or valor < 0:
        raise SueldoInvalido(f"El sueldo base debe ser un entero mayor o igual a 0, no {valor!r}")
    return valor


def validar_horas(valor):
    if not isinstance(valor, (int, float)) or not 0 < valor <= 24:
        raise HorasInvalidas(f"Las horas deben ser un número mayor que 0 y hasta 24, no {valor!r}")
    return valor


def validar_rut(valor):
    """Formato 12345678-5 y dígito verificador (módulo 11).

    Acepta puntos y la k minúscula; devuelve el RUT normalizado
    (sin puntos, K mayúscula), que es como se guarda en la base.
    """
    if not isinstance(valor, str):
        raise RutInvalido(f"El RUT debe ser texto, no {valor!r}")
    rut = valor.strip().replace(".", "").upper()
    coincidencia = _FORMATO_RUT.match(rut)
    if not coincidencia:
        raise RutInvalido(f"RUT {valor!r} inválido: se espera el formato 12345678-5")
    cuerpo, dv = coincidencia.groups()
    if _digito_verificador(cuerpo) != dv:
        raise RutInvalido(f"RUT {valor!r} inválido: el dígito verificador no corresponde")
    return rut


def _digito_verificador(cuerpo):
    suma = 0
    factor = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = factor + 1 if factor < 7 else 2
    resto = 11 - suma % 11
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)
