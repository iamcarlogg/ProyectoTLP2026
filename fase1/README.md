# Fase 1 — Parsers (P1)

Lexer y parser de mini-C, y motor genérico para analizar oraciones del español.
Las reglas, convenciones y decisiones del equipo están en [decisiones_tomadas.md](decisiones_tomadas.md).

## Archivos

| Archivo | Qué hace | Estado |
| --- | --- | --- |
| `lexer.py` | Convierte código mini-C en tokens (`tokenizar`) y define `ErrorDeAnalisis` | Listo |
| `motor.py` | Motor descendente con backtracking; devuelve todos los árboles (`todos_los_arboles`, `parsear`) | Listo |
| `gramatica_es.py` | Gramática del español como diccionario (`GRAMATICA`, `INICIAL`) | Listo (de ejemplo; la reemplaza P2) |
| `parser_formal.py` | Parser descendente recursivo de mini-C (`parsear_codigo`) | Listo |
| `test_parser_formal.py` | Pruebas con pytest del lexer y el parser (24) | Listo |

## Entorno

Desde la raíz del repositorio (Python 3.10 o más reciente):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cómo ejecutar

Desde `fase1/`:

```bash
cd fase1
python lexer.py     # tokeniza un ejemplo de mini-C
python motor.py     # analiza oraciones de ejemplo con gramatica_es.py
python parser_formal.py  # árbol de un ejemplo válido y error de uno inválido
pytest -v           # 24 passed
```

## Cómo usarlo desde tu código

Los archivos se importan desde `fase1/` (o con `fase1/` en el `sys.path`).

### Parser de mini-C

```python
from lexer import ErrorDeAnalisis
from parser_formal import parsear_codigo

try:
    arbol = parsear_codigo("int x = 2 + 3 * 4;")
    print(arbol)            # notación de corchetes (formato del equipo)
    arbol.pretty_print()    # dibujo en la terminal
except ErrorDeAnalisis as e:
    print("Error:", e)      # p. ej. "Línea 1: se esperaba ';' y se encontró el fin del código"
```

- `parsear_codigo(codigo)` devuelve un `nltk.Tree` o lanza `ErrorDeAnalisis` (la única excepción, sea error del lexer o del parser).
- Cada nodo lleva el nombre de su no terminal (`programa`, `declaracion`, `expr`, …); el `else` va en un nodo `sino`.
- Salida del ejemplo: `(programa (declaracion (tipo int) x (expr (termino (factor 2)) + (termino (factor 3) * (factor 4)))))`.
- Detalle del formato del árbol: [decisiones_tomadas.md](decisiones_tomadas.md#parser-de-mini-c-parser_formalpy).

### Motor del español

```python
from motor import parsear, todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL

arbol = parsear("El perro come la carne", GRAMATICA, INICIAL)   # primer árbol o None
arboles = todos_los_arboles("El perro come la carne", GRAMATICA, INICIAL)
print(len(arboles))     # más de 1 = la oración es ambigua; 0 = rechazada
```

- No lanza excepciones: si la oración no cumple la gramática, `parsear` devuelve `None` y `todos_los_arboles` una lista vacía.
- Reglas para escribir la gramática: [decisiones_tomadas.md](decisiones_tomadas.md#reglas-para-escribir-la-gramática).

## Gramática de mini-C (EBNF)

No terminales en minúscula, clases de token en MAYÚSCULAS, texto literal entre comillas simples.

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

## Limitaciones conocidas

- «El perro duermen» se acepta: la gramática de ejemplo no controla la concordancia sujeto-verbo.
- El backtracking del motor es exponencial en el peor caso.
- El parser de mini-C se detiene en el primer error (no hay recuperación en modo pánico).
