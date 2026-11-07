# 4. Explosión de reglas — P2 (tarea 5, 28 oct)

**Objetivo:** medir cuánto crece la gramática al representar la concordancia de género y número con categorías separadas. Es la evidencia numérica del costo de la CFG.

**Archivo:** `analisis_explosion.py`.

```bash
python fase1/analisis_explosion.py           # tamaños y desglose
python fase1/analisis_explosion.py --probar  # además, las 20 oraciones con las tres gramáticas
```

## Cómo se cuenta

Cada alternativa del diccionario es **una producción**, incluida `[]` (ε). Por ejemplo, `sn → det n | det n adj` suma dos, y `n → 'perro' | 'gata'` también suma dos. No se cuentan los pasos internos del backtracking.

## Las tres versiones

Para no confundir el costo de la concordancia con el de agregar subordinadas, modificadores y vocabulario, se comparan tres gramáticas:

1. **Base (tarea 2):** 7 no terminales, sin concordancia ni construcciones extendidas. El script guarda una copia (`GRAMATICA_BASE`).
2. **Control sin concordancia:** se genera **automáticamente** a partir de la extendida, fusionando las categorías de género y número y quitando duplicados. Tiene las mismas construcciones y las mismas 25 palabras que la extendida. No es la gramática de la tarea 2.
3. **Extendida con concordancia (tarea 3):** el contenido real de `gramatica_es.py`.

| Versión | No terminales | Producciones | Palabras distintas |
| --- | ---: | ---: | ---: |
| Base, tarea 2 | 7 | 22 | 17 |
| Extendida **sin** concordancia (control) | 15 | 48 | 25 |
| Extendida **con** concordancia, tarea 3 | 34 | 93 | 25 |

**Descomposición:**

- De **22 a 48** (+26): ampliar construcciones y vocabulario.
- De **48 a 93** (+45): **solo** representar la concordancia, con el mismo vocabulario y las mismas construcciones.
- Total de **22 a 93** (+71): la gramática final tiene **4,23 veces** las producciones de la base, y **1,94 veces** las del control.

## Dónde aparecen las 45 producciones de la concordancia

| Grupo | Sin concordancia | Con concordancia | Aumento |
| --- | ---: | ---: | ---: |
| Reglas de oración | 1 | 4 | +3 |
| Sintagma nominal | 2 | 8 | +6 |
| Modificadores nominales | 8 | 32 | +24 |
| Relativas | 2 | 6 | +4 |
| Sintagmas verbales | 8 | 16 | +8 |
| Léxico, adverbios y SP | 27 | 27 | 0 |
| **Total** | **48** | **93** | **+45** |

La mayor duplicación está en los modificadores: las 8 alternativas de `mod` se repiten para cada una de las 4 combinaciones (`mod_ms`, `mod_fs`, `mod_mp`, `mod_fp`) = 32. Los sintagmas verbales se duplican por singular y plural (8 → 16). Las palabras no aumentan: el crecimiento viene de las **reglas de combinación**.

**Ejemplo:**

```text
# Sin concordancia (control)
oracion → sn_tipo sv

# Con concordancia (extendida)
oracion → sn_ms sv_s | sn_fs sv_s | sn_mp sv_p | sn_fp sv_p
```

La segunda versión impide «el perro duermen», a costa de enumerar cuatro casos. Sigue siendo **CFG de Tipo 2**.

## Prueba de control (`--probar`)

| Gramática | Clasificaciones correctas (20 oraciones) |
| --- | ---: |
| Base | 9/20 |
| Extendida sin concordancia | 16/20 |
| Extendida con concordancia | 20/20 |

La versión sin concordancia ya reconoce subordinadas y modificadores, pero acepta las 4 oraciones con errores de concordancia. En este set, las 45 producciones extra son lo que permite rechazar esas 4 oraciones.

## Conclusión formal

El problema que se ilustra es el **costo de especificación y mantenimiento**: cada rasgo nuevo (persona, tiempo verbal, más géneros de palabras) multiplica las alternativas en varias categorías. Las producciones siguen siendo libres de contexto (Tipo 2). Otra forma de organizar la gramática daría otros conteos: el experimento mide **esta implementación**, no una cota para toda CFG.

---

← Anterior: [3. Tabla de fallas](03_tabla_de_fallas.md) · [Índice de la Fase 1](../README.md) · Siguiente: [5. Dónde sí falla una CFG](05_donde_si_falla_la_cfg.md) →
