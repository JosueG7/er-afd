import pytest

from erafd import convertir
from erafd.simulador import acepta
from corpus import CORPUS
from oraculo import coincide

CASOS = [
    pytest.param(er, cadena, esperado, id="%s: %r" % (categoria, cadena))
    for categoria, (er, ejemplos) in CORPUS.items()
    for cadena, esperado in ejemplos
]


@pytest.mark.parametrize("er, cadena, esperado", CASOS)
def test_deteccion(er, cadena, esperado):
    arbol, _, afd = convertir(er)
    assert coincide(arbol, cadena) == esperado, "la etiqueta del corpus no coincide con el oráculo"
    assert acepta(afd, cadena) == esperado
