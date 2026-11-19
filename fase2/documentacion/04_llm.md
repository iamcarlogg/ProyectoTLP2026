# 4. LLM — P4 (Allan)

## Estado

Preparación nueva del 18 de noviembre de 2026 con el corpus y evaluador actuales.
Corrida completada el 18 de noviembre de 2026: 60 respuestas zero-shot y 60
few-shot de `gemini-3.1-flash-lite`. No se reutilizaron respuestas de intentos
anteriores. La primera llamada de prueba del ID 1 forma parte del log zero-shot
y no se repitió. Resultados oficiales: `fase2/resultados/tablas.md`.

Proveedor vigente: Google Gemini, a petición de Allan. Modelo seleccionado:
`gemini-3.1-flash-lite`, API `v1beta`, temperatura solicitada 0,
`thinkingConfig.thinkingLevel=MINIMAL` y `maxOutputTokens=2048`.
La primera solicitud de generación con estos parámetros fue aceptada por la API;
eso no demuestra determinismo ni que exista cuota suficiente para toda la corrida.
`MINIMAL` no significa razonamiento desactivado.
La clave `GEMINI_API_KEY` se carga del entorno o `.env` solo con `--ejecutar`.
El contador de tokens la lee solo con `--consultar`. Los modos locales no leen claves.

Se eligió una variante Flash-Lite por costo y volumen, sin usar el modelo de mayor
capacidad. Google publica nivel gratuito sujeto a cuotas; tarifa estándar de texto
pagada: USD 0.25 por millón de tokens de entrada y USD 1.50 por millón de salida
(incluido razonamiento). Tener Google AI Pro no permite inferir la cuota o el estado
de facturación del proyecto. Sus créditos de desarrollador requieren reclamación.

Google desaconseja personalizar los parámetros de muestreo en Gemini 3.x. Se solicita
0 para conservar el requisito experimental del equipo y se registrará lo enviado;
no se promete determinismo. No se cambiará silenciosamente a un modelo que ignore
el parámetro si la API rechaza esta configuración.

