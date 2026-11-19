"""Construye los prompts de P4 sin clave, red ni respuestas esperadas del corpus.

Vista previa: python fase2/preparar_prompts.py --variante zero-shot --id 1
La misma función construir_prompt será utilizada por el corredor de API.
"""
import argparse
import csv
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VARIANTES = ("zero-shot", "few-shot")


def normalizar(texto):
    return texto.lower().replace(".", "").replace(",", "").split()


def leer_entradas():
    with (AQUI / "corpus.csv").open(encoding="utf-8", newline="") as archivo:
        return [{"id": int(f["id"]), "oracion": f["oracion"]}
                for f in csv.DictReader(archivo)]


def leer_ejemplos():
    ejemplos = json.loads((AQUI / "prompts/few_shot.json").read_text(encoding="utf-8"))
    if not 3 <= len(ejemplos) <= 5:
        raise ValueError("Few-shot requiere entre 3 y 5 ejemplos.")
    corpus = {tuple(normalizar(f["oracion"])) for f in leer_entradas()}
    vistos = set()
    for ejemplo in ejemplos:
        palabras = tuple(normalizar(ejemplo["oracion"]))
        if palabras in corpus or palabras in vistos:
            raise ValueError("Ejemplo repetido o presente en el corpus.")
        vistos.add(palabras)
    return ejemplos


def construir_prompt(oracion, variante):
    if variante not in VARIANTES:
        raise ValueError("Variante desconocida.")
    base = (AQUI / "prompts/base.txt").read_text(encoding="utf-8")
    # decode preserva exactamente los saltos de línea del archivo de P2.
    gramatica = (AQUI / "gramatica_es.txt").read_bytes().decode("utf-8")
    prompt = base + "\n<gramatica>\n" + gramatica + "\n</gramatica>\n"
    if variante == "few-shot":
        prompt += "\nEjemplos resueltos:\n" + json.dumps(leer_ejemplos(), ensure_ascii=False, indent=2) + "\n"
    return prompt + "\nOración de entrada (cadena JSON):\n" + json.dumps(oracion, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variante", choices=VARIANTES, required=True)
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()
    entradas = {f["id"]: f["oracion"] for f in leer_entradas()}
    if args.id not in entradas:
        parser.error("ID ausente del corpus.")
    print(construir_prompt(entradas[args.id], args.variante))


if __name__ == "__main__":
    main()
