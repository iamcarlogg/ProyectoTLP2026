# 1. Parser propio y CFG del español controlado — P1

Material para la **sección 1 del informe** («Resumen del parser propio y de la CFG», máximo 1 página, sin repetir la Fase 1) y para la parte del parser en la **metodología** y el **análisis de errores**.

## 1. Resumen del parser

El parser es el **motor genérico de la Fase 1** (`fase1/motor.py`), sin cambios. Recibe la gramática como un diccionario de Python y, con descenso recursivo y *backtracking*, busca **todos** los árboles que cubren la oración completa:

- **ningún árbol** → la oración se rechaza;
- **un árbol** → se acepta;
- **más de uno** → se acepta y es ambigua.

Antes de analizar, `normalizar()` pasa la oración a minúsculas y quita puntos y comas. Los signos `¿?¡!` no se quitan; es una decisión del equipo.

La Fase 2 no copia el motor: `correr_parser.py` lo importa desde `fase1/`. La gramática nueva está en `fase2/gramatica_es.py`, y como esa carpeta va primero en la búsqueda de módulos, se usa en lugar de la de la Fase 1 sin tocar código.

## 2. La CFG del español controlado

Es la gramática extendida de la Fase 1, ampliada con lo que pide el docente para la Fase 2: **dos tiempos verbales** y más variedad de sujetos. Sigue siendo una CFG pura de Tipo 2: la concordancia se codifica dividiendo cada categoría por sus rasgos, sin chequeos fuera de la gramática.

| | Fase 1 (extendida) | Fase 2 |
| --- | ---: | ---: |
| No terminales | 34 | 57 |
| Producciones | 93 | **207** |
| Palabras | 25 | 47 |

### Qué cubre

| Fenómeno | Cómo se codifica | Ejemplo |
| --- | --- | --- |
| Concordancia de género y número en el SN | `sn_ms → det_ms n_ms mod_ms` (y `_fs`, `_mp`, `_fp`) | *el perro negro* / \**la perro* |
| Concordancia sujeto-verbo | `oracion → sn_ms sv_s \| sn_mp sv_p \| …` | *los perros duermen* / \**el perro duermen* |
| Dos tiempos: presente y pretérito | categorías `_pret`: `sv_s_pret`, `v_p_pret`, `rel_obj_pret` | *la gata comió la carne* |
| Primera persona | `pron_1s`, `pron_1p` con `sv_1s_pres`, `sv_1p_pret`, … | *yo duermo*, *nosotras comimos la carne* |
| Relativas de sujeto y de objeto, también anidadas | `rel_suj_s → 'que' sv_s`; `rel_obj → 'que' sn_fs vt_s` | *el perro que la gata que duerme persigue duerme* |
| Modificadores | adjetivos (`adj_*`), adverbios (`adv`), sintagmas preposicionales (`sp → p sn`, con *en* y *con*) | *duermen en el jardín* |
| Negación y coordinación de verbos (solo intransitivos) | `sv_s → 'no' v_s \| v_s 'y' v_s` | *el perro no duerme* |

La gramática completa, en texto, está en `fase2/gramatica_es.txt`, que es la misma que recibe el LLM en el prompt.

### Costo de agregar rasgos

Pasar de 93 a 207 producciones confirma con datos la **explosión de reglas** de la Fase 1:

- **51 producciones** son solo de la primera persona: el pronombre, 4 familias de sintagmas verbales y sus verbos.
- **34** son del pretérito de tercera persona.
- Las demás también crecieron: `oracion` pasó de 4 a 12 alternativas y cada `mod_*` de 8 a 12, para admitir relativas en pretérito.

Cada rasgo nuevo multiplica categorías, aunque el vocabulario apenas crezca.

## 3. Metodología

| Parámetro | Valor |
| --- | --- |
| Script | `python fase2/correr_parser.py` |
| Motor | `fase1/motor.py` (descenso recursivo con *backtracking*, todos los árboles) |
| Gramática | `fase2/gramatica_es.py`: 57 no terminales, 207 producciones, 47 palabras |
| Entrada | Las 60 oraciones de `fase2/corpus.csv` |
| Log | `fase2/logs/parser.json` |

Por oración, el log guarda:
- `salida`: `acepta` o `rechaza`;
- `arbol`: el primer árbol, en una línea;
- `n_arboles`: más de uno indica ambigüedad;
- `motivo` del rechazo: `vocabulario` (hay palabras que la gramática no conoce), `estructura` (todas las palabras se conocen, pero ninguna regla las combina así) o `error` (excepción del motor);
- `palabras_desconocidas`, `tiempo_ms` y `timestamp`.

## 4. Resultados del parser

| Medida | Valor |
| --- | ---: |
| Aceptadas / rechazadas | 36 / 24 |
| Rechazos por vocabulario | 0 |
| Rechazos por estructura | 24 |
| Oraciones ambiguas (más de un árbol) | 1 (id 47) |
| Tiempo medio por oración | 0,09 ms (máximo 0,26 ms) |
| Exactitud | 56/60 (93,3 %) |
| Precisión / cobertura / rechazo correcto | 100 % / 90,0 % / 100 % |
| Árboles distintos del esperado (en las aceptadas) | 0 de 36 |

Las métricas completas y la comparación con los demás enfoques están en `resultados/tablas.md`.

## 5. Análisis de errores

**Cero falsos positivos.** El parser rechaza las 20 oraciones incorrectas, incluidas las 8 del nivel 3 con concordancia a distancia (por ejemplo, *el perro que la gata persigue **duermen***). Es lo esperado: las dependencias de estas oraciones son **anidadas**, y la CFG las controla con sus categorías.

**Cuatro falsos negativos, todos del nivel 3 y todos por estructura:**

| Id | Oración | Por qué la CFG la rechaza |
| --: | --- | --- |
| 49 | El perro y la gata duermen. | No hay regla de sujeto coordinado (`sn y sn`) ni regla que vuelva plural un sujeto formado por dos singulares |
| 50 | El perro come la carne y duerme. | La coordinación existe solo entre verbos intransitivos (`v_s 'y' v_s`); aquí el primero tiene objeto directo |
| 51 | El perro duerme y la gata come. | No hay coordinación de oraciones completas |
| 52 | El perro no come la carne. | La negación existe solo antes de un verbo intransitivo (`'no' v_s`); aquí el verbo tiene objeto |

Ninguno se debe al vocabulario: todas las palabras del corpus están en la gramática. Son **límites de cobertura**: las cuatro se arreglan agregando producciones, como `sv_s → 'no' vt_s sn`. Pero cada arreglo se tendría que repetir para cada combinación de número, persona y tiempo. Es la misma explosión de reglas: la CFG no falla por poder expresivo, sino porque **cada combinación hay que escribirla a mano**.

**Ambigüedad.** *El perro come la carne en la casa* (id 47) recibe 2 árboles: el sintagma preposicional cuelga del verbo o del objeto. El primer árbol coincide con el `arbol_esperado`. Es la única oración ambigua del corpus para esta gramática.
