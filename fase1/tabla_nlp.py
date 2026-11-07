"""P3 - Tabla lado a lado: respuesta correcta, nuestra CFG y spaCy, oración por oración.

spaCy nunca rechaza, así que le damos una regla: "rechaza" una oración si sus
propios rasgos de género y número muestran un error de concordancia.

Ejecutar desde la raíz:
    python fase1/tabla_nlp.py           # las 20 oraciones de P2 (tarea 1)
    python fase1/tabla_nlp.py --fallas  # los 24 casos de la tabla de fallas (tarea 4)
"""
import sys

from demo_nlp import nlp, raiz                  # el modelo de spaCy ya cargado (paso 3)
from motor import parsear                       # el motor de P1
from gramatica_es import GRAMATICA, INICIAL     # la gramática de P2
from pruebas_base import PRUEBAS                # (oracion, es_valida)
from pruebas_fallas import CASOS                # (oracion, es_valida, aceptacion_t3, descripcion)


def valor(palabra, rasgo):
    """Devuelve 'Masc', 'Sing', etc., o None si spaCy no le asignó ese rasgo."""
    valores = palabra.morph.get(rasgo)
    return valores[0] if valores else None


def errores_concordancia(doc):
    """Busca desacuerdos de género y número usando solo lo que spaCy dijo.

    Regla 1, dentro del grupo nominal: el sustantivo, su determinante (det) y
    sus adjetivos (amod) deben tener el mismo género y el mismo número.
    Regla 2, sujeto y verbo: el número del sujeto (nsubj) debe coincidir con el del verbo.

    Si a una palabra le falta un rasgo (como a 'perro' cuando spaCy lo toma
    por nombre propio), no se compara: no se puede detectar lo que no se ve.
    """
    errores = []

    # Regla 1: grupo nominal = cada palabra que tiene un det o un amod colgando
    for nucleo in doc:
        grupo = [nucleo] + [h for h in nucleo.children if h.dep_ in ("det", "amod")]
        if len(grupo) == 1:
            continue
        for rasgo in ("Gender", "Number"):
            vistos = {p.text: valor(p, rasgo) for p in grupo if valor(p, rasgo)}
            if len(set(vistos.values())) > 1:          # dos valores distintos = desacuerdo
                errores.append(f"{rasgo}: " + " / ".join(f"{t}={v}" for t, v in vistos.items()))

    # Regla 2: número del sujeto frente al número de su verbo
    for sujeto in doc:
        if sujeto.dep_ != "nsubj":
            continue
        verbo = sujeto.head
        # si el sujeto no tiene número, se toma el de su determinante ("El perro" → El = Sing)
        numero_suj = valor(sujeto, "Number") or next(
            (valor(h, "Number") for h in sujeto.children if h.dep_ == "det" and valor(h, "Number")), None)
        numero_verbo = valor(verbo, "Number")
        if numero_suj and numero_verbo and numero_suj != numero_verbo:
            errores.append(f"sujeto-verbo: {sujeto.text}={numero_suj} / {verbo.text}={numero_verbo}")

    return errores


def comparar(oraciones):
    """Imprime la tabla y devuelve los aciertos de cada enfoque."""
    aciertos_cfg = aciertos_spacy = raiz_ok = 0

    print(f"{'N.º':>3}  {'Oración':50} {'Español':10} {'CFG':9} {'spaCy':9} {'Raíz':6} Motivo de spaCy")
    for numero, (oracion, es_valida) in enumerate(oraciones, 1):
        acepta_cfg = parsear(oracion, GRAMATICA, INICIAL) is not None
        doc = nlp(oracion)
        errores = errores_concordancia(doc)
        acepta_spacy = not errores
        verbo_raiz = raiz(doc).pos_ == "VERB"

        aciertos_cfg += acepta_cfg == es_valida
        aciertos_spacy += acepta_spacy == es_valida
        raiz_ok += verbo_raiz

        def marca(acepta):     # ✓ si coincide con la respuesta correcta, ✗ si no
            return ("acepta" if acepta else "rechaza") + (" ✓" if acepta == es_valida else " ✗")

        print(
            f"{numero:>3}  {oracion:50} {'correcta' if es_valida else 'INCORRECTA':10} "
            f"{marca(acepta_cfg):9} {marca(acepta_spacy):9} {'verbo' if verbo_raiz else 'NO':6} "
            f"{'; '.join(errores)}"
        )

    total = len(oraciones)
    print(f"\nAciertos de la CFG:   {aciertos_cfg}/{total}")
    print(f"Aciertos de spaCy:    {aciertos_spacy}/{total}  (con la regla de concordancia)")
    print(f"Raíz = verbo (spaCy): {raiz_ok}/{total}")


if __name__ == "__main__":
    if "--fallas" in sys.argv:
        comparar([(oracion, es_valida) for oracion, es_valida, _, _ in CASOS])
    else:
        comparar(PRUEBAS)
