"""P2, tarea 4: pruebas adicionales para documentar los limites de la CFG.

No sustituye las 20 entradas de pruebas_base.py. Los casos se eligieron
para explorar estructuras no cubiertas y casos de control, incluida la
ambiguedad. Ejecutar desde la raiz: python fase1/pruebas_fallas.py

'es_valida' indica correccion gramatical del espanol (no plausibilidad
semantica). 'aceptacion_t3' registra la salida comprobada de la gramática
extendida de la tarea 3. Al modificar la gramatica se notifican cambios.
"""

from motor import todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL


# (oracion, es_valida_gramaticalmente, aceptacion_observada_en_tarea_3, descripcion)
CASOS = [
    ("El perro que la gata persigue duerme.", True, True, "control: relativa de objeto"),
    ("Los perros negros comen rápidamente en el jardín.", True, True, "control: varios modificadores"),
    ("El perro duerme con la gata.", True, False, "preposicion 'con' ausente"),
    ("El perro persigue a la gata.", True, False, "objeto animado marcado por 'a'"),
    ("El perro no duerme.", True, False, "negacion verbal no implementada"),
    ("El perro duerme porque la gata come.", True, False, "subordinada causal ausente"),
    ("El perro come y la gata duerme.", True, False, "coordinacion de oraciones ausente"),
    ("El perro negro y grande duerme.", True, False, "coordinacion de adjetivos y nuevo vocabulario"),
    ("El perro muy negro duerme.", True, False, "intensificador adjetival ausente"),
    ("El perro negro pequeño duerme.", True, False, "dos adjetivos y nuevo vocabulario"),
    ("El perro negro que come duerme.", True, True, "control: adjetivo y relativa"),
    ("El perro que duerme en la casa come la carne.", True, True, "control: relativa con complemento"),
    ("La gata que el perro persigue duerme.", True, True, "control: relativa de objeto"),
    ("El perro que las gatas persiguen duerme.", True, True, "control: verbo subordinado plural"),
    ("El perro que la gata persiguen duerme.", False, False, "error de concordancia en relativa"),
    ("Los perros que comen duerme.", False, False, "error de concordancia principal"),
    ("El perro duerme en el jardín.", True, True, "control: sintagma preposicional"),
    ("La carne negra duerme.", True, True, "sintaxis correcta, semantica inusual"),
    ("El perro come la carne en la casa.", True, True, "ambiguedad por adjuncion del SP"),
    ("¿El perro duerme?", True, False, "puntuacion interrogativa sin normalizar"),
    ("El perro y la gata duermen.", True, False, "coordinacion de sujetos ausente"),
    ("La gata duerme lentamente.", True, True, "control: adverbio"),
    ("El perro negro duerme en la casa.", True, True, "control: adjetivo y SP"),
    ("El perro duerme la carne.", False, False, "uso transitivo no admitido para 'dormir'"),
]


def ejecutar_pruebas():
    aciertos = 0
    aceptadas = 0
    rechazos_validos = 0
    aceptaciones_invalidas = 0
    rechazos_invalidos = 0
    diferencias_con_t3 = []
    arboles_caso_19 = None

    for numero, (oracion, es_valida, aceptacion_t3, motivo) in enumerate(CASOS, 1):
        arboles = todos_los_arboles(oracion, GRAMATICA, INICIAL)
        aceptada = bool(arboles)
        if numero == 19:
            arboles_caso_19 = len(arboles)
        coincidencia = aceptada == es_valida
        aciertos += int(coincidencia)
        aceptadas += int(aceptada)
        rechazos_validos += int(es_valida and not aceptada)
        aceptaciones_invalidas += int(not es_valida and aceptada)
        rechazos_invalidos += int(not es_valida and not aceptada)
        if aceptada != aceptacion_t3:
            diferencias_con_t3.append(numero)

        print(
            f"{numero:02}. {'ACEPTADA ' if aceptada else 'RECHAZADA'} | "
            f"Español: {'válida' if es_valida else 'inválida'} | "
            f"Árboles: {len(arboles)} | "
            f"{'COINCIDE' if coincidencia else 'NO COINCIDE'}"
        )
        print(f"    {oracion} ({motivo})")

    print("\nRESUMEN DE LOS 24 CASOS ADICIONALES")
    print(f"Total: {len(CASOS)}")
    print(f"Aceptadas: {aceptadas} | Rechazadas: {len(CASOS)-aceptadas}")
    print(f"Aciertos de clasificación gramatical: {aciertos}/{len(CASOS)}")
    print(f"Oraciones válidas rechazadas: {rechazos_validos}")
    print(f"Oraciones inválidas aceptadas: {aceptaciones_invalidas}")
    print(f"Oraciones inválidas rechazadas: {rechazos_invalidos}")
    print(f"Árboles del caso 19 (ambigüedad): {arboles_caso_19}; se esperan 2 con la gramática de tarea 3.")
    if diferencias_con_t3:
        print(f"ATENCIÓN: resultados distintos a tarea 3 en casos: {diferencias_con_t3}")
    else:
        print("Los 24 resultados coinciden con la instantánea de la tarea 3.")


if __name__ == "__main__":
    ejecutar_pruebas()
