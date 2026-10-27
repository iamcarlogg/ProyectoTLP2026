"""P2 — Producciones base del español (Fase 1).

Gramática inicial para el motor descendente recursivo de P1.
Esta versión comprueba el orden básico de las palabras, pero todavía
NO controla concordancia, subordinadas ni modificadores adverbiales
/ preposicionales. Esos fenómenos se incorporan en la siguiente etapa.

Interfaz acordada con P1: GRAMATICA (dict) e INICIAL (str).
Las categorías y los terminales se escriben en minúsculas.
"""

GRAMATICA = {
    # Estructura de una oración: sujeto y predicado.
    "oracion": [["sn", "sv"]],

    # Sintagma nominal: determinante + sustantivo (+ adjetivo opcional).
    "sn": [["det", "n"], ["det", "n", "adj"]],

    # Sintagma verbal: verbo intransitivo o verbo con objeto directo.
    "sv": [["v"], ["v", "sn"]],

    # Vocabulario de la primera versión.
    "det": [["el"], ["la"], ["los"], ["las"]],
    "n": [["perro"], ["perros"], ["gata"], ["gatas"], ["carne"]],
    "adj": [["negro"], ["negros"], ["negra"], ["negras"]],
    "v": [["come"], ["comen"], ["duerme"], ["duermen"]],
}

INICIAL = "oracion"
