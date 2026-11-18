"""P3 - Corre NLTK sobre el corpus y guarda la salida bruta en un log.

NLTK no trae un modelo de español listo como spaCy: hay que ENTRENAR un etiquetador.
  1. Corpus de entrenamiento: cess_esp (unas 6 000 oraciones de prensa en español,
     etiquetadas a mano con el sistema EAGLES: 'da0ms0' = determinante artículo
     masculino singular, 'vmip3p0' = verbo principal indicativo presente 3.ª plural...).
  2. Etiquetador en cadena (backoff): bigramas → unigramas → reglas de sufijos.
     Si un nivel no sabe qué etiqueta poner, le pasa la palabra al siguiente.
  3. Criterio de rechazo: el mismo de spaCy (error de concordancia de género o número),
     pero como NLTK no da árbol de dependencias, se aplica sobre palabras vecinas.

Ejecutar desde la raíz: python fase2/correr_nltk.py
La primera vez descarga cess_esp (unos 2 MB).
"""
import csv
import json
import platform
import re
import time
from datetime import datetime
from pathlib import Path

import nltk
from nltk.corpus import cess_esp
from nltk.tag import BigramTagger, RegexpTagger, UnigramTagger

AQUI = Path(__file__).parent
CORPUS = AQUI / "corpus.csv"
LOG = AQUI / "logs" / "nltk.json"

# ---------------------------------------------------------------------------
# 1. Entrenar el etiquetador
# ---------------------------------------------------------------------------

# Reglas para palabras que no aparecen en cess_esp, según la terminación (morfología del español).
# Se prueban en orden y gana la primera que coincide. La última es el valor por defecto.
SUFIJOS = [
    (r".*mente$", "rg"),                    # lentamente → adverbio
    (r".*(aron|ieron)$", "vmis3p0"),        # durmieron → verbo pasado 3.ª plural
    (r".*ó$", "vmis3s0"),                   # durmió → verbo pasado 3.ª singular
    (r".*(amos|emos|imos)$", "vmip1p0"),    # comemos → verbo 1.ª plural
    (r".*(an|en)$", "vmip3p0"),             # duermen → verbo presente 3.ª plural
    (r".*as$", "ncfp000"),                  # gatas → sustantivo femenino plural
    (r".*os$", "ncmp000"),                  # perros → sustantivo masculino plural
    (r".*a$", "ncfs000"),                   # gata → sustantivo femenino singular
    (r".*", "ncms000"),                     # cualquier otra → sustantivo masculino singular
]


def oraciones_de_entrenamiento():
    """Oraciones de cess_esp en minúscula, sin los sujetos vacíos ('*0*') que marca el corpus."""
    try:
        oraciones = cess_esp.tagged_sents()
        oraciones[0]
    except LookupError:                     # la primera vez: se descarga
        nltk.download("cess_esp", quiet=True)
        oraciones = cess_esp.tagged_sents()
    return [[(palabra.lower(), etiqueta.lower()) for palabra, etiqueta in oracion
             if not palabra.startswith("*")]
            for oracion in oraciones]


def entrenar(oraciones):
    """Etiquetador en cadena: bigramas → unigramas → sufijos."""
    sufijos = RegexpTagger(SUFIJOS)
    unigramas = UnigramTagger(oraciones, backoff=sufijos)
    return BigramTagger(oraciones, backoff=unigramas)


# ---------------------------------------------------------------------------
# 2. Rasgos de una etiqueta EAGLES
# ---------------------------------------------------------------------------
# La posición del género y del número depende de la categoría (primera letra):
#   determinante d a 0 m s 0   adjetivo a q 0 m s 0   pronombre p p 1 c s n 0 0
#   sustantivo   n c m s 0 0 0                          verbo     v m i p 3 s 0
POSICION = {"d": (3, 4), "a": (3, 4), "p": (3, 4), "n": (2, 3), "v": (None, 5)}


def rasgos(etiqueta):
    """Devuelve (género, número): 'm'/'f' y 's'/'p', o None si la etiqueta no lo indica."""
    pos_genero, pos_numero = POSICION.get(etiqueta[:1], (None, None))

    def leer(pos, validos):
        valor = etiqueta[pos] if pos is not None and pos < len(etiqueta) else None
        return valor if valor is not None and valor in validos else None   # 'c' (común) y 'n' (invariable) no cuentan

    return leer(pos_genero, "mf"), leer(pos_numero, "sp")


# ---------------------------------------------------------------------------
# 3. Criterio de rechazo: concordancia entre palabras vecinas
# ---------------------------------------------------------------------------

def grupos_nominales(etiquetas):
    """Grupos de posiciones [det] sustantivo [adj...] o un pronombre solo, en orden."""
    grupos, i = [], 0
    while i < len(etiquetas):
        grupo = []
        if etiquetas[i].startswith("d"):
            grupo.append(i)
            i += 1
        if i < len(etiquetas) and etiquetas[i].startswith(("n", "pp")):
            grupo.append(i)
            i += 1
            while i < len(etiquetas) and etiquetas[i].startswith("a"):   # adjetivos que siguen
                grupo.append(i)
                i += 1
        if grupo:
            grupos.append(grupo)
        else:
            i += 1
    return grupos


def numero_de(grupo, etiquetas):
    """Número del grupo: el del sustantivo; si no lo tiene, el del determinante."""
    for i in reversed(grupo[:2]):
        numero = rasgos(etiquetas[i])[1]
        if numero:
            return numero
    return None


