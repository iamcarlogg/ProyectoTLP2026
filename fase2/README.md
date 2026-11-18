# Fase 2 — Benchmark: parser propio frente a NLP moderno y un LLM

Un mismo corpus de 60 oraciones pasa por cuatro enfoques, y un script calcula las métricas de todos con la misma regla. El alcance que pidió el docente está en [docs/alcance_fase2.md](../docs/alcance_fase2.md).

```text
                 ┌─ correr_parser.py    (P1) ─→ logs/parser.json        ─┐
corpus.csv ──────┼─ correr_spacy.py     (P3) ─→ logs/spacy.json         ─┼─→ evaluar.py (P3) ─→ resultados/
(P2, 60 orac.)   ├─ correr_nltk.py      (P3) ─→ logs/nltk.json          ─┤
                 └─ llm_experimento.py  (P4) ─→ logs/llm_zero_shot.json ─┤
                                                 logs/llm_few_shot.json  ─┘
```

## Archivos

| Grupo | Archivo | Rol | Qué es |
| --- | --- | --- | --- |
| **Entradas** | `corpus.csv` | P2 | 60 oraciones en 3 niveles, con la respuesta esperada (`acepta`/`rechaza`) y el árbol esperado |
| | `gramatica_es.py` | P2 | La CFG del español controlado que usa el parser |
| | `gramatica_es.txt` | P2 | La misma gramática en texto, para el prompt del LLM |
| **Correr cada enfoque** | `correr_parser.py` | P1 | Parser propio (motor de `fase1/`) |
| | `correr_spacy.py` | P3 | spaCy con `es_core_news_md` |
| | `correr_nltk.py` | P3 | Etiquetador NLTK entrenado con `cess_esp` |
| | `llm_experimento.py` | P4 | LLM por API, zero-shot y few-shot *(pendiente)* |
| **Evaluar** | `evaluar.py` | P3 | Lee el corpus y los logs y calcula las métricas |
| **Salidas** | `logs/` | todos | Salida bruta de cada enfoque (anexo obligatorio del informe) |
| | `resultados/` | P3 | Tablas en CSV y Markdown, y las dos gráficas |
| **Documentación** | `documentacion/` | todos | Sección de cada rol para el informe y decisiones tomadas |

### Documentación

| Documento | Rol | Contenido |
| --- | --- | --- |
| [decisiones_tomadas.md](documentacion/decisiones_tomadas.md) | P1 | Decisiones del equipo y formato de los logs |
| [01_parser_propio.md](documentacion/01_parser_propio.md) | P1 | Resumen del parser y la CFG, metodología y análisis de sus errores |
| [02_corpus.md](documentacion/02_corpus.md) | P2 | Descripción del corpus y criterios de selección por nivel |
| [03_nlp_y_evaluacion.md](documentacion/03_nlp_y_evaluacion.md) | P3 | Metodología de spaCy, NLTK y la evaluación; resultados y análisis de errores |
| `04_llm.md` | P4 | Prompts, modelo, parámetros y análisis del LLM *(pendiente)* |

## Cómo reproducir todo, paso a paso

Desde la raíz del repositorio y con Python 3.10 o más reciente.

**1. Instalar las dependencias** (incluye el modelo de español de spaCy y matplotlib):

```bash
pip install -r requirements.txt
```

**2. Correr los cuatro enfoques.** Cada uno escribe su log en `fase2/logs/`:

```bash
python fase2/correr_parser.py      # → logs/parser.json
python fase2/correr_spacy.py       # → logs/spacy.json
python fase2/correr_nltk.py        # → logs/nltk.json (la primera vez descarga cess_esp)
python fase2/llm_experimento.py    # → logs/llm_zero_shot.json y llm_few_shot.json
```

El LLM necesita una clave de API en una variable de entorno (ver el script de P4) y **cuesta dinero**, así que se corre una sola vez. Sus logs quedan en el repositorio para que la evaluación se reproduzca sin volver a llamar a la API.

**3. Calcular las métricas:**

```bash
python fase2/evaluar.py
```

Escribe en `fase2/resultados/`:

| Archivo | Contenido |
| --- | --- |
| `tablas.md` | Las tablas del informe: métricas, clasificación de errores y aciertos por nivel |
| `metricas.csv` | Una fila por enfoque: VP, FN, FP, VN, precisión, cobertura, rechazo correcto, errores de etiquetado |
| `metricas_por_nivel.csv` | Aciertos, falsos positivos y falsos negativos por nivel |
| `detalle.csv` | Una fila por oración: qué respondió cada enfoque y si acertó |
| `metricas.png`, `aciertos_por_nivel.png` | Las gráficas |

Con los mismos logs, `evaluar.py` produce siempre los mismos archivos. Si un log es de un corpus distinto (otra cantidad de oraciones u otro texto), se detiene con un error en vez de mezclar corridas.

## Estado (17 nov 2026)

| Pieza | Rol | Estado |
| --- | --- | --- |
| Corpus (60 oraciones) y gramática | P2 | ✅ Listo |
| `logs/parser.json` con el corpus final | P1 | ✅ Listo (56/60) |
| `logs/spacy.json` y `logs/nltk.json` | P3 | ✅ Listo |
| `evaluar.py`, tablas y gráficas | P3 | ✅ Listo; volver a correr cuando estén los logs del LLM |
| `llm_experimento.py` y sus dos logs | P4 | ⏳ Pendiente |
| Documentación de P1, P2 y P3 | P1, P2, P3 | ✅ Listo en `documentacion/` |
| Documentación de P4 | P4 | ⏳ Pendiente |
| Informe en PDF (8–10 páginas + anexos) | P4 | ⏳ Pendiente — entrega jueves 19 nov, 17:30 |