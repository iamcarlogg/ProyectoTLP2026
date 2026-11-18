# 3. spaCy, NLTK y evaluación — P3

Este documento cubre la parte de P3 en la Fase 2. Es el material para las secciones del informe de **metodología** (spaCy, NLTK y el cálculo de métricas), **resultados** y **análisis de errores** de las dos herramientas de NLP.

| Archivo | Qué hace | Salida |
| --- | --- | --- |
| `correr_spacy.py` | Corre spaCy sobre el corpus | `logs/spacy.json` |
| `correr_nltk.py` | Entrena un etiquetador NLTK con `cess_esp` y lo corre sobre el corpus | `logs/nltk.json` |
| `evaluar.py` | Lee el corpus y los logs y calcula todas las métricas | `resultados/` (3 CSV, `tablas.md`, 2 PNG) |

```bash
python fase2/correr_spacy.py
python fase2/correr_nltk.py      # la primera vez descarga cess_esp (unos 2 MB)
python fase2/evaluar.py          # después de que estén los logs del parser y del LLM
```

## 1. Metodología: spaCy

| Parámetro | Valor |
| --- | --- |
| Librería | spaCy 3.8.18 |
| Modelo | `es_core_news_md` 3.8.0 (red neuronal entrenada con noticias en español; categorías, rasgos y dependencias) |
| Entrada | La oración tal como está en el corpus, con mayúscula inicial y punto |
| Criterio de rechazo | Error de concordancia en los rasgos de spaCy: función `errores_concordancia()` de `fase1/tabla_nlp.py`, **la misma de la Fase 1** (se importa, no se copia) |
| Log | Por oración: `salida`, `errores_concordancia`, categoría (`pos`), rasgos (`morph`), relación (`dep`) y cabeza de cada palabra, raíz, tiempo y `timestamp` |

spaCy nunca rechaza una oración por sí mismo. La regla lo hace «rechazar» cuando sus propios rasgos se contradicen:

1. **Grupo nominal:** el sustantivo, su determinante (`det`) y sus adjetivos (`amod`) deben tener el mismo género y número.
2. **Sujeto y verbo:** el sujeto (`nsubj`) y su verbo deben tener el mismo número.

## 2. Metodología: NLTK

NLTK no trae un modelo de español listo. Hay que **entrenar** un etiquetador.

| Parámetro | Valor |
| --- | --- |
| Librería | NLTK 3.10.3 |
| Datos de entrenamiento | `cess_esp`: 6 030 oraciones y 188 802 palabras de prensa en español, etiquetadas a mano con el sistema **EAGLES** |
| Etiquetador | En cadena (*backoff*): `BigramTagger` → `UnigramTagger` → `RegexpTagger` de sufijos |
| Exactitud del etiquetador | **86,2 %**, entrenado con el 90 % inicial de `cess_esp` y probado con el 10 % final. La división es fija, así que el número no cambia entre corridas |
| Etiquetador del experimento | Entrenado con el 100 % de `cess_esp` |
| Entrada | La oración en minúscula y sin signos de puntuación, igual que el entrenamiento |
| Criterio de rechazo | Error de concordancia de género o número entre **palabras vecinas** (ver abajo) |
| Log | Por oración: `salida`, `errores_concordancia`, etiqueta EAGLES de cada palabra y si la palabra aparece en `cess_esp` (`conocida`) |

**Cómo funciona el etiquetador en cadena.** Para cada palabra se prueba primero el modelo de bigramas: la etiqueta más frecuente de esa palabra después de la etiqueta anterior. Si no la conoce, pasa al de unigramas, con la etiqueta más frecuente de la palabra sola. Si la palabra nunca apareció en `cess_esp`, se aplican reglas de sufijos del español: `-mente` → adverbio, `-ieron/-aron` → verbo pasado plural, `-ó` → verbo pasado singular, `-an/-en` → verbo presente plural, `-as/-os/-a` → sustantivo con su género y número.

**Etiquetas EAGLES.** El género y el número vienen dentro de la etiqueta. Por ejemplo, `da0ms0` es un **d**eterminante **a**rtículo **m**asculino **s**ingular, y `vmip3p0` es un **v**erbo principal en **i**ndicativo **p**resente, **3**.ª persona **p**lural.

**Palabras del corpus que no están en `cess_esp` (11):** comen, duermen, duermo, durmieron, durmió, gata, gatas, nosotras, persiguen, persiguieron, persiguió. Se etiquetaron con las reglas de sufijos.

**Criterio de rechazo.** NLTK solo da etiquetas, sin árbol de dependencias, así que las relaciones entre palabras se deciden por su posición:

