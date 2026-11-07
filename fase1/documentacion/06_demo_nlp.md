# 6. Demo con NLP: nuestra CFG frente a spaCy — P3

**Objetivo:** mostrar qué hace una herramienta moderna de NLP con las mismas oraciones que P2 probó con la CFG: cuáles procesa sin problema aunque rompan nuestra gramática, cuáles analiza mal y qué captura que la CFG no.

**Archivos:**

| Archivo | Qué hace |
| --- | --- |
| `demo_nlp.py` | Carga spaCy y analiza las 20 oraciones de P2: categoría, género, número, relación y raíz de cada palabra. |
| `tabla_nlp.py` | Tabla lado a lado: respuesta correcta, CFG y spaCy, con los aciertos de cada uno. |
| `visualizar_nlp.py` | Genera la página interactiva de la demo con los datos de la CFG y de spaCy. |
| `plantilla_demo.html` | Diseño de esa página (HTML, CSS y JavaScript); `visualizar_nlp.py` la llena con los datos. |

```bash
python fase1/demo_nlp.py              # análisis de las 20 oraciones (--detalle: tabla por palabra)
python fase1/tabla_nlp.py             # tabla de las 20 oraciones
python fase1/tabla_nlp.py --fallas    # tabla de los 24 casos de la tabla de fallas
python fase1/visualizar_nlp.py        # página de la demo (también --todas y --fallas)
```

## 1. La herramienta: spaCy

spaCy es una librería de NLP que analiza texto con **modelos estadísticos**: redes neuronales entrenadas con miles de oraciones reales anotadas a mano. No tiene reglas gramaticales escritas; aprendió patrones de esos ejemplos.

Con una sola línea, `doc = nlp(oracion)`, devuelve para cada palabra:

