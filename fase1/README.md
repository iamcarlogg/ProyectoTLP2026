# Fase 1 — Parsers (P1) y Gramáticas del Español (P2)

Lexer y parser de mini-C, motor genérico para analizar oraciones del español y gramática base para las primeras pruebas. Las reglas, convenciones y decisiones del equipo están en [decisiones_tomadas.md](decisiones_tomadas.md).

## Archivos

| Archivo | Qué hace | Estado |
| --- | --- | --- |
| `lexer.py` | Convierte código mini-C en tokens (`tokenizar`) y define `ErrorDeAnalisis`. | Listo (P1) |
| `motor.py` | Motor descendente con backtracking; devuelve todos los árboles (`todos_los_arboles`, `parsear`). | Listo (P1) |
| `gramatica_es.py` | Gramática base del español como diccionario (`GRAMATICA`, `INICIAL`). | Base implementada (P2); extensión pendiente |
| `pruebas_base.py` | Ejecuta las 20 oraciones y compara aceptación/rechazo con la validez esperada en español. | Listo (P2) |
| `parser_formal.py` | Parser descendente recursivo de mini-C. | Pendiente (P1) |
| `test_parser_formal.py` | Pruebas con pytest del lexer y el parser formal. | Pendiente (P1) |
| `decisiones_tomadas.md` | Registra acuerdos de nombres, estructura e interfaz del equipo. | Documento compartido |

## Entorno

Desde la raíz del repositorio (Python 3.10 o más reciente):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows (PowerShell), para activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si la política de PowerShell impide activarlo, puedes usar directamente `.\.venv\Scripts\python.exe` desde la raíz del repositorio.

## Cómo ejecutar

Desde la raíz del repositorio, una vez preparado el entorno:

```bash
cd fase1
python lexer.py         # Tokeniza un ejemplo de mini-C (P1)
python motor.py         # Analiza ejemplos con gramatica_es.py (P1 + P2)
python pruebas_base.py  # Evalúa las 20 oraciones de prueba (P2)
pytest -v               # Cuando exista test_parser_formal.py (P1)
```

> `pruebas_base.py` debe estar en la misma carpeta que `motor.py` y `gramatica_es.py` para utilizar sus importaciones actuales.

## Gramática de mini-C (EBNF) — P1

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

## Gramática base del español — P2 (tarea 2, entrega: 24 de octubre de 2026)

### Objetivo y alcance

Implementar una gramática libre de contexto (CFG) inicial que reconozca oraciones sencillas en español mediante el motor de P1. Esta primera versión comprueba principalmente **el orden de las categorías**, no su concordancia de género o número. Tampoco incluye todavía subordinadas, adverbios ni frases preposicionales: esos fenómenos corresponden a la próxima ampliación.

### Símbolos

| Símbolo | Significado | Ejemplo |
| --- | --- | --- |
| `oracion` | Oración completa (símbolo inicial). | El perro duerme. |
| `sn` | Sintagma nominal. | El perro negro |
| `sv` | Sintagma verbal. | come la carne |
| `det` | Determinante. | el, la, los, las |
| `n` | Sustantivo. | perro, gata, carne |
| `adj` | Adjetivo. | negro, negra |
| `v` | Verbo. | come, duermen |

### Reglas de producción

Notación adoptada por el equipo: no terminales en minúsculas y palabras literales entre comillas simples. Estas producciones se representan en el diccionario `GRAMATICA` de `gramatica_es.py`.

```text
oracion → sn sv
sn      → det n | det n adj
sv      → v | v sn
det     → 'el' | 'la' | 'los' | 'las'
n       → 'perro' | 'perros' | 'gata' | 'gatas' | 'carne'
adj     → 'negro' | 'negros' | 'negra' | 'negras'
v       → 'come' | 'comen' | 'duerme' | 'duermen'
```

- `oracion → sn sv`: una oración contiene un sujeto y un predicado.
- `sn → det n | det n adj`: un grupo nominal tiene determinante y sustantivo, con adjetivo opcional.
- `sv → v | v sn`: el predicado puede incluir solo un verbo o verbo más objeto directo.
- `det`, `n`, `adj`, `v`: especifican el vocabulario disponible en esta primera versión.

**Ejemplo de derivación** de «El perro negro come la carne»:

```text
oracion
→ sn sv
→ det n adj sv
→ 'el' 'perro' 'negro' sv
→ 'el' 'perro' 'negro' v sn
→ 'el' 'perro' 'negro' 'come' det n
→ 'el' 'perro' 'negro' 'come' 'la' 'carne'
```

**Interfaz con P1:** `gramatica_es.py` exporta `GRAMATICA` (diccionario de producciones) e `INICIAL = "oracion"`. El motor compara palabras en minúscula y recibe las producciones sin que P2 tenga que modificar `motor.py` ni `lexer.py`.

## Oraciones de prueba — P2 (tarea 1, entrega: 22 de octubre de 2026)

