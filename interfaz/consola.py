"""Lectura de datos por teclado.

Cada función vuelve a preguntar hasta recibir un dato válido: un error de
tipeo nunca interrumpe el programa.
"""
from datetime import date, datetime


def pedir(mensaje, convertir=str, actual=None, opcional=False):
    """Pregunta hasta que `convertir` acepte lo escrito.

    - `convertir` recibe el texto y lanza ValueError si no sirve. Los errores
      de datos del dominio (RutInvalido, ...) también son ValueError.
    - Con `actual` (al editar), Enter vacío conserva el valor actual.
    - Con `opcional`, Enter vacío devuelve None.
    """
    if actual is not None:
        mostrado = actual.strftime("%d-%m-%Y") if isinstance(actual, date) else actual
        mensaje = f"{mensaje} [{mostrado}]"
    while True:
        texto = input(f"{mensaje}: ").strip()
        if not texto:
            if actual is not None:
                return actual
            if opcional:
                return None
            print("  ✘ Este dato es obligatorio.")
            continue
        try:
            return convertir(texto)
        except ValueError as e:
            print(f"  ✘ {e}")


def confirmar(mensaje):
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("  ✘ Responde s o n.")


def mostrar_lista(elementos):
    if not elementos:
        print("  (sin resultados)")
    for elemento in elementos:
        print(f"  {elemento}")


# ---------- Convertidores: texto -> tipo de Python, con mensajes claros ----------

def a_entero(texto):
    try:
        return int(texto.replace(".", ""))      # acepta 950.000
    except ValueError:
        raise ValueError(f"{texto!r} no es un número entero") from None


def a_decimal(texto):
    try:
        return float(texto.replace(",", "."))   # acepta 7,5
    except ValueError:
        raise ValueError(f"{texto!r} no es un número") from None


def a_fecha(texto):
    try:
        return datetime.strptime(texto, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError(f"{texto!r} no es una fecha válida: se espera DD-MM-AAAA") from None
