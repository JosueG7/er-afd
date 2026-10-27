"""Construcción de Thompson: árbol sintáctico -> AFND con transiciones ε.

Reglas (N(r) es el autómata de la subexpresión r; i = inicio, f = final):

    símbolo a      i --a--> f
    ε              i --ε--> f
    st             N(s) seguido de N(t); el final de N(s) se fusiona con
                   el inicio de N(t)
    s|t            i --ε--> N(s), i --ε--> N(t), finales --ε--> f
    s*             i --ε--> N(s), i --ε--> f,
                   final de N(s) --ε--> inicio de N(s) y --ε--> f

Los estados se numeran en orden estructural (el inicio de cada
construcción, luego sus partes y al final su estado final), como en el
libro del Dragón (Aho, Lam, Sethi y Ullman, sección 3.7.4). Así q0 es el
inicial y el último estado es el único de aceptación.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .arbol import Cerradura, Concatenacion, Epsilon, Nodo, Simbolo, Union, hojas
from .simbolos import EPSILON, Caracteres

# Una transición ε se identifica con la clave None; las demás, con el
# conjunto de caracteres del símbolo.
Clave = Optional[Caracteres]


@dataclass
class AFND:
    num_estados: int
    inicial: int
    final: int
    # Σ en orden de presentación: (clave, etiqueta).
    alfabeto: List[Tuple[Clave, str]]
    # transiciones[estado][clave] = destinos ordenados.
    transiciones: List[Dict[Clave, Tuple[int, ...]]]

    def etiqueta(self, clave: Clave) -> str:
        for candidata, etiqueta in self.alfabeto:
            if candidata == clave:
                return etiqueta
        raise KeyError(clave)


class _Estado:
    __slots__ = ("aristas",)

    def __init__(self) -> None:
        self.aristas: List[Tuple[Clave, "_Estado"]] = []


# Fragmento: (inicio, final, estados en orden estructural).
_Fragmento = Tuple[_Estado, _Estado, List[_Estado]]


def _construir(nodo: Nodo) -> _Fragmento:
    if isinstance(nodo, (Simbolo, Epsilon)):
        inicio, final = _Estado(), _Estado()
        clave = nodo.caracteres if isinstance(nodo, Simbolo) else None
        inicio.aristas.append((clave, final))
        return inicio, final, [inicio, final]

    if isinstance(nodo, Concatenacion):
        i1, f1, estados1 = _construir(nodo.izquierda)
        i2, f2, estados2 = _construir(nodo.derecha)
        # Fusión: el final de N(s) hereda las transiciones del inicio de N(t).
        # Es seguro porque en Thompson el final no tiene transiciones de
        # salida y el inicio no tiene transiciones de entrada.
        f1.aristas.extend(i2.aristas)
        return i1, f2, estados1 + estados2[1:]

    if isinstance(nodo, Union):
        inicio = _Estado()
        i1, f1, estados1 = _construir(nodo.izquierda)
        i2, f2, estados2 = _construir(nodo.derecha)
        final = _Estado()
        inicio.aristas += [(None, i1), (None, i2)]
        f1.aristas.append((None, final))
        f2.aristas.append((None, final))
        return inicio, final, [inicio] + estados1 + estados2 + [final]

    assert isinstance(nodo, Cerradura)
    inicio = _Estado()
    i1, f1, estados1 = _construir(nodo.hijo)
    final = _Estado()
    inicio.aristas += [(None, i1), (None, final)]
    f1.aristas += [(None, i1), (None, final)]
    return inicio, final, [inicio] + estados1 + [final]


def alfabeto_de(arbol: Nodo) -> List[Tuple[Clave, str]]:
    """Σ del AFND: símbolos en orden de aparición; ε al final si no aparece.

    Dos símbolos con el mismo conjunto de caracteres (por ejemplo `\\N` y
    `[0-9]`) son el mismo símbolo; conserva la primera etiqueta.
    """
    alfabeto: List[Tuple[Clave, str]] = []
    vistos = set()
    for hoja in hojas(arbol):
        clave = hoja.caracteres if isinstance(hoja, Simbolo) else None
        if clave in vistos:
            continue
        vistos.add(clave)
        alfabeto.append((clave, hoja.etiqueta if isinstance(hoja, Simbolo) else EPSILON))
    if None not in vistos:
        alfabeto.append((None, EPSILON))
    return alfabeto


def thompson(arbol: Nodo) -> AFND:
    inicio, final, estados = _construir(arbol)
    numero = {id(estado): i for i, estado in enumerate(estados)}

    transiciones: List[Dict[Clave, Tuple[int, ...]]] = []
    for estado in estados:
        destinos: Dict[Clave, List[int]] = {}
        for clave, destino in estado.aristas:
            destinos.setdefault(clave, []).append(numero[id(destino)])
        transiciones.append({c: tuple(sorted(set(d))) for c, d in destinos.items()})

    return AFND(
        num_estados=len(estados),
        inicial=numero[id(inicio)],
        final=numero[id(final)],
        alfabeto=alfabeto_de(arbol),
        transiciones=transiciones,
    )
