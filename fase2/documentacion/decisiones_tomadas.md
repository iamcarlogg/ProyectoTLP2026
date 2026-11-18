# Fase 2 — Decisiones tomadas y qué debe rehacer cada integrante

Creado: 15 nov 2026 · @Carlo (P1) · Actualizado: 17 nov 2026 (P3: pendientes resueltos y avance de cada integrante)

Resumen para el equipo de lo que ya se decidió en la Fase 2 y de lo que cada uno debe hacer o rehacer para que su parte encaje. El detalle está en [docs/decisiones.md](../../docs/decisiones.md); el alcance del docente, en [docs/alcance_fase2.md](../../docs/alcance_fase2.md); las fechas, en [docs/tareas_fase2.md](../../docs/tareas_fase2.md).

## Decisiones tomadas

| # | Decisión | Por qué |
| --- | --- | --- |
| 1 | **Cuatro enfoques:** parser propio, spaCy, **NLTK** y un LLM por API (zero-shot y few-shot). | Lo pide el docente; NLTK porque ya está instalado y sus etiquetas EAGLES traen género y número, así que permite el mismo criterio de concordancia que spaCy. |
| 2 | **El LLM se usa por API, no por el chat.** Modelo y proveedor los elige P4. | El docente pide cada llamada con prompt exacto, respuesta completa y timestamp; desde el chat no se puede demostrar. |
| 3 | **Corpus en `fase2/corpus.csv`** con columnas `id, oracion, nivel, esperado, arbol_esperado`. | Formato acordado en la Fase 1; todos los scripts lo leen. |
| 4 | **`esperado` = si la oración es correcta en español**, no si la gramática la acepta. | Es la vara de medir: si el parser rechaza una oración correcta, es un falso negativo (límite de la CFG). |
| 5 | **Un log JSON por enfoque** en `fase2/logs/`, con `metadatos` y `resultados`. | `evaluar.py` lee los cinco igual; los metadatos sirven para la metodología. |
| 6 | **Campos obligatorios en cada resultado:** `id`, `oracion`, `salida`, `timestamp`. | Es lo mínimo para calcular las métricas y demostrar cuándo se corrió. |
| 7 | **`salida` vale `acepta`, `rechaza` o `invalida`** (`invalida` = el LLM no respondió en el formato pedido; cuenta como error). | Evita que una respuesta rara rompa la evaluación o se cuente a favor. |
| 8 | **El parser guarda el primer árbol y `n_arboles`.** | `n_arboles > 1` mide la ambigüedad estructural con datos. |
| 9 | **El parser guarda el `motivo` del rechazo:** `vocabulario`, `estructura` o `error`. | Distingue «le falta una palabra» (no es límite de la CFG) de «ninguna regla la arma» (sí lo es). |
| 10 | **Los signos `¿?¡!` no se normalizan.** | Coherente con la Fase 1; esas oraciones se rechazan por `vocabulario` y así se explica en el análisis. |
| 11 | **La Fase 2 usa el motor de `fase1/`** (no se copia). Si P2 deja su gramática en `fase2/gramatica_es.py`, se usa esa sola. | Un solo motor; cambiar la gramática no exige tocar código. |
| 12 | **Los logs se escriben con `ensure_ascii=False`.** | Tildes y ñ legibles en los anexos. |
| 13 | **Concordancia:** la gramática nueva sigue duplicando no terminales (`sn_ms`, `sv_s_pret`…). | Sigue siendo una CFG pura; el costo (207 producciones) se analiza en el informe. |
| 14 | **spaCy y NLTK «rechazan» con la regla de concordancia:** spaCy con la de `fase1/tabla_nlp.py`; NLTK con la misma sobre palabras vecinas. | Ninguna de las dos herramientas rechaza por sí sola. |
| 15 | **Errores de etiquetado = categorías por palabra**, sacadas de `arbol_esperado` y traducidas a categorías comunes en `evaluar.py`. | Los cuatro enfoques se miden igual sin que P2 anote nada extra. |
| 16 | **La documentación de cada rol va en `fase2/documentacion/`**, numerada: `01_parser_propio`, `02_corpus`, `03_nlp_y_evaluacion`, `04_llm`. | Mismo orden que la Fase 1 y que el informe. |

Formato del log, con un ejemplo real del parser:

```json
{
  "metadatos": {"enfoque": "parser", "fecha": "2026-11-15T19:41:31", "python": "3.14.5",
                "nltk": "3.10.3", "gramatica": "fase1/gramatica_es.py", "reglas": 93,
                "vocabulario": 25, "corpus": "fase2/corpus.csv", "oraciones": 44},
  "resultados": [
    {"id": 23, "oracion": "El perro duerme con la gata.", "salida": "rechaza",
     "motivo": "vocabulario", "arbol": null, "n_arboles": 0,
     "palabras_desconocidas": ["con"], "tiempo_ms": 0.022, "error": null,
     "timestamp": "2026-11-15T19:41:31"}
  ]
}
```