| Atributo | Qué es | Ejemplo |
| --- | --- | --- |
| `pos_` | Categoría gramatical (etiquetas Universal Dependencies) | `DET`, `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `ADP` |
| `morph` | Rasgos morfológicos | `Gender=Masc`, `Number=Sing` |
| `dep_` | Relación con la palabra de la que depende | `nsubj` sujeto, `obj` objeto, `det`, `amod` adjetivo, `ROOT` |
| `head` | La palabra de la que depende | «negra» depende de «perro» |

### Decisiones de configuración

| Decisión | Motivo |
| --- | --- |
| **Modelo `es_core_news_md`** (mediano) y no `sm` (pequeño) | Con 5 oraciones de prueba, `sm` etiquetó «come» como sustantivo y «duermen» como singular en pasado; `md` acertó en esos casos. |
| **Las oraciones se pasan tal como están escritas**, con mayúscula inicial | spaCy está entrenado con texto normal. Pasarlas en minúscula bajó los errores de nombre propio de 10 a 7, pero no corrigió las relativas, así que no cambia las conclusiones. |
| **Las mismas oraciones que la CFG**, importadas de `pruebas_base.py` y `pruebas_fallas.py` | Si P2 cambia una oración, la comparación se actualiza sola, y los dos enfoques reciben exactamente la misma entrada. |

## 2. Dos tipos de árbol

La comparación no puede ser «¿salió el mismo árbol?», porque cada enfoque produce un tipo de árbol distinto.

| | Nuestra CFG | spaCy |
| --- | --- | --- |
| Tipo de árbol | **Constituyentes**: las palabras se agrupan en frases | **Dependencias**: cada palabra apunta a otra |
| Ejemplo: «El perro duerme» | `(oracion (sn_ms (det_ms el) (n_ms perro) (mod_ms)) (sv_s (v_s duerme)))` | `El →det perro →nsubj duerme (ROOT)` |
| Nodos internos | Sí (`sn_ms`, `sv_s`, …) | No: solo palabras |
| ¿Puede rechazar? | Sí: si ninguna regla genera la oración | **No**: siempre devuelve un análisis |
| Cómo decide | Reglas escritas a mano | Probabilidades aprendidas de textos |

## 3. Criterio de acierto

Como spaCy nunca rechaza, le dimos una regla para que pueda «rechazar»: **la oración tiene un error si los propios rasgos de spaCy muestran un desacuerdo de concordancia.** La función es `errores_concordancia()` en `tabla_nlp.py`:

1. **Dentro del grupo nominal:** el sustantivo, su determinante (`det`) y sus adjetivos (`amod`) deben tener el mismo género y número.
2. **Sujeto y verbo:** el número del sujeto (`nsubj`) debe coincidir con el de su verbo. Si el sujeto no trae número, se toma el de su determinante.
3. Si a una palabra le falta un rasgo, no se compara.

Esta regla **la escribimos nosotros**; no es parte de spaCy. Mide si la información que spaCy produce alcanza para detectar el error.

Un enfoque **acierta** cuando su respuesta coincide con la respuesta correcta en español, que P2 escribió a mano en `pruebas_base.py` (`True`/`False`). Además se revisa una segunda señal: si la **raíz** que elige spaCy es un verbo, como debería ser en todas estas oraciones.

## 4. Resultados

| Medida | 20 oraciones de P2 | 24 casos de fallas |
| --- | ---: | ---: |
| Aciertos de la CFG | **20/20** | 14/24 |
| Aciertos de spaCy (con nuestra regla) | 19/20 | **22/24** |
| spaCy con la raíz en un verbo | 14/20 | 15/24 |
| *Referencia: aceptar todo sin analizar* | *16/20* | *21/24* |

La última fila es un punto de comparación: como la mayoría de las oraciones son correctas, un programa que acepte todo ya saca puntajes altos. Por eso importa **dónde** acierta cada enfoque, no solo cuántas.

### 20 oraciones de P2 (tarea 1)

| N.º | Oración | Correcta | CFG | spaCy | Raíz | Nota |
| --: | --- | --- | --- | --- | --- | --- |
| 1 | El perro duerme. | Sí | ✓ | ✓ | ✗ | spaCy toma «perro» y «duerme» como nombre propio |
| 2–11 | Concordancia y modificadores | Sí | ✓ | ✓ | ✓ | Los dos aciertan |
| 12–15 | Relativas con «que» | Sí | ✓ | ✓ | ✗ | spaCy elige el sustantivo como raíz |
| 16 | La perro come. | No | ✓ | ✗ | ✗ | «perro» como nombre propio, sin género: el error no se ve |
| 17 | El perro negra duerme. | No | ✓ | ✓ | ✓ | Gender: El=Masc / negra=Fem |
| 18 | El perro duermen. | No | ✓ | ✓ | ✓ | sujeto-verbo: perro=Sing / duermen=Plur |
| 19 | El perro que come la carne duermen. | No | ✓ | ✓ | ✓ | sujeto-verbo, con la relativa en medio |
| 20 | El perro come la carne en la casa. | Sí | ✓ (2 árboles) | ✓ | ✓ | spaCy elige una sola lectura |

### 24 casos de la tabla de fallas (tarea 4)

| Casos | Qué pasa |
| --- | --- |
| 3–10 y 20 | **La CFG rechaza oraciones correctas y spaCy las procesa sin problema**: «con», «a la gata», «no», «porque», coordinación, «muy», dos adjetivos, signos de pregunta. Es el objetivo de esta demo. |
| 15 y 16 | Los dos detectan el error de concordancia, incluso dentro de una relativa o con una relativa en medio. |
| 21 | «El perro y la gata duermen»: la CFG la rechaza por falta de reglas y **nuestra regla** marca un error falso, porque solo mira «perro» como sujeto. |
| 24 | «El perro duerme la carne»: la CFG la rechaza (`duerme` no es transitivo); spaCy no sabe qué verbos llevan objeto y la deja pasar. |

## 5. Qué captura spaCy que la CFG no

1. **Cobertura.** spaCy analiza cualquier oración del español, con cualquier vocabulario y estructura. La CFG solo conoce 25 palabras y las construcciones que P2 escribió; cada estructura nueva requiere reglas nuevas, y el documento 4 muestra cuánto cuestan.
2. **Robustez.** Nunca se detiene: incluso una oración incorrecta recibe un análisis completo con rasgos. Eso permite **señalar dónde** está el error (qué palabras no concuerdan), mientras la CFG solo dice «rechazada».
3. **Rasgos explícitos.** Género, número, persona y tiempo vienen como datos (`Gender=Fem`). La CFG los codifica en los nombres de las categorías (`sn_fs`) y por eso las multiplica.

## 6. Qué captura la CFG que spaCy no

1. **Rechazo.** spaCy no distingue una oración correcta de una incorrecta; hace falta una regla externa como la nuestra.
2. **Estructura de las relativas.** En las 4 relativas, spaCy pone el sustantivo como raíz; en «El perro que come duerme» etiqueta «duerme» como adjetivo. La CFG las analiza bien con `rel_suj_s` y `rel_obj`.
3. **Ambigüedad visible.** La CFG devuelve los 2 árboles de la oración 20; spaCy elige uno sin avisar que había otra lectura.
4. **Restricciones del verbo.** La CFG sabe que «dormir» no lleva objeto; spaCy no.
5. **Determinismo.** La CFG da siempre la misma respuesta y se puede explicar regla por regla. spaCy depende de señales superficiales: la mayúscula de «El» le hace tomar «perro» por nombre propio («El Perro»), y eso borra el género que necesitaba para ver el error de la oración 16.

## 7. Visualización para la demo

`visualizar_nlp.py` genera una página web interactiva (`fase1/salidas/`), sin necesidad de internet:

- **Árbol de la CFG:** nodos con colores por tipo de constituyente, zoom y desplazamiento, y un selector entre los árboles cuando la oración es ambigua.
- **Árbol de spaCy:** las flechas de dependencias, con la raíz marcada y las palabras con error de concordancia en rojo. Los datos vienen de `displacy.parse_deps()`, la misma función que usa displacy para dibujar; se dibujan con el mismo estilo que la CFG.
- **Resultado:** tarjetas con la respuesta correcta y lo que dijo cada enfoque, con el aviso de si coincide.
- **Panel de detalles:** al hacer clic en un nodo de la CFG muestra la regla aplicada y todas sus alternativas en la gramática; al hacer clic en una palabra de spaCy muestra sus rasgos y su relación.

| Comando | Página | Para qué |
| --- | --- | --- |
| `python fase1/visualizar_nlp.py` | `demo_nlp.html` | Las 5 oraciones de la presentación |
| `python fase1/visualizar_nlp.py --todas` | `demo_nlp_todas.html` | Las 20 oraciones de P2 |
| `python fase1/visualizar_nlp.py --fallas` | `demo_nlp_fallas.html` | Los 24 casos de la tabla de fallas |

### Las 5 oraciones de la presentación

| N.º | Oración | Qué muestra |
| --: | --- | --- |
| 1 | El perro negra duerme. | La CFG rechaza; spaCy analiza, pero sus rasgos delatan el error. |
| 2 | La perro come. | El error que spaCy no ve (nombre propio sin género). |
| 3 | El perro que come duerme. | La CFG entiende la relativa; spaCy elige mal la raíz. |
| 4 | El perro no duerme. | La CFG se rompe por una regla que falta; spaCy no. |
| 5 | El perro come la carne en la casa. | La CFG muestra la ambigüedad; spaCy la esconde. |

## 8. Limitaciones

- **Set pequeño y controlado:** 44 oraciones con 25 palabras. Los porcentajes no se pueden generalizar al español real.
- **La regla de concordancia es nuestra:** falla con sujetos coordinados (caso 21) y depende de que spaCy asigne los rasgos.
- **Un solo modelo de una sola herramienta.** La Fase 2 agrega HuggingFace y métricas formales (precisión, recall, tasa de rechazo correcto).
- **Sin análisis semántico en ninguno de los dos:** «La carne negra duerme» pasa en ambos.

## Conclusión

La CFG es **exacta pero rígida**: dentro de su gramática no se equivoca, detecta errores y muestra la ambigüedad, pero cualquier palabra o estructura nueva la rompe. spaCy es **flexible pero aproximado**: procesa todo, incluidas las 9 oraciones correctas que la CFG rechaza, pero nunca rechaza por sí mismo y se equivoca en la estructura de las relativas y con señales superficiales como una mayúscula.

Esto se conecta con el documento 5: la CFG no falla aquí por un límite de la jerarquía de Chomsky, sino por **cobertura**, porque escribir reglas para todo el español es inviable a mano. Los modelos estadísticos resuelven la cobertura aprendiendo de datos, a cambio de perder las garantías de una gramática formal.

---

← Anterior: [5. Dónde sí falla una CFG](05_donde_si_falla_la_cfg.md) · [Índice de la Fase 1](../README.md) · Siguiente: [informe final](../../informe/informe_fase1.pdf) →
