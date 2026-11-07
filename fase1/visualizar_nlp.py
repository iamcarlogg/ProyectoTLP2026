"""P3 - Visualización interactiva para la demo: CFG frente a spaCy.

El trabajo se divide en dos archivos:
  - visualizar_nlp.py (este): calcula los DATOS. Corre la CFG y spaCy sobre
    cada oración y guarda los resultados en un diccionario.
  - plantilla_demo.html: la PRESENTACIÓN. Recibe esos datos y dibuja los
    árboles con JavaScript (zoom, colores, selector de árboles, panel de detalles).

Ejecutar desde la raíz:
    python fase1/visualizar_nlp.py           # 5 oraciones elegidas  -> salidas/demo_nlp.html
    python fase1/visualizar_nlp.py --todas   # las 20 de P2          -> salidas/demo_nlp_todas.html
    python fase1/visualizar_nlp.py --fallas  # los 24 casos de fallas -> salidas/demo_nlp_fallas.html
Abre el archivo generado en el navegador. Funciona sin internet.
"""
import json
import sys
from pathlib import Path

from spacy import displacy

from demo_nlp import nlp, raiz
from motor import todos_los_arboles
from gramatica_es import GRAMATICA, INICIAL
from tabla_nlp import errores_concordancia, valor
from pruebas_base import PRUEBAS     # las 20 oraciones de P2: (oracion, es_valida)
from pruebas_fallas import CASOS     # los 24 casos: (oracion, es_valida, aceptacion_t3, descripcion)

# Oraciones para la demo: (oración, ¿es correcta en español?, qué queremos mostrar con ella).
# Se pueden cambiar sin tocar el resto del código.
ORACIONES_DEMO = [
    ("El perro negra duerme.", False,
     "Error de concordancia: la CFG la rechaza; spaCy la analiza, pero sus propios rasgos delatan el error."),
    ("La perro come.", False,
     "Error que spaCy no detecta: toma «perro» por nombre propio y no le asigna género, así que no hay nada que comparar."),
    ("El perro que come duerme.", True,
     "Relativa: la CFG la analiza bien con rel_suj_s; spaCy pone el sustantivo como raíz y etiqueta «duerme» como adjetivo."),
    ("El perro no duerme.", True,
     "Oración correcta fuera de la gramática: la CFG la rechaza porque no tiene regla para «no»; spaCy no tiene problema."),
    ("El perro come la carne en la casa.", True,
     "Ambigüedad: «en la casa» puede colgar del verbo (come en la casa) o del objeto (la carne de la casa). La CFG da los dos árboles; spaCy elige uno sin avisar."),
]

CARPETA = Path(__file__).parent
PLANTILLA = CARPETA / "plantilla_demo.html"
CARPETA_SALIDA = CARPETA / "salidas"

# Las palabras que conoce la gramática: todo símbolo que aparece a la derecha y no es una clave
VOCABULARIO = {s for producciones in GRAMATICA.values() for p in producciones for s in p} - set(GRAMATICA)


def arbol_a_dict(arbol):
    """Convierte un nltk.Tree en diccionarios {etiqueta, hijos}; las palabras son hojas.

    Un nodo sin hijos es una producción vacía (ε): se le agrega una hoja 'ε' para que se vea.
    """
    if isinstance(arbol, str):
        return {"etiqueta": arbol, "hoja": True}
    hijos = [arbol_a_dict(h) for h in arbol]
    if not hijos:
        hijos = [{"etiqueta": "ε", "hoja": True, "vacio": True}]
    return {"etiqueta": arbol.label(), "hijos": hijos}


def datos_cfg(oracion):
    """Árboles de nuestra CFG y, si la rechaza, qué palabras no están en su vocabulario."""
    arboles = todos_los_arboles(oracion, GRAMATICA, INICIAL)
    palabras = oracion.lower().replace(".", "").replace(",", "").split()   # igual que motor.py
    return {
        "arboles": [arbol_a_dict(a) for a in arboles],
        "desconocidas": [p for p in palabras if p not in VOCABULARIO],
    }


