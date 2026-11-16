"""P1 - Corre el parser propio sobre el corpus y guarda la salida bruta en un log.

Lee fase2/corpus.csv, analiza cada oración con el motor de la Fase 1 y escribe
fase2/logs/parser.json con dos partes:
- metadatos: datos de la corrida (versiones, tamaño de la gramática, fecha).
- resultados: una entrada por oración, con la salida, el árbol y el motivo del fallo.

Ejecutar desde la raíz: python fase2/correr_parser.py
"""
import csv
import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import nltk

AQUI = Path(__file__).parent
# El motor vive en fase1/: se importa desde ahí para no tener dos copias.
# fase2/ va primero en sys.path, así que si P2 deja su gramática en fase2/gramatica_es.py,
# esa gana sobre la de la Fase 1 sin tocar este script.
sys.path.append(str(AQUI.parent / "fase1"))

from motor import normalizar, todos_los_arboles   # noqa: E402
import gramatica_es                                 # noqa: E402
from gramatica_es import GRAMATICA, INICIAL         # noqa: E402

CORPUS = AQUI / "corpus.csv"
LOG = AQUI / "logs" / "parser.json"


def vocabulario(gramatica):
    """Palabras de la gramática: símbolos de las producciones que no son no terminales."""
    return {simbolo
            for producciones in gramatica.values()
            for produccion in producciones
            for simbolo in produccion
            if simbolo not in gramatica}


def analizar(fila, vocab):
    """Analiza una oración del corpus y devuelve su entrada del log."""
    oracion = fila["oracion"]
    desconocidas = [p for p in normalizar(oracion) if p not in vocab]
    arboles, error = [], None

    inicio = time.perf_counter()
    try:
        arboles = todos_los_arboles(oracion, GRAMATICA, INICIAL)
    except Exception as e:          # p. ej. RecursionError: se anota y se sigue con la siguiente
        error = f"{type(e).__name__}: {e}"
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    # Motivo del fallo: si hay palabras desconocidas, ese es el motivo aunque también
    # pudiera fallar la estructura; "estructura" solo cuando todas las palabras se conocen.
    if error:
        motivo = "error"
    elif arboles:
        motivo = None
    elif desconocidas:
        motivo = "vocabulario"
    else:
        motivo = "estructura"

    return {
        "id": int(fila["id"]),
        "oracion": oracion,
        "salida": "acepta" if arboles else "rechaza",
        "motivo": motivo,
        # Primer árbol en una sola línea (str() de NLTK parte los árboles largos)
        "arbol": arboles[0].pformat(margin=10**6) if arboles else None,
        "n_arboles": len(arboles),          # > 1 = ambigua según la gramática
        "palabras_desconocidas": desconocidas,
        "tiempo_ms": round(tiempo_ms, 3),
        "error": error,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    with open(CORPUS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    vocab = vocabulario(GRAMATICA)
    log = {
        "metadatos": {
            "enfoque": "parser",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "nltk": nltk.__version__,
            "gramatica": str(Path(gramatica_es.__file__).relative_to(AQUI.parent)),
            "reglas": sum(len(p) for p in GRAMATICA.values()),
            "vocabulario": len(vocab),
            "corpus": str(CORPUS.relative_to(AQUI.parent)),
            "oraciones": len(filas),
        },
        "resultados": [analizar(fila, vocab) for fila in filas],
    }

    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)   # ensure_ascii=False: ñ y tildes legibles

    # Resumen en pantalla
    res = log["resultados"]
    print(f"{len(res)} oraciones → {LOG.relative_to(AQUI.parent)}")
    for valor in ("acepta", "rechaza"):
        print(f"  {valor}: {sum(r['salida'] == valor for r in res)}")
    for motivo in ("vocabulario", "estructura", "error"):
        print(f"  rechazo por {motivo}: {sum(r['motivo'] == motivo for r in res)}")
    print(f"  ambiguas (más de un árbol): {sum(r['n_arboles'] > 1 for r in res)}")


if __name__ == "__main__":
    main()
