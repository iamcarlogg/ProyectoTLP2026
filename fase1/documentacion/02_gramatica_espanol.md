# 2. Gramática del español: de la base a la extendida — P2

**Objetivo:** llevar la CFG al español con el mismo motor de P1 y ver qué se puede cubrir. Se hizo en dos etapas para poder comparar: una gramática **base** (tarea 2) y una **extendida** (tarea 3), probadas con las mismas 20 oraciones (tarea 1).

**Archivos:** `gramatica_es.py` (contiene la versión extendida), `pruebas_base.py` (las 20 oraciones), `motor.py` (no se modifica).

## Las 20 oraciones de prueba (tarea 1, 22 oct)

Cubren concordancia de género y número, modificadores, subordinadas relativas y errores o ambigüedades. El mismo conjunto se comparte con P1 (pruebas del parser) y P3 (demo de NLP).

La columna **«Español»** es la corrección lingüística de la oración, que no depende de lo que responda el parser. Las otras dos columnas son las salidas de cada gramática con el mismo motor.

| N.º | Grupo | Oración | Español | Gramática base | Gramática extendida |
| --: | --- | --- | --- | --- | --- |
| 1 | Concordancia | El perro duerme. | Válida | Aceptada | Aceptada |
| 2 | Concordancia | Los perros duermen. | Válida | Aceptada | Aceptada |
| 3 | Concordancia | Las gatas duermen. | Válida | Aceptada | Aceptada |
| 4 | Concordancia | El perro negro duerme. | Válida | Aceptada | Aceptada |
| 5 | Concordancia | La gata negra duerme. | Válida | Aceptada | Aceptada |
| 6 | Concordancia | Los perros negros duermen. | Válida | Aceptada | Aceptada |
| 7 | Concordancia | Las gatas negras duermen. | Válida | Aceptada | Aceptada |
| 8 | Modificadores | El perro come la carne. | Válida | Aceptada | Aceptada |
| 9 | Modificadores | La gata come lentamente. | Válida | Rechazada | Aceptada |
| 10 | Modificadores | El perro duerme en la casa. | Válida | Rechazada | Aceptada |
| 11 | Modificadores | Los perros negros comen rápidamente en el jardín. | Válida | Rechazada | Aceptada |
| 12 | Subordinadas | El perro que come duerme. | Válida | Rechazada | Aceptada |
| 13 | Subordinadas | La gata que duerme come la carne. | Válida | Rechazada | Aceptada |
| 14 | Subordinadas | Los perros que comen duermen en la casa. | Válida | Rechazada | Aceptada |
| 15 | Subordinadas | El perro que la gata persigue duerme. | Válida | Rechazada | Aceptada |
| 16 | Errores y ambigüedad | La perro come. | Inválida | Aceptada | Rechazada |
| 17 | Errores y ambigüedad | El perro negra duerme. | Inválida | Aceptada | Rechazada |
| 18 | Errores y ambigüedad | El perro duermen. | Inválida | Aceptada | Rechazada |
| 19 | Errores y ambigüedad | El perro que come la carne duermen. | Inválida | Rechazada | Rechazada |
| 20 | Errores y ambigüedad | El perro come la carne en la casa. | Válida; ambigua | Rechazada | Aceptada (2 árboles) |

**Qué mide cada grupo:**

- **Concordancia (1–7):** número en sujeto y verbo, y género/número entre determinante, sustantivo y adjetivo.
- **Modificadores (8–11):** objetos directos, adjetivos, adverbios y frases preposicionales.
- **Subordinadas (12–15):** relativas con «que»; la 15 es una relativa donde «el perro» funciona como objeto de «persigue».
- **Errores y ambigüedad (16–20):** desacuerdo determinante-sustantivo, sustantivo-adjetivo y sujeto-verbo, incluso con una cláusula en medio; la 20 admite dos estructuras para «en la casa».

## Etapa 1: gramática base (tarea 2, 24 oct)

Primera CFG: comprueba solo **el orden de las categorías**, no la concordancia. No tiene subordinadas, adverbios ni frases preposicionales. Ya no está en `gramatica_es.py`; se conserva como instantánea en `analisis_explosion.py` (`GRAMATICA_BASE`) para poder compararla.

```text
oracion → sn sv
sn      → det n | det n adj
sv      → v | v sn
det     → 'el' | 'la' | 'los' | 'las'
n       → 'perro' | 'perros' | 'gata' | 'gatas' | 'carne'
adj     → 'negro' | 'negros' | 'negra' | 'negras'
v       → 'come' | 'comen' | 'duerme' | 'duermen'
```

