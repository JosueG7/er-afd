"""Construcción de subconjuntos: AFND -> AFD.

    Q0 = cerradura-ε({q0})
    mientras haya un estado T sin marcar:
        marcar T
        para cada símbolo c de Σ:
            U = cerradura-ε(mover(T, c))
            si U no está vacío: agregar U si es nuevo; δ(T, c) = U

Antes de aplicar el algoritmo, el alfabeto se divide en clases disjuntas.
Los símbolos de una ER pueden solaparse: en `a|.`, la letra `a` pertenece
tanto a `a` como a `.`. Si se tomaran como símbolos independientes, desde
un mismo estado habría dos transiciones posibles con la entrada `a` y el
autómata no sería determinista. Por eso los caracteres se agrupan según
los símbolos de la ER a los que pertenecen. Para `a|.` las clases son {a}
y "todo lo demás", y cada carácter de la entrada cae en exactamente una.
"""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple

from .simbolos import UNIVERSO, Caracteres, etiqueta_conjunto
from .thompson import AFND


@dataclass
class AFD:
    num_estados: int
    inicial: int
    finales: Set[int]
    # Σ del AFD: clases disjuntas en orden de presentación (etiqueta, caracteres).
    alfabeto: List[Tuple[str, Caracteres]]
    # transiciones[estado][índice de clase en Σ] = estado destino.
    transiciones: List[Dict[int, int]]
    # Estados del autómata de origen que agrupa cada estado (para -v).
    subconjuntos: List[FrozenSet[int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._clase_de: List[Optional[int]] = [None] * len(UNIVERSO)
        for indice, (_, caracteres) in enumerate(self.alfabeto):
            for codigo in caracteres:
                self._clase_de[codigo] = indice

    def clase_de(self, caracter: str) -> Optional[int]:
        """Índice en Σ de la clase que contiene al carácter, o None."""
        codigo = ord(caracter)
        return self._clase_de[codigo] if codigo < len(self._clase_de) else None

    def siguiente(self, estado: int, caracter: str) -> Optional[int]:
        clase = self.clase_de(caracter)
        if clase is None:
            return None
        return self.transiciones[estado].get(clase)


def particionar(simbolos: List[Tuple[Caracteres, str]]) -> List[Tuple[str, Caracteres]]:
    """Divide los caracteres de los símbolos en clases disjuntas, con su etiqueta.

    Dos caracteres quedan en la misma clase si pertenecen exactamente a los
    mismos símbolos de la ER.
    """
    por_firma: Dict[Tuple[bool, ...], Set[int]] = {}
    for codigo in sorted(UNIVERSO):
        firma = tuple(codigo in caracteres for caracteres, _ in simbolos)
        if any(firma):
            por_firma.setdefault(firma, set()).add(codigo)

    clases = []
    for firma, codigos in por_firma.items():
        bloque = frozenset(codigos)
        contenedores = [i for i, presente in enumerate(firma) if presente]
        iguales = [i for i in contenedores if simbolos[i][0] == bloque]
        if iguales:
            # La clase coincide con un símbolo de la ER: usa su nombre.
            orden = iguales[0]
            etiqueta = simbolos[orden][1]
        elif len(contenedores) == 1 and simbolos[contenedores[0]][1] == ".":
            # Lo que solo cubre `.` se lee como "cualquier otro símbolo".
            orden = contenedores[0]
            etiqueta = "."
        else:
            orden = contenedores[0]
            etiqueta = etiqueta_conjunto(bloque)
        clases.append(((orden, min(bloque)), etiqueta, bloque))

    clases.sort(key=lambda clase: clase[0])
    return [(etiqueta, bloque) for _, etiqueta, bloque in clases]


def cerradura_epsilon(afnd: AFND, estados: Iterable[int]) -> FrozenSet[int]:
    """Estados alcanzables desde `estados` usando solo transiciones ε."""
    resultado = set(estados)
    pila = list(resultado)
    while pila:
        estado = pila.pop()
        for destino in afnd.transiciones[estado].get(None, ()):
            if destino not in resultado:
                resultado.add(destino)
                pila.append(destino)
    return frozenset(resultado)


def mover(afnd: AFND, estados: Iterable[int], clase: Caracteres) -> Set[int]:
    """Estados alcanzables con una transición sobre la clase de caracteres.

    Como las clases dividen a los símbolos, una clase está contenida por
    completo en un símbolo o no comparte caracteres con él; basta revisar
    uno de sus caracteres.
    """
    representante = next(iter(clase))
    resultado: Set[int] = set()
    for estado in estados:
        for clave, destinos in afnd.transiciones[estado].items():
            if clave is not None and representante in clave:
                resultado.update(destinos)
    return resultado


def construir_afd(afnd: AFND) -> AFD:
    simbolos = [(clave, etiqueta) for clave, etiqueta in afnd.alfabeto if clave is not None]
    alfabeto = particionar(simbolos)

    inicial = cerradura_epsilon(afnd, [afnd.inicial])
    estados: List[FrozenSet[int]] = [inicial]
    numero: Dict[FrozenSet[int], int] = {inicial: 0}
    transiciones: List[Dict[int, int]] = []

    marcados = 0
    while marcados < len(estados):
        actual = estados[marcados]
        fila: Dict[int, int] = {}
        for indice, (_, clase) in enumerate(alfabeto):
            destino = cerradura_epsilon(afnd, mover(afnd, actual, clase))
            if not destino:
                continue
            if destino not in numero:
                numero[destino] = len(estados)
                estados.append(destino)
            fila[indice] = numero[destino]
        transiciones.append(fila)
        marcados += 1

    return AFD(
        num_estados=len(estados),
        inicial=0,
        finales={i for i, conjunto in enumerate(estados) if afnd.final in conjunto},
        alfabeto=alfabeto,
        transiciones=transiciones,
        subconjuntos=estados,
    )
