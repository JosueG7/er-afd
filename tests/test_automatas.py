from erafd import convertir
from erafd.formato import lineas_afd, lineas_afnd, lineas_recorrido
from erafd.minimizacion import minimizar
from erafd.simulador import acepta, simular
from erafd.subconjuntos import particionar


def test_thompson_reproduce_el_libro_del_dragon():
    """Figura 3.34 de Aho et al.: AFND de (a|b)*abb con estados 0-10."""
    _, afnd, _ = convertir("(a|b)*abb")
    assert lineas_afnd(afnd) == [
        "AFND",
        "Q={q0,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10}",
        "Σ={a,b,ε}",
        "F={q10}",
        "q0|ε|{q1,q7}",
        "q1|ε|{q2,q4}",
        "q2|a|{q3}",
        "q3|ε|{q6}",
        "q4|b|{q5}",
        "q5|ε|{q6}",
        "q6|ε|{q1,q7}",
        "q7|a|{q8}",
        "q8|b|{q9}",
        "q9|b|{q10}",
    ]


def test_subconjuntos_reproduce_el_libro_del_dragon():
    """Ejemplo 3.21 de Aho et al.: estados A-E del AFD de (a|b)*abb."""
    _, _, afd = convertir("(a|b)*abb")
    assert afd.subconjuntos == [
        frozenset({0, 1, 2, 4, 7}),            # A
        frozenset({1, 2, 3, 4, 6, 7, 8}),      # B
        frozenset({1, 2, 4, 5, 6, 7}),         # C
        frozenset({1, 2, 4, 5, 6, 7, 9}),      # D
        frozenset({1, 2, 4, 5, 6, 7, 10}),     # E
    ]
    assert lineas_afd(afd) == [
        "AFD",
        "Q={Q0,Q1,Q2,Q3,Q4}",
        "Σ={a,b}",
        "F={Q4}",
        "Q0|a|Q1", "Q0|b|Q2",
        "Q1|a|Q1", "Q1|b|Q3",
        "Q2|a|Q1", "Q2|b|Q2",
        "Q3|a|Q1", "Q3|b|Q4",
        "Q4|a|Q1", "Q4|b|Q2",
    ]


def test_minimizacion_fusiona_estados_equivalentes():
    """En el libro, A y C son equivalentes: el AFD mínimo tiene 4 estados."""
    _, _, afd = convertir("(a|b)*abb")
    minimo = minimizar(afd)
    assert minimo.num_estados == 4
    assert frozenset({0, 2}) in minimo.subconjuntos


def test_epsilon_en_su_posicion_dentro_de_sigma():
    _, afnd, _ = convertir("aε|b")
    assert lineas_afnd(afnd)[2] == "Σ={a,ε,b}"


def test_epsilon_al_final_si_no_aparece():
    _, afnd, _ = convertir("ba")
    assert lineas_afnd(afnd)[2] == "Σ={b,a,ε}"


def test_sigma_del_afd_no_incluye_epsilon():
    _, _, afd = convertir("aε|b")
    assert lineas_afd(afd)[2] == "Σ={a,b}"


def test_simbolos_equivalentes_se_unifican():
    _, afnd, _ = convertir("\\N|[0-9]")
    assert lineas_afnd(afnd)[2] == "Σ={\\N,ε}"


def test_punto_es_simbolo_y_el_afd_es_determinista():
    _, afnd, afd = convertir("a.b")
    assert lineas_afnd(afnd)[2] == "Σ={a,.,b,ε}"
    assert lineas_afd(afd)[2] == "Σ={a,.,b}"
    assert acepta(afd, "axb") and acepta(afd, "aab") and acepta(afd, "abb")
    assert not acepta(afd, "ab")


def test_particion_en_clases_disjuntas():
    clases = particionar([(frozenset(range(97, 123)), "[a-z]"), (frozenset({97}), "a")])
    assert clases == [("[b-z]", frozenset(range(98, 123))), ("a", frozenset({97}))]


def test_clases_cubren_cada_caracter_una_sola_vez():
    _, _, afd = convertir("[a-z]*a|.\\N|[^x]")
    vistos = set()
    for _, clase in afd.alfabeto:
        assert not (vistos & clase)
        vistos |= clase


def test_recorrido_aceptado():
    _, _, afd = convertir("(a|b)*abb")
    pasos, aceptada = simular(afd, "abb")
    assert aceptada
    assert lineas_recorrido(pasos, aceptada) == [
        "Q0|a|Q1", "Q1|b|Q3", "Q3|b|Q4", "Cadena aceptada",
    ]


def test_recorrido_sin_transicion_se_detiene():
    _, _, afd = convertir("ab")
    pasos, aceptada = simular(afd, "acb")
    assert lineas_recorrido(pasos, aceptada) == ["Q0|a|Q1", "Q1|c|∅", "Cadena rechazada"]


def test_cadena_vacia():
    assert acepta(convertir("a*")[2], "")
    assert not acepta(convertir("a")[2], "")
    assert acepta(convertir("ε")[2], "")


def test_caracter_fuera_de_ascii_se_rechaza():
    _, _, afd = convertir(".*")
    assert not acepta(afd, "año")


def test_recorrido_muestra_caracteres_especiales_escapados():
    _, _, afd = convertir("\\|\\ ")
    pasos, aceptada = simular(afd, "| ")
    assert lineas_recorrido(pasos, aceptada) == ["Q0|\\||Q1", "Q1|\\h20|Q2", "Cadena aceptada"]
