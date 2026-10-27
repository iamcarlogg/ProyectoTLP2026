"""Prueba de la gramática inicial sobre las 20 oraciones acordadas.

Colocar este archivo, motor.py y gramatica_es.py en la misma carpeta
(`fase1/`) y ejecutar `python pruebas_base.py`.
"""

from motor import parsear
from gramatica_es import GRAMATICA, INICIAL

PRUEBAS = [
    ("El perro duerme.", True),
    ("Los perros duermen.", True),
    ("Las gatas duermen.", True),
    ("El perro negro duerme.", True),
    ("La gata negra duerme.", True),
    ("Los perros negros duermen.", True),
    ("Las gatas negras duermen.", True),
    ("El perro come la carne.", True),
    ("La gata come lentamente.", True),
    ("El perro duerme en la casa.", True),
    ("Los perros negros comen rápidamente en el jardín.", True),
    ("El perro que come duerme.", True),
    ("La gata que duerme come la carne.", True),
    ("Los perros que comen duermen en la casa.", True),
    ("El perro que la gata persigue duerme.", True),
    ("La perro come.", False),
    ("El perro negra duerme.", False),
    ("El perro duermen.", False),
    ("El perro que come la carne duermen.", False),
    ("El perro come la carne en la casa.", True),
]

if __name__ == "__main__":
    for numero, (oracion, es_valida) in enumerate(PRUEBAS, 1):
        arbol = parsear(oracion, GRAMATICA, INICIAL)
        aceptada = arbol is not None
        estado = "ACEPTADA" if aceptada else "RECHAZADA"
        coincide = "SI" if aceptada == es_valida else "NO"
        print(f"{numero:02}. [{estado:9}] {oracion} | Coincide con español: {coincide}")
