"""ER-AFD: convertidor de expresiones regulares a autómatas finitos deterministas."""

from typing import Tuple

from .arbol import Nodo
from .parser import analizar
from .subconjuntos import AFD, construir_afd
from .thompson import AFND, thompson

__version__ = "1.0.0"


def convertir(expresion: str) -> Tuple[Nodo, AFND, AFD]:
    """ER -> (árbol sintáctico, AFND de Thompson, AFD por subconjuntos)."""
    arbol = analizar(expresion)
    afnd = thompson(arbol)
    return arbol, afnd, construir_afd(afnd)
