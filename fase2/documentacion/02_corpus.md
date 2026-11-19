# 2. Corpus de prueba — P2

Material para la **sección 2 del informe**: descripción del corpus de prueba y criterios de selección por nivel. El corpus completo es un **anexo obligatorio** (`fase2/corpus.csv`).

## 1. Formato

`fase2/corpus.csv` tiene una oración por fila, con estas columnas:

| Columna | Contenido |
| --- | --- |
| `id` | Número de la oración (1–60); todos los logs se cruzan por este campo |
| `oracion` | La oración, con mayúscula inicial y punto final |
| `nivel` | 1 (simple), 2 (intermedia) o 3 (compleja) |
| `esperado` | `acepta` si la oración es **correcta en español**, `rechaza` si no lo es |
| `arbol_esperado` | Para las correctas, la estructura esperada en notación de corchetes de `nltk.Tree` |

**La etiqueta `esperado` mide el español, no la gramática.** Si una oración es correcta pero la gramática no la cubre, se etiqueta `acepta`, y que el parser la rechace cuenta como falso negativo. Así se mide hasta dónde llega la CFG.

## 2. Composición

| Nivel | Correctas | Incorrectas | Total | Largo medio |
| --- | ---: | ---: | ---: | ---: |
| 1 — simples | 14 | 6 | 20 | 2,9 palabras |
| 2 — intermedias | 14 | 6 | 20 | 4,5 palabras |
| 3 — complejas | 12 | 8 | 20 | 6,7 palabras |
| **Total** | **40** | **20** | **60** | |

Controles de calidad del corpus:

- **Sin duplicados:** las 60 oraciones son distintas, así que ninguna cuenta doble en las métricas.
- **Todas las palabras están en el vocabulario de la gramática.** Ningún rechazo del parser se debe a una palabra desconocida, así que en el nivel 3 se prueba la **estructura** y no el léxico. Con el borrador anterior, los 10 falsos negativos eran todos por vocabulario.
- **Un tercio de oraciones incorrectas:** 20 de 60. Con eso, cada error en la tasa de rechazo correcto pesa un 5 % (1 de 20), frente al 14 % del borrador, que tenía solo 7.
- **Todas las incorrectas tienen errores de concordancia.** Se eligieron así para probar el fenómeno que la CFG controla con sus categorías y que las herramientas de NLP no rechazan por sí mismas.

## 3. Criterios de selección por nivel

### Nivel 1 — Simples (ids 1–20)

Sujeto y verbo, sin modificadores. Deben aceptarse sin problema.

| Grupo | Ids | Qué prueba | Ejemplo |
| --- | --- | --- | --- |
| Correctas: las 4 combinaciones de género y número | 1–8 | Concordancia básica con «dormir» y «comer» en presente | *Las gatas comen.* |
| Correctas: pretérito | 9–12 | El segundo tiempo verbal | *Los perros durmieron.* |
| Correctas: primera persona | 13–14 | Sujetos pronominales | *Nosotros comemos.* |
| Incorrectas: determinante y sustantivo | 15–18 | Desacuerdo de género o número dentro del SN | \**La perro duerme.* |
| Incorrectas: sujeto y verbo | 19–20 | Desacuerdo de número entre palabras vecinas | \**Las gatas duerme.* |

### Nivel 2 — Intermedias (ids 21–40)

Modificadores y variaciones **dentro** de lo que cubre la gramática.

| Grupo | Ids | Qué prueba | Ejemplo |
| --- | --- | --- | --- |
| Correctas: adjetivo | 21–24 | Concordancia de adjetivo, sustantivo y determinante | *La gata negra come.* |
| Correctas: adverbio | 25–26 | Modificador del verbo | *Las gatas comen rápidamente.* |
| Correctas: objeto directo | 27–28 | Verbo transitivo en presente y pretérito | *La gata comió la carne.* |
| Correctas: sintagma preposicional | 29–30 | Complemento con «en» | *Los perros duermen en el jardín.* |
| Correctas: combinaciones | 31–34 | Adjetivo + adverbio, adjetivo + objeto, primera persona con objeto | *Nosotras comimos la carne.* |
| Incorrectas: adjetivo | 35–40 | Desacuerdo de género o número entre el adjetivo y su sustantivo | \**Los perros negras comieron.* |

### Nivel 3 — Complejas (ids 41–60)

Fenómenos que probablemente exceden la gramática o la ponen al límite. Son los tres que pidió el docente: **subordinadas anidadas**, **ambigüedad estructural** y **concordancia a distancia**.

| Grupo | Ids | Qué prueba | Ejemplo |
| --- | --- | --- | --- |
| Correctas: relativas de sujeto y de objeto | 41–46 | Subordinadas, en presente y pretérito | *La gata que el perro persiguió durmió.* |
| Correcta: ambigüedad estructural | 47 | El SP puede depender del verbo o del objeto | *El perro come la carne en la casa.* |
| Correcta: relativas anidadas | 48 | Una relativa dentro de otra | *El perro que la gata que duerme persigue duerme.* |
| Correctas: coordinación y negación con objeto | 49–52 | Construcciones del español que la gramática **no** cubre | *El perro y la gata duermen.* |
| Incorrectas: concordancia dentro de la relativa | 53, 55, 56 | El verbo de la relativa no concuerda con su sujeto: el SN de la relativa (53, 55) o el antecedente (56) | \**El perro negro que comen duerme.* |
| Incorrectas: concordancia a distancia | 54, 57, 58 | Con una relativa en medio, el verbo principal no concuerda con el sujeto | \**Los perros que comen duerme.* |
| Incorrecta: adjetivo fuera de lugar | 59 | El adjetivo queda separado de su sustantivo | \**El perro que la gata persigue negra duerme.* |
| Incorrecta: dos verbos sin enlace | 60 | Un segundo verbo sin conjunción ni sujeto | \**El perro come la carne duermen.* |

Las oraciones 49–52 son las que más aportan al experimento. Son **correctas en español** y la gramática **no** las acepta, así que miden directamente:

- el límite de cobertura de la CFG;
- si el LLM sigue las reglas que se le dan o se desvía hacia su conocimiento general del español. Si las acepta, no está aplicando la gramática del prompt.

Su `arbol_esperado` usa nodos que la gramática no tiene (`sn_coord`, `sv_coord`, `oracion_coord`, `negacion`): describe la estructura que tendrían si la gramática las cubriera.

## 4. Gramática que acompaña al corpus

| Archivo | Uso |
| --- | --- |
| `fase2/gramatica_es.py` | El diccionario `GRAMATICA` que usa el parser (57 no terminales, 207 producciones, 47 palabras) |
| `fase2/gramatica_es.txt` | Las mismas producciones en texto (A → α \| β, ε para la alternativa vacía, palabras entre comillas) y los rasgos de cada verbo. Es lo que recibe el LLM en el prompt |

El corpus usa 40 de las 47 palabras de la gramática. Las 7 que no aparecen (*comí, con, dormí, dormimos, perseguí, perseguimos, persigo*) son formas de primera persona y una preposición que la gramática cubre pero que no hicieron falta para los fenómenos elegidos.
