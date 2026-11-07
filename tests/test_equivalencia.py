"""Pruebas masivas: el AFD, el AFND, el AFD mínimo y el oráculo deben coincidir."""

import random

import pytest

from erafd import convertir
from erafd.minimizacion import minimizar
from erafd.simulador import acepta
from generador import acepta_afnd, cadenas_aleatorias, er_aleatoria
from oraculo import coincide


@pytest.mark.parametrize("semilla", range(40))
def test_automatas_equivalentes_al_oraculo(semilla):
    rng = random.Random(semilla)
    for _ in range(10):
        er = er_aleatoria(rng)
        arbol, afnd, afd = convertir(er)
        minimo = minimizar(afd)
        for cadena in cadenas_aleatorias(rng, 25):
            esperado = coincide(arbol, cadena)
            assert acepta(afd, cadena) == esperado, (er, cadena)
            assert acepta_afnd(afnd, cadena) == esperado, (er, cadena)
            assert acepta(minimo, cadena) == esperado, (er, cadena)
