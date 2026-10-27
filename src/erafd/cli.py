"""Interfaz de línea de comandos:  er-afd [opciones] <ER> <cadena>

Códigos de retorno: 1 = cadena aceptada, 0 = cadena rechazada,
2 = error de uso o de sintaxis en la ER.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__, convertir
from .dot import afd_a_dot, afnd_a_dot
from .errores import ErrorSintaxis
from .formato import lineas_afd, lineas_afnd, lineas_recorrido, lineas_subconjuntos
from .minimizacion import minimizar
from .simulador import simular

ACEPTADA, RECHAZADA, ERROR = 1, 0, 2


class _Formato(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):  # type: ignore[override]
        return super().add_usage(usage, actions, groups, prefix or "uso: ")


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        self.exit(ERROR, "%s: error: argumentos inválidos (%s)\n" % (self.prog, message))


def _crear_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="er-afd",
        formatter_class=_Formato,
        add_help=False,
        description=(
            "Convierte una expresión regular en un AFND (Thompson) y en un AFD\n"
            "(construcción de subconjuntos) y evalúa una cadena con el AFD."
        ),
        epilog=(
            "códigos de retorno: 1 = cadena aceptada, 0 = cadena rechazada, 2 = error\n\n"
            "ejemplos:\n"
            "  er-afd '(a|b)*abb' aabb\n"
            "  er-afd 'hola\\ mundo' \"hola mundo\"\n"
            "  er-afd -v -m '\\N\\N*(\\.\\N\\N*|ε)' 3.1416\n\n"
            "Escriba la ER entre comillas simples para que el shell no interprete\n"
            "'*', '\\' ni los espacios. Si la ER empieza con '-', anteponga '--'."
        ),
    )
    parser._positionals.title = "argumentos"
    parser._optionals.title = "opciones"
    parser.add_argument("er", metavar="ER", help="expresión regular")
    parser.add_argument("cadena", help="cadena a evaluar (use \"\" para la cadena vacía)")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="muestra qué estados del AFND agrupa cada estado del AFD",
    )
    parser.add_argument(
        "-m", "--min", action="store_true",
        help="muestra también el AFD mínimo (algoritmo de Moore)",
    )
    parser.add_argument(
        "-q", "--silencioso", action="store_true",
        help="omite las tablas; solo muestra el recorrido y el resultado",
    )
    parser.add_argument(
        "--dot", metavar="PREFIJO",
        help="exporta PREFIJO_afnd.dot y PREFIJO_afd.dot para Graphviz",
    )
    parser.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    parser.add_argument(
        "--version", action="version", version="er-afd " + __version__,
        help="muestra la versión y termina",
    )
    return parser


def _imprimir(lineas: List[str]) -> None:
    for linea in lineas:
        print(linea)


def main(argumentos: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    # Thompson recorre el árbol recursivamente; una ER larga produce un
    # árbol profundo de concatenaciones.
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    args = _crear_parser().parse_args(argumentos)
    try:
        _, afnd, afd = convertir(args.er)
    except ErrorSintaxis as error:
        print("er-afd: error de sintaxis en la expresión regular: %s" % error, file=sys.stderr)
        return ERROR

    if not args.silencioso:
        _imprimir(lineas_afnd(afnd))
        print()
        _imprimir(lineas_afd(afd))
        if args.verbose:
            print()
            _imprimir(lineas_subconjuntos(afd))
        if args.min:
            minimo = minimizar(afd)
            print()
            _imprimir(lineas_afd(minimo, titulo="AFD mínimo", prefijo="M"))
            if args.verbose:
                print()
                _imprimir(lineas_subconjuntos(minimo, prefijo="M", prefijo_origen="Q"))
        print()

    if args.dot:
        for sufijo, contenido in (("afnd", afnd_a_dot(afnd)), ("afd", afd_a_dot(afd))):
            ruta = "%s_%s.dot" % (args.dot, sufijo)
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            print("Diagrama exportado: %s" % ruta, file=sys.stderr)

    pasos, aceptada = simular(afd, args.cadena)
    _imprimir(lineas_recorrido(pasos, aceptada))
    return ACEPTADA if aceptada else RECHAZADA


def ejecutar() -> None:
    """Punto de entrada del ejecutable: el código de retorno es el resultado."""
    sys.exit(main())
