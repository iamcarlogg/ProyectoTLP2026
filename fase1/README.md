# Fase 1 — Parsers (P1) y Gramáticas del Español (P2)

Lexer y parser de mini-C, motor genérico para analizar oraciones del español y dos etapas de gramática (base y extendida) para comparar sus resultados. Las reglas, convenciones y decisiones del equipo están en [decisiones_tomadas.md](decisiones_tomadas.md).

## Archivos

| Archivo                 | Qué hace                                                                                                                | Estado               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `lexer.py`              | Convierte código mini-C en tokens (`tokenizar`) y define `ErrorDeAnalisis`.                                             | Listo (P1)           |
| `motor.py`              | Motor descendente con backtracking; devuelve todos los árboles (`todos_los_arboles`, `parsear`).                        | Listo (P1)           |
| `gramatica_es.py`       | Gramática extendida del español, como diccionario (`GRAMATICA`, `INICIAL`): concordancia, subordinadas y modificadores. | Listo: tarea 3 (P2)  |
| `pruebas_base.py`       | Ejecuta las 20 oraciones y compara aceptación/rechazo con la validez esperada en español.                               | Listo (P2)           |
| `parser_formal.py`      | Parser descendente recursivo de mini-C.                                                                                 | Listo (P1)           |
| `test_parser_formal.py` | Pruebas con pytest del lexer y el parser formal (24 casos).                                                             | Listo (P1)           |
| `decisiones_tomadas.md` | Registra acuerdos de nombres, estructura e interfaz del equipo.                                                         | Documento compartido |

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
python lexer.py          # tokeniza un ejemplo de mini-C (P1)
python parser_formal.py  # ejemplo del parser de mini-C (P1)
python motor.py          # ejemplos del español con la gramática actual (P1 + P2)
python pruebas_base.py   # las 20 oraciones acordadas con la gramática extendida (P2)
pytest -v                # pruebas automatizadas del mini-C de P1: 24 passed
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

> **Referencia histórica:** las siguientes producciones describen la primera versión, probada antes de la tarea 3. Ahora `gramatica_es.py` contiene la **gramática extendida**. Esta sección se conserva para comparar ambas etapas; no representa el contenido ejecutable actual del archivo.

### Objetivo y alcance

Implementar una gramática libre de contexto (CFG) inicial que reconozca oraciones sencillas en español mediante el motor de P1. Esta primera versión comprueba principalmente **el orden de las categorías**, no su concordancia de género o número. Tampoco incluye todavía subordinadas, adverbios ni frases preposicionales: esos fenómenos corresponden a la próxima ampliación.

### Símbolos

| Símbolo   | Significado                         | Ejemplo            |
| --------- | ----------------------------------- | ------------------ |
| `oracion` | Oración completa (símbolo inicial). | El perro duerme.   |
| `sn`      | Sintagma nominal.                   | El perro negro     |
| `sv`      | Sintagma verbal.                    | come la carne      |
| `det`     | Determinante.                       | el, la, los, las   |
| `n`       | Sustantivo.                         | perro, gata, carne |
| `adj`     | Adjetivo.                           | negro, negra       |
| `v`       | Verbo.                              | come, duermen      |

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

La columna **«Español esperado»** indica la corrección lingüística de la oración. Las columnas de las dos gramáticas registran las salidas obtenidas con el mismo motor y las mismas entradas, antes y después de la ampliación. La clasificación gramatical esperada no depende de lo que responda el parser.

| N.º | Grupo                | Oración                                           | Español esperado               | Gramática base | Gramática extendida |
| --: | -------------------- | ------------------------------------------------- | ------------------------------ | -------------- | ------------------- |
|   1 | Concordancia         | El perro duerme.                                  | Válida                         | Aceptada       | Aceptada            |
|   2 | Concordancia         | Los perros duermen.                               | Válida                         | Aceptada       | Aceptada            |
|   3 | Concordancia         | Las gatas duermen.                                | Válida                         | Aceptada       | Aceptada            |
|   4 | Concordancia         | El perro negro duerme.                            | Válida                         | Aceptada       | Aceptada            |
|   5 | Concordancia         | La gata negra duerme.                             | Válida                         | Aceptada       | Aceptada            |
|   6 | Concordancia         | Los perros negros duermen.                        | Válida                         | Aceptada       | Aceptada            |
|   7 | Concordancia         | Las gatas negras duermen.                         | Válida                         | Aceptada       | Aceptada            |
|   8 | Modificadores        | El perro come la carne.                           | Válida                         | Aceptada       | Aceptada            |
|   9 | Modificadores        | La gata come lentamente.                          | Válida                         | Rechazada      | Aceptada            |
|  10 | Modificadores        | El perro duerme en la casa.                       | Válida                         | Rechazada      | Aceptada            |
|  11 | Modificadores        | Los perros negros comen rápidamente en el jardín. | Válida                         | Rechazada      | Aceptada            |
|  12 | Subordinadas         | El perro que come duerme.                         | Válida                         | Rechazada      | Aceptada            |
|  13 | Subordinadas         | La gata que duerme come la carne.                 | Válida                         | Rechazada      | Aceptada            |
|  14 | Subordinadas         | Los perros que comen duermen en la casa.          | Válida                         | Rechazada      | Aceptada            |
|  15 | Subordinadas         | El perro que la gata persigue duerme.             | Válida                         | Rechazada      | Aceptada            |
|  16 | Errores y ambigüedad | La perro come.                                    | Inválida                       | Aceptada       | Rechazada           |
|  17 | Errores y ambigüedad | El perro negra duerme.                            | Inválida                       | Aceptada       | Rechazada           |
|  18 | Errores y ambigüedad | El perro duermen.                                 | Inválida                       | Aceptada       | Rechazada           |
|  19 | Errores y ambigüedad | El perro que come la carne duermen.               | Inválida                       | Rechazada      | Rechazada           |
|  20 | Errores y ambigüedad | El perro come la carne en la casa.                | Válida; potencialmente ambigua | Rechazada      | Aceptada            |