## Pendientes de decidir

- [x] **Errores de etiquetado** (P3, 17 nov): decisión 15. Detalle en [03_nlp_y_evaluacion.md](03_nlp_y_evaluacion.md#errores-de-etiquetado).
- [x] **Criterio de acierto de NLTK** (P3, 17 nov): decisión 14.
- [ ] **Criterio de acierto del LLM** (P4): lo que responda en el formato pedido; si no lo respeta, `invalida`.
- [x] **Concordancia en la gramática nueva** (P2): decisión 13.

## Qué debe hacer o rehacer cada integrante

### P2 — Federico · Gramática y corpus

- [x] **Rehacer el corpus** (60 oraciones; ver [02_corpus.md](02_corpus.md)) partiendo del borrador `fase2/corpus.csv` (hoy tiene las 44 oraciones de la Fase 1 con niveles provisionales):
  - Revisar el `nivel` de cada oración; el borrador lo asignó por largo.
  - **Agregar oraciones incorrectas:** hoy hay 7 de 44, y con tan pocas un solo fallo mueve la tasa de rechazo correcto un 14 %.
  - **Nivel 3 con palabras del vocabulario:** concordancia a distancia, subordinadas anidadas, ambigüedad. Con el borrador, los 10 falsos negativos del parser son por palabras que faltan y ninguno por estructura, así que no prueban el límite de la CFG.
  - Llenar `arbol_esperado` cuando aplique, en la notación de corchetes del motor.
- [x] **Gramática final** en `fase2/gramatica_es.py`, con las mismas variables `GRAMATICA` e `INICIAL` y las reglas del motor (minúsculas, sin recursión por la izquierda).
- [x] **Reglas en texto** (`fase2/gramatica_es.txt`) para el prompt del LLM; pasarlas a P4.
- [x] **Avisar a P1** cuando el corpus y la gramática estén listos: el parser se vuelve a correr con un comando.

### P3 — Kelvin · NLP y evaluación

- [x] **Rehacer la corrida de spaCy** sobre `fase2/corpus.csv` (la de la Fase 1 era sobre otras oraciones) y guardarla en `fase2/logs/spacy.json` **con el formato común**: metadatos (versión de spaCy y del modelo) y, por oración, como mínimo `id, oracion, salida, timestamp`.
- [x] **NLTK:** descargar `cess_esp`, entrenar el etiquetador y aplicar el criterio de rechazo acordado → `fase2/logs/nltk.json`, en el mismo formato.
- [x] **`fase2/evaluar.py`:** lee el corpus y los cinco logs, cruza por `id` y calcula precisión, cobertura, tasa de rechazo correcto, falsos positivos, falsos negativos y errores de etiquetado. Trata `invalida` como error. Salida: tablas en CSV y al menos una gráfica PNG. Documentado en [03_nlp_y_evaluacion.md](03_nlp_y_evaluacion.md).

### P4 — Allan · LLM e informe

- [ ] **`fase2/llm_experimento.py` por API**, con la clave en una variable de entorno (nunca en el repositorio).
- [ ] **Dos logs, `llm_zero_shot.json` y `llm_few_shot.json`, con el formato común.** En `metadatos`: proveedor, ID exacto del modelo y parámetros. En cada resultado, además de los obligatorios: `prompt` y `respuesta_completa`. Si la respuesta no se puede interpretar, `salida = "invalida"`.
- [ ] **Una llamada por oración**, con el mismo prompt base, para que las respuestas no se influyan entre sí.
- [x] **README de `fase2/`** con los pasos para reproducir todo: [fase2/README.md](../README.md). Falta agregar los detalles del LLM (variable de entorno de la clave).
- [ ] **`04_llm.md`** en esta carpeta: prompts exactos, modelo, parámetros y análisis.

### P1 — Carlo · Parser propio

- [x] `fase2/correr_parser.py` listo y probado con el borrador (log en `fase2/logs/parser.json`).
- [x] Volver a correrlo cuando lleguen la gramática y el corpus finales (17 nov: 56/60).
- [x] Sección del informe: resumen del parser y de la CFG (máximo 1 página) y análisis de sus errores → [01_parser_propio.md](01_parser_propio.md).

## Orden para rehacer la corrida completa

Cuando el corpus y la gramática estén finales, se rehace todo en este orden, desde la raíz del repositorio. Si cambia el corpus, **hay que volver a correr los cinco logs**: un log de un corpus viejo no es comparable.

```bash
python fase2/correr_parser.py      # P1 → fase2/logs/parser.json
python fase2/correr_spacy.py       # P3 → fase2/logs/spacy.json
python fase2/correr_nltk.py        # P3 → fase2/logs/nltk.json
python fase2/llm_experimento.py    # P4 → fase2/logs/llm_*.json      (cuesta dinero: correr una vez)
python fase2/evaluar.py            # P3 → tablas y gráfica
```

Antes de entregar, comprobar que los metadatos de los cinco logs apuntan al mismo `corpus` con el mismo número de `oraciones`.