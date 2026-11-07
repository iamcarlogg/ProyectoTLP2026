# Decisiones y convenciones del equipo

Este documento reúne los acuerdos vigentes del equipo. Cuando se toma una decisión nueva, se agrega una fila al registro y se actualiza la sección correspondiente. Lo técnico de cada fase (gramáticas, resultados) está en la documentación de esa fase.

## Registro de decisiones

| Fecha | Decisión |
| --- | --- |
| 2026-11-05 | P3: spaCy usa el modelo `es_core_news_md`; las oraciones se pasan tal como están escritas |
| 2026-11-05 | P3: spaCy «rechaza» una oración si sus rasgos muestran un error de concordancia (`errores_concordancia()` en `tabla_nlp.py`) |
| 2026-11-05 | Fechas extendidas: Fase 1 el 7 de noviembre y Fase 2 el 18 de noviembre |
| 2026-10-25 | Pruebas en `test_parser_formal.py`: 24 casos, incluido uno con comentarios `//` |
| 2026-10-25 | Parser de mini-C: interfaz `parsear_codigo(codigo)`, árbol `nltk.Tree` con un nodo por no terminal y el `else` en un nodo `sino` |
| 2026-10-25 | Errores del parser: `Línea N: se esperaba X y se encontró Y` |
| 2026-10-21 | Abreviaturas de categorías del español: oracion, sn, sv, sp, det, n, v, adj, p |
| 2026-10-21 | Motor genérico: gramática como diccionario, no terminales y palabras en minúscula, símbolo inicial `oracion` |
| 2026-10-20 | `.venv` en la raíz del repositorio y fuera de Git; dependencias en `requirements.txt` |
| 2026-10-20 | El lexer ignora comentarios de una línea (`//`) |
| 2026-10-20 | Notación: EBNF con flechas; terminales en MAYÚSCULAS, no terminales en minúscula, texto literal entre comillas |
| 2026-10-20 | El parser de mini-C se llama `parser_formal.py`, no `parser.py` |
| 2026-10-20 | Subconjunto mini-C aprobado por el docente |

## Acuerdos que conectan los roles

Sin estos acuerdos, el trabajo de cada rol no encaja con el de los demás.

| Acuerdo | Detalle | Quién lo define → quién lo usa |
| --- | --- | --- |
| Formato de árbol común | Notación de corchetes de `nltk.Tree` para el parser, NLP y LLM. Sin esto, las métricas no son comparables. | Todos |
| Interfaz `parsear(oracion)` | Devuelve el árbol o `None`. | P1 → P3 y P4 |
| Formato del set de prueba | CSV con columnas `id, oracion, nivel, esperado, arbol_esperado` (`esperado` = acepta o rechaza). | P2 → P3 y P4 |
| Oraciones a tiempo | Fase 1 antes del 22 oct (cumplido); set de la Fase 2 antes del 7 nov. | P2 → todos |
| Informe por secciones | Cada integrante redacta la suya; P4 integra y unifica. | Todos → P4 |
| Revisión cruzada de código | P1 con P2, P3 con P4. | Todos |
| Asistencia | Al menos 3 de los 4 integrantes en cada presentación. | Todos |

## Notación de las gramáticas

Todas las gramáticas del informe se escriben en EBNF con flechas. En el informe se dice "notación EBNF", no "BNF".

| Elemento | Cómo se escribe | Ejemplo |
| --- | --- | --- |
| No terminal | minúsculas, sin comillas | `expr`, `sentencia`, `sn` |
| Terminal que es una clase de token | MAYÚSCULAS, sin comillas | `ID`, `NUM`, `OP_REL`, `EOF` |
| Terminal con texto exacto | entre comillas simples | `'if'`, `';'`, `'+'`, `'perro'` |
| "está hecho de" | `→` | `bloque → '{' sentencia* '}'` |
| "o" | `\|` | `tipo → 'int' \| 'float'` |
| Cero o más veces | `*` | `sentencia*` |
| Opcional | `?` | `( 'else' sentencia )?` |
| Agrupar | `( )` | `( '+' \| '-' )` |
| Producción vacía | `ε` | `mod_ms → ε \| adj_ms` |

Las palabras reservadas van en minúscula porque están entre comillas: lo que va entre comillas es el texto literal, y en C se escribe `if`.

En el código se mantiene la misma correspondencia: cada no terminal `x` es la función `x()` del parser de mini-C, y cada terminal en mayúsculas es el tipo de token del mismo nombre en el lexer.