### Qué mide cada grupo

- **Concordancia (1–7):** número en sujeto y verbo, y género/número entre determinante, sustantivo y adjetivo.
- **Modificadores (8–11):** objetos directos, adjetivos, adverbios y frases preposicionales.
- **Subordinadas (12–15):** cláusulas relativas con «que»; la 15 incluye una relativa donde «el perro» funciona como objeto de «persigue».
- **Errores y ambigüedad (16–20):** desacuerdo de determinante-sustantivo, sustantivo-adjetivo y sujeto-verbo, incluso con una cláusula intermedia; la 20 puede admitir más de una estructura de adjunción para «en la casa».

### Resultados de la gramática base

Resultados obtenidos con las 20 entradas de `pruebas_base.py` y el motor de P1:

| Resultado                        | Cantidad |
| -------------------------------- | -------: |
| Oraciones analizadas             |       20 |
| Aceptadas por la gramática base  |       11 |
| Rechazadas por la gramática base |        9 |
| Válidas aceptadas correctamente  |        8 |
| Válidas rechazadas               |        8 |
| Inválidas aceptadas              |        3 |
| Inválidas rechazadas             |        1 |

**Interpretación:** las oraciones 16–18 muestran que la gramática base no controla concordancia. Las válidas 9–15 y 20 se rechazan porque faltan construcciones en la gramática inicial, **no porque una CFG sea incapaz de representarlas**. La oración 19 se rechaza, pero todavía **no demuestra** detección de concordancia a distancia: la versión base ya rechaza cualquier cláusula con «que».

Esta medición es el **punto de partida** para comparar con la gramática extendida, no el resultado final del proyecto.

### Comparación de los resultados obtenidos

| Medida                                             | Gramática base (tarea 2) | Gramática extendida (tarea 3) |
| -------------------------------------------------- | -----------------------: | ----------------------------: |
| Oraciones correctas del español aceptadas          |                        8 |                            16 |
| Oraciones correctas rechazadas (falsos negativos)  |                        8 |                             0 |
| Oraciones incorrectas aceptadas (falsos positivos) |                        3 |                             0 |
| Oraciones incorrectas rechazadas                   |                        1 |                             4 |
| **Clasificaciones acertadas**                      |                 **9/20** |                     **20/20** |
| Total de producciones en la gramática              |                       22 |                            93 |
| Total de no terminales                             |                        7 |                            34 |

El aumento en producciones muestra el costo de modelar variantes gramaticales en una CFG explícita. **No demuestra por sí solo que el español no sea libre de contexto.** El conjunto de prueba es pequeño y controlado: 20/20 no implica cobertura general del español.

## Gramática extendida del español — P2 (tarea 3, entrega: 26 de octubre de 2026)

La extensión mantiene **exactamente la interfaz de P1**: `GRAMATICA` es un diccionario de listas de producciones, `INICIAL = "oracion"`, todas las categorías están en minúscula y no hay recursión por la izquierda. Solo se reemplaza el contenido de `fase1/gramatica_es.py`; `motor.py` y `lexer.py` no se modifican.

### Fenómenos cubiertos

1. **Concordancia de género y número dentro del SN:** `det_ms`, `n_ms`, `adj_ms` (análogamente `_fs`, `_mp`, `_fp`) impiden combinaciones como «La perro» o «perro negra».
2. **Concordancia sujeto-verbo:** `oracion → sn_ms sv_s | sn_fs sv_s | sn_mp sv_p | sn_fp sv_p` obliga al singular/plural correcto, incluso cuando se interpone una subordinada.
3. **Relativas de sujeto y de objeto:** `rel_suj_s`, `rel_suj_p` y `rel_obj` permiten tanto «El perro que come duerme» como «El perro que la gata persigue duerme».
4. **Modificadores:** adjetivos (`adj_*`), adverbios (`adv`) y sintagmas preposicionales (`sp → p sn`).

### Producciones extendidas (resumen formal)

