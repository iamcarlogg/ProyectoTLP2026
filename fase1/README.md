# Fase 1 — Parsers (P1) y Gramáticas del Español (P2)

Lexer y parser de mini-C, motor genérico para analizar oraciones del español y dos etapas de gramática (base y extendida) para comparar sus resultados. Las reglas, convenciones y decisiones del equipo están en [decisiones_tomadas.md](decisiones_tomadas.md).

## Archivos

| Archivo                 | Qué hace                                                                                                                | Estado                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `lexer.py`              | Convierte código mini-C en tokens (`tokenizar`) y define `ErrorDeAnalisis`.                                             | Listo (P1)             |
| `motor.py`              | Motor descendente con backtracking; devuelve todos los árboles (`todos_los_arboles`, `parsear`).                        | Listo (P1)             |
| `gramatica_es.py`       | Gramática extendida del español, como diccionario (`GRAMATICA`, `INICIAL`): concordancia, subordinadas y modificadores. | Listo: tarea 3 (P2)    |
| `pruebas_base.py`       | Ejecuta las 20 oraciones iniciales y compara aceptación/rechazo con la validez esperada.                                | Listo: tareas 1–3 (P2) |
| `pruebas_fallas.py`     | Ejecuta 24 pruebas adicionales y registra aceptación, número de árboles y fallas.                                       | Listo: tarea 4 (P2)    |
| `analisis_explosion.py` | Cuenta alternativas, construye un control sin concordancia y cuantifica el crecimiento de reglas.                       | Listo: tarea 5 (P2)    |
| `parser_formal.py`      | Parser descendente recursivo de mini-C.                                                                                 | Listo (P1)             |
| `test_parser_formal.py` | Pruebas con pytest del lexer y el parser formal (24 casos).                                                             | Listo (P1)             |
| `decisiones_tomadas.md` | Registra acuerdos de nombres, estructura e interfaz del equipo.                                                         | Documento compartido   |

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
python pruebas_fallas.py # 24 casos extra para la tabla de fallas (P2)
python analisis_explosion.py --probar  # crecimiento y pruebas comparativas (P2)
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
- En la **tarea 4** se agregaron 24 casos de estrés y se distinguió _regla ausente_ de _limitación formal_, sin inventar fallas ni atribuir a toda subordinación un nivel superior a Tipo 2.
- Para la **tarea 5**, conservar el recuento de 22 producciones base frente a 93 extendidas, identificando cuáles se añadieron por concordancia y cuáles por otras construcciones.

## Tabla de fallas y análisis formal — P2 (tarea 4, entrega: 28 de octubre de 2026)

### Metodología

Se conservaron **sin cambios las 20 oraciones de la tarea 1**, que la gramática extendida de la tarea 3 clasifica correctamente (16 válidas aceptadas y 4 inválidas rechazadas). Como ese conjunto ya no presenta discrepancias, se ejecutaron **24 casos adicionales** con `pruebas_fallas.py` para estudiar estructuras no cubiertas, controles positivos, errores reales de concordancia y ambigüedad. Las pruebas se realizaron con el mismo `motor.py` de P1, la versión extendida de `gramatica_es.py` y sin añadir reglas de propósito especial para superar los casos.

```powershell
# Desde la raíz del repositorio
python fase1/pruebas_base.py
python fase1/pruebas_fallas.py
```

| Medida                                    | Resultado de los 24 casos adicionales |
| ----------------------------------------- | ------------------------------------: |
| Oraciones gramaticalmente válidas         |                                    21 |
| Oraciones gramaticalmente inválidas       |                                     3 |
| Válidas aceptadas                         |                                    11 |
| **Válidas rechazadas (falsos negativos)** |                                **10** |
| Inválidas aceptadas (falsos positivos)    |                                     0 |
| Inválidas rechazadas                      |                                     3 |
| **Clasificaciones correctas**             |                             **14/24** |

