# Resultados de la evaluación

Corpus: 60 oraciones (40 correctas, 20 incorrectas). Generado por `python fase2/evaluar.py`.

## Métricas

| Métrica | Parser (CFG) | spaCy | NLTK |
|---|---|---|---|
| Exactitud | 93.3 % | 88.3 % | 96.7 % |
| Precisión | 100.0 % | 86.7 % | 95.2 % |
| Cobertura (recall) | 90.0 % | 97.5 % | 100.0 % |
| Tasa de rechazo correcto | 100.0 % | 70.0 % | 90.0 % |

## Clasificación de errores

| Tipo | Parser (CFG) | spaCy | NLTK |
|---|---|---|---|
| Verdaderos positivos (VP) | 36 | 39 | 40 |
| Verdaderos negativos (VN) | 20 | 14 | 18 |
| Falsos positivos (FP) | 0 | 6 | 2 |
| Falsos negativos (FN) | 4 | 1 | 0 |
| Errores de etiquetado (de los VP) | 0 | 16 | 3 |
| Árbol distinto del esperado (de los VP) | 0 | n/a | n/a |
| Respuestas inválidas | 0 | 0 | 0 |

## Aciertos por nivel

| Nivel | Parser (CFG) | spaCy | NLTK |
|---|---|---|---|
| 1 (20 oraciones) | 20/20 | 18/20 | 20/20 |
| 2 (20 oraciones) | 20/20 | 20/20 | 20/20 |
| 3 (20 oraciones) | 16/20 | 15/20 | 18/20 |

**Pendientes (sin log todavía):** LLM zero-shot, LLM few-shot
