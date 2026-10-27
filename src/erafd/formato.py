"""Presentación de los autómatas y del recorrido con el formato del enunciado:

    <estado actual>|<símbolo>|<estado o conjunto de estados destino>
"""

from typing import Iterable, List

from .simbolos import VACIO, mostrar_caracter
from .simulador import Paso
from .subconjuntos import AFD
from .thompson import AFND


def _conjunto(nombres: Iterable[str]) -> str:
    return "{" + ",".join(nombres) + "}"


def lineas_afnd(afnd: AFND) -> List[str]:
    nombre = lambda estado: "q%d" % estado  # noqa: E731
    lineas = [
        "AFND",
        "Q=" + _conjunto(nombre(e) for e in range(afnd.num_estados)),
        "Σ=" + _conjunto(etiqueta for _, etiqueta in afnd.alfabeto),
        "F=" + _conjunto([nombre(afnd.final)]),
    ]
    for estado in range(afnd.num_estados):
        for clave, etiqueta in afnd.alfabeto:
            destinos = afnd.transiciones[estado].get(clave)
            if destinos:
                lineas.append(
                    "%s|%s|%s" % (nombre(estado), etiqueta, _conjunto(nombre(d) for d in destinos))
                )
    return lineas


def lineas_afd(afd: AFD, titulo: str = "AFD", prefijo: str = "Q") -> List[str]:
    nombre = lambda estado: "%s%d" % (prefijo, estado)  # noqa: E731
    lineas = [
        titulo,
        "Q=" + _conjunto(nombre(e) for e in range(afd.num_estados)),
        "Σ=" + _conjunto(etiqueta for etiqueta, _ in afd.alfabeto),
        "F=" + _conjunto(nombre(e) for e in sorted(afd.finales)),
    ]
    for estado in range(afd.num_estados):
        for indice, (etiqueta, _) in enumerate(afd.alfabeto):
            destino = afd.transiciones[estado].get(indice)
            if destino is not None:
                lineas.append("%s|%s|%s" % (nombre(estado), etiqueta, nombre(destino)))
    return lineas


def lineas_subconjuntos(afd: AFD, prefijo: str = "Q", prefijo_origen: str = "q") -> List[str]:
    """Composición de cada estado del AFD (opción -v)."""
    return [
        "%s%d=%s" % (prefijo, i, _conjunto("%s%d" % (prefijo_origen, e) for e in sorted(conjunto)))
        for i, conjunto in enumerate(afd.subconjuntos)
    ]


def lineas_recorrido(pasos: List[Paso], aceptada: bool, prefijo: str = "Q") -> List[str]:
    lineas = []
    for paso in pasos:
        destino = VACIO if paso.destino is None else "%s%d" % (prefijo, paso.destino)
        lineas.append(
            "%s%d|%s|%s" % (prefijo, paso.origen, mostrar_caracter(ord(paso.caracter)), destino)
        )
    lineas.append("Cadena aceptada" if aceptada else "Cadena rechazada")
    return lineas
