"""Pruebas del programa completo ejecutado como proceso, igual que er-afd."""

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def er_afd(*argumentos):
    entorno = dict(os.environ, PYTHONPATH=str(RAIZ / "src"), PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "erafd", *argumentos],
        capture_output=True, text=True, encoding="utf-8", env=entorno,
    )


def test_cadena_aceptada_retorna_1():
    resultado = er_afd("(a|b)*abb", "aabb")
    assert resultado.returncode == 1
    assert resultado.stdout.rstrip().endswith("Q3|b|Q4\nCadena aceptada")


def test_cadena_rechazada_retorna_0():
    resultado = er_afd("(a|b)*abb", "abab")
    assert resultado.returncode == 0
    assert resultado.stdout.rstrip().endswith("Cadena rechazada")


def test_error_de_sintaxis_retorna_2():
    resultado = er_afd("(a|b", "a")
    assert resultado.returncode == 2
    assert "falta ')'" in resultado.stderr
    assert resultado.stdout == ""


def test_faltan_argumentos_retorna_2():
    assert er_afd("a").returncode == 2


def test_salida_completa_en_el_orden_del_enunciado():
    salida = er_afd("ab", "ab").stdout
    assert salida == (
        "AFND\nQ={q0,q1,q2}\nΣ={a,b,ε}\nF={q2}\nq0|a|{q1}\nq1|b|{q2}\n\n"
        "AFD\nQ={Q0,Q1,Q2}\nΣ={a,b}\nF={Q2}\nQ0|a|Q1\nQ1|b|Q2\n\n"
        "Q0|a|Q1\nQ1|b|Q2\nCadena aceptada\n"
    )


def test_opcion_silenciosa_omite_tablas():
    assert er_afd("-q", "ab", "ab").stdout == "Q0|a|Q1\nQ1|b|Q2\nCadena aceptada\n"


def test_opciones_verbose_y_min():
    salida = er_afd("-v", "-m", "(a|b)*abb", "abb").stdout
    assert "Q0={q0,q1,q2,q4,q7}" in salida
    assert "AFD mínimo" in salida
    assert "M0={Q0,Q2}" in salida


def test_exportacion_dot(tmp_path):
    prefijo = tmp_path / "diagrama"
    er_afd("--dot", str(prefijo), "a*b", "b")
    afd = (tmp_path / "diagrama_afd.dot").read_text(encoding="utf-8")
    assert "digraph AFD" in afd and "doublecircle" in afd
    assert (tmp_path / "diagrama_afnd.dot").exists()


def test_espacios_en_er_y_cadena():
    assert er_afd("hola\\ mundo", "hola mundo").returncode == 1
    assert er_afd("hola mundo", "hola mundo").returncode == 1


def test_epsilon_como_er():
    assert er_afd("ε", "").returncode == 1