**Precaución metodológica:** la columna de validez se refiere a la _gramaticalidad sintáctica_; el significado puede ser extraño sin dejar de ser gramatical. La regla «implicada» se identificó mediante inspección de las producciones, porque el motor devuelve árboles completos o una lista vacía, pero no señala una producción fallida concreta.

### Tabla de fallas: oraciones correctas rechazadas

| Caso | Oración                              | Regla implicada o ausente                                           | Fenómeno y causa del rechazo                                                                                                                       | Jerarquía de Chomsky                                        |
| ---: | ------------------------------------ | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
|    3 | El perro duerme con la gata.         | `sp → p sn`, pero `p → 'en'`                                        | Falta `con` en el vocabulario de preposiciones.                                                                                                    | **Tipo 2**: ampliable en CFG.                               |
|    4 | El perro persigue a la gata.         | `sv_s → vt_s sn`                                                    | Falta la variante del objeto directo animado introducido por `a`. No basta con añadir la preposición a `p` sin revisar la construcción del objeto. | **Tipo 2**: ampliable en CFG.                               |
|    5 | El perro no duerme.                  | `sv_s` y `sv_p` no admiten `no` antes del verbo.                    | Negación verbal ausente.                                                                                                                           | **Tipo 2**: ampliable en CFG.                               |
|    6 | El perro duerme porque la gata come. | `oracion → sn_* sv_*`; `sv_*` no permite una cláusula causal final. | Subordinación causal no implementada (solo relativas).                                                                                             | **Tipo 2**: ampliable en CFG.                               |
|    7 | El perro come y la gata duerme.      | `oracion` solo contiene una estructura `sn sv`.                     | Coordinación de dos oraciones ausente.                                                                                                             | **Tipo 2**: ampliable en CFG.                               |
|    8 | El perro negro y grande duerme.      | `mod_ms` no admite `adj_ms 'y' adj` y no existe `grande`.           | Coordinación de adjetivos y vocabulario insuficiente.                                                                                              | **Tipo 2**: ampliable en CFG.                               |
|    9 | El perro muy negro duerme.           | `mod_ms → adj_ms` pero no existe estructura `adv_grado adj_ms`.     | Intensificación adjetival no incluida.                                                                                                             | **Tipo 2**: ampliable en CFG.                               |
|   10 | El perro negro pequeño duerme.       | `mod_ms` admite solo un adjetivo y `pequeño` no está en el léxico.  | Secuencia de adjetivos y vocabulario ausentes.                                                                                                     | **Tipo 2**: ampliable en CFG.                               |
|   20 | ¿El perro duerme?                    | `motor.py` elimina puntos y comas, pero conserva `¿` y `?`.         | El primer terminal queda `¿el` y el último `duerme?`: problema de normalización; no demuestra un límite de las CFG.                                | **No es un salto de nivel**: problema del preprocesamiento. |
|   21 | El perro y la gata duermen.          | `sn_ms` / `sn_fs` forman un SN simple, no un sujeto coordinado.     | Coordinación nominal y concordancia plural del conjunto ausentes.                                                                                  | **Tipo 2**: ampliable en CFG.                               |

**Interpretación:** todos los rechazos anteriores se explican por reglas ausentes o por tratamiento de la entrada. No se ha demostrado que un lenguaje de Tipo 2 sea formalmente insuficiente para ninguna de esas oraciones. La longitud de una oración y la existencia de una subordinada, por sí mismas, no prueban que se necesite Tipo 1.

### Rechazos correctos y controles