Se prepararon **20 oraciones** para cubrir concordancia de género y número, modificadores, cláusulas subordinadas relativas y posibles errores o ambigüedades. El mismo conjunto se comparte con P1 (pruebas del parser) y P3 (demostración de NLP).

La columna **«Español esperado»** indica la corrección lingüística de la oración; **no implica** que la gramática base deba reconocer todas las oraciones correctas. La columna **«Gramática base»** registra la salida comprobada con `motor.py` y las producciones iniciales de P2.

| N.º | Grupo | Oración | Español esperado | Gramática base |
| ---: | --- | --- | --- | --- |
| 1 | Concordancia | El perro duerme. | Válida | Aceptada |
| 2 | Concordancia | Los perros duermen. | Válida | Aceptada |
| 3 | Concordancia | Las gatas duermen. | Válida | Aceptada |
| 4 | Concordancia | El perro negro duerme. | Válida | Aceptada |
| 5 | Concordancia | La gata negra duerme. | Válida | Aceptada |
| 6 | Concordancia | Los perros negros duermen. | Válida | Aceptada |
| 7 | Concordancia | Las gatas negras duermen. | Válida | Aceptada |
| 8 | Modificadores | El perro come la carne. | Válida | Aceptada |
| 9 | Modificadores | La gata come lentamente. | Válida | Rechazada |
| 10 | Modificadores | El perro duerme en la casa. | Válida | Rechazada |
| 11 | Modificadores | Los perros negros comen rápidamente en el jardín. | Válida | Rechazada |
| 12 | Subordinadas | El perro que come duerme. | Válida | Rechazada |
| 13 | Subordinadas | La gata que duerme come la carne. | Válida | Rechazada |
| 14 | Subordinadas | Los perros que comen duermen en la casa. | Válida | Rechazada |
| 15 | Subordinadas | El perro que la gata persigue duerme. | Válida | Rechazada |
| 16 | Errores y ambigüedad | La perro come. | Inválida | Aceptada |
| 17 | Errores y ambigüedad | El perro negra duerme. | Inválida | Aceptada |
| 18 | Errores y ambigüedad | El perro duermen. | Inválida | Aceptada |
| 19 | Errores y ambigüedad | El perro que come la carne duermen. | Inválida | Rechazada |
| 20 | Errores y ambigüedad | El perro come la carne en la casa. | Válida; potencialmente ambigua | Rechazada |

### Qué mide cada grupo

- **Concordancia (1–7):** número en sujeto y verbo, y género/número entre determinante, sustantivo y adjetivo.
- **Modificadores (8–11):** objetos directos, adjetivos, adverbios y frases preposicionales.
- **Subordinadas (12–15):** cláusulas relativas con «que»; la 15 incluye una relativa donde «el perro» funciona como objeto de «persigue».
- **Errores y ambigüedad (16–20):** desacuerdo de determinante-sustantivo, sustantivo-adjetivo y sujeto-verbo, incluso con una cláusula intermedia; la 20 puede admitir más de una estructura de adjunción para «en la casa».

### Resultados de la gramática base

Resultados obtenidos con las 20 entradas de `pruebas_base.py` y el motor de P1:

| Resultado | Cantidad |
| --- | ---: |
| Oraciones analizadas | 20 |
| Aceptadas por la gramática base | 11 |
| Rechazadas por la gramática base | 9 |
| Válidas aceptadas correctamente | 8 |
| Válidas rechazadas | 8 |
| Inválidas aceptadas | 3 |
| Inválidas rechazadas | 1 |

**Interpretación:** las oraciones 16–18 muestran que la gramática base no controla concordancia. Las válidas 9–15 y 20 se rechazan porque faltan construcciones en la gramática inicial, **no porque una CFG sea incapaz de representarlas**. La oración 19 se rechaza, pero todavía **no demuestra** detección de concordancia a distancia: la versión base ya rechaza cualquier cláusula con «que».

Esta medición es el **punto de partida** para comparar con la gramática extendida, no el resultado final del proyecto.

## Limitaciones conocidas y siguientes pasos

- «El perro duermen» se acepta en la gramática base porque todavía no hay concordancia entre sujeto y verbo.
- Los sustantivos, adjetivos y determinantes se pueden combinar sin comprobar género ni número.
- No se reconocen subordinadas, adverbios ni frases preposicionales en esta versión.
- La gramática actual no permite analizar aún la ambigüedad potencial de la oración 20.
- El backtracking del motor es exponencial en el peor caso (limitación señalada por P1).
- **Siguiente tarea P2 (26 de octubre):** ampliar `gramatica_es.py` para concordancia de género/número, subordinadas y modificadores; volver a ejecutar exactamente las mismas 20 pruebas.
- **Tarea posterior P2 (28 de octubre):** registrar las fallas observadas y cuantificar el crecimiento de reglas, diferenciando límites del diseño o del parser de límites formales de las CFG.