- `oracion → sn sv`: una oración tiene sujeto y predicado.
- `sn → det n | det n adj`: el grupo nominal tiene determinante y sustantivo, con adjetivo opcional.
- `sv → v | v sn`: el predicado es un verbo solo o un verbo con objeto directo.
- `det`, `n`, `adj`, `v`: el vocabulario disponible.

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

**Resultado: 9/20.** Acepta las inválidas 16–18 porque no controla la concordancia. Rechaza las válidas 9–15 y 20 porque faltan construcciones, **no porque una CFG sea incapaz de representarlas**. La 19 se rechaza, pero no por detectar la concordancia: la base rechaza cualquier oración con «que».

## Etapa 2: gramática extendida (tarea 3, 26 oct)

Es el contenido actual de `gramatica_es.py`. Mantiene la interfaz de P1 (`GRAMATICA`, `INICIAL = "oracion"`, minúsculas, sin recursión por la izquierda) y no modifica `motor.py` ni `lexer.py`.

### Qué agrega

1. **Concordancia de género y número dentro del SN:** `det_ms`, `n_ms`, `adj_ms` (y sus versiones `_fs`, `_mp`, `_fp`) impiden «la perro» o «perro negra».
2. **Concordancia sujeto-verbo:** `oracion → sn_ms sv_s | sn_fs sv_s | sn_mp sv_p | sn_fp sv_p` obliga al número correcto, incluso con una subordinada en medio.
3. **Relativas de sujeto y de objeto:** `rel_suj_s`, `rel_suj_p` y `rel_obj` permiten «el perro que come duerme» y «el perro que la gata persigue duerme».
4. **Modificadores:** adjetivos (`adj_*`), adverbios (`adv`) y sintagmas preposicionales (`sp → p sn`).

### Producciones

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

sp  → p sn
p   → 'en'
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

`vt_s` y `vt_p` son verbos transitivos. En las relativas de objeto falta el objeto por diseño («que la gata persigue ___»). No se hace análisis semántico: aceptar una oración solo significa que se puede derivar con estas reglas.

### Resultado: 20/20

| Medida | Base (tarea 2) | Extendida (tarea 3) |
| --- | ---: | ---: |
| Oraciones correctas aceptadas | 8 | 16 |
| Correctas rechazadas (falsos negativos) | 8 | 0 |
| Incorrectas aceptadas (falsos positivos) | 3 | 0 |
| Incorrectas rechazadas | 1 | 4 |
| **Clasificaciones acertadas** | **9/20** | **20/20** |
| Producciones | 22 | 93 |
| No terminales | 7 | 34 |

Qué cambio arregló cada una de las 11 discrepancias de la base:

| Oración | Base | Motivo | Solución en la extendida |
| --- | --- | --- | --- |
| 9 | Rechazada (mal) | `sv` no admitía adverbios. | `sv_s → v_s adv` |
| 10 | Rechazada (mal) | No existía `sp`. | `sv_s → v_s sp`; `sp → p sn` |
| 11 | Rechazada (mal) | Faltaban adverbio y frase preposicional juntos. | `sv_p → v_p adv sp` |
| 12 y 13 | Rechazadas (mal) | No existían relativas. | `rel_suj_s` |
| 14 | Rechazada (mal) | Faltaban relativa plural y frase preposicional. | `rel_suj_p` y `sp` |
| 15 | Rechazada (mal) | No existía relativa de objeto. | `rel_obj` |
| 16 | Aceptada (mal) | `sn → det n` no diferenciaba género. | `det_fs` y `n_ms` ya no se combinan |
| 17 | Aceptada (mal) | `sn → det n adj` no diferenciaba género. | `mod_ms` solo admite `adj_ms` |
| 18 | Aceptada (mal) | `oracion → sn sv` no imponía número. | `oracion → sn_ms sv_s` |
| 20 | Rechazada (mal) | Sin `sp` no cabía «en la casa». | `sp` dentro del SN o del SV |

La 19 se rechaza en las dos versiones, pero **solo en la extendida** el rechazo se debe a la concordancia del verbo principal.

### Ambigüedad

```python
from motor import todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL

arboles = todos_los_arboles("El perro come la carne en la casa.", GRAMATICA, INICIAL)
print(len(arboles))  # 2: el SP se adjunta al verbo o al SN objeto
```

Dos árboles no es un error ni prueba que la CFG no alcance: son dos derivaciones válidas en la gramática diseñada (¿come en la casa, o come la carne que está en la casa?).

### Precaución

20/20 no significa que la gramática cubra el español: el set es pequeño y controlado. El aumento de 22 a 93 producciones muestra el costo de modelar variantes, pero **por sí solo no demuestra que el español no sea libre de contexto**. Eso se analiza en los documentos 3 y 4.
