"""P4 - Genera el informe de la Fase 2 (PDF con la evidencia adjunta) y el ZIP de entrega.

Mismo formato que el informe de la Fase 1: la fuente es informe/informe_fase2.html y se
imprime con Chromium (Playwright). Este script llena las marcas {{...}} del HTML con:
  - las tablas de fase2/resultados/tablas.md (las que genera evaluar.py), sin copiarlas a mano;
  - el corpus completo de fase2/corpus.csv;
  - el prompt y la respuesta exactos del ID 1 de cada log del LLM.
No usa la red ni la clave de API.

Requiere Playwright y pypdf (ver informe/requirements-informe.txt):
    pip install -r informe/requirements-informe.txt
    playwright install chromium
Ejecutar desde la raíz, después de python fase2/evaluar.py:
    python informe/generar_fase2.py
Salidas: output/pdf/informe_fase2.pdf, output/pdf/entrega_fase2.zip y output/pdf/anexos/.
"""
import csv
import hashlib
import html
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "informe/informe_fase2.html"
DESTINO = RAIZ / "output/pdf"


# ---------------------------------------------------------------------------
# Piezas que se insertan en el HTML
# ---------------------------------------------------------------------------

def celda(texto):
    """Escapa y convierte `código` y **negrita** de Markdown."""
    texto = html.escape(texto.strip())
    texto = re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)


def tabla_html(bloque_md):
    """Tabla Markdown de tablas.md → <table>. Las columnas de cifras se alinean a la derecha."""
    filas = [[c for c in linea.strip().strip("|").split("|")] for linea in bloque_md.strip().splitlines()]
    filas = [f for f in filas if not all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in f)]
    partes = ["<table>"]
    for i, fila in enumerate(filas):
        etiqueta = "th" if i == 0 else "td"
        numerica = ' class="n"'
        partes.append("<tr>" + "".join(
            f"<{etiqueta}{'' if j == 0 else numerica}>{celda(c)}</{etiqueta}>"
            for j, c in enumerate(fila)) + "</tr>")
    partes.append("</table>")
    return "\n".join(partes)


def tablas_oficiales():
    texto = (RAIZ / "fase2/resultados/tablas.md").read_text(encoding="utf-8")
    bloques = re.findall(r"(?:^\|.*(?:\n|$))+", texto, re.M)
    assert len(bloques) == 4, "tablas.md debe tener 4 tablas: métricas, errores, niveles y fidelidad"
    return dict(zip(["METRICAS", "ERRORES", "NIVELES", "FIDELIDAD"], map(tabla_html, bloques)))


def tabla_corpus():
    with (RAIZ / "fase2/corpus.csv").open(encoding="utf-8") as f:
        corpus = list(csv.DictReader(f))
    filas = ["<table class=\"corpus\"><tr><th>ID</th><th>Nivel</th><th>Esperado</th><th>Oración</th></tr>"]
    for r in corpus:
        filas.append(f"<tr><td>{r['id']}</td><td>{r['nivel']}</td><td>{r['esperado']}</td>"
                     f"<td>{html.escape(r['oracion'])}</td></tr>")
    filas.append("</table>")
    return "\n".join(filas)


def evidencia():
    """Archivos que se adjuntan al PDF, los prompts del ID 1 y el manifiesto SHA-256."""
    archivos = ["fase2/corpus.csv", "fase2/gramatica_es.py", "fase2/gramatica_es.txt",
                "fase1/motor.py", "fase2/evaluar.py", "requirements.txt",
                "fase2/resultados/tablas.md", "fase2/documentacion/07_auditoria_corrida.json"]
    archivos += [f"fase2/logs/{n}.json" for n in ["parser", "spacy", "nltk", "llm_zero_shot", "llm_few_shot"]]
    datos = {a: (RAIZ / a).read_bytes() for a in archivos}
    muestras = {}
    for variante in ["zero_shot", "few_shot"]:
        log = json.loads(datos[f"fase2/logs/llm_{variante}.json"])
        assert len(log["resultados"]) == 60 and log["metadatos"]["completo"]
        r = next(x for x in log["resultados"] if x["id"] == 1)
        datos[f"anexos/prompts/{variante}_id1.txt"] = r["prompt"].encode("utf-8")
        muestras[variante] = r
    lineas = ["SHA-256 de la evidencia digital adjunta. Los prompts conservan sus bytes UTF-8."]
    lineas += [hashlib.sha256(v).hexdigest() + "  " + k for k, v in sorted(datos.items())]
    datos["anexos/MANIFIESTO_EVIDENCIA.txt"] = ("\n".join(lineas) + "\n").encode("utf-8")
    return datos, muestras


