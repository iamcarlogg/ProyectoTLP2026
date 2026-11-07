# Fase 1 — Encontrar el límite

Primero se construye un parser que funciona perfecto sobre un lenguaje formal (mini-C). Después se usa un motor genérico para intentar describir el español con una CFG y se documenta dónde y por qué falla.

El panorama del proyecto está en el [README principal](../README.md) y las convenciones del equipo en [docs/decisiones.md](../docs/decisiones.md).

## Archivos

### Parte A — Lenguaje formal (mini-C) · P1

| Archivo | Qué hace |
| --- | --- |
| `lexer.py` | Convierte código mini-C en tokens (`tokenizar`). Define `ErrorDeAnalisis`, la única excepción del parser formal. |
| `parser_formal.py` | Parser descendente recursivo: una función por regla. `parsear_codigo(codigo)` devuelve el árbol. |
| `test_parser_formal.py` | 24 pruebas con pytest: código válido, inválido, precedencia, else colgante y línea del error. |

### Parte B — Español · P1 (motor) y P2 (gramática y análisis)

| Archivo | Qué hace |
| --- | --- |
| `motor.py` | Parser genérico con backtracking: recibe cualquier gramática escrita como diccionario y devuelve todos los árboles. |
| `gramatica_es.py` | Gramática extendida del español: concordancia, relativas y modificadores (93 producciones). |
| `pruebas_base.py` | Las 20 oraciones acordadas; compara la respuesta del parser con la esperada. |
| `pruebas_fallas.py` | 24 casos adicionales para la tabla de fallas. |
| `analisis_explosion.py` | Cuenta cuánto crece la gramática por la concordancia (22 → 48 → 93). |

### Parte C — NLP · P3

| Archivo | Qué hace |
| --- | --- |
| `demo_nlp.py` | Analiza las 20 oraciones de P2 con spaCy: categoría, género, número, relación y raíz. |
| `tabla_nlp.py` | Tabla lado a lado: respuesta correcta, CFG y spaCy. Define la regla de concordancia con la que spaCy «rechaza». |
| `visualizar_nlp.py` | Genera la página interactiva de la demo en `salidas/`. |
| `plantilla_demo.html` | Diseño de esa página; `visualizar_nlp.py` la llena con los datos. |

### Documentación (en orden de lectura)

| Documento | Contenido |
| --- | --- |
| [01_parser_minic.md](documentacion/01_parser_minic.md) | Alcance de mini-C, gramática EBNF, diseño del lexer y del parser, pruebas. |
| [02_gramatica_espanol.md](documentacion/02_gramatica_espanol.md) | Las 20 oraciones, la gramática base y la extendida, comparación 9/20 → 20/20, ambigüedad. |
| [03_tabla_de_fallas.md](documentacion/03_tabla_de_fallas.md) | 24 casos extra, tabla de fallas y relación con la jerarquía de Chomsky. |
| [04_explosion_de_reglas.md](documentacion/04_explosion_de_reglas.md) | Cuánto cuesta la concordancia en número de reglas. |
| [05_donde_si_falla_la_cfg.md](documentacion/05_donde_si_falla_la_cfg.md) | Dependencias cruzadas: el fenómeno que sí excede a una CFG, con demostración y nivel de Chomsky. |
| [06_demo_nlp.md](documentacion/06_demo_nlp.md) | spaCy frente a la CFG: criterio de acierto, resultados, qué captura cada uno y la página de la demo. |

## Cómo ejecutar

Con el entorno preparado (ver el [README principal](../README.md#preparar-el-entorno)), desde la raíz del repositorio:

| Comando | Qué muestra | Resultado esperado |
| --- | --- | --- |
| `pytest -v` | Pruebas del parser de mini-C | 24 passed |
| `python fase1/lexer.py` | Tokens de un ejemplo | Lista de tokens terminada en `EOF` |
| `python fase1/parser_formal.py` | Árbol de un programa y un error | Árbol dibujado y `Línea 1: se esperaba ';'…` |
| `python fase1/motor.py` | Cuatro oraciones en español | 2 aceptadas, 2 rechazadas |
| `python fase1/pruebas_base.py` | Las 20 oraciones | 20/20 coinciden |
| `python fase1/pruebas_fallas.py` | Los 24 casos extra | 14/24, caso 19 con 2 árboles |
| `python fase1/analisis_explosion.py --probar` | Crecimiento de reglas | 22 / 48 / 93; 9/20, 16/20, 20/20 |
| `python fase1/demo_nlp.py` | spaCy sobre las 20 oraciones | Raíz = verbo en 14/20 |
| `python fase1/tabla_nlp.py` | CFG frente a spaCy | 20/20 frente a 19/20 (`--fallas`: 14/24 frente a 22/24) |
| `python fase1/visualizar_nlp.py` | Página de la demo | `salidas/demo_nlp.html` (también `--todas` y `--fallas`) |

También funcionan desde dentro de `fase1/` (`python motor.py`, etc.).

## Cómo usarlo desde tu código

Los módulos se importan desde `fase1/` (o con `fase1/` en el `sys.path`).

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

- `parsear_codigo(codigo)` devuelve un `nltk.Tree` o lanza `ErrorDeAnalisis` (sea error del lexer o del parser).
- Salida del ejemplo: `(programa (declaracion (tipo int) x (expr (termino (factor 2)) + (termino (factor 3) * (factor 4)))))`.

### Motor del español

```python
from motor import parsear, todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL

arbol = parsear("El perro come la carne", GRAMATICA, INICIAL)   # primer árbol o None
arboles = todos_los_arboles("El perro come la carne", GRAMATICA, INICIAL)
print(len(arboles))     # 0 = rechazada; más de 1 = ambigua
```

- No lanza excepciones: si la oración no cumple la gramática, `parsear` devuelve `None` y `todos_los_arboles` una lista vacía.
- Para escribir otra gramática, seguir las [reglas del motor](../docs/decisiones.md#motor-genérico-reglas-para-escribir-una-gramática).

## Limitaciones conocidas

- El parser de mini-C se detiene en el primer error (sin recuperación en modo pánico).
- El backtracking del motor puede ser exponencial en el peor caso.
- El motor no quita `¿` ni `?`, así que las preguntas se rechazan (caso 20 de la tabla de fallas).
- spaCy no rechaza oraciones: la regla de concordancia de `tabla_nlp.py` es nuestra y falla con sujetos coordinados.