|                    Caso | Oración                                | Resultado                 | Regla y explicación                                                                                                                                      |
| ----------------------: | -------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                      15 | El perro que la gata persiguen duerme. | Rechazada correctamente   | `rel_obj → 'que' sn_fs vt_s` exige verbo subordinado singular (`persigue`); `persiguen` pertenece a `vt_p`. Es concordancia dentro de la relativa.       |
|                      16 | Los perros que comen duerme.           | Rechazada correctamente   | `oracion → sn_mp sv_p` obliga a un verbo principal plural, incluso con una relativa intermedia.                                                          |
|                      24 | El perro duerme la carne.              | Rechazada correctamente   | No existe `sv_s → v_s sn`; `duerme` no está incluido entre los verbos transitivos `vt_s`.                                                                |
| 1, 2, 11–14, 17, 22, 23 | Oraciones de control                   | Aceptadas                 | Confirman que funcionan ciertas relativas, concordancias, adverbios y preposiciones dentro del alcance.                                                  |
|                      18 | La carne negra duerme.                 | Aceptada                  | Bien formada sintácticamente bajo nuestras reglas, aunque el significado resulte inusual. El parser **no** comprueba la plausibilidad semántica.         |
|                      19 | El perro come la carne en la casa.     | Aceptada: **dos árboles** | `sp` puede depender de `sv_s` o de `sn` (objeto). Es **ambigüedad estructural**, no falla de reconocimiento ni evidencia de que la CFG sea insuficiente. |

### Fallas históricas detectadas en la gramática base

La gramática base de la tarea 2 tenía **11 discrepancias** respecto de las 20 oraciones iniciales. La extensión de la tarea 3 solucionó las once:

| Oración original | Resultado de la base         | Motivo inicial                                    | Solución introducida en la tarea 3                                             |
| ---------------- | ---------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------ |
| 9                | Rechazada (incorrectamente)  | `sv` no admitía adverbios.                        | `sv_s → v_s adv`.                                                              |
| 10               | Rechazada (incorrectamente)  | No existía `sp`.                                  | `sv_s → v_s sp`; `sp → p sn`.                                                  |
| 11               | Rechazada (incorrectamente)  | Faltaban adverbio y frase preposicional juntos.   | `sv_p → v_p adv sp`.                                                           |
| 12 y 13          | Rechazadas (incorrectamente) | No existían subordinadas relativas.               | `rel_suj_s`.                                                                   |
| 14               | Rechazada (incorrectamente)  | Faltaban relativa plural y frase preposicional.   | `rel_suj_p` y `sp`.                                                            |
| 15               | Rechazada (incorrectamente)  | No existía relativa de objeto.                    | `rel_obj`.                                                                     |
| 16               | Aceptada (incorrectamente)   | `sn → det n` no diferenciaba género.              | `det_fs` y `n_ms` ya no pueden combinarse en `sn`.                             |
| 17               | Aceptada (incorrectamente)   | `sn → det n adj` no diferenciaba género.          | `mod_ms` solo admite `adj_ms`.                                                 |
| 18               | Aceptada (incorrectamente)   | `oracion → sn sv` no imponía número sujeto-verbo. | `oracion → sn_ms sv_s` obliga al sujeto singular a usar un predicado singular. |
| 20               | Rechazada (incorrectamente)  | Sin `sp`, no se podía adjuntar «en la casa».      | `sp` dentro del SN o del SV; dos árboles.                                      |

La oración original 19 («El perro que come la carne duermen») fue rechazada por ambas versiones, pero **solo la versión extendida permite atribuirlo a la concordancia principal** dentro del alcance de sus reglas; la versión base la rechazaba por no reconocer ninguna relativa.

### Relación formal con la jerarquía de Chomsky

