"""Generación aleatoria y reproducible de ER y cadenas para pruebas masivas."""

import random
from typing import List

from erafd.subconjuntos import cerradura_epsilon
from erafd.thompson import AFND

HOJAS = ["a", "b", "c", ".", "ε", "[ab]", "[^a]", "[a-c]", "\\N", "0", "\\h61", "\\.", "\\*"]
ALFABETO_CADENAS = "abc0.*x"


def er_aleatoria(rng: random.Random, profundidad: int = 4) -> str:
    if profundidad == 0 or rng.random() < 0.25:
        return rng.choice(HOJAS)
    operacion = rng.choice(["concatenacion", "concatenacion", "union", "cerradura"])
    if operacion == "concatenacion":
        return er_aleatoria(rng, profundidad - 1) + er_aleatoria(rng, profundidad - 1)
    if operacion == "union":
        return "(%s|%s)" % (er_aleatoria(rng, profundidad - 1), er_aleatoria(rng, profundidad - 1))
    return "(%s)*" % er_aleatoria(rng, profundidad - 1)


def cadenas_aleatorias(rng: random.Random, cantidad: int, largo_maximo: int = 6) -> List[str]:
    return [
        "".join(rng.choice(ALFABETO_CADENAS) for _ in range(rng.randint(0, largo_maximo)))
        for _ in range(cantidad)
    ]


def acepta_afnd(afnd: AFND, cadena: str) -> bool:
    """Simulación directa del AFND (conjunto de estados activos)."""
    actuales = cerradura_epsilon(afnd, [afnd.inicial])
    for caracter in cadena:
        codigo = ord(caracter)
        siguientes = set()
        for estado in actuales:
            for clave, destinos in afnd.transiciones[estado].items():
                if clave is not None and codigo in clave:
                    siguientes.update(destinos)
        actuales = cerradura_epsilon(afnd, siguientes)
    return afnd.final in actuales
