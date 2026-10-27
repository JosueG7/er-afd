# Plan del proyecto ER-AFD

Convertidor de expresiones regulares a autómatas finitos deterministas
(ER → AFND por Thompson → AFD por construcción de subconjuntos) con
simulación paso a paso de cadenas. Entrega: **31/10/2026**.

## 1. Requisitos (resumen del enunciado)

| Requisito | Cómo se cumple |
|---|---|
| `er-afd <ER> <cadena>` en Python sobre Linux | `make build` genera `bin/er-afd` (zipapp ejecutable); `make install` lo copia a `~/.local/bin` sin root |
| Operadores: concatenación, `\|`, `*`, `()` | Parser descendente recursivo propio |
| `.` `ε` `[abc]` `[^abc]` `[a-z]` `\x` `\N` `\hHH` `\A` `\a` `\z` | Todos soportados, dentro y fuera de conjuntos donde aplica |
| Thompson + subconjuntos | `thompson.py`, `subconjuntos.py` |
| Tablas AFND/AFD con formato `estado\|símbolo\|destino` | `formato.py`, formato exacto del enunciado |
| Recorrido paso a paso y `Cadena aceptada/rechazada` | `simulador.py` |
| Retorno 1 = aceptada, 0 = rechazada | `main()` devuelve el código; errores de sintaxis devuelven 2 |
| Sin librerías de regex | Sin `re` en ningún archivo (ni siquiera en pruebas); una prueba automática lo verifica |
| Makefile `config/build/run/clean` | Además `test`, `metrics`, `install`, `diagramas` |
| `doc/` en PDF: reporte, casos de prueba, manual | Fase 6 |

## 2. Decisiones de diseño (y por qué)

**D1. Los símbolos son conjuntos de caracteres.**
Cada hoja de la ER (`a`, `.`, `[a-z]`, `\N`...) se representa como el conjunto
de caracteres ASCII (0–127) que acepta. El AFND usa las hojas tal cual: su Σ
es la lista de símbolos en orden de aparición, con `ε` en su posición, o al
final si no aparece. Para el AFD, el universo se divide en **clases
disjuntas** de caracteres que se comportan igual en todos los símbolos.
*Por qué:* si `.` y `a` fueran símbolos independientes, la entrada `a` podría
seguir dos transiciones y el "AFD" no sería determinista. Con clases
disjuntas, el AFD es determinista siempre.
*Etiquetas:* una clase que coincide con un símbolo de la ER lleva su nombre
(`a`, `[a-z]`, `\N`). La clase "todo lo que solo cubre `.`" se etiqueta `.`
y se lee como "cualquier otro símbolo". Las demás clases se muestran en
notación de conjunto (`[b-z]`). Si los símbolos no se solapan, Σ del AFD es
exactamente la de la ER, sin `ε`.

**D2. AFD parcial.**
No se imprimen transiciones al conjunto vacío. Si en la simulación no hay
transición, se imprime `Qi|c|∅` y la cadena se rechaza.
*Por qué:* el ejemplo del enunciado lista `Q={Q0,Q1,Q2}`, así que no tiene
estado sumidero (el `Q3` del ejemplo es una errata).

**D3. Numeración estructural de Thompson.**
Es la del libro del Dragón: el inicio de cada construcción se numera antes
que sus partes y el final después. Así `q0` es el inicial, el final es
siempre el último y `(a|b)*abb` reproduce los estados 0–10 del libro.
El AFD numera `Q0, Q1...` en orden de descubrimiento (BFS), recorriendo Σ en
orden. Para `(a|b)*abb` obtiene los 5 estados A–E del libro.

**D4. Concatenación de Thompson con fusión de estados.**
El final de N(s) se fusiona con el inicio de N(t), como en el libro, en
lugar de unirlos con una transición ε.

**D5. Visualización de caracteres especiales.**
Los caracteres que son operadores se muestran escapados (`\|`, `\.`, `\*`,
`\(`, `\)`, `\[`, `\]`, `\\`) y los no imprimibles y el espacio como `\hXX`
(`\h20`). Así nunca se rompe el formato `estado|símbolo|destino`.

