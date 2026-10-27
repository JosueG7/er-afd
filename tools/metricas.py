"""Informe de métricas de detección para la defensa del proyecto.

1. Corpus de detecciones reales (tests/corpus.py): matriz de confusión,
   exactitud, precisión, exhaustividad y F1 por categoría y en total.
2. Verificación cruzada aleatoria: AFD vs. AFND vs. AFD mínimo vs. oráculo.
3. Tamaño de los autómatas de cada categoría.

Uso:  PYTHONPATH=src python3 tools/metricas.py   (o bien: make metrics)
"""

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

from corpus import CORPUS  # noqa: E402
from generador import acepta_afnd, cadenas_aleatorias, er_aleatoria  # noqa: E402
from oraculo import coincide  # noqa: E402

from erafd import convertir  # noqa: E402
from erafd.minimizacion import minimizar  # noqa: E402
from erafd.simulador import acepta  # noqa: E402


def _porcentaje(numerador: int, denominador: int) -> str:
    return "%6.2f%%" % (100.0 * numerador / denominador) if denominador else "    n/a"


def informe_corpus() -> bool:
    print("1. DETECCIONES REALES (corpus etiquetado a mano)")
    print("-" * 78)
    print("%-34s %5s %5s %5s %5s %9s" % ("Categoría", "VP", "VN", "FP", "FN", "Exactitud"))
    vp = vn = fp = fn = 0
    fallos = []
    for categoria, (er, ejemplos) in CORPUS.items():
        _, _, afd = convertir(er)
        c_vp = c_vn = c_fp = c_fn = 0
        for cadena, esperado in ejemplos:
            obtenido = acepta(afd, cadena)
            if obtenido and esperado:
                c_vp += 1
            elif not obtenido and not esperado:
                c_vn += 1
            elif obtenido:
                c_fp += 1
                fallos.append((categoria, cadena, esperado))
            else:
                c_fn += 1
                fallos.append((categoria, cadena, esperado))
        total = len(ejemplos)
        print("%-34s %5d %5d %5d %5d %9s" % (
            categoria[:34], c_vp, c_vn, c_fp, c_fn, _porcentaje(c_vp + c_vn, total)))
        vp, vn, fp, fn = vp + c_vp, vn + c_vn, fp + c_fp, fn + c_fn

    total = vp + vn + fp + fn
    precision = vp / (vp + fp) if vp + fp else 0.0
    exhaustividad = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * precision * exhaustividad / (precision + exhaustividad) if precision else 0.0
    print("-" * 78)
    print("%-34s %5d %5d %5d %5d %9s" % ("TOTAL", vp, vn, fp, fn, _porcentaje(vp + vn, total)))
    print()
    print("  Casos evaluados : %d (%d positivos, %d negativos)" % (total, vp + fn, vn + fp))
    print("  Exactitud       : %s" % _porcentaje(vp + vn, total))
    print("  Precisión       : %s" % _porcentaje(vp, vp + fp))
    print("  Exhaustividad   : %s" % _porcentaje(vp, vp + fn))
    print("  F1              : %6.2f%%" % (100 * f1))
    for categoria, cadena, esperado in fallos:
        print("  FALLO  %s: %r (esperado: %s)" % (
            categoria, cadena, "aceptar" if esperado else "rechazar"))
    print()
    return not fallos


def informe_aleatorio(cantidad_er: int = 500, cadenas_por_er: int = 40) -> bool:
    print("2. VERIFICACIÓN CRUZADA ALEATORIA (semilla fija, reproducible)")
    print("-" * 78)
    rng = random.Random(2026)
    comparaciones = coincidencias = 0
    inicio = time.perf_counter()
    for _ in range(cantidad_er):
        er = er_aleatoria(rng)
        arbol, afnd, afd = convertir(er)
        minimo = minimizar(afd)
        for cadena in cadenas_aleatorias(rng, cadenas_por_er):
            esperado = coincide(arbol, cadena)
            resultados = (acepta(afd, cadena), acepta_afnd(afnd, cadena), acepta(minimo, cadena))
            comparaciones += 1
            coincidencias += all(r == esperado for r in resultados)
    segundos = time.perf_counter() - inicio
    print("  ER aleatorias   : %d" % cantidad_er)
    print("  Cadenas         : %d (AFD, AFND y AFD mínimo contra el oráculo)" % comparaciones)
    print("  Coincidencia    : %s" % _porcentaje(coincidencias, comparaciones))
    print("  Tiempo          : %.2f s" % segundos)
    print()
    return coincidencias == comparaciones


def informe_tamanos() -> None:
    print("3. TAMAÑO DE LOS AUTÓMATAS")
    print("-" * 78)
    print("%-34s %6s %6s %7s %6s" % ("Categoría", "AFND", "AFD", "Mínimo", "|Σ|"))
    for categoria, (er, _) in CORPUS.items():
        _, afnd, afd = convertir(er)
        print("%-34s %6d %6d %7d %6d" % (
            categoria[:34], afnd.num_estados, afd.num_estados,
            minimizar(afd).num_estados, len(afd.alfabeto)))
    print()


def main() -> int:
    correcto = informe_corpus()
    correcto = informe_aleatorio() and correcto
    informe_tamanos()
    return 0 if correcto else 1


if __name__ == "__main__":
    sys.exit(main())
