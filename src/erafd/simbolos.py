"""Conjuntos de caracteres y su representación textual.

Cada símbolo de una expresión regular se modela como el conjunto (frozenset)
de códigos ASCII que acepta. Así `a`, `.`, `[a-z]` o `\\N` se tratan de forma
uniforme en todo el programa.
"""

from typing import FrozenSet, Iterable, List

Caracteres = FrozenSet[int]

EPSILON = "ε"
VACIO = "∅"

# El universo de símbolos es el código ASCII (0-127).
UNIVERSO: Caracteres = frozenset(range(128))


def _rango(desde: str, hasta: str) -> Caracteres:
    return frozenset(range(ord(desde), ord(hasta) + 1))


DIGITOS = _rango("0", "9")
MAYUSCULAS = _rango("A", "Z")
MINUSCULAS = _rango("a", "z")
LETRAS = MAYUSCULAS | MINUSCULAS

# Clases predefinidas por secuencias de escape especiales.
CLASES_ESCAPE = {
    "N": DIGITOS,
    "A": MAYUSCULAS,
    "a": MINUSCULAS,
    "z": LETRAS,
}

# Caracteres que actúan como operadores fuera de un conjunto.
ESPECIALES = set(".|*()[]\\")

# Caracteres que deben escaparse al escribirse dentro de un conjunto.
ESPECIALES_EN_CONJUNTO = set("[]\\^-")


def _no_imprimible(codigo: int) -> bool:
    return codigo <= 32 or codigo == 127


def mostrar_caracter(codigo: int) -> str:
    """Representación de un carácter tal como se escribiría en una ER.

    Los operadores se escapan (`\\|`, `\\.`) y el espacio y los caracteres
    de control se muestran en hexadecimal (`\\h20`), para que nunca se
    confundan con el separador `|` de las tablas.
    """
    if codigo > 127:
        return chr(codigo)
    if _no_imprimible(codigo):
        return "\\h%02X" % codigo
    caracter = chr(codigo)
    if caracter in ESPECIALES:
        return "\\" + caracter
    return caracter


def _mostrar_en_conjunto(codigo: int) -> str:
    if _no_imprimible(codigo):
        return "\\h%02X" % codigo
    caracter = chr(codigo)
    if caracter in ESPECIALES_EN_CONJUNTO:
        return "\\" + caracter
    return caracter


def _rangos(codigos: Iterable[int]) -> str:
    """Escribe una colección de códigos con notación de rangos: `a-dxz`."""
    ordenados = sorted(codigos)
    partes: List[str] = []
    i = 0
    while i < len(ordenados):
        j = i
        while j + 1 < len(ordenados) and ordenados[j + 1] == ordenados[j] + 1:
            j += 1
        if j - i >= 2:
            partes.append(
                _mostrar_en_conjunto(ordenados[i]) + "-" + _mostrar_en_conjunto(ordenados[j])
            )
        else:
            partes.extend(_mostrar_en_conjunto(c) for c in ordenados[i : j + 1])
        i = j + 1
    return "".join(partes)


def etiqueta_conjunto(caracteres: Caracteres) -> str:
    """Nombre legible de un conjunto de caracteres (`a`, `\\N`, `[b-z]`, `[^a]`)."""
    if len(caracteres) == 1:
        return mostrar_caracter(next(iter(caracteres)))
    if caracteres == UNIVERSO:
        return "."
    for letra, clase in CLASES_ESCAPE.items():
        if caracteres == clase:
            return "\\" + letra
    complemento = UNIVERSO - caracteres
    if len(complemento) < len(caracteres):
        return "[^" + _rangos(complemento) + "]"
    return "[" + _rangos(caracteres) + "]"
