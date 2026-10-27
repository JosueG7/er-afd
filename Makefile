# ER-AFD: convertidor de expresiones regulares a AFD.
#
#   make config    crea el entorno virtual e instala pytest (solo para pruebas)
#   make build     genera el ejecutable bin/er-afd
#   make run       ejecuta:  make run ER='(a|b)*abb' CADENA=aabb [OPCIONES=-v]
#   make clean     elimina lo generado por build y por las pruebas
#
#   make test      ejecuta las pruebas automáticas
#   make metrics   informe de exactitud/precisión para la defensa
#   make install   copia er-afd a ~/.local/bin (no requiere root)
#   make diagramas genera PNG del AFND y del AFD (requiere Graphviz)

PYTHON   ?= python3
VENV     := .venv
BIN      := bin/er-afd
DESTINO  ?= $(HOME)/.local/bin
ER       ?= (a|b)*abb
CADENA   ?= aabb
OPCIONES ?=

PYTEST_PY := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PYTHON))

.PHONY: all config build run test metrics install diagramas clean distclean

all: build

config:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --quiet --upgrade pip
	$(VENV)/bin/python -m pip install --quiet -r requirements-dev.txt
	@echo "Entorno listo en $(VENV). Siguiente paso: make build"

build:
	@$(PYTHON) -c 'import sys; sys.exit(sys.version_info < (3, 8))' || \
		{ echo "Se requiere Python 3.8 o superior"; exit 1; }
	$(PYTHON) -m compileall -q src
	@rm -rf build/app && mkdir -p build/app bin
	cp -r src/erafd build/app/
	@find build/app -name __pycache__ -prune -exec rm -rf {} +
	$(PYTHON) -m zipapp build/app -m "erafd.cli:ejecutar" -p "/usr/bin/env python3" -o $(BIN)
	chmod +x $(BIN)
	@echo "Ejecutable generado: $(BIN)"

# er-afd devuelve 1 cuando acepta la cadena (así lo pide el enunciado);
# make trataría ese 1 como un fallo, así que solo se considera error el 2.
run: build
	@echo "\$$ er-afd $(OPCIONES) '$(ER)' '$(CADENA)'"
	@./$(BIN) $(OPCIONES) '$(ER)' '$(CADENA)'; codigo=$$?; \
		echo "[código de retorno: $$codigo]"; [ $$codigo -le 1 ]

test:
	$(PYTEST_PY) -m pytest

metrics:
	PYTHONPATH=src $(PYTHON) tools/metricas.py

install: build
	mkdir -p $(DESTINO)
	cp $(BIN) $(DESTINO)/er-afd
	@echo "Instalado en $(DESTINO)/er-afd"
	@case ":$$PATH:" in *":$(DESTINO):"*) ;; \
		*) echo "Agregue $(DESTINO) al PATH: export PATH=\"$(DESTINO):\$$PATH\"";; esac

diagramas: build
	@command -v dot >/dev/null || { echo "Instale Graphviz: sudo apt install graphviz"; exit 1; }
	@mkdir -p build/diagramas
	-@./$(BIN) -q --dot build/diagramas/automata '$(ER)' '$(CADENA)' >/dev/null
	dot -Tpng build/diagramas/automata_afnd.dot -o build/diagramas/afnd.png
	dot -Tpng build/diagramas/automata_afd.dot -o build/diagramas/afd.png
	@echo "Diagramas en build/diagramas/"

clean:
	rm -rf build bin .pytest_cache
	find . -name __pycache__ -prune -not -path "./$(VENV)/*" -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)
