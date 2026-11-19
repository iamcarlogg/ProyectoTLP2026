# Resultados de la evaluación

Corpus: 60 oraciones (40 correctas, 20 incorrectas). Generado por `python fase2/evaluar.py`.

## Métricas

| Métrica | Parser (CFG) | spaCy | NLTK | LLM zero-shot | LLM few-shot |
|---|---|---|---|---|---|
| Exactitud | 93.3 % | 88.3 % | 96.7 % | 90.0 % | 91.7 % |
| Precisión | 100.0 % | 86.7 % | 95.2 % | 97.2 % | 97.3 % |
| Cobertura (recall) | 90.0 % | 97.5 % | 100.0 % | 87.5 % | 90.0 % |
| Tasa de rechazo correcto | 100.0 % | 70.0 % | 90.0 % | 95.0 % | 95.0 % |

## Clasificación de errores

| Tipo | Parser (CFG) | spaCy | NLTK | LLM zero-shot | LLM few-shot |
|---|---|---|---|---|---|
| Verdaderos positivos (VP) | 36 | 39 | 40 | 35 | 36 |
| Verdaderos negativos (VN) | 20 | 14 | 18 | 19 | 19 |
| Falsos positivos (FP) | 0 | 6 | 2 | 1 | 1 |
| Falsos negativos (FN) | 4 | 1 | 0 | 5 | 4 |
| Errores de etiquetado (de los VP) | 0 | 16 | 3 | 6 | 0 |
| Árbol distinto del esperado (de los VP) | 0 | n/a | n/a | 25 | 6 |
| Respuestas inválidas | 0 | 0 | 0 | 3 | 0 |

## Aciertos por nivel

| Nivel | Parser (CFG) | spaCy | NLTK | LLM zero-shot | LLM few-shot |
|---|---|---|---|---|---|
| 1 (20 oraciones) | 20/20 | 18/20 | 20/20 | 18/20 | 20/20 |
| 2 (20 oraciones) | 20/20 | 20/20 | 20/20 | 19/20 | 20/20 |
| 3 (20 oraciones) | 16/20 | 15/20 | 18/20 | 17/20 | 15/20 |

## Fidelidad a la gramática

Mide si el enfoque acepta exactamente las oraciones que genera la CFG (36 de 60) y rechaza las demás, sin importar si son correctas en español. Es la medida de la pregunta 2: un LLM que sigue las reglas dadas tiene 100 %. El parser es la referencia (100 % por construcción); spaCy y NLTK no reciben la gramática, así que en ellos solo es informativa.

| Medida | Parser (CFG) | spaCy | NLTK | LLM zero-shot | LLM few-shot |
|---|---|---|---|---|---|
| Fidelidad a la gramática | 100.0 % | 85.0 % | 90.0 % | 90.0 % | 98.3 % |
| Correctas en español fuera de la gramática aceptadas (de 4) | 0/4 | 3/4 | 4/4 | 2/4 | 0/4 |

Oraciones correctas en español que la gramática no genera: 49 «El perro y la gata duermen.», 50 «El perro come la carne y duerme.», 51 «El perro duerme y la gata come.», 52 «El perro no come la carne.». Si un enfoque las acepta, usó su conocimiento del español en vez de las reglas.
