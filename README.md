# ER-AFD: Convertidor de expresiones regulares a AFD

Proyecto del curso de Autómatas y Lenguajes Formales, Universidad Mariano
Gálvez de Guatemala.

`er-afd` recibe una expresión regular (ER) y una cadena, y:

1. Construye el **AFND** con el algoritmo de **Thompson** y muestra su tabla de transiciones.
2. Lo convierte en un **AFD** con la **construcción de subconjuntos** y muestra su tabla.
3. Evalúa la cadena **paso a paso** con la matriz de transiciones del AFD y
   devuelve `1` si la acepta o `0` si la rechaza.

No usa librerías de expresiones regulares: el analizador, los autómatas y
el simulador están implementados desde cero, solo con la biblioteca
estándar de Python.

## Requisitos

- Linux de 64 bits (cualquier distribución). No necesita permisos de root.
- Python 3.8 o superior y `make`.
- Opcional: Graphviz (`dot`), solo para generar diagramas.

## Instalación y uso rápido

```bash
make config    # entorno virtual con pytest (solo para pruebas)
make build     # genera el ejecutable bin/er-afd
make run       # ejemplo: (a|b)*abb con la cadena aabb
make run ER='\N\N*(\.\N\N*|ε)' CADENA=3.1416
make clean     # elimina lo generado
```

Ejecución directa:

```bash
./bin/er-afd '(a|b)*abb' aabb
echo $?        # 1 = aceptada, 0 = rechazada, 2 = error
```

Para usar el comando `er-afd` desde cualquier carpeta: `make install`, que
lo copia a `~/.local/bin`.

> **Importante:** escriba la ER entre **comillas simples**. Sin comillas,
> bash expande `*` como comodín de archivos y elimina las `\`. Si la ER
> empieza con `-`, anteponga `--`: `er-afd -- '-\N' -5`.

## Salida

```
$ er-afd ab ab
AFND
Q={q0,q1,q2}
Σ={a,b,ε}
F={q2}
q0|a|{q1}
q1|b|{q2}

AFD
Q={Q0,Q1,Q2}
Σ={a,b}
F={Q2}
Q0|a|Q1
Q1|b|Q2

Q0|a|Q1
Q1|b|Q2
Cadena aceptada
```

Si en un paso no existe transición, el recorrido muestra `Qi|c|∅` y la
cadena se rechaza.

## Sintaxis de las expresiones regulares

| Símbolo | Significado |
|---|---|
| `ab` | Concatenación (implícita) |
| `a\|b` | Unión |
| `a*` | Cerradura de Kleene |
| `(r)` | Agrupación |
| `.` | Cualquier símbolo ASCII |
| `ε` | Cadena vacía |
| `[abc]` `[a-z]` `[^abc]` | Conjunto, rango y conjunto negado |
| `\x` | El carácter `x` literal (`\*`, `\|`, `\\`, `\ `) |
| `\N` `\A` `\a` `\z` | Dígito, mayúscula, minúscula, letra |
| `\hHH` | Carácter por su código ASCII hexadecimal (`\h41` = `A`) |

Precedencia, de mayor a menor: `*`, concatenación, `|`.

## Opciones adicionales

| Opción | Efecto |
|---|---|
| `-v` | Muestra qué estados del AFND agrupa cada estado del AFD |
| `-m` | Muestra también el AFD mínimo (algoritmo de Moore) |
| `-q` | Omite las tablas; solo muestra el recorrido |
| `--dot PREFIJO` | Exporta los diagramas en formato Graphviz |

## Pruebas y métricas

```bash
make test      # pruebas automáticas (pytest)
make metrics   # exactitud, precisión, exhaustividad y F1
```

La validación compara los autómatas contra un **oráculo independiente**
(un emparejador recursivo sobre el árbol sintáctico) en un corpus de
detecciones reales y en miles de casos aleatorios. Una prueba verifica
además que ningún archivo importe librerías de regex.

## Estructura

```
src/erafd/      parser, Thompson, subconjuntos, minimización, simulador, salida
tests/          pruebas, corpus de detecciones reales y oráculo
tools/          informe de métricas
doc/            reporte, casos de prueba y manual de usuario (PDF)
```

Los algoritmos y las decisiones de diseño se explican en el reporte técnico
de la carpeta [doc](doc).

## Referencias

- A. V. Aho, M. S. Lam, R. Sethi y J. D. Ullman, *Compiladores: principios,
  técnicas y herramientas*, 2.ª ed., Pearson, 2008. Secciones 3.7.1
  (construcción de subconjuntos), 3.7.4 (algoritmo de Thompson) y 3.9.6
  (minimización).
- K. Thompson, "Regular expression search algorithm", *Communications of
  the ACM*, 11(6), 1968.
