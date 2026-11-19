# Fase 2 — Alcance ajustado por el docente

Recibido el 15 de noviembre de 2026. **Reemplaza** lo que dicen el enunciado original y el reparto sobre la Fase 2. Si otro documento contradice a este, manda este.

## Qué cambió

| Antes | Ahora |
| --- | --- |
| Informe de 7–10 páginas, presentación de 15–20 min con demo | **Solo informe escrito (8–10 páginas) con evidencia experimental. No hay presentación oral.** |
| Set de 60+ oraciones | **40+ oraciones** en tres niveles |
| spaCy + HuggingFace + LLM | **4 enfoques**: parser propio, spaCy, NLTK **o** HuggingFace, LLM vía API |
| Entrega 18 nov, 23:59 | **Jueves 19 nov 2026, a más tardar 17:30**, por correo institucional: enlace al repositorio Git + informe en PDF adjunto |
| Árboles visuales para la demo (`visualizar.py`, PNG) | Ya no se exigen: la generación de árboles se cubrió en la Fase 1 |

**Verificación (19 nov, en clase):** debe asistir al menos un representante por equipo. El docente puede preguntar al azar cómo se generaron los logs, qué significa una celda concreta de las tablas o por qué el LLM respondió como lo hizo en un caso del set. Si no se sabe explicar, se ajusta la nota.

## Preguntas que el informe debe responder con datos

1. ¿Qué tan lejos llega una CFG bien diseñada frente a las técnicas modernas?
2. ¿Un LLM respeta reglas formales cuando se le dan explícitamente, o se desvía hacia su conocimiento general?
3. ¿Mejora el LLM con ejemplos en el prompt (few-shot) frente a solo las reglas (zero-shot)?

## Los cuatro enfoques (mismo corpus para todos)

1. **Parser propio** sobre la CFG del español.
2. **spaCy**.
3. **NLTK o HuggingFace Transformers** (elegir una).
4. **LLM vía API** (Claude, OpenAI, Gemini u otro), con las reglas de producción de la gramática explícitas en el prompt; variantes zero-shot y few-shot.

## Corpus de prueba

Al menos **40 oraciones** en tres niveles:

| Nivel | Contenido |
| --- | --- |
| 1 — simples | La gramática debería aceptarlas sin problema. |
| 2 — intermedias | Modificadores y variaciones dentro de lo que la gramática intenta cubrir. |
| 3 — complejas | Fenómenos que probablemente exceden la gramática: concordancia a distancia, subordinadas anidadas, ambigüedad estructural. |

Cada oración va etiquetada con la salida esperada: aceptada / rechazada y, cuando aplique, la estructura esperada.

## Métricas (para cada uno de los cuatro enfoques)

- Precisión
- Cobertura (recall)
- Tasa de rechazo correcto
- Clasificación de errores: falsos positivos, falsos negativos, errores de etiquetado

Presentación: tablas comparativas con las cuatro columnas y **al menos una gráfica**.

## Contenido del informe (8–10 páginas, anexos aparte)

1. Resumen del parser propio y de la CFG (máximo 1 página; no repetir la Fase 1).
2. Descripción del corpus y criterios de selección por nivel.
3. Metodología: cómo se corrió cada enfoque, versiones de librerías, modelo de LLM, parámetros, prompts exactos (zero-shot y few-shot).
4. Resultados cuantitativos en tablas y gráficas, con las cuatro columnas.
5. Análisis de errores: dónde falla cada enfoque y por qué, con énfasis en el LLM frente a reglas formales.
6. Conclusiones respaldadas por los datos, no por impresiones.

## Evidencia obligatoria (anexos)

Sirve para demostrar que el experimento se corrió de verdad y no se armó a posteriori.

- [x] Corpus completo en `.csv` o `.txt`, con la etiqueta esperada por oración. → `fase2/corpus.csv`
- [x] Logs brutos de cada uno de los cuatro enfoques sobre el corpus completo (`.txt`, `.json` o `.csv`; nada de capturas). → `fase2/logs/`: los cinco logs completos; LLM zero-shot y few-shot con 60 resultados cada uno
- [x] Prompts exactos del LLM (zero-shot y few-shot) y las respuestas completas; **cada llamada con su timestamp**.
- [x] Script de evaluación en Python que lee los logs y calcula las métricas; reproducible: mismas entradas → mismas tablas del informe. → `fase2/evaluar.py`
- [x] Repositorio Git (o zip) con código, corpus, logs y un README que explique paso a paso cómo reproducir los experimentos. → Código y anexos incluidos en esta revisión, ZIP en `output/pdf/entrega_fase2.zip` y README completo; envío del correo pendiente