1. **Grupo nominal:** determinante + sustantivo + los adjetivos que lo siguen, con el mismo género y número.
2. **Relativas:** desde cada «que» hasta el primer verbo que le sigue. El sujeto de la relativa es el grupo nominal que está dentro («que *la gata* persigue»); si no hay ninguno, es el antecedente («*el perro* que come»). Ese sujeto debe concordar en número con el verbo de la relativa.
3. **Sujeto principal:** el primer grupo nominal debe concordar en número con el primer verbo que no está dentro de una relativa. Un sujeto «X y Y» cuenta como plural.

## 3. Metodología: evaluación (`evaluar.py`)

### Clasificación de cada respuesta

La respuesta correcta es la columna `esperado` del corpus, que indica si la oración es correcta **en español**. La clase positiva es *acepta*.

| | El enfoque acepta | El enfoque rechaza |
| --- | --- | --- |
| **Correcta en español** | VP (verdadero positivo) | FN (falso negativo) |
| **Incorrecta en español** | FP (falso positivo) | VN (verdadero negativo) |

Una respuesta `invalida` (el LLM no respondió en el formato pedido) siempre cuenta como error: FN si la oración era correcta y FP si era incorrecta.

### Métricas

| Métrica | Fórmula | Qué mide |
| --- | --- | --- |
| Precisión | VP / (VP + FP) | De lo que aceptó, cuánto era realmente correcto |
| Cobertura (recall) | VP / (VP + FN) | De las oraciones correctas, cuántas aceptó |
| Tasa de rechazo correcto | VN / (VN + FP) | De las oraciones incorrectas, cuántas rechazó |
| Exactitud | (VP + VN) / total | Aciertos totales |

### Errores de etiquetado

Cada enfoque etiqueta con su propio sistema, así que todo se traduce a categorías comunes:

| Categoría | Nuestra gramática | spaCy (UD) | NLTK (EAGLES) |
| --- | --- | --- | --- |
| det | `det_*` | `DET` | `d…` |
| n | `n_*` | `NOUN` | `nc…` |
| n_propio | — | `PROPN` | `np…` |
| pron | `pron_*` | `PRON` | `p…` |
| v | `v_*`, `vt_*` | `VERB`, `AUX` | `v…` |
| adj | `adj_*` | `ADJ` | `a…` |
| adv | `adv`, `negacion` | `ADV` | `r…` |
| p | `p` | `ADP` | `s…` |
| conj | «y» | `CCONJ`, `SCONJ` | `c…` |
| que | «que» | «que» | «que» |

- **Categorías esperadas:** salen del `arbol_esperado` que P2 escribió en el corpus. Por ejemplo, `(det_ms el)` significa que *el* es `det`.
- **Error de etiquetado:** el enfoque **aceptó bien** la oración (VP), pero al menos una palabra quedó con una categoría distinta de la esperada.
- `n_propio` es una categoría aparte a propósito: que spaCy tome «perro» por nombre propio es un error de etiquetado.
- Para el parser y el LLM, que entregan árbol, también se cuenta si el árbol completo es distinto de `arbol_esperado`.

### Controles

- **Corpus correcto:** si un log tiene otra cantidad de oraciones o un texto distinto del corpus, `evaluar.py` se detiene con un error. Así se evita mezclar corridas de corpus distintos.
- **Logs pendientes:** un log que todavía no existe se marca como pendiente y no detiene la evaluación.
- **Reproducibilidad:** no hay azar. Corriendo dos veces con las mismas entradas, los seis archivos de `resultados/` salen idénticos, byte a byte.
- **`detalle.csv`:** tiene una fila por oración con la salida, el tipo (VP, FN, FP, VN) y el error de etiquetado de cada enfoque. Sirve para responder qué pasó en cualquier oración concreta.

## 4. Resultados (parser, spaCy y NLTK)

> Las columnas del LLM se agregan solas cuando P4 deje `logs/llm_zero_shot.json` y `logs/llm_few_shot.json` y se vuelva a correr `evaluar.py`. Las cifras finales están siempre en `resultados/tablas.md`.

Corpus: 60 oraciones (40 correctas y 20 incorrectas), 20 por nivel.

| Métrica | Parser (CFG) | spaCy | NLTK |
| --- | --- | --- | --- |
| Exactitud | 93,3 % | 88,3 % | 96,7 % |
| Precisión | 100,0 % | 86,7 % | 95,2 % |
| Cobertura (recall) | 90,0 % | 97,5 % | 100,0 % |
| Tasa de rechazo correcto | 100,0 % | 70,0 % | 90,0 % |

| Tipo | Parser (CFG) | spaCy | NLTK |
| --- | --- | --- | --- |
| Verdaderos positivos | 36 | 39 | 40 |
| Verdaderos negativos | 20 | 14 | 18 |
| Falsos positivos | 0 | 6 | 2 |
| Falsos negativos | 4 | 1 | 0 |
| Errores de etiquetado (de los VP) | 0 | 16 | 3 |

| Nivel | Parser (CFG) | spaCy | NLTK |
| --- | --- | --- | --- |
| 1 — simples | 20/20 | 18/20 | 20/20 |
| 2 — intermedias | 20/20 | 20/20 | 20/20 |
| 3 — complejas | 16/20 | 15/20 | 18/20 |

