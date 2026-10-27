"""Exportación de autómatas al lenguaje DOT de Graphviz.

Las imágenes se generan con:  dot -Tpng archivo.dot -o archivo.png
"""

from typing import Dict, List, Tuple

from .subconjuntos import AFD
from .thompson import AFND


def _texto(etiqueta: str) -> str:
    return etiqueta.replace("\\", "\\\\").replace('"', '\\"')


def _grafo(
    nombre: str,
    estados: List[str],
    finales: List[str],
    aristas: Dict[Tuple[str, str], List[str]],
) -> str:
    lineas = [
        "digraph %s {" % nombre,
        "  rankdir=LR;",
        '  node [shape=circle, fontname="Helvetica"];',
        '  edge [fontname="Helvetica"];',
        "  inicio [shape=point];",
    ]
    for estado in estados:
        forma = "doublecircle" if estado in finales else "circle"
        lineas.append('  %s [shape=%s, label="%s"];' % (estado, forma, estado))
    lineas.append("  inicio -> %s;" % estados[0])
    for (origen, destino), etiquetas in aristas.items():
        lineas.append(
            '  %s -> %s [label="%s"];' % (origen, destino, _texto(", ".join(etiquetas)))
        )
    lineas.append("}")
    return "\n".join(lineas) + "\n"


def afnd_a_dot(afnd: AFND) -> str:
    aristas: Dict[Tuple[str, str], List[str]] = {}
    for estado in range(afnd.num_estados):
        for clave, etiqueta in afnd.alfabeto:
            for destino in afnd.transiciones[estado].get(clave, ()):
                aristas.setdefault(("q%d" % estado, "q%d" % destino), []).append(etiqueta)
    estados = ["q%d" % e for e in range(afnd.num_estados)]
    return _grafo("AFND", estados, ["q%d" % afnd.final], aristas)


def afd_a_dot(afd: AFD, prefijo: str = "Q") -> str:
    aristas: Dict[Tuple[str, str], List[str]] = {}
    for estado in range(afd.num_estados):
        for indice, (etiqueta, _) in enumerate(afd.alfabeto):
            destino = afd.transiciones[estado].get(indice)
            if destino is not None:
                clave = ("%s%d" % (prefijo, estado), "%s%d" % (prefijo, destino))
                aristas.setdefault(clave, []).append(etiqueta)
    estados = ["%s%d" % (prefijo, e) for e in range(afd.num_estados)]
    finales = ["%s%d" % (prefijo, e) for e in afd.finales]
    return _grafo("AFD", estados, finales, aristas)
