# TLP02 — Reglas y convenciones (P1)

Oct 25, 2026 · @Carlo

Este documento reúne las reglas y convenciones que el equipo va acordando para la parte de P1 (Parsers). Se actualiza cada vez que se toma una decisión nueva; lo que está aquí es lo vigente.

## Registro de decisiones

| Fecha | Decisión |
| --- | --- |
| 2026-10-25 | Pruebas en `test_parser_formal.py`: 24 casos, incluido uno con comentarios `//` |
| 2026-10-25 | Parser de mini-C: interfaz `parsear_codigo(codigo)`, árbol `nltk.Tree` con un nodo por no terminal y el `else` en un nodo `sino` |
| 2026-10-25 | Errores del parser: `Línea N: se esperaba X y se encontró Y` |
| 2026-10-21 | Abreviaturas de categorías del español: oracion, sn, sv, sp, det, n, v, adj, p |
| 2026-10-21 | Motor genérico: gramática como diccionario, no terminales y palabras en minúscula, símbolo inicial `oracion` |
| 2026-10-20 | `.venv` en la raíz del repositorio y fuera de Git; dependencias en `requirements.txt` |
| 2026-10-20 | El lexer ignora comentarios de una línea (`//`) |
| 2026-10-20 | Notación: EBNF con flechas; terminales en MAYÚSCULAS, no terminales en minúscula, texto literal entre comillas |
| 2026-10-20 | El parser de mini-C se llama `parser_formal.py`, no `parser.py` |
| 2026-10-20 | Subconjunto mini-C aprobado por el docente |

## Alcance de mini-C

El docente aprobó este subconjunto de C el 20 de octubre de 2026.

| Construcción | Ejemplo |
| --- | --- |
| Declaración de variables | `int x;` · `float y = 3;` |
| Asignación | `x = x + 1;` |
| Condicional | `if (x > 5) { ... } else { ... }` |
| Ciclo | `while (i < 10) { ... }` |
| Bloque | `{ ... }` |
| Aritmética con precedencia | `+ - * /` y paréntesis |
| Comparaciones | `< > <= >= == !=` |
| Comentarios de una línea | `// texto` (el lexer los descarta) |

Queda fuera: funciones, arreglos, cadenas, operadores lógicos (`&&`, `||`), `for` y comentarios de bloque (`/* */`).

## Notación de las gramáticas

Todas las gramáticas del informe se escriben en EBNF con flechas. En el informe se dice "notación EBNF", no "BNF".

| Elemento | Cómo se escribe | Ejemplo |
| --- | --- | --- |
| No terminal | minúsculas, sin comillas | `expr`, `sentencia`, `sn` |
| Terminal que es una clase de token | MAYÚSCULAS, sin comillas | `ID`, `NUM`, `OP_REL`, `EOF` |
| Terminal con texto exacto | entre comillas simples | `'if'`, `';'`, `'+'` |
| "está hecho de" | `→` | `bloque → '{' sentencia* '}'` |
| "o" | `\|` | `tipo → 'int' \| 'float'` |
| Cero o más veces | `*` | `sentencia*` |
| Opcional | `?` | `( 'else' sentencia )?` |
| Agrupar | `( )` | `( '+' \| '-' )` |

Las palabras reservadas van en minúscula porque están entre comillas: lo que va entre comillas es el texto literal, y en C se escribe `if`.

En el código se mantiene la misma correspondencia: cada no terminal `x` es la función `x()` del parser, y cada terminal en mayúsculas es el tipo de token del mismo nombre en el lexer.

### Clases de token

| Terminal | Qué representa | Patrón |
| --- | --- | --- |
| `ID` | nombre de variable | `[A-Za-z_]\w*`, excepto palabras reservadas |
| `NUM` | número entero o decimal | `\d+(?:\.\d+)?` |
| `OP_REL` | operador relacional | `== != <= >= < >` |
| `EOF` | fin de la entrada | lo agrega el lexer al final |

## Gramática de mini-C

Esta es la versión vigente; va tal cual al informe.

```text
programa    → sentencia* EOF
sentencia   → declaracion | asignacion | si | mientras | bloque
declaracion → tipo ID ( '=' expr )? ';'
tipo        → 'int' | 'float'
asignacion  → ID '=' expr ';'
si          → 'if' '(' condicion ')' sentencia ( 'else' sentencia )?
mientras    → 'while' '(' condicion ')' sentencia
bloque      → '{' sentencia* '}'
condicion   → expr OP_REL expr
expr        → termino ( ( '+' | '-' ) termino )*
termino     → factor ( ( '*' | '/' ) factor )*
factor      → NUM | ID | '(' expr ')'
```