- **Tipo 2 (gramáticas libres de contexto, CFG):** nuestras producciones (`A → ...`, con un único no terminal a la izquierda) pertenecen a este nivel. Su vocabulario reducido y las reglas no implementadas explican los falsos negativos documentados. La concordancia finita puede codificarse con categorías como `_ms`, `_fs`, `_mp`, `_fp` sin abandonar Tipo 2.
- **Tipo 1 (gramáticas sensibles al contexto):** existen lenguajes que necesitan mayor poder expresivo; sin embargo, **ninguno de los ejemplos probados constituye una demostración de que la CFG sea insuficiente como clase formal**. «Concordancia a distancia» en nuestros ejemplos tampoco requiere Tipo 1 porque los rasgos comprobados son finitos.
- **Ambigüedad:** el caso 19 produce dos análisis bajo una CFG de Tipo 2. Disponer de varios árboles es una propiedad de la gramática, no automáticamente un fallo ni evidencia de Tipo 1.
- **Semántica y pragmática:** `La carne negra duerme` evidencia que reconocer sintaxis no equivale a entender plausibilidad o significado. Esa distinción no se traduce automáticamente en una categoría distinta de Chomsky.
- **Dependencias cruzadas:** no se ha implementado ni verificado un caso que pruebe formalmente una dependencia cruzada no expresable por CFG. Debe indicarse como **no demostrado**, no atribuirlo artificialmente a un rechazo.

**Conclusión de la tarea 4:** identificamos reglas ausentes, casos de concordancia que la CFG sí resuelve, ambigüedad reconocida y limitaciones de preprocesamiento. Es evidencia de los límites de _esta gramática controlada_, no una prueba de imposibilidad para todas las CFG. Para la tarea 5 se analizará por separado cuánto creció el conjunto de producciones (22 en la base; 93 en la extendida) y qué parte del crecimiento corresponde a la concordancia.

## Explosión de reglas — P2 (tarea 5, entrega: 28 de octubre de 2026)

### Objetivo y criterio de conteo

Se estudia el crecimiento de **producciones** al ampliar una gramática libre de contexto (CFG) para el español y, especialmente, al codificar **concordancia de género y número** mediante categorías separadas. Para evitar confundir la concordancia con las nuevas subordinadas, los modificadores y el vocabulario, se comparan **tres versiones**:

1. **Base (tarea 2):** gramática original de 7 no terminales, sin concordancia ni construcciones extendidas. El script conserva su diccionario como instantánea histórica, sin alterar el código operativo.
2. **Control sin concordancia:** derivado **automáticamente de la gramática extendida** al fusionar las categorías de género y número y quitar producciones duplicadas. Retiene las familias de construcciones y las **mismas 25 palabras terminales** de la extendida. No es la misma gramática de la tarea 2.
3. **Extendida con concordancia (tarea 3):** el contenido real de `gramatica_es.py`, con categorías `_ms`, `_fs`, `_mp`, `_fp`, verbos singulares/plurales y las producciones correspondientes.

Cada alternativa del diccionario cuenta como **una producción**, incluido `[]` (ε). Por ejemplo `sn → det n | det n adj` suma dos. Las reglas de vocabulario también se cuentan: `n → 'perro' | 'gata'` suma dos. No se cuentan los pasos internos que hace el motor durante el backtracking.

### Comparación cuantitativa

| Versión                                  | No terminales | Producciones | Terminales distintos |
| ---------------------------------------- | ------------: | -----------: | -------------------: |
| Gramática base, tarea 2                  |             7 |           22 |                   17 |
| Extendida **sin** concordancia (control) |            15 |           48 |                   25 |
| Extendida **con** concordancia, tarea 3  |            34 |           93 |                   25 |

**Descomposición:** de **22 a 48** hay **26 producciones adicionales** asociadas a ampliar las estructuras y el vocabulario. Comparando **48 y 93**, con el mismo vocabulario y las mismas familias de construcciones, hay **45 producciones adicionales** por representar rasgos de concordancia en las categorías. El aumento total de **22 a 93** es de **71 producciones**: la gramática final tiene **4,23 veces** tantas producciones como la base. Frente al control sin rasgos, tiene **1,94 veces** tantas.

### ¿Dónde aparecen las 45 producciones adicionales?

