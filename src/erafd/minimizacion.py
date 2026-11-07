"""Minimización de un AFD por refinamiento de particiones (algoritmo de Moore).

1. Se completa el AFD con un estado sumidero implícito.
2. Partición inicial: {estados de aceptación, estados de no aceptación}.
3. Se separan los estados de un bloque cuyas transiciones lleven, con
   algún símbolo, a bloques distintos. Se repite hasta que no cambie.
4. Cada bloque es un estado del AFD mínimo; el bloque del sumidero se
   descarta y los estados se renumeran en orden de descubrimiento.
"""

from typing import Dict, FrozenSet, List, Tuple

from .subconjuntos import AFD


def minimizar(afd: AFD) -> AFD:
    sumidero = afd.num_estados
    simbolos = range(len(afd.alfabeto))

    def destino(estado: int, simbolo: int) -> int:
        if estado == sumidero:
            return sumidero
        return afd.transiciones[estado].get(simbolo, sumidero)

    todos = list(range(afd.num_estados + 1))
    bloque = {e: (1 if e in afd.finales else 0) for e in todos}
    while True:
        firmas: Dict[Tuple[int, ...], int] = {}
        nuevo = {}
        for estado in todos:
            firma = (bloque[estado],) + tuple(bloque[destino(estado, s)] for s in simbolos)
            nuevo[estado] = firmas.setdefault(firma, len(firmas))
        if len(firmas) == len(set(bloque.values())):
            break
        bloque = nuevo

    # Renumeración BFS desde el bloque inicial, omitiendo el del sumidero.
    muerto = bloque[sumidero]
    numero = {bloque[afd.inicial]: 0}
    orden = [bloque[afd.inicial]]
    representante = {}
    for estado in range(afd.num_estados):
        representante.setdefault(bloque[estado], estado)
    transiciones: List[Dict[int, int]] = []
    i = 0
    while i < len(orden):
        estado = representante[orden[i]]
        fila = {}
        for simbolo in simbolos:
            b = bloque[destino(estado, simbolo)]
            if b == muerto:
                continue
            if b not in numero:
                numero[b] = len(orden)
                orden.append(b)
            fila[simbolo] = numero[b]
        transiciones.append(fila)
        i += 1

    subconjuntos: List[FrozenSet[int]] = [
        frozenset(e for e in range(afd.num_estados) if bloque[e] == b) for b in orden
    ]
    return AFD(
        num_estados=len(orden),
        inicial=0,
        finales={numero[bloque[e]] for e in afd.finales if bloque[e] in numero},
        alfabeto=afd.alfabeto,
        transiciones=transiciones,
        subconjuntos=subconjuntos,
    )