def datos_spacy(oracion):
    """Palabras, flechas, raíz y errores de concordancia según spaCy.

    Las flechas salen de displacy.parse_deps: son los mismos datos que usa displacy
    para dibujar, pero los dibujamos nosotros para que combinen con el árbol de la CFG.
    """
    doc = nlp(oracion)
    dibujo = displacy.parse_deps(doc)                  # une la puntuación a la palabra anterior
    sin_puntuacion = [p for p in doc if not p.is_punct]
    posicion = {p.i: n for n, p in enumerate(sin_puntuacion)}

    palabras = []
    for n, palabra in enumerate(sin_puntuacion):
        palabras.append({
            "texto": dibujo["words"][n]["text"] if len(dibujo["words"]) == len(sin_puntuacion) else palabra.text,
            "pos": palabra.pos_,
            "genero": valor(palabra, "Gender"),
            "numero": valor(palabra, "Number"),
            "dep": palabra.dep_,
            "cabeza": posicion.get(palabra.head.i, n),
        })

    centro = raiz(doc)
    return {
        "palabras": palabras,
        "arcos": dibujo["arcs"],
        "raiz": {"texto": centro.text, "pos": centro.pos_, "indice": posicion.get(centro.i, 0)},
        "errores": errores_concordancia(doc),
    }


def idea_automatica(correcta, cfg, spacy):
    """Explicación en una frase para las oraciones que no tienen una escrita a mano."""
    acepta_cfg = bool(cfg["arboles"])
    acepta_spacy = not spacy["errores"]
    partes = []
    if acepta_cfg == correcta:
        partes.append("La CFG acierta" + (f" con {len(cfg['arboles'])} árboles (ambigua)" if len(cfg["arboles"]) > 1 else ""))
    elif correcta:
        motivo = (f"no conoce {', '.join('«' + p + '»' for p in cfg['desconocidas'])}"
                  if cfg["desconocidas"] else "le faltan reglas para combinar estas palabras")
        partes.append(f"La CFG rechaza una oración correcta: {motivo}")
    else:
        partes.append("La CFG acepta una oración incorrecta")
    if acepta_spacy == correcta:
        partes.append("spaCy acierta" + ("" if acepta_spacy else " al detectar un error de concordancia"))
    elif correcta:
        partes.append("spaCy marca un error que no existe")
    else:
        partes.append("spaCy no detecta el error")
    if spacy["raiz"]["pos"] != "VERB":
        partes.append(f"spaCy pone como raíz a «{spacy['raiz']['texto']}» ({spacy['raiz']['pos']}), no a un verbo")
    return "; ".join(partes) + "."


def preparar(oracion, correcta, idea=None, prefijo=""):
    """Junta en un diccionario todo lo que la página necesita de una oración."""
    cfg, spacy = datos_cfg(oracion), datos_spacy(oracion)
    return {"texto": oracion, "correcta": correcta, "cfg": cfg, "spacy": spacy,
            "idea": prefijo + (idea or idea_automatica(correcta, cfg, spacy))}


def generar_pagina(oraciones, nombre_archivo, titulo):
    datos = {
        "modelo": f"{nlp.meta['lang']}_{nlp.meta['name']}",
        "titulo": titulo,
        "gramatica": GRAMATICA,
        "oraciones": oraciones,
    }
    if not PLANTILLA.exists():
        raise SystemExit(f"No encuentro la plantilla: {PLANTILLA}\n"
                         "Copia plantilla_demo.html dentro de la carpeta fase1/, junto a este script.")

    # Se reemplaza el marcador de la plantilla por los datos en formato JSON
    json_datos = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    pagina = PLANTILLA.read_text(encoding="utf-8").replace("/*__DATOS__*/null", json_datos)

    CARPETA_SALIDA.mkdir(exist_ok=True)
    destino = CARPETA_SALIDA / nombre_archivo
    destino.write_text(pagina, encoding="utf-8")
    return destino


if __name__ == "__main__":
    # Si una oración también está en ORACIONES_DEMO, se usa su explicación escrita a mano
    a_mano = {oracion: idea for oracion, _, idea in ORACIONES_DEMO}

    if "--todas" in sys.argv:
        oraciones = [preparar(o, v, a_mano.get(o)) for o, v in PRUEBAS]
        archivo = generar_pagina(oraciones, "demo_nlp_todas.html", "Las 20 oraciones de P2")
    elif "--fallas" in sys.argv:
        oraciones = [preparar(o, v, a_mano.get(o), prefijo=f"[{d}] ") for o, v, _, d in CASOS]
        archivo = generar_pagina(oraciones, "demo_nlp_fallas.html", "Los 24 casos de la tabla de fallas")
    else:
        oraciones = [preparar(o, v, idea) for o, v, idea in ORACIONES_DEMO]
        archivo = generar_pagina(oraciones, "demo_nlp.html", "Oraciones elegidas para la demo")
    print(f"Página generada: {archivo}")
    print("Ábrela en el navegador (doble clic en el archivo).")
