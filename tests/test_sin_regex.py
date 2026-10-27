"""Auditoría: el proyecto no importa librerías de expresiones regulares."""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PROHIBIDOS = {"re", "regex", "sre_compile", "sre_parse", "fnmatch", "glob"}
ARCHIVOS = sorted(
    p for carpeta in ("src", "tests", "tools") for p in (RAIZ / carpeta).rglob("*.py")
)


@pytest.mark.parametrize("archivo", ARCHIVOS, ids=lambda p: str(p.relative_to(RAIZ)))
def test_no_importa_regex(archivo):
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos = [alias.name for alias in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            modulos = [nodo.module or ""]
        else:
            continue
        for modulo in modulos:
            assert modulo.split(".")[0] not in PROHIBIDOS, "%s importa %s" % (archivo, modulo)
