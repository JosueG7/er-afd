"""Evaluación de una cadena con la matriz de transiciones de un AFD."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .subconjuntos import AFD


@dataclass(frozen=True)
class Paso:
    origen: int
    caracter: str
    destino: Optional[int]  # None: no existe transición (la cadena se rechaza)


def simular(afd: AFD, cadena: str) -> Tuple[List[Paso], bool]:
    """Recorre el AFD carácter por carácter.

    Devuelve los pasos realizados y si la cadena es aceptada. El recorrido
    se detiene en el primer carácter sin transición.
    """
    pasos: List[Paso] = []
    estado = afd.inicial
    for caracter in cadena:
        destino = afd.siguiente(estado, caracter)
        pasos.append(Paso(estado, caracter, destino))
        if destino is None:
            return pasos, False
        estado = destino
    return pasos, estado in afd.finales


def acepta(afd: AFD, cadena: str) -> bool:
    return simular(afd, cadena)[1]
