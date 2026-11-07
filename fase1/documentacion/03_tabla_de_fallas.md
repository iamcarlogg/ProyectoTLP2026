# 3. Tabla de fallas y relación con Chomsky — P2 (tarea 4, 28 oct)

**Objetivo:** encontrar dónde falla la gramática extendida, qué fenómeno la rompe y a qué nivel de la jerarquía de Chomsky corresponde.

**Archivo:** `pruebas_fallas.py`.

## Metodología

Las 20 oraciones de la tarea 1 ya no fallan con la gramática extendida (20/20), así que se ejecutaron **24 casos adicionales** para buscar sus límites: estructuras no cubiertas, controles positivos, errores reales de concordancia y ambigüedad. Se usó el mismo `motor.py`, la misma `gramatica_es.py` y **no se añadieron reglas especiales** para que pasaran los casos.

```bash
python fase1/pruebas_fallas.py
```

| Medida | Resultado |
| --- | ---: |
| Oraciones gramaticalmente válidas | 21 |
| Oraciones gramaticalmente inválidas | 3 |
| Válidas aceptadas | 11 |
| **Válidas rechazadas (falsos negativos)** | **10** |
| Inválidas aceptadas (falsos positivos) | 0 |
| Inválidas rechazadas | 3 |
| **Clasificaciones correctas** | **14/24** |

**Precauciones:**

- «Válida» se refiere a la gramaticalidad sintáctica; una oración puede ser extraña en significado y seguir siendo gramatical.
- La regla «implicada» se identificó leyendo las producciones, porque el motor devuelve árboles completos o una lista vacía; no señala qué regla falló.

## Fallas: oraciones correctas rechazadas

| Caso | Oración | Regla implicada o ausente | Causa del rechazo | Jerarquía de Chomsky |
| ---: | --- | --- | --- | --- |
| 3 | El perro duerme con la gata. | `sp → p sn`, pero `p → 'en'` | Falta `con` en las preposiciones. | **Tipo 2**: ampliable en CFG |
| 4 | El perro persigue a la gata. | `sv_s → vt_s sn` | Falta el objeto directo animado con `a`. No basta con añadir `a` a `p`: hay que revisar cómo se construye el objeto. | **Tipo 2**: ampliable en CFG |
| 5 | El perro no duerme. | `sv_s` y `sv_p` no admiten `no` antes del verbo. | Negación ausente. | **Tipo 2**: ampliable en CFG |
| 6 | El perro duerme porque la gata come. | `sv_*` no permite una cláusula causal al final. | Solo hay relativas, no causales. | **Tipo 2**: ampliable en CFG |
| 7 | El perro come y la gata duerme. | `oracion` tiene una sola estructura `sn sv`. | Coordinación de oraciones ausente. | **Tipo 2**: ampliable en CFG |
| 8 | El perro negro y grande duerme. | `mod_ms` no admite `adj_ms 'y' adj`; no existe `grande`. | Coordinación de adjetivos y vocabulario. | **Tipo 2**: ampliable en CFG |
| 9 | El perro muy negro duerme. | No existe `adv_grado adj_ms`. | Intensificador ausente. | **Tipo 2**: ampliable en CFG |
| 10 | El perro negro pequeño duerme. | `mod_ms` admite un solo adjetivo; no existe `pequeño`. | Secuencia de adjetivos y vocabulario. | **Tipo 2**: ampliable en CFG |
| 20 | ¿El perro duerme? | `motor.py` quita puntos y comas, pero no `¿` ni `?`. | Las palabras quedan `¿el` y `duerme?`: es un problema de preprocesamiento. | **No es un salto de nivel** |
| 21 | El perro y la gata duermen. | `sn_ms`/`sn_fs` forman un SN simple, no un sujeto coordinado. | Coordinación nominal y su plural ausentes. | **Tipo 2**: ampliable en CFG |

**Interpretación:** todos estos rechazos se explican por reglas que faltan o por cómo se prepara la entrada. Ninguno demuestra que una gramática de Tipo 2 sea insuficiente. Que una oración sea larga o tenga una subordinada no prueba, por sí solo, que haga falta Tipo 1.

## Rechazos correctos y controles

| Caso | Oración | Resultado | Explicación |
| ---: | --- | --- | --- |
| 15 | El perro que la gata persiguen duerme. | Rechazada (bien) | `rel_obj → 'que' sn_fs vt_s` exige `persigue`; `persiguen` es `vt_p`. Concordancia dentro de la relativa. |
| 16 | Los perros que comen duerme. | Rechazada (bien) | `oracion → sn_mp sv_p` exige verbo principal plural, aunque haya una relativa en medio. |
| 24 | El perro duerme la carne. | Rechazada (bien) | `duerme` no está entre los transitivos `vt_s`. |
| 1, 2, 11–14, 17, 22, 23 | Oraciones de control | Aceptadas | Confirman que funcionan relativas, concordancias, adverbios y preposiciones dentro del alcance. |
| 18 | La carne negra duerme. | Aceptada | Sintácticamente bien formada, aunque rara. El parser **no** revisa el significado. |
| 19 | El perro come la carne en la casa. | Aceptada, **dos árboles** | `sp` puede colgar de `sv_s` o del `sn` objeto. Es **ambigüedad estructural**, no una falla. |

## Relación con la jerarquía de Chomsky

- **Tipo 2 (libres de contexto):** todas nuestras producciones tienen un solo no terminal a la izquierda (`A → ...`). Los falsos negativos se explican por vocabulario reducido y reglas no implementadas. La concordancia de rasgos finitos (género y número) se puede codificar con categorías `_ms`, `_fs`, `_mp`, `_fp` sin salir de Tipo 2.
- **Tipo 1 (sensibles al contexto):** hay lenguajes que necesitan más poder expresivo, pero **ninguno de los ejemplos probados demuestra que la CFG sea insuficiente como clase formal**. La «concordancia a distancia» de nuestros ejemplos tampoco requiere Tipo 1, porque los rasgos son finitos.
- **Ambigüedad:** el caso 19 tiene dos análisis con una CFG de Tipo 2. Tener varios árboles es una propiedad de la gramática, no un fallo ni evidencia de Tipo 1.
- **Semántica:** «La carne negra duerme» muestra que reconocer la sintaxis no es entender el significado. Eso no corresponde a otro nivel de Chomsky.
- **Dependencias cruzadas:** ninguna de nuestras oraciones tiene dependencias cruzadas, que son el fenómeno que sí excede a una CFG. Se explica en el [documento 5](05_donde_si_falla_la_cfg.md).

## Conclusión

Encontramos reglas ausentes, concordancias que la CFG sí resuelve, ambigüedad reconocida y un problema de preprocesamiento. Es evidencia de los límites de *esta gramática controlada*, no una prueba de que ninguna CFG pueda describir esas oraciones. El costo de la concordancia se mide en el [documento 4](04_explosion_de_reglas.md), y lo que sí rompe a una CFG se explica en el [documento 5](05_donde_si_falla_la_cfg.md).

---

← Anterior: [2. Gramática del español](02_gramatica_espanol.md) · [Índice de la Fase 1](../README.md) · Siguiente: [4. Explosión de reglas](04_explosion_de_reglas.md) →
