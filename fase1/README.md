# Fase 1 — Parsers (P1)

Lexer y parser de mini-C, y motor genérico para analizar oraciones del español.
Las reglas, convenciones y decisiones del equipo están en [decisiones_tomadas.md](decisiones_tomadas.md).

## Archivos

| Archivo | Qué hace | Estado |
| --- | --- | --- |
| `lexer.py` | Convierte código mini-C en tokens (`tokenizar`) y define `ErrorDeAnalisis` | Listo |
| `motor.py` | Motor descendente con backtracking; devuelve todos los árboles (`todos_los_arboles`, `parsear`) | Listo |
| `gramatica_es.py` | Gramática del español como diccionario (`GRAMATICA`, `INICIAL`) | Listo (de ejemplo; la reemplaza P2) |
| `parser_formal.py` | Parser descendente recursivo de mini-C | Pendiente |
| `test_parser_formal.py` | Pruebas con pytest del lexer y el parser | Pendiente |

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
pytest -v           # cuando exista test_parser_formal.py
```

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
