# Fase 2 — Qué hace cada integrante

Entrega: **jueves 19 nov 2026, a más tardar 17:30**, por correo institucional (enlace al repositorio Git + informe en PDF). No hay presentación oral. Alcance completo: [alcance_fase2.md](alcance_fase2.md). Decisiones y qué rehacer: [fase2/documentacion/decisiones_tomadas.md](../fase2/documentacion/decisiones_tomadas.md).

Todo va en `fase2/`, con los logs en `fase2/logs/`. Las fechas son propuestas y hay que confirmarlas con el equipo.

## Acuerdos que hay que cerrar ya (16 nov)

- [x] Segunda herramienta de NLP: **NLTK** (decidido el 15 nov).
- [x] Modelo de LLM (P4, 18 nov): Google, `gemini-3.1-flash-lite`, temperatura solicitada 0, razonamiento MINIMAL, API `v1beta`, `maxOutputTokens=2048`. Conexión verificada y corrida completa: 120 respuestas.
- [x] Formato común de los logs: JSON con `metadatos` y `resultados`; obligatorios `id, oracion, salida, timestamp` (detalle en [decisiones.md](decisiones.md#formato-de-los-logs-fase-2); ejemplo real en `fase2/logs/parser.json`).
- [x] Errores de etiquetado: categorías esperadas sacadas de `arbol_esperado` y una tabla de traducción por enfoque (P3, 17 nov; ver [03_nlp_y_evaluacion.md](../fase2/documentacion/03_nlp_y_evaluacion.md#errores-de-etiquetado)).
- [x] Criterio de acierto de spaCy y NLTK: regla de concordancia (spaCy, la de `tabla_nlp.py`; NLTK, la misma sobre palabras vecinas).

## P1 — Carlo · Parser propio

- [x] **15 nov** — `fase2/correr_parser.py` listo y probado con un corpus provisional (las 44 oraciones de la Fase 1): log en `fase2/logs/parser.json`.
- [x] **17 nov** — Cuando lleguen la gramática y el corpus de P2: volver a correr `python fase2/correr_parser.py` (si la gramática queda en `fase2/gramatica_es.py`, se usa sola). → 60 oraciones, 207 producciones, 56/60. **Subir a Git este `parser.json` nuevo:** el del zip del 16 nov aún es el de 44 oraciones.
- [x] **17 nov** — Sección del informe en [fase2/documentacion/01_parser_propio.md](../fase2/documentacion/01_parser_propio.md): resumen del parser y la CFG (sección 1), metodología (sección 3) y estructura del análisis de errores (sección 5).
- [x] **17 nov** — Completar ese documento con los números de la corrida final y el análisis de errores, y entregarlo a P4.

## P2 — Federico · Gramática y corpus

- [x] **16 nov** — `fase2/corpus.csv` con **40+ oraciones** (quedó con 60: 40 correctas y 20 incorrectas; sin duplicados y sin palabras fuera del vocabulario) y columnas `id, oracion, nivel, esperado, arbol_esperado`:
  - Nivel 1 (simples): la gramática debería aceptarlas sin problema.
  - Nivel 2 (intermedias): modificadores y variaciones dentro de lo que cubre la gramática.
  - Nivel 3 (complejas): concordancia a distancia, subordinadas anidadas, ambigüedad estructural.
  - Incluir **bastantes** oraciones que deban rechazarse (el borrador tiene solo 7 de 44: un fallo mueve la tasa un 14 %).
  - En el nivel 3, usar **palabras que estén en el vocabulario** de la gramática: si falta una palabra, el parser rechaza por `vocabulario` y no se prueba el límite de la CFG. Con el borrador, los 10 falsos negativos son todos por vocabulario y ninguno por estructura.
  - **Sin duplicados:** el borrador repite «El perro come la carne en la casa.» (ids 20 y 39); una oración repetida cuenta doble en las métricas.
  - Hay un borrador en `fase2/corpus.csv` (44 oraciones de la Fase 1, niveles provisionales) para partir de él.
  - Se pueden reutilizar las 20 de `fase1/pruebas_base.py` y las 24 de `fase1/pruebas_fallas.py`.
- [x] **16 nov** — Reglas de producción en texto legible (`fase2/gramatica_es.txt`) para pegarlas en el prompt del LLM; pasárselas a P4.
- [x] **17 nov** — Entregar a P4: descripción del corpus y criterios de selección de cada nivel → [fase2/documentacion/02_corpus.md](../fase2/documentacion/02_corpus.md).

## P3 — Kelvin · NLP y evaluación

- [x] **17 nov** — NLTK: descargar `cess_esp`, entrenar el etiquetador y anotar las versiones exactas de spaCy, su modelo y NLTK.
- [x] **17 nov** — Correr spaCy y NLTK sobre el corpus completo → `fase2/logs/spacy.*` y `fase2/logs/nltk.*`.
- [x] **17 nov** — `fase2/evaluar.py`: lee el corpus y los cinco logs (parser, spaCy, NLTK, LLM zero-shot, LLM few-shot) y calcula para cada uno:
  - precisión, cobertura (recall) y tasa de rechazo correcto;
  - falsos positivos, falsos negativos y errores de etiquetado.
  - Salida: tablas en CSV y **al menos una gráfica** en PNG. Debe ser reproducible: si se corre de nuevo, salen las mismas cifras.
- [x] **17 nov** — Entregar a P4: [fase2/documentacion/03_nlp_y_evaluacion.md](../fase2/documentacion/03_nlp_y_evaluacion.md) (metodología, tablas y análisis de errores) y `fase2/resultados/`. Al llegar los logs del LLM, volver a correr `evaluar.py`.

## P4 — Allan · LLM e informe

- [x] **18 nov** — Dos prompts nuevos con las reglas completas de P2: zero-shot y few-shot con cinco ejemplos externos al corpus; salida JSON fija con veredicto y árbol. Ver `fase2/prompts/` y `fase2/preparar_prompts.py`.
- [x] **18 nov** — `fase2/llm_experimento.py` (**por API, no por el chat**): corre todo el corpus con ambos prompts y guarda en `fase2/logs/llm_zero_shot.*` y `llm_few_shot.*`, por cada llamada, **el prompt exacto, la respuesta completa y el timestamp**.
- [x] **18 nov** — Análisis del LLM: ¿respeta las reglas o se desvía hacia su conocimiento general? (la clave son las oraciones correctas en español que la gramática no acepta), y ¿few-shot mejora frente a zero-shot? → `fase2/documentacion/04_llm.md`; exactitud 90,0 % / 91,7 %, fidelidad CFG 90,0 % / 98,3 %.
- [x] **18 nov** — Informe integrado en `output/pdf/informe_fase2.pdf`: 9 páginas de informe (portada incluida) + 9 de anexos; código y evidencia en `output/pdf/entrega_fase2.zip`:
  1. Parser y CFG (P1) · 2. Corpus (P2) · 3. Metodología (todos) · 4. Resultados (P3) · 5. Análisis de errores (todos; énfasis en el LLM) · 6. Conclusiones con datos.
  - Anexos: corpus, logs de los cuatro enfoques, prompts y respuestas con timestamp, `evaluar.py`.
- [x] **18 nov** — README de `fase2/` actualizado: variable `GEMINI_API_KEY`, ejecución y reproducción desde los cinco logs, sin volver a consultar la API.

## Todos

- [ ] **19 nov antes de las 17:30** — Revisar que el repositorio tenga todos los anexos y que `python fase2/evaluar.py` reproduzca las tablas del PDF. Enviar el correo.
- [ ] **19 nov en clase** — Debe ir al menos un integrante. Cualquiera tiene que poder explicar cómo se generó cada log, qué significa cada celda de las tablas y por qué el LLM respondió como lo hizo en un caso concreto.