Gráficas: `resultados/metricas.png` (precisión, cobertura y rechazo correcto por enfoque) y `resultados/aciertos_por_nivel.png`.

## 5. Análisis de errores

### spaCy: 7 errores de clasificación y 16 de etiquetado

| Id | Oración | Tipo | Causa |
| --: | --- | --- | --- |
| 15 | La perro duerme. | FP | Toma «perro» por nombre propio (`PROPN`), sin género: no hay nada que comparar con «La» |
| 17 | Los perro duermen. | FP | La misma causa: «perro» sin rasgos |
| 56 | El perro negro que comen duerme. | FP | En la relativa, el sujeto de «comen» es «que», que no tiene número; la regla no puede compararlo con el antecedente |
| 57 | El perro que la gata persigue duermen. | FP | El error está lejos: el sujeto y el verbo principal están separados por la relativa, y spaCy no los relaciona como sujeto y verbo |
| 59 | El perro que la gata persigue negra duerme. | FP | El adjetivo está lejos del sustantivo al que debería modificar; spaCy no lo cuelga de «perro» |
| 60 | El perro come la carne duermen. | FP | «perro» sin rasgos, y dos verbos sin conjunción |
| 49 | El perro y la gata duermen. | FN | **Error de la regla, no de spaCy:** solo mira «perro» como sujeto y no suma «y la gata» |

- **Patrón 1, nombre propio:** spaCy etiqueta «perro» como `PROPN` en 18 oraciones. Con mayúscula inicial y sin contexto, el modelo cree que «El perro» es un nombre como «El Salvador». Es la causa de 2 FP y de la mayoría de los 16 errores de etiquetado. También marca como `PROPN` a «come» y «duerme» en oraciones muy cortas.
- **Patrón 2, concordancia a distancia:** 4 de los 6 FP están en el nivel 3, con una relativa o un adjetivo entre las palabras que deben concordar. Es justo el fenómeno que el docente pidió poner a prueba.
- **Patrón 3, estructura:** spaCy elige un verbo como raíz en 45 de 60 oraciones. En las relativas suele poner el sustantivo como raíz, como ya se vio en la Fase 1.

### NLTK: 2 errores de clasificación y 3 de etiquetado

| Id | Oración | Tipo | Causa |
| --: | --- | --- | --- |
| 59 | El perro que la gata persigue negra duerme. | FP | «negra» queda después del verbo de la relativa; la regla solo une adjetivos pegados al sustantivo |
| 60 | El perro come la carne duermen. | FP | La regla compara el sujeto con el **primer** verbo («come», que concuerda) y no ve el segundo |

Errores de etiquetado, todos en oraciones que acertó:

- **«Yo duermo»**: «duermo» no está en `cess_esp` y la regla de sufijos lo toma por sustantivo, por la terminación en -o.
- **«Yo como la carne»**: «como» aparece 727 veces en `cess_esp`, casi siempre como conjunción («como dijo…»), y el etiquetador elige esa etiqueta.
- **«Nosotras comimos la carne»**: «nosotras» no está en `cess_esp` y se etiqueta como sustantivo femenino plural.

### Comparación con el parser

- **El parser no tiene falsos positivos:** nunca acepta una oración incorrecta (100 % de precisión y de rechazo correcto).
- **Sus 4 errores son falsos negativos del nivel 3:** «El perro y la gata duermen», «come la carne y duerme», «duerme y la gata come» y «no come la carne». Son construcciones que la gramática no cubre, es decir, **límites de cobertura de la CFG**.
- Las herramientas de NLP tienen el perfil opuesto: aceptan casi todo lo correcto (cobertura de 97,5 % y 100 %), pero dejan pasar errores de concordancia a distancia.

## 6. Amenazas a la validez

- **La regla de NLTK es más elaborada que la de spaCy.** Conoce las relativas y la coordinación con «y», y se escribió conociendo el tipo de oraciones del corpus. La de spaCy viene de la Fase 1, antes de que existiera este corpus. El 96,7 % de NLTK mide **etiquetador + reglas escritas a mano**, no solo NLTK.
- **Ni spaCy ni NLTK rechazan por sí mismos.** Sus tasas de rechazo correcto miden nuestra regla de concordancia aplicada a sus análisis, y por eso dependen de cómo se escribió esa regla.
- **Los 20 errores del corpus son todos de concordancia.** Una regla de concordancia está bien adaptada a este corpus; con otro tipo de errores (orden de palabras, verbos que no llevan objeto) el resultado sería distinto.
- **Corpus pequeño:** 60 oraciones con un vocabulario reducido. Un solo error mueve la tasa de rechazo correcto un 5 % (1 de 20).
- **`cess_esp` es prensa:** casi no tiene «gata», «duermen» ni la 1.ª persona, por eso hay 11 palabras desconocidas.