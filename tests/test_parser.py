import pytest

from erafd.arbol import Simbolo, representar
from erafd.errores import ErrorSintaxis
from erafd.parser import analizar
from erafd.simbolos import DIGITOS, LETRAS, MAYUSCULAS, MINUSCULAS, UNIVERSO


@pytest.mark.parametrize(
    "er, esperado",
    [
        ("a", "a"),
        ("ab", "(ab)"),
        ("abc", "((ab)c)"),
        ("a|b", "(a|b)"),
        ("a|b|c", "((a|b)|c)"),
        ("ab|c*", "((ab)|(c)*)"),
        ("(a|b)*abb", "(((((a|b))*a)b)b)"),
        ("a**", "((a)*)*"),
        ("aε|b", "((aε)|b)"),
        ("(a)", "a"),
    ],
)
def test_precedencia_y_asociatividad(er, esperado):
    assert representar(analizar(er)) == esperado


def _simbolo(er):
    nodo = analizar(er)
    assert isinstance(nodo, Simbolo)
    return nodo


@pytest.mark.parametrize(
    "er, etiqueta, caracteres",
    [
        (".", ".", UNIVERSO),
        ("\\N", "\\N", DIGITOS),
        ("\\A", "\\A", MAYUSCULAS),
        ("\\a", "\\a", MINUSCULAS),
        ("\\z", "\\z", LETRAS),
        ("\\*", "\\*", {ord("*")}),
        ("\\p", "p", {ord("p")}),
        ("\\\\", "\\\\", {ord("\\")}),
        ("\\|", "\\|", {ord("|")}),
        ("\\h41", "A", {ord("A")}),
        ("\\h20", "\\h20", {ord(" ")}),
        ("\\h7e", "~", {ord("~")}),
        ("\\ ", "\\h20", {ord(" ")}),
        (" ", "\\h20", {ord(" ")}),
        ("+", "+", {ord("+")}),
        ("-", "-", {ord("-")}),
        ("^", "^", {ord("^")}),
    ],
)
def test_simbolos_y_escapes(er, etiqueta, caracteres):
    simbolo = _simbolo(er)
    assert simbolo.etiqueta == etiqueta
    assert simbolo.caracteres == frozenset(caracteres)


@pytest.mark.parametrize(
    "er, caracteres",
    [
        ("[abc]", "abc"),
        ("[a-e]", "abcde"),
        ("[a-cx-z]", "abcxyz"),
        ("[-a]", "-a"),
        ("[a-]", "a-"),
        ("[\\]\\-]", "]-"),
        ("[\\h41-\\h43]", "ABC"),
        ("[.*|]", ".*|"),
        ("[\\N_]", "0123456789_"),
    ],
)
def test_conjuntos(er, caracteres):
    assert _simbolo(er).caracteres == frozenset(ord(c) for c in caracteres)


def test_conjunto_conserva_su_texto_como_etiqueta():
    assert _simbolo("[a-z]").etiqueta == "[a-z]"
    assert _simbolo("[^abc]").etiqueta == "[^abc]"


def test_conjunto_de_un_caracter_es_ese_caracter():
    assert _simbolo("[a]").etiqueta == "a"


def test_conjunto_negado():
    simbolo = _simbolo("[^abc]")
    assert len(simbolo.caracteres) == 128 - 3
    assert ord("a") not in simbolo.caracteres
    assert ord("d") in simbolo.caracteres


@pytest.mark.parametrize(
    "er, fragmento",
    [
        ("", "vacía"),
        ("()", "paréntesis vacíos"),
        ("a|", "derecha de '|'"),
        ("|a", "izquierda de '|'"),
        ("a||b", "derecha de '|'"),
        ("(|a)", "izquierda de '|'"),
        ("*a", "'*' no tiene operando"),
        ("a|*", "'*' no tiene operando"),
        ("(a", "falta ')'"),
        ("a)", "')' sin '('"),
        ("]", "']' sin '['"),
        ("[]", "conjunto vacío"),
        ("[^]", "conjunto vacío"),
        ("[abc", "falta ']'"),
        ("[z-a]", "rango invertido"),
        ("[\\N-z]", "extremos de un rango"),
        ("\\", "al final"),
        ("\\h4", "dos dígitos hexadecimales"),
        ("\\hZZ", "dos dígitos hexadecimales"),
        ("\\h80", "fuera del rango ASCII"),
        ("ñ", "no ASCII"),
        ("[ε]", "ε no puede usarse"),
    ],
)
def test_errores_de_sintaxis(er, fragmento):
    with pytest.raises(ErrorSintaxis) as error:
        analizar(er)
    assert fragmento in error.value.mensaje


def test_error_indica_posicion():
    with pytest.raises(ErrorSintaxis) as error:
        analizar("ab(c")
    assert error.value.posicion == 2
    assert str(error.value).splitlines()[-1] == "    ^"
