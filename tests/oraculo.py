"""Oráculo independiente para validar los autómatas.

Decide si una cadena pertenece al lenguaje de la ER recorriendo
directamente el árbol sintáctico, sin construir autómatas. Para cada
subexpresión calcula las posiciones de la cadena en las que puede terminar
un emparejamiento que empieza en la posición i. No usa librerías de regex.
"""

from typing import Dict, FrozenSet, Tuple

from erafd.arbol import Cerradura, Concatenacion, Epsilon, Nodo, Simbolo, Union


def coincide(arbol: Nodo, cadena: str) -> bool:
    memo: Dict[Tuple[int, int], FrozenSet[int]] = {}

    def fines(nodo: Nodo, i: int) -> FrozenSet[int]:
        clave = (id(nodo), i)
        if clave in memo:
            return memo[clave]
        if isinstance(nodo, Simbolo):
            ok = i < len(cadena) and ord(cadena[i]) in nodo.caracteres
            resultado = frozenset({i + 1}) if ok else frozenset()
        elif isinstance(nodo, Epsilon):
            resultado = frozenset({i})
        elif isinstance(nodo, Concatenacion):
            acumulado = set()
            for j in fines(nodo.izquierda, i):
                acumulado |= fines(nodo.derecha, j)
            resultado = frozenset(acumulado)
        elif isinstance(nodo, Union):
            resultado = fines(nodo.izquierda, i) | fines(nodo.derecha, i)
        else:
            assert isinstance(nodo, Cerradura)
            alcanzadas = {i}
            pendientes = [i]
            while pendientes:
                for k in fines(nodo.hijo, pendientes.pop()):
                    if k not in alcanzadas:
                        alcanzadas.add(k)
                        pendientes.append(k)
            resultado = frozenset(alcanzadas)
        memo[clave] = resultado
        return resultado

    return len(cadena) in fines(arbol, 0)
