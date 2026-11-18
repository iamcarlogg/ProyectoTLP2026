"""P3 - Corre spaCy sobre el corpus y guarda la salida bruta en un log.

Lee fase2/corpus.csv, analiza cada oración con spaCy y escribe fase2/logs/spacy.json
con el formato común de la Fase 2 (metadatos + resultados).

spaCy nunca rechaza una oración. Se usa el mismo criterio de la Fase 1: "rechaza"
si sus propios rasgos de género y número muestran un error de concordancia
(función errores_concordancia() de fase1/tabla_nlp.py; se importa, no se copia).

Ejecutar desde la raíz: python fase2/correr_spacy.py
"""
import csv
import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

import spacy

AQUI = Path(__file__).parent
sys.path.append(str(AQUI.parent / "fase1"))      # el código de la Fase 1 vive en fase1/

from demo_nlp import MODELO, nlp                  # noqa: E402  modelo ya cargado
from tabla_nlp import errores_concordancia        # noqa: E402  la regla de la Fase 1

CORPUS = AQUI / "corpus.csv"
LOG = AQUI / "logs" / "spacy.json"


def analizar(fila):
    """Analiza una oración del corpus y devuelve su entrada del log."""
    oracion = fila["oracion"]

    inicio = time.perf_counter()
    doc = nlp(oracion)                            # todo el análisis de spaCy
    errores = errores_concordancia(doc)
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    palabras = [p for p in doc if not p.is_punct]
    return {
        "id": int(fila["id"]),
        "oracion": oracion,
        "salida": "rechaza" if errores else "acepta",
        "errores_concordancia": errores,          # el motivo del rechazo, si lo hay
        # Lo que spaCy dijo de cada palabra: sirve para los errores de etiquetado
        "palabras": [
            {
                "texto": p.text,
                "pos": p.pos_,                    # categoría (Universal Dependencies)
                "morph": str(p.morph),            # rasgos: Gender=Masc|Number=Sing ...
                "dep": p.dep_,                    # relación con su cabeza
                "cabeza": p.head.text,
            }
            for p in palabras
        ],
        "raiz": next(p.text for p in doc if p.dep_ == "ROOT"),
        "raiz_pos": next(p.pos_ for p in doc if p.dep_ == "ROOT"),
        "tiempo_ms": round(tiempo_ms, 3),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    with open(CORPUS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    log = {
        "metadatos": {
            "enfoque": "spacy",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "spacy": spacy.__version__,
            "modelo": MODELO,
            "version_modelo": nlp.meta["version"],
            "criterio_rechazo": "error de concordancia de género o número en los rasgos de spaCy "
                                "(fase1/tabla_nlp.py: errores_concordancia)",
            "corpus": CORPUS.relative_to(AQUI.parent).as_posix(),   # con / también en Windows
            "oraciones": len(filas),
        },
        "resultados": [analizar(fila) for fila in filas],
    }

    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    res = log["resultados"]
    print(f"{len(res)} oraciones → {LOG.relative_to(AQUI.parent).as_posix()}")
    for valor in ("acepta", "rechaza"):
        print(f"  {valor}: {sum(r['salida'] == valor for r in res)}")
    print(f"  raíz = verbo: {sum(r['raiz_pos'] == 'VERB' for r in res)}")


if __name__ == "__main__":
    main()