Decisiones de diseño que hay que poder defender:

- **Sin recursión por la izquierda.** `expr` y `termino` usan `*` en lugar de `expr → expr '+' termino`, que dejaría al parser descendente en un bucle infinito.
- **Precedencia por niveles.** `termino` (multiplicación y división) está dentro de `expr` (suma y resta), así que `*` y `/` se agrupan primero.
- **Casi LL(1).** El primer token decide cada alternativa: FIRST(sentencia) = { `int`, `float`, `ID`, `if`, `while`, `{` }.
- **Else colgante.** Es la única ambigüedad; el `else` se asocia al `if` más cercano, igual que en C.
- **EBNF a BNF.** Para mostrar la equivalencia, `expr` en BNF puro queda `expr → termino expr_resto` y `expr_resto → '+' termino expr_resto | '-' termino expr_resto | ε`.

## Lexer (`lexer.py`)

El lexer convierte el código en una lista de tokens con tipo, valor, línea y columna, y siempre termina con `EOF`. No revisa el orden: eso lo hace el parser.

- **El orden de `TOKENS` importa.** La regex prueba las alternativas de izquierda a derecha y se queda con la primera que coincide. Reglas fijas: `COMENTARIO` antes de `OP_MULT` (si no, `//` serían dos divisiones), `OP_REL` antes de `ASIGNA` (si no, `==` serían dos `=`), y `DESCONOCIDO` siempre al final.
- **Palabras reservadas:** `int`, `float`, `if`, `else`, `while`. Se leen como `ID` y luego se les cambia el tipo a su nombre en mayúsculas (`IF`), así que `ifx` sigue siendo `ID`.
- **Se descartan:** espacios, tabulaciones, `\r` y comentarios `//` hasta el fin de la línea. Los saltos de línea se descartan pero se cuentan.
- **Errores:** un carácter fuera del lenguaje lanza `ErrorDeAnalisis` con el formato `Línea L, columna C: carácter no válido 'x'`. Las líneas y las columnas se cuentan desde 1.
- **Una sola excepción** para todo el proyecto formal: `ErrorDeAnalisis`, definida en `lexer.py` y usada también por el parser y las pruebas.

## Parser de mini-C (`parser_formal.py`)

Parser descendente recursivo: una función por cada no terminal de la gramática (`programa()`, `sentencia()`, `declaracion()`, `tipo()`, …), con su regla EBNF como comentario encima. Recorre los tokens del lexer con cuatro herramientas: `actual()`, `ver(*tipos)`, `consumir(tipo)` y `error(mensaje)`.

- **Interfaz:** `parsear_codigo(codigo)` devuelve un `nltk.Tree` o lanza `ErrorDeAnalisis`.
- **Árbol:** cada nodo lleva el nombre de su no terminal; las hojas son los valores de los tokens (`x`, `5`, `+`). Se guardan los nombres, números, operadores (`+`, `*`, `>`, …), el tipo (`int`/`float`) y los `( )` de `factor`; no se guardan `;`, `=`, las llaves, los paréntesis de `if`/`while` ni las palabras `if`, `else`, `while`, porque el nodo ya dice qué regla es. La rama del `else` va dentro de un nodo `sino`, que no es un no terminal de la gramática: solo marca la rama para que se vea a qué `if` quedó pegada.
- **Ejemplo:** `int x = 2 + 3 * 4;` da `(programa (declaracion (tipo int) x (expr (termino (factor 2)) + (termino (factor 3) * (factor 4)))))`. `3 * 4` queda en un solo `termino`: la multiplicación va primero.
- **Else colgante:** se resuelve solo; `si()` mira si sigue un `else` justo después de su sentencia, así que el `if` más interno se lo queda.
- **Errores:** `Línea N: se esperaba X y se encontró Y`. Si se acabó la entrada, dice «se encontró el fin del código». Ejemplo: `int y = 5` → `Línea 1: se esperaba ';' y se encontró el fin del código`.
- **Sin recuperación de errores:** se detiene en el primer error (el modo pánico es opcional).

### Pruebas (`test_parser_formal.py`)

