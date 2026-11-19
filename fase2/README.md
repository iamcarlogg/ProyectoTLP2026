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
| | `llm_experimento.py` | P4 | Gemini por API; ambas variantes completas |
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
| [04_llm.md](documentacion/04_llm.md) | P4 | Prompts, metodología, resultados y análisis completos |

## Cómo reproducir todo, paso a paso

Desde la raíz del repositorio y con Python 3.10 o más reciente.

**1. Instalar las dependencias** (incluye el modelo de español de spaCy y matplotlib):

```bash
pip install -r requirements.txt
```

**2. Generar los logs (solo si se inicia una nueva corrida).** Para reproducir
las cifras entregadas basta instalar dependencias y pasar al paso 3: los cinco
logs ya están completos. No volver a consultar la API para recalcular métricas.
Cada corredor escribe en `fase2/logs/`:

```bash
python fase2/correr_parser.py      # → logs/parser.json
python fase2/correr_spacy.py       # → logs/spacy.json
python fase2/correr_nltk.py        # → logs/nltk.json (la primera vez descarga cess_esp)
python fase2/llm_experimento.py    # solo plan local, sin API ni escritura de logs
```

Si la descarga de `cess_esp` falla por el proxy, configurar antes en PowerShell:

```powershell
$env:NLTK_ALLOW_PROXIED_URLOPEN = "1"
```

El corredor del LLM usa solo la biblioteca estándar de Python. Lee
`GEMINI_API_KEY` del entorno o, si no está definida allí, de `.env` en la raíz
del repositorio (ignorado por Git). Acepta `GEMINI_API_KEY=valor` o el valor
entre comillas simples/dobles, en una línea; no requiere instalar dotenv. Nunca
poner la clave en código, prompts o logs. El modo local no lee ese archivo.

Configuración: `gemini-3.1-flash-lite`, API `v1beta`, temperatura solicitada 0,
razonamiento `MINIMAL` y `maxOutputTokens=2048` (registrado también como `max_tokens`).
La API aceptó la configuración y la corrida está completa. El saldo y la cuota
restante de la cuenta no se infieren de los logs. Una solicitud independiente por oración,
60 por variante, sin historial ni herramientas. Antes de la corrida de pago,
revisar presupuesto y configuración. El comando que **envía solicitudes de pago** es:

```powershell
python fase2/llm_experimento.py --ejecutar
```

Para verificar previamente el conteo de tokens sin generar respuestas:

```powershell
python fase2/verificar_api.py --consultar
```

Para limitar la primera ejecución a una sola llamada real, que se conserva como
parte del experimento y no se repite al continuar:

```powershell
python fase2/llm_experimento.py --ejecutar --variante zero-shot --max-nuevas 1
```

`--max-nuevas` limita llamadas nuevas entre todas las variantes seleccionadas;
no reduce el corpus ni cambia la configuración experimental de la corrida.

Escribe `logs/llm_zero_shot.json` y `logs/llm_few_shot.json` progresivamente. Al
reanudar con el mismo comando omite todos los resultados ya guardados, incluso
los inválidos, y recupera respuestas brutas recibidas antes de una interrupción.
Cambios en corpus, gramática, prompts, código o parámetros bloquean la mezcla
con los logs existentes. No borrar resultados ni repetir para mejorar las cifras.

No hay reintentos automáticos. Un fallo HTTP o de conexión detiene la corrida y
deja evidencia del intento sin inventar un rechazo. Si hubo un envío sin respuesta
local, la API podría haberlo cobrado: revisar el intento antes de autorizar su
repetición con `--ejecutar --reintentar-errores`. `.llm.lock` impide ejecuciones
simultáneas; si quedó tras terminar forzosamente el proceso, verificar que no haya
otra corrida activa antes de eliminar solo ese archivo de bloqueo.

Si Google devuelve explícitamente HTTP 503 (`UNAVAILABLE`), se puede usar el
auxiliar operativo sin cambiar modelo, prompts, parámetros ni el corredor:

```powershell
python fase2/continuar_corrida.py --ejecutar
```

Este auxiliar reanuda únicamente errores 503 confirmados, con pausas de 15, 30 y
45 segundos y hasta tres reintentos consecutivos sin progreso. Conserva cada
intento en el log. Se detiene ante errores de cuota, timeouts o envíos cuyo estado
sea ambiguo; no repite respuestas recibidas, aunque sean inválidas. Se incorporó
durante la corrida por errores 503 intermitentes del servicio. Usa cinco segundos
entre respuestas y prioriza las entradas con menos fallos, sin excluir ninguna.
El log final puede tener IDs fuera de orden: la evaluación cruza por ID.

No evaluar logs parciales: `metadatos.completo` debe ser true en ambos, con 60
resultados distintos. Los logs finales quedan en Git para reproducir métricas sin
volver a llamar a la API. Pruebas locales sin red ni claves:

```powershell
python -m unittest discover -s fase2 -p test_llm.py -v
```

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

## Estado (18 nov 2026)

| Pieza | Rol | Estado |
| --- | --- | --- |
| Corpus (60 oraciones) y gramática | P2 | ✅ Listo |
| `logs/parser.json` con el corpus final | P1 | ✅ Listo (56/60) |
| `logs/spacy.json` y `logs/nltk.json` | P3 | ✅ Listo |
| `evaluar.py`, tablas y gráficas | P3 | ✅ Listo; actualizado con los cinco logs y reproducibilidad verificada |
| `llm_experimento.py` | P4 | ✅ Preparado y probado sin red |
| Los dos logs del LLM | P4 | ✅ Completos: 60/60 por variante |
| Documentación de P1, P2 y P3 | P1, P2, P3 | ✅ Listo en `documentacion/` |
| Documentación de P4 | P4 | ✅ Lista en `documentacion/04_llm.md` |
| Informe PDF y paquete de entrega | P4 | ✅ Listos en `output/pdf/`: 9 páginas de informe (portada incluida) + 9 de anexos y ZIP con código/evidencia |

## Informe y anexos de entrega

PDF: `output/pdf/informe_fase2.pdf`. Paquete: `output/pdf/entrega_fase2.zip`
(rutas relativas a la raíz). El PDF tiene 9 páginas de informe (portada incluida) + 9 de anexos:
índice de evidencia, corpus etiquetado y prompts exactos de ambas variantes para el ID 1.
Incluye 16 archivos adjuntos con el corpus completo, cinco logs, gramática, motor,
evaluador, tablas y huellas. El ZIP contiene el proyecto y toda la evidencia.

Para editar y regenerar el informe sin API:

```powershell
python -m pip install -r informe/requirements-informe.txt
playwright install chromium
python informe/generar_fase2.py
```

Editar primero `informe/informe_fase2.html` (mismo formato que el informe de la Fase 1).
El generador inserta las tablas oficiales de `resultados/tablas.md`, el corpus
y utiliza las gráficas existentes; los prompts impresos se extraen de los logs.
Los TXT de los prompts conservan bytes exactos y se adjuntan al PDF y al ZIP.
