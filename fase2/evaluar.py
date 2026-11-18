"""P3 - Evaluación: lee el corpus y los logs de los enfoques y calcula las métricas del informe.

Entradas (no se modifican):
    fase2/corpus.csv                     la respuesta correcta de cada oración (columna esperado)
    fase2/logs/parser.json               P1
    fase2/logs/spacy.json                P3
    fase2/logs/nltk.json                 P3
    fase2/logs/llm_zero_shot.json        P4
    fase2/logs/llm_few_shot.json         P4
Un log que todavía no existe se marca como pendiente y no detiene la evaluación.
Un log de otro corpus (otra cantidad de oraciones u otro texto) sí la detiene: no es comparable.

Salidas en fase2/resultados/:
    metricas.csv            una fila por enfoque: matriz de confusión y métricas
    metricas_por_nivel.csv  aciertos, falsos positivos y falsos negativos por nivel
    detalle.csv             una fila por oración: qué respondió cada enfoque y si acertó
    tablas.md               las mismas tablas en Markdown, listas para el informe
    metricas.png            gráfica de precisión, cobertura y rechazo correcto
    aciertos_por_nivel.png  gráfica de exactitud por nivel

Además de las métricas contra el español (columna esperado), mide la FIDELIDAD A LA
GRAMÁTICA: si cada enfoque acepta exactamente las oraciones que la CFG genera. Es la
medida de la pregunta 2 del informe (¿el LLM respeta las reglas o se desvía hacia su
conocimiento general del español?). Para saber qué oraciones genera la CFG, este script
las analiza con el motor de la Fase 1 y la gramática de fase2/gramatica_es.py.

Reproducible: no hay azar. Con los mismos archivos de entrada salen las mismas cifras.
Ejecutar desde la raíz: python fase2/evaluar.py
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                    # dibuja a archivo, sin abrir ventanas
import matplotlib.pyplot as plt          # noqa: E402
from nltk import Tree                    # noqa: E402

AQUI = Path(__file__).parent
# Igual que correr_parser.py: el motor está en fase1/ y la gramática en fase2/
# (fase2/ va primero en sys.path, así que gana fase2/gramatica_es.py).
sys.path.append(str(AQUI.parent / "fase1"))
from motor import todos_los_arboles                 # noqa: E402
from gramatica_es import GRAMATICA, INICIAL         # noqa: E402

CORPUS = AQUI / "corpus.csv"
LOGS = AQUI / "logs"
SALIDA = AQUI / "resultados"

# Orden fijo de los enfoques: es el orden de las columnas en todas las tablas y gráficas
ENFOQUES = [
    ("parser", "Parser (CFG)"),
    ("spacy", "spaCy"),
    ("nltk", "NLTK"),
    ("llm_zero_shot", "LLM zero-shot"),
    ("llm_few_shot", "LLM few-shot"),
]

# ---------------------------------------------------------------------------
# Categorías por palabra, para los errores de etiquetado
# ---------------------------------------------------------------------------
# Cada enfoque etiqueta con su propio sistema. Todo se traduce a estas categorías:
#   det, n, n_propio, pron, v, adj, adv, p, conj, que
# 'n_propio' existe para que tomar "perro" por nombre propio cuente como error.


def categoria_cfg(etiqueta, palabra):
    """Etiqueta de nuestra gramática (det_ms, vt_s_pret, pron_1s, negacion...) → categoría."""
    base = etiqueta.split("_")[0]
    if palabra == "que":
        return "que"
    return {"det": "det", "n": "n", "pron": "pron", "v": "v", "vt": "v", "adj": "adj",
            "adv": "adv", "negacion": "adv", "p": "p"}.get(base, base)


def categorias_de_arbol(texto):
    """Lista (palabra, categoría) de un árbol en corchetes; None si no se puede leer."""
    try:
        arbol = Tree.fromstring(texto)
    except ValueError:
        return None
    resultado = []

    def recorrer(nodo):
        for hijo in nodo:
            if isinstance(hijo, Tree):
                if len(hijo) == 1 and isinstance(hijo[0], str):          # preterminal: (det_ms el)
                    resultado.append((hijo[0], categoria_cfg(hijo.label(), hijo[0])))
                else:
                    recorrer(hijo)
            else:                                                         # palabra suelta: que, y, no
                resultado.append((hijo, {"que": "que", "y": "conj", "no": "adv"}.get(hijo, "?")))

    recorrer(arbol)
    return resultado


UD = {"DET": "det", "NOUN": "n", "PROPN": "n_propio", "PRON": "pron", "VERB": "v", "AUX": "v",
      "ADJ": "adj", "ADV": "adv", "ADP": "p", "CCONJ": "conj", "SCONJ": "conj"}
EAGLES = {"d": "det", "n": "n", "p": "pron", "v": "v", "a": "adj", "r": "adv", "s": "p", "c": "conj"}


def categorias_spacy(resultado):
    return [(p["texto"].lower(), "que" if p["texto"].lower() == "que" else UD.get(p["pos"], p["pos"]))
            for p in resultado["palabras"]]


def categorias_nltk(resultado):
    salida = []
    for p in resultado["palabras"]:
        e = p["etiqueta"]
        if p["texto"] == "que":
            cat = "que"
        elif e.startswith("np"):
            cat = "n_propio"
        else:
            cat = EAGLES.get(e[:1], e)
        salida.append((p["texto"], cat))
    return salida


def categorias_por_arbol(resultado):
    """Parser y LLM: las categorías salen del árbol que devolvieron."""
    arbol = resultado.get("arbol")
    return categorias_de_arbol(arbol) if arbol else None


EXTRAER = {"parser": categorias_por_arbol, "spacy": categorias_spacy, "nltk": categorias_nltk,
           "llm_zero_shot": categorias_por_arbol, "llm_few_shot": categorias_por_arbol}


def normalizar_arbol(texto):
    """Árbol en una línea y con espacios uniformes, para compararlo como texto."""
    try:
        return Tree.fromstring(texto).pformat(margin=10**6)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Lectura y validación
# ---------------------------------------------------------------------------

def leer_corpus():
    with open(CORPUS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for fila in filas:
        fila["id"] = int(fila["id"])
        fila["nivel"] = int(fila["nivel"])
        cats = categorias_de_arbol(fila["arbol_esperado"]) if fila["arbol_esperado"] else None
        fila["categorias"] = cats

        # Qué dice la gramática de esta oración: todos sus árboles (puede haber varios si es
        # ambigua, como la 47) y si la oración pertenece al lenguaje que genera la CFG.
        arboles = {normalizar_arbol(str(a)) for a in todos_los_arboles(fila["oracion"], GRAMATICA, INICIAL)}
        fila["en_gramatica"] = bool(arboles)
        # Árboles que cuentan como correctos: el esperado y cualquier otro que la gramática asigne.
        fila["arboles_validos"] = arboles | ({normalizar_arbol(fila["arbol_esperado"])}
                                             if fila["arbol_esperado"] else set())
    return filas


def leer_log(clave, corpus):
    """Devuelve {id: resultado} o None si el log no existe. Se detiene si el log es de otro corpus."""
    ruta = LOGS / f"{clave}.json"
    if not ruta.exists():
        return None
    with open(ruta, encoding="utf-8") as f:
        log = json.load(f)
    resultados = {r["id"]: r for r in log["resultados"]}

    problemas = []
    if set(resultados) != {f["id"] for f in corpus}:
        problemas.append(f"tiene {len(resultados)} oraciones y el corpus {len(corpus)}")
    else:
        distintas = [f["id"] for f in corpus if resultados[f["id"]]["oracion"] != f["oracion"]]
        if distintas:
            problemas.append(f"el texto de las oraciones {distintas[:5]} no coincide con el corpus")
    if problemas:
        sys.exit(f"ERROR: {ruta.relative_to(AQUI.parent).as_posix()} no corresponde al corpus actual "
                 f"({'; '.join(problemas)}). Vuelvan a correr ese enfoque.")
    return resultados


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------
# Clase positiva = "acepta". Para cada oración:
#   VP verdadero positivo   correcta en español y el enfoque la acepta
#   FN falso negativo       correcta y el enfoque la rechaza (o responde 'invalida')
#   FP falso positivo       incorrecta y el enfoque la acepta (o responde 'invalida')
#   VN verdadero negativo   incorrecta y el enfoque la rechaza
# Una respuesta 'invalida' (el LLM no respetó el formato) siempre cuenta como error.

def clasificar(esperado, salida):
    if esperado == "acepta":
        return "VP" if salida == "acepta" else "FN"
    return "VN" if salida == "rechaza" else "FP"


def dividir(a, b):
    return a / b if b else None


def evaluar(clave, resultados, corpus):
    filas_detalle = {}
    conteo = {"VP": 0, "FN": 0, "FP": 0, "VN": 0}
    invalidas = etiquetado = arbol_distinto = medibles_arbol = 0
    fieles = fuera_aceptadas = 0

    for fila in corpus:
        r = resultados[fila["id"]]
        tipo = clasificar(fila["esperado"], r["salida"])
        conteo[tipo] += 1
        invalidas += r["salida"] == "invalida"

        # Fidelidad a la gramática: acepta exactamente lo que la CFG genera y rechaza lo demás.
        # Una respuesta 'invalida' no es ni aceptar ni rechazar: cuenta como no fiel.
        fiel = (r["salida"] == "acepta" and fila["en_gramatica"]) or \
               (r["salida"] == "rechaza" and not fila["en_gramatica"])
        fieles += fiel
        # Las oraciones clave de la pregunta 2: correctas en español pero fuera de la gramática.
        # Aceptarlas = usar el conocimiento general del español en vez de las reglas dadas.
        if fila["esperado"] == "acepta" and not fila["en_gramatica"]:
            fuera_aceptadas += r["salida"] == "acepta"

        # Error de etiquetado: solo en las aceptadas correctamente (VP) con categorías esperadas.
        error_etq = None
        if tipo == "VP" and fila["categorias"]:
            obtenidas = EXTRAER[clave](r)
            if obtenidas is not None:
                esperadas = [c for _, c in fila["categorias"]]
                error_etq = [c for _, c in obtenidas] != esperadas
                etiquetado += error_etq
            # Parser y LLM entregan árbol: además se compara la estructura completa.
            # Cuenta como correcto cualquier árbol que la gramática asigne: en una oración
            # ambigua (la 47 tiene 2), dar la otra lectura válida no es un error.
            if clave in ("parser", "llm_zero_shot", "llm_few_shot") and r.get("arbol"):
                medibles_arbol += 1
                arbol_distinto += normalizar_arbol(r["arbol"]) not in fila["arboles_validos"]

        filas_detalle[fila["id"]] = {"salida": r["salida"], "tipo": tipo, "error_etiquetado": error_etq,
                                     "fiel": fiel}

    vp, fn, fp, vn = conteo["VP"], conteo["FN"], conteo["FP"], conteo["VN"]
    n = vp + fn + fp + vn
    metricas = {
        "VP": vp, "FN": fn, "FP": fp, "VN": vn, "invalidas": invalidas,
        "exactitud": dividir(vp + vn, n),
        "precision": dividir(vp, vp + fp),
        "cobertura": dividir(vp, vp + fn),
        "rechazo_correcto": dividir(vn, vn + fp),
        "errores_etiquetado": etiquetado,
        "arbol_distinto": arbol_distinto if medibles_arbol else None,
        "fidelidad_cfg": dividir(fieles, n),
        "fuera_cfg_aceptadas": fuera_aceptadas,
    }
    return metricas, filas_detalle


def por_nivel(detalle, corpus):
    salida = {}
    for nivel in sorted({f["nivel"] for f in corpus}):
        ids = [f["id"] for f in corpus if f["nivel"] == nivel]
        tipos = [detalle[i]["tipo"] for i in ids]
        salida[nivel] = {"n": len(ids), "aciertos": tipos.count("VP") + tipos.count("VN"),
                         "FP": tipos.count("FP"), "FN": tipos.count("FN")}
    return salida


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------

def pct(x):
    return "n/d" if x is None else f"{x * 100:.1f} %"


def escribir_csv(ruta, encabezado, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(encabezado)
        escritor.writerows(filas)


def tabla_md(encabezado, filas):
    lineas = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return "\n".join(lineas)


# Una sola familia de azules en todas las gráficas: claro, medio y oscuro.
# Los tres tonos se distinguen por su claridad (validados), y la leyenda y los
# números sobre las barras dicen qué es cada una, así que no dependen solo del color.
AZULES = ["#86b6ef", "#2a78d6", "#104281"]
COLORES = AZULES                                      # métricas: precisión, cobertura, rechazo
NIVELES = AZULES                                      # niveles 1, 2 y 3


def grafica_metricas(nombres, metricas, ruta):
    series = [("precision", "Precisión"), ("cobertura", "Cobertura (recall)"),
              ("rechazo_correcto", "Tasa de rechazo correcto")]
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=200)
    ancho = 0.26
    for k, (clave, etiqueta) in enumerate(series):
        xs = [i + (k - 1) * (ancho + 0.02) for i in range(len(nombres))]
        valores = [(m[clave] or 0) * 100 for m in metricas]
        barras = ax.bar(xs, valores, ancho, color=COLORES[k], label=etiqueta, zorder=2)
        for barra, v in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width() / 2, v + 1.2, f"{v:.0f}", ha="center",
                    va="bottom", fontsize=7.5, color="#3d3d3a")
    estilo_ejes(ax, nombres, "Porcentaje", "Métricas por enfoque (corpus de 60 oraciones)")
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    guardar(fig, ruta)


def grafica_niveles(nombres, niveles, ruta):
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=200)
    ancho = 0.26
    for k, nivel in enumerate((1, 2, 3)):
        xs = [i + (k - 1) * (ancho + 0.02) for i in range(len(nombres))]
        valores = [100 * n[nivel]["aciertos"] / n[nivel]["n"] for n in niveles]
        barras = ax.bar(xs, valores, ancho, color=NIVELES[k], label=f"Nivel {nivel}", zorder=2)
        for barra, v in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width() / 2, v + 1.2, f"{v:.0f}", ha="center",
                    va="bottom", fontsize=7.5, color="#3d3d3a")
    estilo_ejes(ax, nombres, "Exactitud (%)", "Exactitud por nivel de complejidad")
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    guardar(fig, ruta)


def estilo_ejes(ax, nombres, eje_y, titulo):
    ax.set_xticks(range(len(nombres)))
    ax.set_xticklabels(nombres, fontsize=9)
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel(eje_y, fontsize=9, color="#3d3d3a")
    ax.set_title(titulo, fontsize=11, loc="left", color="#1a1a19")
    ax.grid(axis="y", color="#e4e3dc", linewidth=0.8, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#a3a29b")
    ax.tick_params(axis="both", colors="#3d3d3a", length=0, labelsize=8.5)


def guardar(fig, ruta):
    fig.tight_layout()
    fig.savefig(ruta, metadata={"Software": None})   # sin metadatos variables: mismo archivo cada vez
    plt.close(fig)


def main():
    corpus = leer_corpus()
    SALIDA.mkdir(exist_ok=True)

    disponibles, pendientes = [], []
    for clave, nombre in ENFOQUES:
        resultados = leer_log(clave, corpus)
        (disponibles if resultados else pendientes).append((clave, nombre, resultados))

    evaluados = []
    for clave, nombre, resultados in disponibles:
        metricas, detalle = evaluar(clave, resultados, corpus)
        evaluados.append((clave, nombre, metricas, detalle, por_nivel(detalle, corpus)))

    # --- metricas.csv ---
    campos = ["VP", "FN", "FP", "VN", "invalidas", "exactitud", "precision", "cobertura",
              "rechazo_correcto", "errores_etiquetado", "arbol_distinto",
              "fidelidad_cfg", "fuera_cfg_aceptadas"]
    escribir_csv(SALIDA / "metricas.csv", ["enfoque"] + campos,
                 [[c] + [round(m[k], 4) if isinstance(m[k], float) else m[k] for k in campos]
                  for c, _, m, _, _ in evaluados])

    # --- metricas_por_nivel.csv ---
    escribir_csv(SALIDA / "metricas_por_nivel.csv", ["enfoque", "nivel", "oraciones", "aciertos", "FP", "FN"],
                 [[c, nivel, d["n"], d["aciertos"], d["FP"], d["FN"]]
                  for c, _, _, _, niv in evaluados for nivel, d in niv.items()])

    # --- detalle.csv: una fila por oración ---
    encabezado = ["id", "nivel", "oracion", "esperado", "en_gramatica"]
    for c, _, _, _, _ in evaluados:
        encabezado += [f"{c}_salida", f"{c}_tipo", f"{c}_error_etiquetado", f"{c}_fiel_cfg"]
    filas = []
    for f in corpus:
        fila = [f["id"], f["nivel"], f["oracion"], f["esperado"], "si" if f["en_gramatica"] else "no"]
        for _, _, _, det, _ in evaluados:
            d = det[f["id"]]
            fila += [d["salida"], d["tipo"], "" if d["error_etiquetado"] is None else int(d["error_etiquetado"]),
                     int(d["fiel"])]
        filas.append(fila)
    escribir_csv(SALIDA / "detalle.csv", encabezado, filas)

    # --- tablas.md ---
    nombres = [n for _, n, _, _, _ in evaluados]
    total = len(corpus)
    correctas = sum(f["esperado"] == "acepta" for f in corpus)
    t1 = tabla_md(["Métrica"] + nombres, [
        ["Exactitud"] + [pct(m["exactitud"]) for _, _, m, _, _ in evaluados],
        ["Precisión"] + [pct(m["precision"]) for _, _, m, _, _ in evaluados],
        ["Cobertura (recall)"] + [pct(m["cobertura"]) for _, _, m, _, _ in evaluados],
        ["Tasa de rechazo correcto"] + [pct(m["rechazo_correcto"]) for _, _, m, _, _ in evaluados],
    ])
    t2 = tabla_md(["Tipo"] + nombres, [
        ["Verdaderos positivos (VP)"] + [m["VP"] for _, _, m, _, _ in evaluados],
        ["Verdaderos negativos (VN)"] + [m["VN"] for _, _, m, _, _ in evaluados],
        ["Falsos positivos (FP)"] + [m["FP"] for _, _, m, _, _ in evaluados],
        ["Falsos negativos (FN)"] + [m["FN"] for _, _, m, _, _ in evaluados],
        ["Errores de etiquetado (de los VP)"] + [m["errores_etiquetado"] for _, _, m, _, _ in evaluados],
        ["Árbol distinto del esperado (de los VP)"] + ["n/a" if m["arbol_distinto"] is None else m["arbol_distinto"]
                                                       for _, _, m, _, _ in evaluados],
        ["Respuestas inválidas"] + [m["invalidas"] for _, _, m, _, _ in evaluados],
    ])
    t3 = tabla_md(["Nivel"] + nombres, [
        [f"{nivel} ({evaluados[0][4][nivel]['n']} oraciones)"] +
        [f"{niv[nivel]['aciertos']}/{niv[nivel]['n']}" for _, _, _, _, niv in evaluados]
        for nivel in (1, 2, 3)
    ])
    fuera = [f for f in corpus if f["esperado"] == "acepta" and not f["en_gramatica"]]
    en_cfg = sum(f["en_gramatica"] for f in corpus)
    t4 = tabla_md(["Medida"] + nombres, [
        ["Fidelidad a la gramática"] + [pct(m["fidelidad_cfg"]) for _, _, m, _, _ in evaluados],
        [f"Correctas en español fuera de la gramática aceptadas (de {len(fuera)})"] +
        [f"{m['fuera_cfg_aceptadas']}/{len(fuera)}" for _, _, m, _, _ in evaluados],
    ])
    lista_fuera = ", ".join(f"{f['id']} «{f['oracion']}»" for f in fuera)
    texto = (f"# Resultados de la evaluación\n\nCorpus: {total} oraciones ({correctas} correctas, "
             f"{total - correctas} incorrectas). Generado por `python fase2/evaluar.py`.\n\n"
             f"## Métricas\n\n{t1}\n\n## Clasificación de errores\n\n{t2}\n\n"
             f"## Aciertos por nivel\n\n{t3}\n\n"
             f"## Fidelidad a la gramática\n\n"
             f"Mide si el enfoque acepta exactamente las oraciones que genera la CFG ({en_cfg} de {total}) "
             f"y rechaza las demás, sin importar si son correctas en español. Es la medida de la "
             f"pregunta 2: un LLM que sigue las reglas dadas tiene 100 %. El parser es la referencia "
             f"(100 % por construcción); spaCy y NLTK no reciben la gramática, así que en ellos "
             f"solo es informativa.\n\n{t4}\n\n"
             f"Oraciones correctas en español que la gramática no genera: {lista_fuera}. "
             f"Si un enfoque las acepta, usó su conocimiento del español en vez de las reglas.\n")
    if pendientes:
        texto += "\n**Pendientes (sin log todavía):** " + ", ".join(n for _, n, _ in pendientes) + "\n"
    (SALIDA / "tablas.md").write_text(texto, encoding="utf-8")

    # --- gráficas ---
    grafica_metricas(nombres, [m for _, _, m, _, _ in evaluados], SALIDA / "metricas.png")
    grafica_niveles(nombres, [niv for _, _, _, _, niv in evaluados], SALIDA / "aciertos_por_nivel.png")

    print(texto)
    print(f"Archivos en {SALIDA.relative_to(AQUI.parent).as_posix()}/: metricas.csv, metricas_por_nivel.csv, "
          "detalle.csv, tablas.md, metricas.png, aciertos_por_nivel.png")


if __name__ == "__main__":
    main()