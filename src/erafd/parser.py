"""Analizador sintáctico descendente recursivo de expresiones regulares.

Gramática (de menor a mayor precedencia):

    union         := concatenacion ('|' concatenacion)*
    concatenacion := repeticion repeticion*        (operador implícito)
    repeticion    := atomo '*'*
    atomo         := '(' union ')' | conjunto | '.' | 'ε' | escape | literal
    conjunto      := '[' '^'? elemento+ ']'
    elemento      := caracter ('-' caracter)? | clase_escape

Cada regla de la gramática es un método de la clase `_Parser`.
"""

from typing import Optional, Set, Tuple

from .arbol import Cerradura, Concatenacion, Epsilon, Nodo, Simbolo, Union
from .errores import ErrorSintaxis
from .simbolos import (
    CLASES_ESCAPE,
    EPSILON,
    UNIVERSO,
    Caracteres,
    mostrar_caracter,
)

HEXADECIMALES = set("0123456789abcdefABCDEF")

# Resultado de leer un escape o un elemento de conjunto:
# ("caracter", código) o ("clase", conjunto de caracteres).
Elemento = Tuple[str, object]


def analizar(expresion: str) -> Nodo:
    """Convierte el texto de una ER en su árbol sintáctico."""
    return _Parser(expresion).analizar()