def html_final(muestras):
    texto = FUENTE.read_text(encoding="utf-8")
    reemplazos = {**tablas_oficiales(), "CORPUS": tabla_corpus()}
    for clave, variante in [("ZERO", "zero_shot"), ("FEW", "few_shot")]:
        r = muestras[variante]
        reemplazos[f"PROMPT_{clave}"] = html.escape(r["prompt"])
        reemplazos[f"RESP_{clave}"] = html.escape(r["respuesta_completa"])
        reemplazos[f"TS_{clave}"] = f"Envío (UTC): {r['timestamp']}. Respuesta (UTC): {r['timestamp_fin']}."
    for clave, valor in reemplazos.items():
        texto = texto.replace("{{" + clave + "}}", valor)
    faltan = re.findall(r"\{\{[A-Z_]+\}\}", texto)
    assert not faltan, f"Marcas sin llenar: {faltan}"
    return texto


# ---------------------------------------------------------------------------
# PDF y ZIP
# ---------------------------------------------------------------------------

def imprimir(texto_html):
    """Imprime el HTML con Chromium. El archivo temporal va junto a la fuente para que
    las rutas relativas de las figuras (../fase2/resultados/*.png) funcionen."""
    temporal = FUENTE.with_name("_informe_fase2_generado.html")
    temporal.write_text(texto_html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            pagina = navegador.new_page()
            pagina.goto(temporal.resolve().as_uri())
            pdf = pagina.pdf(format="Letter", print_background=True, prefer_css_page_size=True)
            navegador.close()
    finally:
        temporal.unlink()
    return pdf


def paquete(datos):
    """ZIP con los archivos del repositorio (sin .git, .venv ni .env), los anexos y el PDF."""
    archivos = subprocess.check_output(["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"],
                                       cwd=RAIZ).decode("utf-8").split("\x00")
    contenido = {}
    for nombre in sorted(set(archivos) - {""}):
        partes = Path(nombre).parts
        if any(p in {".git", ".venv", "__pycache__", "output", "tmp"} or p.startswith(".env") for p in partes):
            continue
        ruta = RAIZ / nombre
        if ruta.is_file():
            contenido[nombre.replace("\\", "/")] = ruta.read_bytes()
    contenido.update({k: v for k, v in datos.items() if k.startswith("anexos/")})
    contenido["output/pdf/informe_fase2.pdf"] = (DESTINO / "informe_fase2.pdf").read_bytes()
    for nombre, datos_archivo in contenido.items():
        if re.search(rb"AIza[0-9A-Za-z_-]{30,}|sk-ant-[0-9A-Za-z_-]{20,}", datos_archivo):
            raise RuntimeError("Posible credencial en un archivo del paquete: " + nombre)
    manifiesto = "\n".join(hashlib.sha256(v).hexdigest() + "  " + k for k, v in sorted(contenido.items())) + "\n"
    contenido["MANIFIESTO_SHA256.txt"] = manifiesto.encode("utf-8")
    with zipfile.ZipFile(DESTINO / "entrega_fase2.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
        for nombre, data in sorted(contenido.items()):
            z.writestr(nombre, data)


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    datos, muestras = evidencia()
    pdf = imprimir(html_final(muestras))

    writer = PdfWriter()
    writer.append(PdfReader(io.BytesIO(pdf)))
    writer.add_metadata({"/Title": "Informe Fase 2 - TLP02-2026 - Grupo 8",
                         "/Author": "Grupo 8 - Carlo Guerra, Federico Calderón, Kelvin Iraheta, Allan López"})
    for nombre, data in datos.items():
        writer.add_attachment(Path(nombre).name, data)
    with (DESTINO / "informe_fase2.pdf").open("wb") as f:
        writer.write(f)
    for nombre, data in datos.items():
        if nombre.startswith("anexos/"):
            ruta = DESTINO / nombre
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(data)
    paquete(datos)

    print(f"PDF: {DESTINO / 'informe_fase2.pdf'} ({len(writer.pages)} páginas, {len(datos)} adjuntos)")
    print(f"ZIP: {DESTINO / 'entrega_fase2.zip'}")


if __name__ == "__main__":
    main()
