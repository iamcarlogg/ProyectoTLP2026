# ProyectoTLP2026 — Gramáticas formales y lenguaje natural

Proyecto de Teoría de Lenguajes de Programación (TLP02-2026): *experimentando los límites de la jerarquía de Chomsky*.

**La pregunta del proyecto:** ¿por qué una gramática libre de contexto (CFG) alcanza para describir un lenguaje de programación como C, pero se queda corta con el español? Para responderla construimos parsers, los llevamos al límite y comparamos el resultado con herramientas modernas de NLP y con un LLM.

## Las dos fases

| Fase | Qué se hace | Peso | Entrega | Presentación |
| --- | --- | ---: | --- | --- |
| **1 — Encontrar el límite** | Parser de un subconjunto de C (mini-C) que funciona perfecto; luego intentar extender la CFG al español y documentar dónde y por qué falla; demo con spaCy/NLTK. | 40 % | **sábado 7 nov 2026** (fecha extendida) | por confirmar |
| **2 — Medir la diferencia** | Benchmark: el mismo corpus de 40+ oraciones etiquetadas pasa por 4 enfoques (parser propio, spaCy, NLTK o HuggingFace, LLM zero-shot y few-shot) y se comparan con métricas. Se evalúa **solo con un informe escrito** (8–10 páginas) y anexos de evidencia. Detalle: [docs/alcance_fase2.md](docs/alcance_fase2.md). | 60 % | **jueves 19 nov 2026, 17:30** (correo institucional: enlace al repositorio + PDF) | **no hay**; el 19 en clase el docente puede preguntar a cualquier equipo (debe ir al menos un integrante) |

La Fase 1 se evaluó así: correctitud técnica 35 %, profundidad del análisis 30 %, rigor experimental 20 %, presentación y demo 15 %. La Fase 2 no tiene presentación: se evalúa por el informe y su evidencia. **Todos deben poder explicar cualquier línea de código.**

## Roles

Cada persona mantiene el mismo eje en las dos fases.

| Rol | Integrante | Fase 1 | Fase 2 |
| --- | --- | --- | --- |
| **P1 — Parsers** | Carlo Enrique Guerra Vega | Lexer y parser de mini-C, árbol, errores, motor genérico | Correr el parser propio sobre el corpus y guardar su log |
| **P2 — Gramáticas** | Federico Josué Calderón Durán | Extensión de la CFG al español y análisis formal de las fallas | CFG del español, reglas en texto para el prompt y corpus de 40+ oraciones etiquetadas |
| **P3 — NLP** | Kelvin Rodrigo Iraheta Morales | Demo con spaCy/NLTK sobre las oraciones de P2 | spaCy + NLTK o HuggingFace (logs), script de evaluación, tablas y gráfica |
| **P4 — Teoría, LLM e integración** | Allan Josué López Escalante | Marco teórico, tests del parser formal, README, informe | LLM zero-shot y few-shot (prompts, respuestas y timestamps) e informe final en PDF |

## Estado (18 de noviembre de 2026)

### Fase 1

| Pieza | Rol | Estado | Dónde |
| --- | --- | --- | --- |
| Lexer y parser de mini-C con árbol y errores | P1 | ✅ Listo | `fase1/lexer.py`, `fase1/parser_formal.py` |
| Pruebas del parser de mini-C (24 casos) | P1 | ✅ 24 passed | `fase1/test_parser_formal.py` |
| Motor genérico (gramática como diccionario) | P1 | ✅ Listo | `fase1/motor.py` |
| 20 oraciones de prueba y gramática extendida del español | P2 | ✅ 20/20 | `fase1/gramatica_es.py`, `fase1/pruebas_base.py` |
| Tabla de fallas (24 casos adicionales) | P2 | ✅ Listo | `fase1/pruebas_fallas.py`, [documento](fase1/documentacion/03_tabla_de_fallas.md) |
| Explosión de reglas (22 → 48 → 93) | P2 | ✅ Listo | `fase1/analisis_explosion.py`, [documento](fase1/documentacion/04_explosion_de_reglas.md) |
| Dónde sí falla la CFG (dependencias cruzadas) | P2 | ✅ Listo | [documento](fase1/documentacion/05_donde_si_falla_la_cfg.md) |
| Demo con spaCy: análisis, tabla y página interactiva | P3 | ✅ Listo | `fase1/demo_nlp.py`, `tabla_nlp.py`, `visualizar_nlp.py`, [documento](fase1/documentacion/06_demo_nlp.md) |
| Marco teórico e informe (7 páginas con portada) | P4 | ✅ Listo | `informe/` |

### Fase 2

Alcance vigente: [docs/alcance_fase2.md](docs/alcance_fase2.md). Pasos completos de
reproducción: [fase2/README.md](fase2/README.md). Para recalcular las cifras desde
los cinco logs guardados, sin volver a consultar ninguna API:

```powershell
python fase2/evaluar.py
```

