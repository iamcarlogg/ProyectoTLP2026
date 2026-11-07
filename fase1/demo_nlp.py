"""P3 - Demo de NLP: analiza con spaCy las mismas oraciones que P2 probó con la CFG.

Ejecutar desde la raíz:
    python fase1/demo_nlp.py            # las 20 oraciones, una línea por oración
    python fase1/demo_nlp.py --detalle  # además, la tabla completa de cada oración
"""
import sys

import spacy

from pruebas_base import PRUEBAS    # las 20 oraciones de P2: (oracion, es_valida)

# Modelo entrenado para español. Se instala aparte con:
#   python -m spacy download es_core_news_md
MODELO = "es_core_news_md"

nlp = spacy.load(MODELO)    # se carga una sola vez: tarda unos segundos


def rasgos(palabra):
    """Género y número abreviados: 'MS' = masculino singular, 'FP' = femenino plural, '-' = sin dato."""
    genero = {"Masc": "M", "Fem": "F"}.get("".join(palabra.morph.get("Gender")), "")
    numero = {"Sing": "S", "Plur": "P"}.get("".join(palabra.morph.get("Number")), "")
    return (genero + numero) or "-"


def analizar(oracion):
    """Paso 2: imprime una fila por palabra con categoría, género, número, relación y de quién depende."""
    doc = nlp(oracion)      # spaCy hace todo el análisis en esta línea

    print(f"     {'N.º':>3}  {'Palabra':12} {'Categoría':9} {'Género':7} {'Número':7} {'Relación':9} Depende de")
    for palabra in doc:
        if palabra.is_punct:                           # el punto final no aporta nada
            continue
        genero = ",".join(palabra.morph.get("Gender")) or "-"   # Masc / Fem
        numero = ",".join(palabra.morph.get("Number")) or "-"   # Sing / Plur
        print(
            f"     {palabra.i:>3}  {palabra.text:12} {palabra.pos_:9} {genero:7} {numero:7} "
            f"{palabra.dep_:9} {palabra.head.text}"
        )
    return doc


def resumen(doc):
    """Paso 3: la oración en una línea, cada palabra como palabra/CATEGORÍA/rasgos."""
    return "  ".join(f"{p.text}/{p.pos_}/{rasgos(p)}" for p in doc if not p.is_punct)


def raiz(doc):
    """La palabra que spaCy eligió como centro de la oración (la que no depende de nadie)."""
    return next(p for p in doc if p.dep_ == "ROOT")


if __name__ == "__main__":
    detalle = "--detalle" in sys.argv
    raiz_verbo = 0

    for numero, (oracion, es_valida) in enumerate(PRUEBAS, 1):
        doc = nlp(oracion)
        centro = raiz(doc)
        if centro.pos_ == "VERB":
            raiz_verbo += 1

        # es_valida es la "respuesta correcta" que P2 escribió a mano en pruebas_base.py:
        # dice si la oración es correcta EN ESPAÑOL, no lo que respondió la CFG.
        etiqueta = "correcta" if es_valida else "INCORRECTA"
        print(f"\n{numero:02}. {oracion}  [{etiqueta} en español]")
        print(f"    {resumen(doc)}")
        print(f"    Raíz: {centro.text} ({centro.pos_})")
        if detalle:
            analizar(oracion)

    print(f"\nOraciones procesadas: {len(PRUEBAS)} de {len(PRUEBAS)} (spaCy nunca rechaza)")
    print(f"Oraciones cuya raíz es un verbo: {raiz_verbo} de {len(PRUEBAS)}")