class _Parser:
    def __init__(self, expresion: str):
        self.er = expresion
        self.pos = 0

    # ----------------------------------------------------------- utilidades

    def _ver(self, adelante: int = 0) -> Optional[str]:
        indice = self.pos + adelante
        return self.er[indice] if indice < len(self.er) else None

    def _anterior(self) -> Optional[str]:
        return self.er[self.pos - 1] if self.pos > 0 else None

    def _error(self, mensaje: str, posicion: Optional[int] = None) -> ErrorSintaxis:
        return ErrorSintaxis(mensaje, self.er, self.pos if posicion is None else posicion)

    def _exigir_ascii(self, caracter: str) -> None:
        if ord(caracter) > 127:
            raise self._error(
                "carácter no ASCII '%s'; use \\hXX para indicar un carácter por su código"
                % caracter
            )

    # -------------------------------------------------------------- reglas

    def analizar(self) -> Nodo:
        if not self.er:
            raise self._error("la expresión regular está vacía (use ε para la cadena vacía)")
        nodo = self._union()
        if self.pos < len(self.er):
            # El único carácter que detiene a _union sin consumirse es ')'.
            raise self._error("')' sin '(' de apertura")
        return nodo

    def _union(self) -> Nodo:
        nodo = self._concatenacion()
        while self._ver() == "|":
            self.pos += 1
            nodo = Union(nodo, self._concatenacion())
        return nodo

    def _concatenacion(self) -> Nodo:
        if self._fin_de_termino():
            raise self._error(self._mensaje_termino_vacio())
        nodo = self._repeticion()
        while not self._fin_de_termino():
            nodo = Concatenacion(nodo, self._repeticion())
        return nodo

    def _fin_de_termino(self) -> bool:
        caracter = self._ver()
        return caracter is None or caracter in "|)"

    def _mensaje_termino_vacio(self) -> str:
        actual, anterior = self._ver(), self._anterior()
        if actual == ")" and anterior == "(":
            return "paréntesis vacíos '()' (use ε para la cadena vacía)"
        if anterior == "|":
            return "falta la expresión a la derecha de '|'"
        if actual == "|":
            return "falta la expresión a la izquierda de '|'"
        if actual == ")":
            return "')' sin '(' de apertura"
        return "expresión incompleta: falta ')' de cierre"

    def _repeticion(self) -> Nodo:
        nodo = self._atomo()
        while self._ver() == "*":
            self.pos += 1
            nodo = Cerradura(nodo)
        return nodo

    def _atomo(self) -> Nodo:
        inicio = self.pos
        caracter = self._ver()
        assert caracter is not None

        if caracter == "(":
            self.pos += 1
            nodo = self._union()
            if self._ver() != ")":
                raise self._error("falta ')' para cerrar este paréntesis", inicio)
            self.pos += 1
            return nodo
        if caracter == "*":
            raise self._error("el operador '*' no tiene operando (use \\* para el carácter)")
        if caracter == "]":
            raise self._error("']' sin '[' de apertura (use \\] para el carácter)")
        if caracter == "[":
            return self._conjunto()
        if caracter == ".":
            self.pos += 1
            return Simbolo(".", UNIVERSO)
        if caracter == EPSILON:
            self.pos += 1
            return Epsilon()
        if caracter == "\\":
            tipo, valor = self._escape()
            if tipo == "clase":
                return Simbolo(self.er[inicio : self.pos], valor)  # type: ignore[arg-type]
            return _simbolo_de(valor)  # type: ignore[arg-type]

        self._exigir_ascii(caracter)
        self.pos += 1
        return _simbolo_de(ord(caracter))

    def _escape(self) -> Elemento:
        """Lee una secuencia que empieza con '\\'."""
        inicio = self.pos
        self.pos += 1
        caracter = self._ver()
        if caracter is None:
            raise self._error("'\\' al final de la expresión: falta el carácter a escapar", inicio)
        self.pos += 1

        if caracter in CLASES_ESCAPE:
            return ("clase", CLASES_ESCAPE[caracter])
        if caracter == "h":
            digitos = self.er[self.pos : self.pos + 2]
            if len(digitos) < 2 or not set(digitos) <= HEXADECIMALES:
                raise self._error(
                    "\\h requiere exactamente dos dígitos hexadecimales (por ejemplo \\h41)",
                    inicio,
                )
            codigo = int(digitos, 16)
            if codigo > 127:
                raise self._error("\\h%s está fuera del rango ASCII (00-7F)" % digitos, inicio)
            self.pos += 2
            return ("caracter", codigo)

        self.pos -= 1
        self._exigir_ascii(caracter)
        self.pos += 1
        return ("caracter", ord(caracter))

    def _conjunto(self) -> Simbolo:
        inicio = self.pos
        self.pos += 1
        negado = self._ver() == "^"
        if negado:
            self.pos += 1

        caracteres: Set[int] = set()
        elementos = 0
        while self._ver() != "]":
            if self._ver() is None:
                raise self._error("falta ']' para cerrar este conjunto", inicio)
            inicio_elemento = self.pos
            primero = self._elemento_conjunto()
            if self._ver() == "-" and self._ver(1) not in (None, "]"):
                self.pos += 1
                ultimo = self._elemento_conjunto()
                if primero[0] != "caracter" or ultimo[0] != "caracter":
                    raise self._error(
                        "los extremos de un rango deben ser caracteres individuales",
                        inicio_elemento,
                    )
                desde, hasta = primero[1], ultimo[1]
                if desde > hasta:  # type: ignore[operator]
                    raise self._error(
                        "rango invertido '%s': el inicio es mayor que el final"
                        % self.er[inicio_elemento : self.pos],
                        inicio_elemento,
                    )
                caracteres.update(range(desde, hasta + 1))  # type: ignore[operator, arg-type]
            elif primero[0] == "clase":
                caracteres.update(primero[1])  # type: ignore[arg-type]
            else:
                caracteres.add(primero[1])  # type: ignore[arg-type]
            elementos += 1
        self.pos += 1

        if elementos == 0:
            raise self._error("conjunto vacío (use \\] para incluir el carácter ']')", inicio)
        resultado = frozenset(UNIVERSO - caracteres if negado else caracteres)
        if not resultado:
            raise self._error("el conjunto no contiene ningún carácter", inicio)
        if len(resultado) == 1:
            return _simbolo_de(next(iter(resultado)))
        return Simbolo(self.er[inicio : self.pos], resultado)

    def _elemento_conjunto(self) -> Elemento:
        caracter = self._ver()
        assert caracter is not None
        if caracter == "\\":
            return self._escape()
        if caracter == EPSILON:
            raise self._error("ε no puede usarse dentro de un conjunto")
        self._exigir_ascii(caracter)
        self.pos += 1
        return ("caracter", ord(caracter))


def _simbolo_de(codigo: int) -> Simbolo:
    caracteres: Caracteres = frozenset({codigo})
    return Simbolo(mostrar_caracter(codigo), caracteres)
