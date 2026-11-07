"""Nodos del árbol sintáctico de una expresión regular."""

from dataclasses import dataclass
from typing import Iterator, Union as Tipos

from .simbolos import EPSILON, Caracteres


@dataclass(frozen=True)
class Simbolo:
    """Hoja que consume un carácter perteneciente a `caracteres`."""

    etiqueta: str
    caracteres: Caracteres


@dataclass(frozen=True)
class Epsilon:
    """Hoja que representa la cadena vacía (ε)."""


@dataclass(frozen=True)
class Concatenacion:
    izquierda: "Nodo"
    derecha: "Nodo"


@dataclass(frozen=True)
class Union:
    izquierda: "Nodo"
    derecha: "Nodo"


@dataclass(frozen=True)
class Cerradura:
    """Cerradura de Kleene: cero o más repeticiones de `hijo`."""

    hijo: "Nodo"


Nodo = Tipos[Simbolo, Epsilon, Concatenacion, Union, Cerradura]


def hojas(nodo: Nodo) -> Iterator[Tipos[Simbolo, Epsilon]]:
    """Recorre las hojas de izquierda a derecha (orden de aparición en la ER)."""
    pila = [nodo]
    while pila:
        actual = pila.pop()
        if isinstance(actual, (Simbolo, Epsilon)):
            yield actual
        elif isinstance(actual, Cerradura):
            pila.append(actual.hijo)
        else:
            pila.append(actual.derecha)
            pila.append(actual.izquierda)


def representar(nodo: Nodo) -> str:
    """Forma textual totalmente parentizada, útil para pruebas y depuración."""
    if isinstance(nodo, Simbolo):
        return nodo.etiqueta
    if isinstance(nodo, Epsilon):
        return EPSILON
    if isinstance(nodo, Cerradura):
        return "(" + representar(nodo.hijo) + ")*"
    if isinstance(nodo, Concatenacion):
        return "(" + representar(nodo.izquierda) + representar(nodo.derecha) + ")"
    return "(" + representar(nodo.izquierda) + "|" + representar(nodo.derecha) + ")"