| Pieza | Rol | Estado |
| --- | --- | --- |
| Corpus de 60 oraciones y CFG (207 producciones) | P2 | ✅ Listo |
| Log del parser con corpus final | P1 | ✅ Listo |
| Logs de spaCy y NLTK | P3 | ✅ Listos |
| Experimento Gemini `gemini-3.1-flash-lite` | P4 | ✅ 60 zero-shot + 60 few-shot |
| Evaluación, tablas y dos gráficas | P3/P4 | ✅ Actualizadas con los cinco logs; reproducción verificada |
| Documentación del LLM | P4 | ✅ [04_llm.md](fase2/documentacion/04_llm.md) |
| Informe PDF y paquete de entrega | P4 | ✅ [PDF](output/pdf/informe_fase2.pdf): 9 páginas de informe (portada incluida) + 9 de anexos; [ZIP](output/pdf/entrega_fase2.zip) con evidencia y código |

Few-shot frente a zero-shot: exactitud española 91.7 % frente a 90.0 %;
fidelidad del veredicto a la CFG 98.3 % frente a 90.0 %. Las cifras oficiales y
las demás métricas están en [tablas.md](fase2/resultados/tablas.md).
La clave `GEMINI_API_KEY` vive en el entorno o `.env` local, ignorado por Git;
no hace falta para evaluar los logs existentes.

El PDF incorpora los archivos completos como adjuntos; el ZIP ofrece la misma evidencia
y el proyecto reproducible sin `.env` ni `.venv`. Fuente editable del informe:
`informe/informe_fase2.html` (mismo formato que el de la Fase 1); generador
`informe/generar_fase2.py` (dependencias en `informe/requirements-informe.txt`).

## Mapa del repositorio

```text
ProyectoTLP2026/
├── README.md                 ← este archivo: visión general, roles, estado
├── requirements.txt          ← dependencias (nltk, pytest, spaCy y su modelo de español)
├── informe/
│   ├── informe_fase1.html    ← fuente del informe (editar aquí)
│   ├── informe_fase1.pdf     ← informe entregable (7 páginas con portada)
│   ├── generar_figuras.py    ← genera la Figura 1 del informe (correr antes de generar_pdf.py)
│   ├── figuras/              ← figuras SVG del informe
│   ├── generar_pdf.py        ← HTML → PDF (Fase 1)
│   ├── informe_fase2.html    ← fuente del informe de la Fase 2 (editar aquí)
│   └── generar_fase2.py      ← HTML → PDF de la Fase 2 con la evidencia adjunta y ZIP
├── docs/
│   └── decisiones.md         ← convenciones del equipo, válidas para las dos fases
└── fase1/
    ├── README.md             ← cómo ejecutar y usar el código de la Fase 1
    │
    │   Parte A — Lenguaje formal (mini-C)
    ├── lexer.py              ← código → tokens
    ├── parser_formal.py      ← tokens → árbol (descendente recursivo)
    ├── test_parser_formal.py ← 24 pruebas con pytest
    │
    │   Parte B — Español
    ├── motor.py              ← parser genérico con backtracking
    ├── gramatica_es.py       ← gramática del español (diccionario)
    ├── pruebas_base.py       ← las 20 oraciones acordadas
    ├── pruebas_fallas.py     ← 24 casos para la tabla de fallas
    ├── analisis_explosion.py ← cuenta cuánto crecen las reglas
    │
    │   Parte C — NLP · P3
    ├── demo_nlp.py           ← analiza las oraciones con spaCy
    ├── tabla_nlp.py          ← tabla lado a lado: CFG frente a spaCy
    ├── visualizar_nlp.py     ← genera la página interactiva de la demo
    ├── plantilla_demo.html   ← diseño de esa página
    ├── salidas/              ← páginas generadas (se regeneran con un comando)
    │
    └── documentacion/        ← análisis para el informe, en orden de lectura
        ├── 01_parser_minic.md
        ├── 02_gramatica_espanol.md
        ├── 03_tabla_de_fallas.md
        ├── 04_explosion_de_reglas.md
        ├── 05_donde_si_falla_la_cfg.md
        └── 06_demo_nlp.md
```

**Regla para ubicar archivos:** lo que pertenece a una fase va en su carpeta; lo que vale para todo el proyecto va en `docs/`.

## Preparar el entorno

Python 3.10 o más reciente. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar todo (Fase 1)

Desde la raíz del repositorio:

```bash
pytest -v                                    # 24 pruebas del parser de mini-C
python fase1/parser_formal.py                # ejemplo de mini-C con su árbol y un error
python fase1/motor.py                        # ejemplos en español aceptados y rechazados
python fase1/pruebas_base.py                 # 20 oraciones: 20/20 correctas
python fase1/pruebas_fallas.py               # 24 casos extra: 14/24, con la tabla de fallas
python fase1/analisis_explosion.py --probar  # 22 → 48 → 93 producciones
python fase1/demo_nlp.py                     # spaCy sobre las 20 oraciones
python fase1/tabla_nlp.py                    # CFG 20/20 frente a spaCy 19/20 (--fallas: 14/24 frente a 22/24)
python fase1/visualizar_nlp.py               # página de la demo en fase1/salidas/
```

## Qué leer y en qué orden

1. Este README, para el panorama.
2. [docs/decisiones.md](docs/decisiones.md), para las convenciones (notación, formato del árbol, reglas del motor).
3. [fase1/README.md](fase1/README.md), para usar el código.
4. `fase1/documentacion/01` a `06`, para el análisis que va al informe.