La siguiente notación usa `ε` para la producción vacía. Cada alternativa se almacena como una lista en `gramatica_es.py`; el código Python contiene las producciones ejecutables completas.

```text
oracion → sn_ms sv_s | sn_fs sv_s | sn_mp sv_p | sn_fp sv_p
sn      → sn_ms | sn_fs | sn_mp | sn_fp
sn_ms   → det_ms n_ms mod_ms
sn_fs   → det_fs n_fs mod_fs
sn_mp   → det_mp n_mp mod_mp
sn_fp   → det_fp n_fp mod_fp

mod_ms → ε | adj_ms | sp | adj_ms sp | rel_suj_s | rel_obj | adj_ms rel_suj_s | adj_ms rel_obj
mod_fs → ε | adj_fs | sp | adj_fs sp | rel_suj_s | rel_obj | adj_fs rel_suj_s | adj_fs rel_obj
mod_mp → ε | adj_mp | sp | adj_mp sp | rel_suj_p | rel_obj | adj_mp rel_suj_p | adj_mp rel_obj
mod_fp → ε | adj_fp | sp | adj_fp sp | rel_suj_p | rel_obj | adj_fp rel_suj_p | adj_fp rel_obj

rel_suj_s → 'que' sv_s
rel_suj_p → 'que' sv_p
rel_obj   → 'que' sn_ms vt_s | 'que' sn_fs vt_s | 'que' sn_mp vt_p | 'que' sn_fp vt_p

sv_s → v_s | v_s adv | v_s sp | v_s adv sp
     | vt_s sn | vt_s sn adv | vt_s sn sp | vt_s sn adv sp
sv_p → v_p | v_p adv | v_p sp | v_p adv sp
     | vt_p sn | vt_p sn adv | vt_p sn sp | vt_p sn adv sp

sp → p sn
p  → 'en'
adv → 'lentamente' | 'rápidamente'

det_ms → 'el'     det_fs → 'la'     det_mp → 'los'    det_fp → 'las'
n_ms   → 'perro' | 'jardín'
n_fs   → 'gata' | 'carne' | 'casa'
n_mp   → 'perros'
n_fp   → 'gatas'
adj_ms → 'negro'   adj_fs → 'negra'   adj_mp → 'negros'  adj_fp → 'negras'
v_s    → 'come' | 'duerme'
v_p    → 'comen' | 'duermen'
vt_s   → 'come' | 'persigue'
vt_p   → 'comen' | 'persiguen'
```

**Observación técnica:** `vt_s` y `vt_p` representan verbos transitivos. Las relativas de objeto contienen una posición de objeto omitida por diseño. No se hace análisis semántico: aceptar una oración significa únicamente que se puede derivar con estas reglas.

### Pruebas y ambigüedad

Desde la raíz del repositorio:

```powershell
python fase1/pruebas_base.py
```

Las 20 entradas se procesan sin errores: 16 válidas aceptadas y 4 inválidas rechazadas. Para examinar la ambigüedad sintáctica de la oración 20, desde `fase1/`:

```python
from motor import todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL

arboles = todos_los_arboles("El perro come la carne en la casa.", GRAMATICA, INICIAL)
print(len(arboles))  # 2: el SP se adjunta al verbo o al SN objeto
```

La ambigüedad no es necesariamente un error ni una prueba de que una CFG no pueda representar la oración: son dos derivaciones posibles en la gramática diseñada.

### Límites que quedan por estudiar

- El vocabulario y los patrones sintácticos son deliberadamente reducidos; las 20 pruebas se eligieron para cubrir el alcance definido.
- No se incluyen otras personas gramaticales, tiempos verbales, coordinación o todas las construcciones con pronombres relativos.
- Algunas relaciones semánticas y restricciones de selección verbal no se comprueban.
- Para la **tarea 4**, es importante agregar casos de estrés fuera del conjunto inicial y diferenciar _regla ausente_ de _limitación formal_. No debemos fabricar fallas ni afirmar que toda subordinación supera a las CFG.
- Para la **tarea 5**, conservar el recuento de 22 producciones base frente a 93 extendidas, identificando cuáles se añadieron por concordancia y cuáles por otras construcciones.

## Limitaciones conocidas y siguientes pasos

- La gramática **base** no controlaba concordancia ni reconocía las relativas, los adverbios y las frases preposicionales; esos casos ya están cubiertos en la **gramática extendida** para el conjunto de 20 pruebas.
- El backtracking del motor de P1 puede tener costo exponencial en los casos más difíciles; se conserva sin modificar.
- El parser de mini-C de P1 se detiene al detectar el primer error sintáctico.
- **Tarea 4 de P2 (28 de octubre):** tabla de fallas y análisis formal de los casos no cubiertos por el subconjunto, además de comparar los resultados de la gramática base y la extendida.
- **Tarea 5 de P2 (28 de octubre):** documentar sistemáticamente la multiplicación de reglas para concordancia (separándola del aumento por modificadores y subordinadas).
- **Informe (30 de octubre):** compartir la sección de gramáticas, pruebas y límites con P4.