def errores_concordancia(palabras, etiquetas):
    errores = []
    grupos = grupos_nominales(etiquetas)

    # Regla 1: dentro de cada grupo nominal, mismo género y mismo número
    for grupo in grupos:
        for nombre, k in (("Gender", 0), ("Number", 1)):
            vistos = {palabras[i]: rasgos(etiquetas[i])[k] for i in grupo if rasgos(etiquetas[i])[k]}
            if len(set(vistos.values())) > 1:
                errores.append(f"{nombre}: " + " / ".join(f"{p}={v}" for p, v in vistos.items()))

    verbos = [i for i, e in enumerate(etiquetas) if e.startswith("v") and rasgos(e)[1]]

    # Las relativas: desde cada 'que' hasta el primer verbo que le sigue
    relativas = []
    for q, palabra in enumerate(palabras):
        if palabra == "que":
            verbo = next((v for v in verbos if v > q), None)
            if verbo is not None:
                relativas.append((q, verbo))
    dentro = {i for q, v in relativas for i in range(q, v + 1)}

    def grupo_que_termina_antes(posicion):
        previos = [g for g in grupos if g[-1] < posicion]
        return previos[-1] if previos else None

    # Regla 2a: en cada relativa, su sujeto concuerda en número con su verbo.
    #   relativa de objeto ("que la gata persigue"): el sujeto es el grupo dentro de la relativa;
    #   relativa de sujeto ("que come"): el sujeto es el antecedente, el grupo antes de 'que'.
    for q, v in relativas:
        interno = [g for g in grupos if q < g[0] < v]
        sujeto = interno[-1] if interno else grupo_que_termina_antes(q)
        if sujeto:
            n_suj, n_verbo = numero_de(sujeto, etiquetas), rasgos(etiquetas[v])[1]
            if n_suj and n_suj != n_verbo:
                errores.append(f"relativa: {palabras[sujeto[-1]]}={n_suj} / {palabras[v]}={n_verbo}")

    # Regla 2b: el sujeto principal (primer grupo) concuerda con el primer verbo fuera de las relativas.
    #   Si el sujeto es "X y Y", es plural.
    principales = [v for v in verbos if v not in dentro]
    if grupos and principales:
        sujeto = grupos[0]
        fin = sujeto[-1]
        coordinado = fin + 1 < len(palabras) and palabras[fin + 1] == "y" and len(grupos) > 1 \
            and grupos[1][0] == fin + 2
        n_suj = "p" if coordinado else numero_de(sujeto, etiquetas)
        v = principales[0]
        n_verbo = rasgos(etiquetas[v])[1]
        if n_suj and n_suj != n_verbo:
            errores.append(f"sujeto-verbo: {palabras[fin]}={n_suj} / {palabras[v]}={n_verbo}")

    return errores


# ---------------------------------------------------------------------------
# 4. Correr el corpus
# ---------------------------------------------------------------------------

def tokenizar(oracion):
    """Palabras en minúscula, sin signos de puntuación (igual que se entrenó)."""
    return re.findall(r"\w+", oracion.lower())


def analizar(fila, etiquetador, conocidas):
    oracion = fila["oracion"]
    inicio = time.perf_counter()
    palabras = tokenizar(oracion)
    etiquetas = [e for _, e in etiquetador.tag(palabras)]
    errores = errores_concordancia(palabras, etiquetas)
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    return {
        "id": int(fila["id"]),
        "oracion": oracion,
        "salida": "rechaza" if errores else "acepta",
        "errores_concordancia": errores,
        "palabras": [
            {"texto": p, "etiqueta": e, "conocida": p in conocidas}   # conocida = aparece en cess_esp
            for p, e in zip(palabras, etiquetas)
        ],
        "tiempo_ms": round(tiempo_ms, 3),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    oraciones = oraciones_de_entrenamiento()

    # Exactitud del etiquetador: se entrena con el 90 % y se prueba con el 10 % restante.
    # La división es fija (las primeras oraciones), así que el número no cambia entre corridas.
    corte = int(len(oraciones) * 0.9)
    exactitud = entrenar(oraciones[:corte]).accuracy(oraciones[corte:])

    # Para el experimento se entrena con todo cess_esp.
    inicio = time.perf_counter()
    etiquetador = entrenar(oraciones)
    segundos = time.perf_counter() - inicio
    conocidas = {palabra for oracion in oraciones for palabra, _ in oracion}

    with open(CORPUS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    log = {
        "metadatos": {
            "enfoque": "nltk",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "nltk": nltk.__version__,
            "corpus_entrenamiento": "cess_esp",
            "oraciones_entrenamiento": len(oraciones),
            "palabras_entrenamiento": sum(len(o) for o in oraciones),
            "etiquetador": "BigramTagger → UnigramTagger → RegexpTagger (sufijos)",
            "exactitud_validacion": round(exactitud, 4),
            "validacion": "entrenado con el 90 % inicial de cess_esp, probado con el 10 % final",
            "segundos_entrenamiento": round(segundos, 2),
            "minusculas": True,
            "criterio_rechazo": "error de concordancia de género o número entre palabras vecinas "
                                "(grupo nominal, relativas y sujeto principal con el primer verbo fuera de ellas)",
            "corpus": CORPUS.relative_to(AQUI.parent).as_posix(),
            "oraciones": len(filas),
        },
        "resultados": [analizar(fila, etiquetador, conocidas) for fila in filas],
    }

    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    res = log["resultados"]
    desconocidas = sorted({p["texto"] for r in res for p in r["palabras"] if not p["conocida"]})
    print(f"Etiquetador entrenado: exactitud en validación {exactitud:.1%}")
    print(f"{len(res)} oraciones → {LOG.relative_to(AQUI.parent).as_posix()}")
    for valor in ("acepta", "rechaza"):
        print(f"  {valor}: {sum(r['salida'] == valor for r in res)}")
    print(f"  palabras del corpus que no están en cess_esp: {len(desconocidas)} → {', '.join(desconocidas)}")


if __name__ == "__main__":
    main()