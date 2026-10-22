"""Gramática de ejemplo del español.
OJO: hay que reemplazarla por la gramática real (la edita P2).

Cada regla: "nombre": [ [opción 1], [opción 2], ... ]
Lo que no tiene reglas propias (como "perro") se trata como palabra.
Sufijos: _ms masculino singular, _fs femenino singular, _mp masculino plural.
"""

GRAMATICA = {
    "oracion": [["sn", "sv"]],                        # sujeto + predicado
    "sn":      [["sn_ms"], ["sn_fs"], ["sn_mp"]],
    "sn_ms":   [["det_ms", "n_ms", "adj_ms"], ["det_ms", "n_ms"]],
    "sn_fs":   [["det_fs", "n_fs"]],
    "sn_mp":   [["det_mp", "n_mp"]],
    "sv":      [["v", "sn"], ["v"]],
    "det_ms":  [["el"]],
    "det_fs":  [["la"]],
    "det_mp":  [["los"]],
    "n_ms":    [["perro"]],
    "n_fs":    [["carne"]],
    "n_mp":    [["perros"]],
    "adj_ms":  [["negro"]],
    "v":       [["come"], ["duerme"], ["comen"], ["duermen"]],
}

INICIAL = "oracion"
