# 1. Parser de mini-C (lenguaje formal) — P1

**Objetivo:** demostrar que un parser clásico funciona perfecto sobre un lenguaje formal. Es la base contra la que luego se compara el español.

**Archivos:** `lexer.py`, `parser_formal.py`, `test_parser_formal.py`.

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

## Gramática (EBNF)

Esta es la versión vigente; va tal cual al informe. La notación está en [docs/decisiones.md](../../docs/decisiones.md#notación-de-las-gramáticas).

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

### Clases de token

| Terminal | Qué representa | Patrón |
| --- | --- | --- |
| `ID` | nombre de variable | `[A-Za-z_]\w*`, excepto palabras reservadas |
| `NUM` | número entero o decimal | `\d+(?:\.\d+)?` |
| `OP_REL` | operador relacional | `== != <= >= < >` |
| `EOF` | fin de la entrada | lo agrega el lexer al final |

### Decisiones de diseño que hay que poder defender

- **Sin recursión por la izquierda.** `expr` y `termino` usan `*` en lugar de `expr → expr '+' termino`, que dejaría al parser descendente en un bucle infinito.
- **Precedencia por niveles.** `termino` (multiplicación y división) está dentro de `expr` (suma y resta), así que `*` y `/` se agrupan primero.
- **Casi LL(1).** El primer token decide cada alternativa: FIRST(sentencia) = { `int`, `float`, `ID`, `if`, `while`, `{` }.
- **Else colgante.** Es la única ambigüedad; el `else` se asocia al `if` más cercano, igual que en C.
- **EBNF a BNF.** Para mostrar la equivalencia, `expr` en BNF puro queda `expr → termino expr_resto` y `expr_resto → '+' termino expr_resto | '-' termino expr_resto | ε`.

## Lexer (`lexer.py`)

Convierte el código en una lista de tokens con tipo, valor, línea y columna, y siempre termina con `EOF`. No revisa el orden: eso lo hace el parser.

- **El orden de `TOKENS` importa.** La regex prueba las alternativas de izquierda a derecha y se queda con la primera que coincide. Reglas fijas: `COMENTARIO` antes de `OP_MULT` (si no, `//` serían dos divisiones), `OP_REL` antes de `ASIGNA` (si no, `==` serían dos `=`), y `DESCONOCIDO` siempre al final.
- **Palabras reservadas:** `int`, `float`, `if`, `else`, `while`. Se leen como `ID` y luego se les cambia el tipo a su nombre en mayúsculas (`IF`), así que `ifx` sigue siendo `ID`.
- **Se descartan:** espacios, tabulaciones, `\r` y comentarios `//` hasta el fin de la línea. Los saltos de línea se descartan pero se cuentan.
- **Errores:** un carácter fuera del lenguaje lanza `ErrorDeAnalisis` con el formato `Línea L, columna C: carácter no válido 'x'`. Las líneas y las columnas se cuentan desde 1.
- **Una sola excepción** para todo el proyecto formal: `ErrorDeAnalisis`, definida en `lexer.py` y usada también por el parser y las pruebas.

## Parser (`parser_formal.py`)

Parser descendente recursivo: una función por cada no terminal de la gramática (`programa()`, `sentencia()`, `declaracion()`, `tipo()`, …), con su regla EBNF como comentario encima. Recorre los tokens del lexer con cuatro herramientas: `actual()`, `ver(*tipos)`, `consumir(tipo)` y `error(mensaje)`.

- **Interfaz:** `parsear_codigo(codigo)` devuelve un `nltk.Tree` o lanza `ErrorDeAnalisis`.
- **Árbol:** cada nodo lleva el nombre de su no terminal; las hojas son los valores de los tokens (`x`, `5`, `+`). Se guardan los nombres, números, operadores (`+`, `*`, `>`, …), el tipo (`int`/`float`) y los `( )` de `factor`; no se guardan `;`, `=`, las llaves, los paréntesis de `if`/`while` ni las palabras `if`, `else`, `while`, porque el nodo ya dice qué regla es. La rama del `else` va dentro de un nodo `sino`, que no es un no terminal de la gramática: solo marca la rama para que se vea a qué `if` quedó pegada.
- **Ejemplo:** `int x = 2 + 3 * 4;` da `(programa (declaracion (tipo int) x (expr (termino (factor 2)) + (termino (factor 3) * (factor 4)))))`. `3 * 4` queda en un solo `termino`: la multiplicación va primero.
- **Else colgante:** se resuelve solo; `si()` mira si sigue un `else` justo después de su sentencia, así que el `if` más interno se lo queda.
- **Errores:** `Línea N: se esperaba X y se encontró Y`. Si se acabó la entrada, dice «se encontró el fin del código». Ejemplo: `int y = 5` → `Línea 1: se esperaba ';' y se encontró el fin del código`.
- **Sin recuperación de errores:** se detiene en el primer error (el modo pánico era opcional y no se implementó).

## Pruebas (`test_parser_formal.py`)

`pytest -v` da **24 passed**:

| Grupo | Casos | Ejemplos |
| --- | ---: | --- |
| Código válido | 11 | declaraciones, `if/else`, `while` anidado, bloque vacío, programa vacío, comentarios `//` |
| Código inválido | 10 | falta `;`, falta `(` o `)`, `else` sin `if`, `5x`, cuenta incompleta, llave sin cerrar, carácter `@`, condición sin comparación |
| Precedencia | 1 | `2 + 3 * 4` agrupa `3 * 4` |
| Else colgante | 1 | el `else` queda en el `if` interno |
| Línea del error | 1 | el error de la segunda línea dice «Línea 2» |

---

[Índice de la Fase 1](../README.md) · Siguiente: [2. Gramática del español](02_gramatica_espanol.md) →
