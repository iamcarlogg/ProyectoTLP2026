# P2 — Producciones base de la gramática del español

**Proyecto:** Gramáticas formales y lenguaje natural: experimentando los límites de la jerarquía de Chomsky  
**Fase:** 1 — Extensión al español y análisis de fallas  
**Responsable:** P2 — Gramáticas  
**Entrega:** Producciones base del español (24 de octubre de 2026)

## 1. Objetivo

Definir una **gramática libre de contexto (CFG) inicial** que reconozca algunas estructuras sencillas del español y pueda ser procesada por `motor.py`, desarrollado por P1.

En esta versión se valida principalmente el **orden de las categorías gramaticales**. Aún no se comprueba la concordancia de género y número, ni se incluyen oraciones subordinadas, adverbios o sintagmas preposicionales. Esos elementos se incorporarán en la siguiente tarea.

## 2. Símbolos utilizados

| Símbolo | Significado | Ejemplo |
|---|---|---|
| `oracion` | Oración completa | El perro duerme |
| `sn` | Sintagma nominal | El perro negro |
| `sv` | Sintagma verbal | Come la carne |
| `det` | Determinante | el, la, los, las |
| `n` | Sustantivo | perro, gata, carne |
| `adj` | Adjetivo | negro, negra |
| `v` | Verbo | come, duermen |

El **símbolo inicial** es `oracion`.

## 3. Reglas de producción

Se usa la notación adoptada por el equipo: flecha `→`, alternativas con `|`, no terminales en minúscula y palabras literales entre comillas simples.

```text
oracion → sn sv

sn      → det n | det n adj

sv      → v | v sn

det     → 'el' | 'la' | 'los' | 'las'

n       → 'perro' | 'perros' | 'gata' | 'gatas' | 'carne'

adj     → 'negro' | 'negros' | 'negra' | 'negras'

v       → 'come' | 'comen' | 'duerme' | 'duermen'
```

### Explicación sencilla

- `oracion → sn sv`: una oración se forma con un sujeto y un predicado.
- `sn → det n | det n adj`: el sujeto puede tener determinante y sustantivo, con un adjetivo opcional.
- `sv → v | v sn`: el predicado puede contener solo un verbo o un verbo seguido de un sintagma nominal.
- `det`, `n`, `adj` y `v`: indican las palabras que la gramática reconoce en esta primera versión.

## 4. Ejemplo de derivación

Oración: **El perro negro come la carne.**

```text
oracion
→ sn sv
→ det n adj sv
→ 'el' 'perro' 'negro' sv
→ 'el' 'perro' 'negro' v sn
→ 'el' 'perro' 'negro' 'come' det n
→ 'el' 'perro' 'negro' 'come' 'la' 'carne'
```

La oración puede analizarse porque sus palabras se ajustan a una secuencia permitida por las reglas.

## 5. Implementación en Python

Las producciones anteriores se representan en el archivo **`fase1/gramatica_es.py`**, utilizando el contrato acordado con P1:

```python
GRAMATICA = {
    "oracion": [["sn", "sv"]],
    "sn": [["det", "n"], ["det", "n", "adj"]],
    "sv": [["v"], ["v", "sn"]],
    "det": [["el"], ["la"], ["los"], ["las"]],
    "n": [["perro"], ["perros"], ["gata"], ["gatas"], ["carne"]],
    "adj": [["negro"], ["negros"], ["negra"], ["negras"]],
    "v": [["come"], ["comen"], ["duerme"], ["duermen"]],
}

INICIAL = "oracion"
```

Esta representación conserva las mismas producciones: cada clave es un **no terminal** y cada lista interna representa una alternativa. `INICIAL` indica desde qué regla empieza el análisis.

## 6. Alcance y limitaciones de la versión base

**Casos que la gramática puede reconocer:**

- `El perro duerme.`
- `Los perros negros duermen.`
- `El perro come la carne.`

**Casos que muestran lo que todavía falta implementar:**

- `La perro come.`: actualmente puede aceptarse porque no se verifica la concordancia determinante–sustantivo.
- `El perro duermen.`: actualmente puede aceptarse porque no se verifica la concordancia sujeto–verbo.
- `El perro que come duerme.`: se rechaza porque aún no hay reglas para subordinadas.
- `La gata come lentamente.`: se rechaza porque aún no hay reglas para adverbios.

**Importante:** estos resultados no prueban que toda CFG sea incapaz de representar dichos fenómenos; muestran limitaciones **de esta versión inicial**. En próximas tareas se añadirán reglas y se comparará su comportamiento con el de la versión base.

## 7. Pruebas y archivos relacionados

- `fase1/gramatica_es.py`: reglas de producción implementadas en Python.
- `fase1/motor.py`: parser de P1; utiliza la gramática, pero no debe modificarse desde P2.
- `fase1/pruebas_base.py`: pruebas con las 20 oraciones de la primera entrega.
- `fase1/documentacion/`: documentación del conjunto de oraciones y de estas reglas.

Desde la carpeta `fase1/`, ejecutar:

```bash
python pruebas_base.py
```

Los resultados obtenidos deben guardarse como **línea base** para compararlos con las extensiones de concordancia, subordinación y modificadores de la tercera tarea.
