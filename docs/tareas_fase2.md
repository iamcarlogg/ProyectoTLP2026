# Fase 2 — Qué hace cada integrante

Entrega: **jueves 19 nov 2026, a más tardar 17:30**, por correo institucional (enlace al repositorio Git + informe en PDF). No hay presentación oral. Alcance completo: [alcance_fase2.md](alcance_fase2.md). Decisiones y qué rehacer: [fase2/decisiones_tomadas.md](../fase2/decisiones_tomadas.md).

Todo va en `fase2/`, con los logs en `fase2/logs/`. Las fechas son propuestas y hay que confirmarlas con el equipo.

## Acuerdos que hay que cerrar ya (16 nov)

- [x] Segunda herramienta de NLP: **NLTK** (decidido el 15 nov).
- [ ] Modelo de LLM: **lo elige P4** (proveedor y modelo libres, siempre por API). Debe anotar el ID exacto del modelo y los parámetros usados para la metodología.
- [x] Formato común de los logs: JSON con `metadatos` y `resultados`; obligatorios `id, oracion, salida, timestamp` (detalle en [decisiones.md](decisiones.md#formato-de-los-logs-fase-2); ejemplo real en `fase2/logs/parser.json`).
- [ ] Errores de etiquetado: cómo se miden si cada enfoque usa etiquetas distintas (P2 y P3; hay una recomendación en [decisiones.md](decisiones.md#formato-de-los-logs-fase-2)).
- [ ] Criterio de acierto para cada enfoque, sobre todo para spaCy y NLTK, que no «rechazan» por sí solos (la Fase 1 usó la regla de concordancia de `tabla_nlp.py`).

## P1 — Carlo · Parser propio

- [x] **15 nov** — `fase2/correr_parser.py` listo y probado con un corpus provisional (las 44 oraciones de la Fase 1): log en `fase2/logs/parser.json`.
- [ ] **16–17 nov** — Cuando lleguen la gramática y el corpus de P2: volver a correr `python fase2/correr_parser.py` (si la gramática queda en `fase2/gramatica_es.py`, se usa sola).
- [ ] **18 nov** — Entregar a P4: resumen del parser y la CFG (máximo 1 página, sin repetir la Fase 1) y el análisis de los errores del parser (qué rechaza y por qué).
- [ ] Sección de metodología del parser: cómo se corre y la versión de Python y NLTK.

## P2 — Federico · Gramática y corpus

- [ ] **16 nov** — `fase2/corpus.csv` con **40+ oraciones** y columnas `id, oracion, nivel, esperado, arbol_esperado`:
  - Nivel 1 (simples): la gramática debería aceptarlas sin problema.
  - Nivel 2 (intermedias): modificadores y variaciones dentro de lo que cubre la gramática.
  - Nivel 3 (complejas): concordancia a distancia, subordinadas anidadas, ambigüedad estructural.
  - Incluir **bastantes** oraciones que deban rechazarse (el borrador tiene solo 7 de 44: un fallo mueve la tasa un 14 %).
  - En el nivel 3, usar **palabras que estén en el vocabulario** de la gramática: si falta una palabra, el parser rechaza por `vocabulario` y no se prueba el límite de la CFG. Con el borrador, los 10 falsos negativos son todos por vocabulario y ninguno por estructura.
  - Hay un borrador en `fase2/corpus.csv` (44 oraciones de la Fase 1, niveles provisionales) para partir de él.
  - Se pueden reutilizar las 20 de `fase1/pruebas_base.py` y las 24 de `fase1/pruebas_fallas.py`.
- [ ] **16 nov** — Reglas de producción en texto legible (`fase2/gramatica_es.txt`) para pegarlas en el prompt del LLM; pasárselas a P4.
- [ ] **18 nov** — Entregar a P4: descripción del corpus y criterios de selección de cada nivel.

## P3 — Kelvin · NLP y evaluación

- [ ] **16 nov** — NLTK: descargar `cess_esp`, entrenar el etiquetador y anotar las versiones exactas de spaCy, su modelo y NLTK.
- [ ] **17 nov** — Correr spaCy y NLTK sobre el corpus completo → `fase2/logs/spacy.*` y `fase2/logs/nltk.*`.
- [ ] **18 nov** — `fase2/evaluar.py`: lee el corpus y los cinco logs (parser, spaCy, NLTK, LLM zero-shot, LLM few-shot) y calcula para cada uno:
  - precisión, cobertura (recall) y tasa de rechazo correcto;
  - falsos positivos, falsos negativos y errores de etiquetado.
  - Salida: tablas en CSV y **al menos una gráfica** en PNG. Debe ser reproducible: si se corre de nuevo, salen las mismas cifras.
- [ ] **18 nov** — Entregar a P4: tablas, gráfica, metodología de spaCy y NLTK, y análisis de sus errores.

## P4 — Allan · LLM e informe

- [ ] **16 nov** — Escribir los dos prompts con las reglas de P2: **zero-shot** (solo reglas) y **few-shot** (reglas + 3–5 ejemplos resueltos), con salida en formato fijo (acepta/rechaza + árbol en corchetes).
- [ ] **17 nov** — `fase2/llm_experimento.py` (**por API, no por el chat**): corre todo el corpus con ambos prompts y guarda en `fase2/logs/llm_zero_shot.*` y `llm_few_shot.*`, por cada llamada, **el prompt exacto, la respuesta completa y el timestamp**.
- [ ] **18 nov** — Análisis del LLM: ¿respeta las reglas o se desvía hacia su conocimiento general? (la clave son las oraciones correctas en español que la gramática no acepta), y ¿few-shot mejora frente a zero-shot?
- [ ] **19 nov, mañana** — Integrar el informe de 8–10 páginas y exportarlo a PDF:
  1. Parser y CFG (P1) · 2. Corpus (P2) · 3. Metodología (todos) · 4. Resultados (P3) · 5. Análisis de errores (todos; énfasis en el LLM) · 6. Conclusiones con datos.
  - Anexos: corpus, logs de los cuatro enfoques, prompts y respuestas con timestamp, `evaluar.py`.
- [ ] **19 nov** — README de `fase2/` con los pasos para reproducir todo desde cero.

## Todos

- [ ] **19 nov antes de las 17:30** — Revisar que el repositorio tenga todos los anexos y que `python fase2/evaluar.py` reproduzca las tablas del PDF. Enviar el correo.
- [ ] **19 nov en clase** — Debe ir al menos un integrante. Cualquiera tiene que poder explicar cómo se generó cada log, qué significa cada celda de las tablas y por qué el LLM respondió como lo hizo en un caso concreto.