`pytest -v` dentro de `fase1/` debe dar **24 passed**: 11 códigos válidos (uno con comentarios `//`), 10 inválidos (incluido un carácter que rechaza el lexer), y una prueba cada una para la precedencia, el else colgante y la línea del error.

## Motor genérico y gramática del español

El motor (`motor.py`) analiza con cualquier gramática escrita como diccionario, usa backtracking y devuelve todos los árboles posibles. P2 edita solo `gramatica_es.py` y prueba con `python motor.py`.

### Reglas para escribir la gramática

1. Clave = no terminal; valor = lista de producciones; cada producción = lista de símbolos. `"sv": [["v", "sn"], ["v"]]` es `sv → v sn | v`.
2. Lo que no es clave del diccionario es una palabra (terminal).
3. Todo en minúsculas, porque el motor pasa la oración a minúsculas.
4. Ningún no terminal puede llamarse igual que una palabra. Por eso el símbolo inicial es `oracion` y no `o` (que chocaría con la conjunción «o»).
5. `[]` es la producción vacía (ε).
6. Prohibida la recursión por la izquierda (`sn → sn adj`): da `RecursionError`. Se reescribe a la derecha: `sn → det n adjs`, `adjs → adj adjs | ε`.
7. Concordancia: sufijos `_ms`, `_fs`, `_mp`, `_fp` (masculino o femenino, singular o plural).

### Interfaz

| Función | Devuelve |
| --- | --- |
| `todos_los_arboles(oracion, gramatica, inicial)` | lista de todos los árboles que cubren la oración completa; vacía = rechazada |
| `parsear(oracion, gramatica, inicial)` | el primer árbol, o `None` si se rechaza |

Antes de analizar, el motor pasa la oración a minúsculas y quita puntos y comas. Los árboles son `nltk.Tree` y se imprimen en notación de corchetes, el formato común del equipo.

### Abreviaturas de categorías

| Abreviatura | Nombre | Ejemplos |
| --- | --- | --- |
| `oracion` | Oración (símbolo inicial) | sujeto + predicado |
| `sn` | Sintagma nominal | el perro negro |
| `sv` | Sintagma verbal | come la carne |
| `sp` | Sintagma preposicional | con el telescopio |
| `det` | Determinante | el, la, los, un |
| `n` | Nombre (sustantivo) | perro, carne |
| `v` | Verbo | come, duerme |
| `adj` | Adjetivo | negro, grande |
| `p` | Preposición | con, de, en |

En esta gramática, `det`, `n`, `v`, `adj` y `p` son no terminales (preterminales): tienen reglas que llevan directo a una palabra. Los terminales son las palabras. En mini-C, en cambio, `ID` es terminal porque lo clasifica el lexer; el motor del español no tiene lexer.

## Repositorio y entorno

El entorno virtual vive en la raíz del repositorio y nunca se sube a Git; cada integrante lo crea con `requirements.txt`.

```text
<repositorio>/
    .venv/                    ← fuera de Git (.gitignore)
    .gitignore
    requirements.txt          ← nltk, pytest
    fase1/
        lexer.py
        parser_formal.py      ← no se llama parser.py
        test_parser_formal.py
        motor.py
        gramatica_es.py       ← la edita P2
```

Para preparar el entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate        # bash/zsh
source .venv/bin/activate.fish   # fish
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

- Python 3.10 o más reciente.
- `pytest -v` antes de cada `git push`.
- Un commit al final de cada día, con un mensaje que diga qué se hizo.

## Limitaciones conocidas y pendientes

### Limitaciones (se documentan, no se arreglan)

- «el perro duermen» se acepta: la gramática de ejemplo no controla la concordancia sujeto-verbo. Arreglarlo exige duplicar `sv` y `v` por número y persona, y las reglas se multiplican. Es evidencia del límite de la CFG para el informe de P2.
- El backtracking es exponencial en el peor caso. Si una oración tarda más de unos segundos, se simplifica esa parte de la gramática.

### Pendientes

- [ ] Confirmar con el equipo que los comentarios `//` entran en el alcance de mini-C.
- [ ] Avisar a P2 de las reglas del motor y de la convención de minúsculas.
- [ ] Avisar a P4 que el archivo es `parser_formal.py` (interfaz `parsear_codigo`, formato del árbol con nodo `sino`), para los tests.
- [ ] Fase 2: decidir cómo se maneja la concordancia (duplicar no terminales o rasgos chequeados aparte).
- [ ] Fase 2: decidir si `parsear_es()` devuelve el primer árbol o todos.