**D6. Sintaxis estricta y mensajes claros.**
Se rechazan con código 2 y se señala la posición: `()`, `a|`, `|a`, `*a`,
`[]`, paréntesis o corchetes sin cerrar, `\h` sin dos dígitos hexadecimales,
rangos invertidos (`[z-a]`), caracteres no ASCII y `ε` dentro de `[...]`.
`+`, `?`, `^`, `-` y `{}` fuera de un conjunto son caracteres literales,
porque el enunciado no los define como operadores. Dentro de un conjunto se
permiten escapes y clases (`[\N_]`). Un `-` al inicio o al final de un
conjunto es literal.

**D7. La cadena se toma literal.**
El shell ya resuelve las comillas y `\ `. El manual recomienda escribir la ER
entre comillas simples para que bash no expanda `*` ni consuma `\`.

**D8. Validación sin regex.**
La exactitud se mide con:
1. un corpus de casos reales etiquetados a mano (`tests/corpus.tsv`);
2. un oráculo independiente (emparejador recursivo sobre el árbol sintáctico,
   sin autómatas);
3. pruebas aleatorias que comparan AFD, AFND, AFD mínimo y oráculo.

`make metrics` muestra la matriz de confusión, la exactitud, la precisión,
la exhaustividad y F1.

**D9. Salida por defecto fiel al enunciado.**
Los extras se activan con opciones:
- `-v` muestra qué estados del AFND contiene cada `Qi`;
- `-m` muestra el AFD mínimo (Moore), con estados `Mi`;
- `--dot PREFIJO` exporta los diagramas a Graphviz;
- `-q` omite las tablas.

**D10. Sin dependencias en tiempo de ejecución.**
Solo se usa la biblioteca estándar, compatible con Python 3.8 o superior.
`pytest` se usa solo para las pruebas (`make config` lo instala en `.venv`).

## 3. Arquitectura

```
src/erafd/
  simbolos.py      conjuntos de caracteres, clases predefinidas, cómo se muestran
  arbol.py         nodos del árbol sintáctico (Simbolo, Epsilon, Concatenacion, Union, Cerradura)
  parser.py        ER -> árbol (descendente recursivo, errores con posición)
  thompson.py      árbol -> AFND
  subconjuntos.py  AFND -> AFD (cerradura-ε, mover, clases disjuntas)
  minimizacion.py  AFD -> AFD mínimo (extra)
  simulador.py     recorrido del AFD sobre una cadena
  formato.py       impresión con el formato del enunciado
  dot.py           exportación a Graphviz (extra)
  cli.py           línea de comandos
tests/             pytest: unitarias, CLI, aleatorias, corpus, auditoría sin regex
tools/metricas.py  informe de métricas para la defensa
doc/               PDFs entregables
```

Flujo: `ER → parser → árbol → Thompson → AFND → subconjuntos → AFD → simulador`.

## 4. Fases (calendario comprimido)

| Fase | Fecha | Contenido | Estado |
|---|---|---|---|
| 0 | 26/10 | Análisis, decisiones, este plan | ✅ |
| 1 | 26/10 | Infraestructura: git, Makefile, esqueleto | ✅ |
| 2 | 26/10 | Parser y símbolos | ✅ |
| 3 | 26/10 | Thompson, subconjuntos, simulación, CLI | ✅ |
| 4 | 26/10 | Pruebas, corpus, métricas, extras | ✅ |
| 5 | 27/10 | Subir a GitHub y probar en Linux (WSL) | ⏳ |
| 6 | 28–29/10 | Documentación PDF (reporte, casos con capturas, manual) | ⏳ |
| 7 | 30/10 | Ensayo de la defensa (guion de 10 min) | ⏳ |
| — | 31/10 | Entrega | 🎯 |

## 5. Riesgos

- **Exit code 1 = éxito** choca con la convención de `make`: `make run` lo
  interpreta y no lo muestra como error.
- **Comillas del shell**: documentar el uso de comillas simples y de `--`
  cuando la ER empieza con `-`.
- **Defensa**: el autor debe dominar Thompson, cerradura-ε y subconjuntos.
  El reporte explica el ejemplo `(a|b)*abb` paso a paso.
