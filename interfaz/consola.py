from datetime import date, datetime


def pedir(mensaje, convertir=str, actual=None, opcional=False):
    if actual is not None:
        if isinstance(actual, date):
            mensaje = f"{mensaje} [{actual.strftime('%d-%m-%Y')}]"
        else:
            mensaje = f"{mensaje} [{actual}]"
    while True:
        texto = input(f"{mensaje}: ").strip()
        if texto == "":
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
        if respuesta == "s":
            return True
        if respuesta == "n":
            return False
        print("  ✘ Responde s o n.")


def mostrar_lista(elementos):
    if len(elementos) == 0:
        print("  (sin resultados)")
    for elemento in elementos:
        print(f"  {elemento}")


def a_entero(texto):
    try:
        return int(texto.replace(".", ""))
    except ValueError:
        raise ValueError(f"'{texto}' no es un número entero")


def a_decimal(texto):
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ValueError(f"'{texto}' no es un número")


def a_fecha(texto):
    try:
        return datetime.strptime(texto, "%d-%m-%Y").date()
    except ValueError:
        raise ValueError(f"'{texto}' no es una fecha válida, usa el formato DD-MM-AAAA")