| Grupo funcional                               | Sin concordancia | Con concordancia | Aumento |
| --------------------------------------------- | ---------------: | ---------------: | ------: |
| Reglas de oración                             |                1 |                4 |      +3 |
| Sintagma nominal y sus variantes              |                2 |                8 |      +6 |
| Modificadores nominales                       |                8 |               32 |     +24 |
| Subordinadas relativas                        |                2 |                6 |      +4 |
| Sintagmas verbales                            |                8 |               16 |      +8 |
| Léxico, adverbios y sintagmas preposicionales |               27 |               27 |       0 |
| **Total**                                     |           **48** |           **93** | **+45** |

La mayor duplicación se produce en los modificadores: la versión sin rasgos tiene **8 alternativas** de `mod` y la extendida necesita repetirlas como **8 por cada una de 4 combinaciones** (`mod_ms`, `mod_fs`, `mod_mp`, `mod_fp`): 32 alternativas. Los sintagmas verbales pasan de 8 a 16 por distinguir singular y plural. Los terminales no aumentan entre las dos gramáticas ampliadas: el aumento se debe a las **reglas de combinación**, no a introducir más palabras.

**Ejemplo concreto de concordancia:**

```text
# Sin distincion (control)
oracion → sn_tipo sv

# Con distincion (gramatica extendida)
oracion → sn_ms sv_s | sn_fs sv_s | sn_mp sv_p | sn_fp sv_p
```

El segundo caso impide que un sujeto singular se combine con un verbo plural, a costa de enumerar cuatro posibilidades. Esta técnica sigue siendo **CFG de Tipo 2**: cada producción tiene un solo no terminal a la izquierda. La multiplicación observada depende del diseño y del subconjunto de español que hemos elegido; **no demuestra que toda CFG deba crecer a esa tasa** ni que la concordancia finita requiera gramáticas de Tipo 1.

### Cómo reproducir el estudio

Agregar `analisis_explosion.py` junto a `gramatica_es.py` y `pruebas_base.py` en `fase1/`. Desde la raíz del repositorio:

```powershell
python fase1/analisis_explosion.py
python fase1/analisis_explosion.py --probar
```

El primer comando compara tamaños y desglosa los 45 casos adicionales; el segundo además ejecuta las 20 oraciones iniciales con las tres gramáticas. **Resultado de control:** base **9/20**, ampliada sin concordancia **16/20** y extendida con concordancia **20/20** clasificaciones correctas. La versión sin concordancia ya reconoce las subordinadas y los modificadores, pero acepta cuatro oraciones incorrectas por no restringir el acuerdo entre palabras. Es una comprobación experimental sobre el conjunto seleccionado, no una medida de precisión para todo el español.

### Conclusión formal

El problema ilustrado es principalmente el **costo de especificación y mantenimiento**: incluir explícitamente género y número implica repetir alternativas en varias categorías, y ese esfuerzo aumenta al añadir nuevas combinaciones. Las producciones siguen siendo libres de contexto (Tipo 2). La gramática podría organizarse de otras formas y obtener otros conteos; nuestro experimento cuantifica **esta implementación**, no una cota universal para las CFG. Los rechazos documentados en la tarea 4 son mayoritariamente reglas ausentes, no imposibilidades formales demostradas.

## Limitaciones conocidas y siguientes pasos

- La gramática **base** no controlaba concordancia ni reconocía las relativas, los adverbios y las frases preposicionales; esos casos ya están cubiertos en la **gramática extendida** para el conjunto de 20 pruebas.
- El backtracking del motor de P1 puede tener costo exponencial en los casos más difíciles; se conserva sin modificar.
- El parser de mini-C de P1 se detiene al detectar el primer error sintáctico.
- **Tarea 4 de P2:** tabla de fallas y análisis formal documentados en este README; 24 pruebas adicionales reproducibles con `pruebas_fallas.py`.
- **Tarea 5 de P2 (28 de octubre):** completada; comparación 22/48/93 y desglose reproducible en `analisis_explosion.py`.
- **Informe (30 de octubre):** compartir con P4 los resultados de las tareas 1–5, las tablas de fallas y la explosión de reglas.