## Motor genérico: reglas para escribir una gramática

El motor (`fase1/motor.py`) analiza con cualquier gramática escrita como diccionario de Python, usa backtracking y devuelve todos los árboles posibles. Quien escribe la gramática solo edita su archivo de gramática; nunca toca `motor.py`.

1. Clave = no terminal; valor = lista de producciones; cada producción = lista de símbolos. `"sv": [["v", "sn"], ["v"]]` es `sv → v sn | v`.
2. Lo que no es clave del diccionario es una palabra (terminal).
3. Todo en minúsculas, porque el motor pasa la oración a minúsculas.
4. Ningún no terminal puede llamarse igual que una palabra. Por eso el símbolo inicial es `oracion` y no `o` (que chocaría con la conjunción «o»).
5. `[]` es la producción vacía (ε).
6. Prohibida la recursión por la izquierda (`sn → sn adj`): da `RecursionError`. Se reescribe a la derecha: `sn → det n adjs`, `adjs → adj adjs | ε`.
7. Concordancia: sufijos `_ms`, `_fs`, `_mp`, `_fp` (masculino o femenino, singular o plural) y `_s`, `_p` para el número del verbo.

### Interfaz del motor

| Función | Devuelve |
| --- | --- |
| `todos_los_arboles(oracion, gramatica, inicial)` | lista de todos los árboles que cubren la oración completa; vacía = rechazada; más de uno = ambigua |
| `parsear(oracion, gramatica, inicial)` | el primer árbol, o `None` si se rechaza |

Antes de analizar, el motor pasa la oración a minúsculas y quita puntos y comas (no quita `¿` ni `?`). No lanza excepciones.

### Abreviaturas de categorías

| Abreviatura | Nombre | Ejemplos |
| --- | --- | --- |
| `oracion` | Oración (símbolo inicial) | sujeto + predicado |
| `sn` | Sintagma nominal | el perro negro |
| `sv` | Sintagma verbal | come la carne |
| `sp` | Sintagma preposicional | en la casa |
| `det` | Determinante | el, la, los, las |
| `n` | Nombre (sustantivo) | perro, carne |
| `v` / `vt` | Verbo / verbo transitivo | duerme / persigue |
| `adj` | Adjetivo | negro |
| `adv` | Adverbio | lentamente |
| `p` | Preposición | en |
| `mod` | Modificadores del nombre | negro, en la casa, que come |
| `rel_suj` / `rel_obj` | Relativa de sujeto / de objeto | que come / que la gata persigue |

En la gramática del español, `det`, `n`, `v`, `adj` y `p` son no terminales (preterminales): tienen reglas que llevan directo a una palabra. Los terminales son las palabras. En mini-C, en cambio, `ID` es terminal porque lo clasifica el lexer; el motor del español no tiene lexer.

## Repositorio y entorno

- El entorno virtual `.venv` vive en la raíz del repositorio y nunca se sube a Git; cada integrante lo crea con `requirements.txt`.
- Python 3.10 o más reciente.
- Lo que pertenece a una fase va en su carpeta (`fase1/`, `fase2/`); lo que vale para todo el proyecto va en `docs/`.
- `pytest -v` antes de cada `git push`.
- Un commit al final de cada día, con un mensaje que diga qué se hizo.

## Pendientes

Fase 1:

- [x] Confirmar que los comentarios `//` entran en el alcance de mini-C (el lexer los descarta y hay una prueba).
- [x] Avisar a P2 de las reglas del motor y de la convención de minúsculas (la gramática extendida las cumple).
- [x] Subir la demo de NLP de P3 (`demo_nlp.py`, `tabla_nlp.py`, `visualizar_nlp.py`) al repositorio.

Fase 2:

- [ ] Decidir cómo se maneja la concordancia: duplicar no terminales (CFG pura, como en la Fase 1) o rasgos chequeados al construir el nodo (ya no es CFG pura; se aclara en el informe).
- [ ] Decidir si `parsear()` devuelve el primer árbol o todos (devolver todos permite medir cuántas oraciones son ambiguas).
- [ ] Decidir el criterio de acierto para el LLM y para HuggingFace. Para spaCy, la Fase 1 usó una regla de concordancia; revisar si alcanza para la Fase 2.
- [ ] Decidir cómo importa la Fase 2 el motor de `fase1/` (copiarlo o añadir `fase1/` al `sys.path`).