Fuentes oficiales consultadas el 18 de noviembre:
- [Modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite).
- [Precios](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite).
- [Parámetros de muestreo](https://aistudio.google.com/docs/whats-new-gemini-3.5#sampling-parameters).
- [Beneficios de Google AI Pro](https://developers.google.com/profile/help/benefits).

Antecedente de conexión, separado de resultados: el contador de Anthropic devolvió
HTTP 400 por saldo insuficiente; no generó respuestas. `05_verificacion_api.json`
conserva ese diagnóstico histórico y su estimación de costo NO se aplica a Gemini.
La comprobación de Google está en `06_verificacion_gemini.json`; la auditoría
final y las huellas de todos los resultados están en `07_auditoria_corrida.json`.

Comprobación de Google completada el 18 de noviembre: `countTokens` respondió
correctamente a cuatro consultas, con 2722 y 2731 tokens para zero-shot (IDs 1 y
48), y 3140 y 3149 para few-shot. La muestra estima 352260 tokens de entrada
para las 120 solicitudes: USD 0.088065 con tarifa de pago de texto. La salida
de 120 solicitudes a 2048 tokens supondría USD 0.36864 adicionales; total
orientativo USD 0.456705 si todas agotaran ese límite. No es el costo real final,
ni una garantía sobre cuota gratuita, créditos activados o saldo de la cuenta.
En esa etapa no se generaron respuestas. `countTokens` no prueba que `generateContent` admita
todos los parámetros configurados ni confirma disponibilidad de cuota de generación.

Prueba posterior de generación: una sola solicitud real de zero-shot, ID 1,
«El perro duerme.», respondió `acepta` con un árbol válido que coincide con el
esperado (ignorando espacios de formato). Modelo devuelto `gemini-3.1-flash-lite`,
terminación `STOP`, 2722 tokens de entrada y 55 de salida; total 2777. El costo
equivalente a tarifa de pago es USD 0.000763; no se infiere un cargo efectivo ni
el estado de los créditos. La respuesta, prompt y timestamps se conservan en
`logs/llm_zero_shot.json`. No se volverá a consultar este ID al reanudar.

## Corredor y conservación de evidencia

`fase2/llm_experimento.py` realiza POST directos a `generateContent` de Gemini mediante
la biblioteca estándar de Python. No necesita SDK ni paquetes adicionales.
Cada solicitud lleva exactamente un mensaje de usuario, sin herramientas ni
historial. Timeout de 120 segundos, pausa de un segundo entre respuestas y
cero reintentos automáticos. No se fuerza un esquema de salida en la API:
el cumplimiento del formato solicitado forma parte del experimento.

Antes de enviar guarda prompt, ID, oración, timestamp UTC e identificador del
intento. Después guarda la respuesta HTTP completa antes de interpretarla.
El resultado incluye `respuesta_completa`, árbol/veredicto interpretados,
modelo devuelto (`modelVersion`), uso de tokens (`usageMetadata`), motivo de
terminación e identificador de respuesta. Se conserva la respuesta HTTP íntegra,
incluidos los bloques de pensamiento si el servicio los devuelve; el texto final
excluye partes marcadas `thought`. Solo `finishReason=STOP` se considera completo;
filtros de seguridad, ausencia de candidatos y truncamientos producen `invalida`.
Los metadatos registran modelo solicitado, parámetros y huellas SHA-256 de
entradas, prompts y código. Se usan escrituras atómicas para evitar JSON parcial.

Reanudar omite resultados existentes (también inválidos) y recupera respuestas
ya recibidas sin otra consulta. Un error de API no se convierte en dato lingüístico:
queda en `intentos`, con código seguro, y detiene la ejecución. Repetir un intento
sin respuesta requiere `--reintentar-errores`; no se garantiza evitar un segundo
cobro si el servidor procesó el primero pero se perdió la respuesta. No mezclar
configuraciones. Un bloqueo de archivo impide dos corridas simultáneas.

Durante la ejecución completa Google devolvió HTTP 503 (`UNAVAILABLE`) de forma
intermitente. Se añadió el auxiliar operativo `continuar_corrida.py`, sin cambiar
el código congelado del corredor, los prompts ni los parámetros. El auxiliar
reanuda solo errores 503 explícitos con pausas de 15, 30 y 45 segundos y un máximo
de tres reintentos consecutivos sin progreso; se detiene ante 429, timeouts o
intentos ambiguos. Cada intento fallido permanece en el log y no se convierte en
un rechazo del modelo. No se repiten resultados existentes.

Para ejecutar el evaluador se preparó un entorno local `.venv` con Python 3.12.14,
NLTK 3.10.3 y matplotlib 3.11.2. La evaluación usa los logs de P1/P3, sin volver
a generar esas respuestas ni volver a entrenar NLTK.

## Prompts exactos y construcción

- Instrucciones comunes: `fase2/prompts/base.txt`.
- Gramática: contenido íntegro de `fase2/gramatica_es.txt`, sin reescribir reglas.
- Few-shot: `fase2/prompts/few_shot.json`, cinco ejemplos fijos.
- Constructor: `fase2/preparar_prompts.py`, función `construir_prompt`.

Zero-shot concatena instrucciones, gramática y oración. Few-shot usa exactamente
lo mismo e inserta los cinco ejemplos antes de la oración. La oración se conserva
tal como está en el CSV; se solicita al modelo la misma normalización del motor.
No se envían IDs, niveles, etiquetas humanas, árboles esperados ni resultados de P3.
Cada llamada guarda el prompt expandido exacto en su log; esos son los prompts
experimentales completos que deben incluirse como evidencia, sin reconstruirlos
a partir de respuestas esperadas.

Vista previa local, sin API:

```powershell
python fase2/preparar_prompts.py --variante zero-shot --id 1
python fase2/preparar_prompts.py --variante few-shot --id 1
```

Los ejemplos cubren pretérito con adverbio, primera persona con objeto, relativa
de objeto, desacuerdo de adjetivo y una oración correcta en español fuera de la
CFG. Son distintos del corpus incluso después de normalizar mayúsculas,
puntuación y espacios. El último enseña explícitamente la distinción entre
gramaticalidad española y pertenencia a la CFG; esto forma parte del tratamiento
few-shot y debe declararse al interpretar mejoras en casos del mismo fenómeno.

## Contrato de respuesta para el corredor

JSON sin Markdown, exactamente con `salida` (`acepta` o `rechaza`) y `arbol`
(cadena con árbol si acepta; null si rechaza). No se solicitan justificaciones.
El corredor conserva la respuesta HTTP íntegra antes de interpretarla y el texto
final completo en `respuesta_completa`.
JSON ilegible, claves/tipos incorrectos, veredicto desconocido, árbol ausente al
aceptar o árbol sintácticamente ilegible implican `salida: "invalida"`.

Una derivación que viola la CFG o un veredicto equivocado son errores del modelo:
se conserva su veredicto legible, sin sustituirlo por el del parser. La comprobación
de producciones, raíz y hojas se registra aparte. Un fallo de red no es un rechazo
lingüístico. No se corrigen respuestas manualmente.

## Resultados finales

Las cifras de las tablas siguientes proceden de `fase2/resultados/tablas.md`,
generado con `fase2/evaluar.py` sin modificar ese script.

| Medida | Zero-shot | Few-shot |
| --- | ---: | ---: |
| Exactitud frente al español | 54/60 (90,0 %) | 55/60 (91,7 %) |
| Precisión | 97,2 % | 97,3 % |
| Cobertura (recall) | 87,5 % | 90,0 % |
| Rechazo correcto | 95,0 % | 95,0 % |
| VP / FN / FP / VN | 35 / 5 / 1 / 19 | 36 / 4 / 1 / 19 |
| Fidelidad del veredicto a la CFG | 54/60 (90,0 %) | 59/60 (98,3 %) |
| Correctas fuera de la CFG aceptadas | 2/4 | 0/4 |
| Respuestas inválidas | 3 | 0 |
| Errores de etiquetado entre VP | 6 | 0 |
| Árbol distinto de una referencia válida entre VP | 25 | 6 |
| Nivel 1 | 18/20 | 20/20 |
| Nivel 2 | 19/20 | 20/20 |
| Nivel 3 | 17/20 | 15/20 |

### ¿Respeta las reglas o usa su conocimiento general del español?

| ID | Oración correcta en español, fuera de la CFG | Zero-shot | Few-shot |
| --- | --- | --- | --- |
| 49 | El perro y la gata duermen. | rechaza | rechaza |
| 50 | El perro come la carne y duerme. | acepta | rechaza |
| 51 | El perro duerme y la gata come. | rechaza | rechaza |
| 52 | El perro no come la carne. | acepta | rechaza |

Zero-shot se desvía en 50 y 52: aceptar construcciones no generadas contradice
las reglas suministradas. Few-shot rechaza las cuatro y respeta ese límite.
La aceptación no demuestra por sí sola el mecanismo interno que produjo la
respuesta; es evidencia observable de incumplimiento de la especificación,
compatible con recurrir a patrones generales del español.

Rechazar 49–52 es un acierto respecto a la CFG y un falso negativo respecto a
`esperado`, que representa corrección en español. Por eso few-shot baja de 17/20
a 15/20 en el nivel 3 mientras mejora en fidelidad: sus rechazos nuevos de 50 y
52 son deseables para la pregunta sobre obediencia formal. No se deben tratar
las dos tablas como si midieran el mismo objetivo.

La fidelidad del evaluador usa solamente el veredicto. El 98,3 % no significa que
el 98,3 % de los árboles sean derivaciones correctas. La auditoría adicional
comprueba raíz, cada producción y hojas en orden: zero-shot entrega 10 árboles
válidos en 36 aceptaciones; few-shot, 30 en 37. Los restantes son errores del
modelo y se conservaron sin reparación. Estos denominadores incluyen el FP 56,
a diferencia de la fila de árboles del evaluador, limitada a los VP.

### ¿Mejora few-shot?

En esta corrida, sí mejora el seguimiento de reglas (+5 decisiones fieles de 60),
el formato (3 inválidas a 0), el etiquetado entre VP (6 a 0) y los árboles
incorrectos entre VP (25 a 6). La exactitud española solo mejora en un caso neto:
recupera las respuestas inválidas 4, 11 y 26, pero rechaza 50 y 52 por fidelidad
a la CFG. No confundir +1,7 puntos de exactitud con +8,3 puntos de fidelidad.

Los cinco cambios de veredicto entre variantes son esos cinco IDs. El few-shot
incluye un ejemplo externo del mismo fenómeno de negación con objeto que 52,
por lo que esta mejora es transferencia desde una demostración pertinente,
no una prueba de generalización a cualquier construcción.

### Errores concretos que deben discutirse

- **Formato zero-shot:** IDs 4, 11 y 26 son `invalida` por árboles sintácticamente
  ilegibles. El ID 4 incluye un nodo sin etiqueta `()`. Las respuestas HTTP
  terminaron con `STOP`: no fueron truncamientos por agotar 2048 tokens.
- **Producciones y hojas:** zero-shot puso palabras entre comillas literales
  dentro de árboles (por ejemplo ID 2), añadió categorías no permitidas y
  estructuras epsilon incorrectas. En ID 25 aparece `(mod_ms (mod_ms))`, una
  producción inexistente. El few-shot corrige ese caso. No se quitaron comillas
  ni se repararon árboles a mano.
- **ID 47, ambigüedad:** ambos aceptan, pero ambos producen árboles inválidos.
  Zero-shot adjunta `sp` dentro de `sn` mediante una producción inexistente;
  few-shot introduce `(mod_fs (mod_ms))` dentro del complemento. El error no es
  elegir la segunda lectura: el evaluador permite las dos derivaciones válidas.
- **ID 56, único FP en ambas variantes:** «El perro negro que comen duerme.»
  es aceptada a pesar del desacuerdo de número. Few-shot escribe `(v_s comen)`,
  aunque `comen` solo es plural en esta gramática. Zero-shot además inserta
  palabras ausentes de la entrada. Es el único veredicto infiel restante de
  few-shot y un contraejemplo a afirmar obediencia perfecta.
- **Etiquetas y estructura:** tener cero errores de etiquetado en few-shot no
  elimina sus seis árboles incorrectos entre VP. El evaluador reduce las
  categorías a clases comunes; la derivación completa impone más condiciones.

## Ejecución, costo y reproducibilidad

Se conservaron 163 intentos: 120 respuestas y 43 errores operativos (42 HTTP 503
y un HTTP 429). El 429 se detuvo para revisión; una solicitud posterior fue
aceptada y se redujo la frecuencia a cinco segundos entre respuestas. Ante 503,
las pausas fueron 15, 30 y 45 segundos, con un máximo de tres reintentos
consecutivos sin progreso por invocación. Tras revisar las detenciones se
priorizaron entradas con menos fallos; 39 y 53 de few-shot se pospusieron sin
excluirlas. El orden físico del log no siempre es el orden de IDs; el evaluador
cruza por ID. No hubo respuestas duplicadas ni cambios de prompts, modelo o
parámetros durante la corrida.

| Uso reportado por la API | Zero-shot | Few-shot | Total |
| --- | ---: | ---: | ---: |
| Tokens de entrada | 163459 | 188539 | 351998 |
| Tokens de salida visible | 3297 | 3084 | 6381 |
| Tokens de pensamiento reportados | 0 | 0 | 0 |
| Equivalente a tarifa estándar, USD | 0.04581025 | 0.05176075 | 0.097571 |

Ese equivalente usa USD 0.25/millón de entrada y USD 1.50/millón de salida; no
confirma un cargo efectivo, saldo o crédito aplicado y no incluye impuestos ni
descuentos. No hay tokens de generación reportados para los errores HTTP. El
mayor tiempo de espera provino de red, servicio y pausas: no debe compararse con
el tiempo de cómputo local del parser como si ambos midieran lo mismo.

Auditoría final: exactamente 60 IDs únicos por variante, textos idénticos al
corpus, prompts iguales al constructor congelado, respuesta HTTP íntegra,
interpretación reproducida, timestamps coherentes, mismo modelo devuelto y
huellas de fuentes coincidentes. No se encontró la clave en los logs. Dieciséis
pruebas locales sin red pasan. Dos ejecuciones de `evaluar.py` produjeron los
seis archivos de resultados idénticos byte a byte, incluidas las dos gráficas,
que se inspeccionaron visualmente. Las huellas están en `07_auditoria_corrida.json`.

## Alcance de las conclusiones y siguiente entrega

El resultado describe un solo modelo, una corrida por variante y un corpus
manual de 60 oraciones. Temperatura solicitada 0 no garantiza nuevas respuestas
idénticas al volver a consultar. La reproducibilidad exigida se obtiene al
recalcular desde los logs guardados, sin volver a usar la API.

La comparación con spaCy/NLTK mide además sus reglas propias de aceptación;
NLTK tiene un adaptador más elaborado. Los casos 59 y 60 incluyen posición del
adjetivo y enlace entre verbos: no describir todas las negativas como errores
exclusivamente de concordancia. Los rechazos 49–52 muestran cobertura faltante
de esta CFG, no una imposibilidad formal de modelarlos con otras producciones.

El experimento, su análisis y el informe final están listos. PDF:
`output/pdf/informe_fase2.pdf` (10 páginas principales más 9 de anexos).
Paquete con código y evidencia: `output/pdf/entrega_fase2.zip`. P3 puede actualizar su documento 03 con las
cifras oficiales de `resultados/tablas.md`; no se reescribió su sección.
