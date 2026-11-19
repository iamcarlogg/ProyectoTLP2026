"""Genera el informe Fase 2 y ZIP de evidencia sin red ni clave de API.

Instalar informe/requirements-informe.txt y ejecutar: python informe/generar_fase2.py
Fuente editable: informe/informe_fase2.md. Salidas: output/pdf/.
"""
from pathlib import Path
import csv
import hashlib
import html
import io
import json
import re
import subprocess
import textwrap
import zipfile

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from pypdf import PdfReader, PdfWriter

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "output/pdf"
ANCHO, ALTO = letter
MARGEN = 54
UTIL = ANCHO - 2 * MARGEN
AZUL = colors.HexColor("#164b78")
GRIS = colors.HexColor("#4c5963")


def fuentes():
    windows = Path("C:/Windows/Fonts")
    vera = Path(reportlab.__file__).parent / "fonts"
    archivos = {"Texto": (windows / "calibri.ttf", vera / "Vera.ttf"),
                "Texto-Bold": (windows / "calibrib.ttf", vera / "VeraBd.ttf"),
                "Texto-Italic": (windows / "calibrii.ttf", vera / "VeraIt.ttf"),
                "Mono": (windows / "consola.ttf", vera / "Vera.ttf")}
    for nombre, opciones in archivos.items():
        ruta = next(p for p in opciones if p.exists())
        pdfmetrics.registerFont(TTFont(nombre, str(ruta)))
    pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Bold", italic="Texto-Italic")


def inline(texto):
    texto = html.escape(texto)
    texto = re.sub(r"`([^`]+)`", r'<font name="Mono" size="8.8">\1</font>', texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#164b78">\1</link>', texto)
    return texto


class Paginas:
    def __init__(self):
        self.memoria = io.BytesIO()
        self.c = canvas.Canvas(self.memoria, pagesize=letter, pageCompression=1)
        self.c.setTitle("Informe técnico Fase 2 - TLP02-2026 - Grupo 8")
        self.c.setAuthor("Carlo Guerra; Federico Calderón; Kelvin Iraheta; Allan López")
        self.numero = 0
        self.anexo = False
        self.titulo_anexo = "Anexos"

    def nueva(self, principal=None, anexo="Anexos"):
        if self.numero:
            self.c.showPage()
        self.numero += 1
        self.anexo = principal is None
        self.titulo_anexo = anexo
        c = self.c
        c.setFillColor(AZUL)
        c.setFont("Texto-Bold", 9)
        c.drawString(MARGEN, ALTO - 33, "TLP02-2026  |  GRUPO 8")
        c.setFillColor(GRIS)
        c.setFont("Texto", 8.8)
        c.drawRightString(ANCHO-MARGEN, ALTO-33, "FASE 2 · EVIDENCIA EXPERIMENTAL")
        c.setStrokeColor(AZUL)
        c.setLineWidth(1.2)
        c.line(MARGEN, ALTO-42, ANCHO-MARGEN, ALTO-42)
        c.setStrokeColor(colors.HexColor("#ccd6de"))
        c.setLineWidth(0.5)
        c.line(MARGEN, 44, ANCHO-MARGEN, 44)
        c.setFont("Texto", 8.5)
        c.setFillColor(GRIS)
        c.drawString(MARGEN, 29, "18 noviembre 2026 · Parser, NLP y Gemini")
        etiqueta = f"Informe principal · {principal}/10" if principal else f"Anexos · {self.numero-10}"
        c.drawRightString(ANCHO-MARGEN, 29, etiqueta)
        self.y = ALTO - 62

    def espacio(self, alto):
        if self.y - alto < 58:
            if not self.anexo:
                raise RuntimeError(f"Desborde en página principal {self.numero}: faltan {alto:.1f} puntos con y={self.y:.1f}")
            self.nueva(anexo=self.titulo_anexo)
            self.parrafo(self.titulo_anexo + " (continuación)", "h2")

    def parrafo(self, texto, tipo="p"):
        estilos = {
            "p": dict(fontSize=10.3, leading=14.1, alignment=TA_JUSTIFY, spaceAfter=7),
            "h1": dict(fontName="Texto-Bold", fontSize=20, leading=23.5, textColor=AZUL, spaceAfter=13),
            "h2": dict(fontName="Texto-Bold", fontSize=13.2, leading=16.1, textColor=AZUL, spaceAfter=9),
            "h3": dict(fontName="Texto-Bold", fontSize=11.4, leading=14.5, textColor=AZUL, spaceAfter=7),
            "nota": dict(fontSize=8.8, leading=11.4, textColor=GRIS, spaceAfter=8),
        }
        datos = {"fontName": "Texto", "textColor": colors.HexColor("#16212b"), **estilos[tipo]}
        if tipo == "p" and re.match(r"^\[\d+\]", texto):
            datos["alignment"] = 0
        despues = datos.pop("spaceAfter")
        p = Paragraph(inline(texto), ParagraphStyle("bloque", **datos))
        _, alto = p.wrap(UTIL, ALTO)
        self.espacio(alto+despues)
        p.drawOn(self.c, MARGEN, self.y-alto)
        self.y -= alto+despues

    def tabla(self, filas, anchos=None, tam=8.9):
        n = len(filas[0])
        if anchos is None:
            if n == 6:
                anchos = [178]+[(UTIL-178)/(n-1)]*(n-1)
            elif n == 4 and filas[0][0] == "ID":
                anchos = [28, UTIL-172, 72, 72]
            elif n == 5 and filas[0][0] == "Nivel":
                anchos = [80,55,60,45,UTIL-240]
            else:
                anchos = [UTIL/n]*n
        st = ParagraphStyle("celda", fontName="Texto", fontSize=tam, leading=tam+2.1)
        celdas = [[Paragraph(inline(str(t)), st) for t in fila] for fila in filas]
        t = Table(celdas, colWidths=anchos)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e4edf5")),
            ("LINEBELOW", (0,0), (-1,0), 0.7, AZUL),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f8fa")]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.HexColor("#ccd6de")),
        ]))
        _, alto = t.wrap(UTIL, ALTO)
        self.espacio(alto+10)
        t.drawOn(self.c, MARGEN, self.y-alto)
        self.y -= alto+10

    def imagen(self, ruta, caption):
        img = Image(str(ruta))
        alto = UTIL * img.imageHeight/img.imageWidth
        self.espacio(alto+32)
        img.drawHeight, img.drawWidth = alto, UTIL
        img.drawOn(self.c, MARGEN, self.y-alto)
        self.y -= alto+4
        self.parrafo(caption, "nota")

    def codigo(self, texto, fuente=8.0, interlineado=10.1):
        # Se envuelve solo para impresión; los anexos digitales retienen el texto exacto.
        limite = 110 if fuente < 8.2 else 100
        for original in texto.splitlines():
            lineas = textwrap.wrap(original.expandtabs(4), width=limite, break_long_words=True,
                                   break_on_hyphens=False, replace_whitespace=False,
                                   drop_whitespace=False) or [""]
            for linea in lineas:
                self.espacio(interlineado)
                self.c.setFillColor(colors.HexColor("#243746"))
                self.c.setFont("Mono", fuente)
                self.c.drawString(MARGEN+5, self.y-interlineado+2, linea)
                self.y -= interlineado
        self.y -= 8

    def markdown(self, texto):
        lineas = texto.splitlines()
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            if not linea:
                i += 1
                continue
            if linea.startswith("```"):
                i += 1
                bloque = []
                while i < len(lineas) and not lineas[i].startswith("```"):
                    bloque.append(lineas[i]); i += 1
                self.codigo("\n".join(bloque)); i += 1
            elif linea.startswith("|"):
                filas = []
                while i < len(lineas) and lineas[i].strip().startswith("|"):
                    campos = [x.strip() for x in lineas[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-+:?", x) for x in campos):
                        filas.append(campos)
                    i += 1
                self.tabla(filas)
            elif linea.startswith("!["):
                m = re.fullmatch(r"!\[(.*)\]\((.*)\)", linea)
                self.imagen((RAIZ/"informe"/m[2]).resolve(), m[1]); i += 1
            elif linea.startswith("#"):
                nivel = len(linea)-len(linea.lstrip("#"))
                self.parrafo(linea[nivel:].strip(), {1:"h1",2:"h2",3:"h3"}[nivel]); i += 1
            elif linea.startswith("- "):
                self.parrafo("• " + linea[2:]); i += 1
            else:
                bloque = [linea]; i += 1
                while i < len(lineas) and lineas[i].strip() and not lineas[i].startswith(("#", "|", "```", "![", "- ")):
                    bloque.append(lineas[i].strip()); i += 1
                self.parrafo(" ".join(bloque))


def tablas_oficiales():
    texto = (RAIZ/"fase2/resultados/tablas.md").read_text(encoding="utf-8")
    bloques = re.findall(r"(?:^\|.*(?:\n|$))+", texto, re.M)
    assert len(bloques) == 4
    return {"METRICAS": bloques[0], "ERRORES": bloques[1], "FIDELIDAD": bloques[3]}


def evidencia():
    archivos = ["fase2/corpus.csv", "fase2/gramatica_es.py", "fase2/gramatica_es.txt",
                "fase1/motor.py", "fase2/evaluar.py", "requirements.txt",
                "fase2/resultados/tablas.md", "fase2/documentacion/07_auditoria_corrida.json"]
    archivos += [f"fase2/logs/{n}.json" for n in ["parser","spacy","nltk","llm_zero_shot","llm_few_shot"]]
    datos = {a: (RAIZ/a).read_bytes() for a in archivos}
    muestras = {}
    for variante in ["zero_shot", "few_shot"]:
        log = json.loads(datos[f"fase2/logs/llm_{variante}.json"])
        assert len(log["resultados"]) == 60 and log["metadatos"]["completo"]
        r = next(x for x in log["resultados"] if x["id"] == 1)
        clave = f"anexos/prompts/{variante}_id1.txt"
        datos[clave] = r["prompt"].encode("utf-8")
        muestras[variante] = r
    lineas = ["SHA-256 de la evidencia digital adjunta. Los prompts conservan sus bytes UTF-8."]
    lineas += [hashlib.sha256(v).hexdigest()+"  "+k for k,v in sorted(datos.items())]
    datos["anexos/MANIFIESTO_EVIDENCIA.txt"] = ("\n".join(lineas)+"\n").encode("utf-8")
    return datos, muestras


def anexos(paginas, datos, muestras):
    paginas.nueva(anexo="Anexo A. Evidencia digital")
    paginas.parrafo("Anexo A. Evidencia digital y trazabilidad", "h1")
    paginas.parrafo("Los archivos completos están incorporados como adjuntos del PDF y también en el ZIP de entrega. Si el visor no muestra adjuntos, abrir el ZIP. Los logs incluyen todas las respuestas, no solo ejemplos seleccionados. Los saltos de línea se conservan en los TXT y JSON; su impresión puede envolverse visualmente.")
    filas = [["Evidencia", "Ubicación en el paquete"]]
    filas += [["Corpus completo y árboles esperados", "fase2/corpus.csv"],
              ["Cinco logs completos", "fase2/logs/parser.json, spacy.json, nltk.json, llm_zero_shot.json y llm_few_shot.json"],
              ["Todos los prompts y respuestas con timestamp", "Campos prompt, respuesta_completa, respuesta_http y timestamp en ambos logs del LLM"],
              ["Gramática, motor y evaluador", "fase2/gramatica_es.py, gramatica_es.txt; fase1/motor.py; fase2/evaluar.py"],
              ["Tablas y gráficas", "fase2/resultados/"],
              ["Huellas y auditoría", "fase2/documentacion/07_auditoria_corrida.json; anexos/MANIFIESTO_EVIDENCIA.txt"],
              ["Prompts exactos del ID 1", "anexos/prompts/zero_shot_id1.txt y few_shot_id1.txt"],
              ["Código de P4 y metodología", "fase2/llm_experimento.py, preparar_prompts.py, validar_respuesta_llm.py y documentacion/04_llm.md"],
              ["Reproducción", "README.md, fase2/README.md y requirements.txt"]]
    paginas.tabla(filas, [180, UTIL-180])
    paginas.parrafo("Integridad", "h3")
    paginas.parrafo("El manifiesto adjunto identifica cada archivo de evidencia por SHA-256. El ZIP incluye además un manifiesto de todos sus contenidos. Los cinco logs se verificaron contra el corpus. La reproducción de las cifras no necesita conexión con Google ni una clave de API.")
    paginas.parrafo("El PDF y el ZIP representan una versión local de entrega. El enlace Git debe apuntar a una revisión que incluya estos cambios antes de enviar el correo institucional. No se incluyen .env, entornos virtuales ni el historial .git.")

    with (RAIZ/"fase2/corpus.csv").open(encoding="utf-8") as f:
        corpus = list(csv.DictReader(f))
    for inicio in [0,30]:
        paginas.nueva(anexo="Anexo B. Corpus completo")
        paginas.parrafo(f"Anexo B. Corpus completo ({inicio+1}–{inicio+30})", "h1")
        paginas.parrafo("La etiqueta indica corrección en español. Los árboles esperados completos se conservan en el CSV adjunto; 49–52 son positivas en español y negativas para la CFG.", "nota")
        filas = [["ID", "Nivel", "Esperado", "Oración"]]
        filas += [[r["id"],r["nivel"],r["esperado"],r["oracion"]] for r in corpus[inicio:inicio+30]]
        paginas.tabla(filas, [25,34,57,UTIL-116], tam=8.4)

    for letra,variante in [("C","zero_shot"),("D","few_shot")]:
        titulo = f"Anexo {letra}. Prompt {variante.replace('_','-')} exacto"
        paginas.nueva(anexo=titulo)
        paginas.parrafo(titulo, "h1")
        r = muestras[variante]
        paginas.parrafo("Transcripción del prompt enviado al ID 1. Los otros 59 prompts de la variante se conservan íntegros en su log; cambia la oración de entrada. El TXT adjunto conserva el texto exacto, sin la envoltura visual de esta impresión.", "nota")
        paginas.codigo(r["prompt"], fuente=7.4, interlineado=9.3)
        paginas.parrafo("Respuesta completa y timestamp del ejemplo", "h3")
        paginas.parrafo(f"Inicio UTC: {r['timestamp']}. Fin UTC: {r['timestamp_fin']}.", "nota")
        paginas.codigo(r["respuesta_completa"], fuente=8, interlineado=10.1)


def paquete(datos):
    archivos = subprocess.check_output(["git","ls-files","-c","-o","--exclude-standard","-z"], cwd=RAIZ).decode("utf-8").split("\x00")
    contenido = {}
    for nombre in sorted(set(archivos)-{""}):
        partes = Path(nombre).parts
        if any(p in {".git",".venv","__pycache__","output","tmp"} or p.startswith(".env") for p in partes):
            continue
        ruta = RAIZ/nombre
        if ruta.is_file():
            contenido[nombre.replace("\\","/")] = ruta.read_bytes()
    contenido.update({k:v for k,v in datos.items() if k.startswith("anexos/")})
    contenido["output/pdf/informe_fase2.pdf"] = (DESTINO/"informe_fase2.pdf").read_bytes()
    for nombre, datos_archivo in contenido.items():
        if re.search(rb"AIza[0-9A-Za-z_-]{30,}|sk-ant-[0-9A-Za-z_-]{20,}", datos_archivo):
            raise RuntimeError("Posible credencial en un archivo del paquete: "+nombre)
    manifiesto = "\n".join(hashlib.sha256(v).hexdigest()+"  "+k for k,v in sorted(contenido.items()))+"\n"
    contenido["MANIFIESTO_SHA256.txt"] = manifiesto.encode("utf-8")
    with zipfile.ZipFile(DESTINO/"entrega_fase2.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
        for nombre, data in sorted(contenido.items()):
            z.writestr(nombre,data)


def main():
    fuentes()
    DESTINO.mkdir(parents=True, exist_ok=True)
    datos, muestras = evidencia()
    texto = (RAIZ/"informe/informe_fase2.md").read_text(encoding="utf-8")
    for clave, tabla in tablas_oficiales().items():
        texto = texto.replace("{{"+clave+"}}", tabla)
    partes = texto.split("<!-- PAGE -->")
    assert len(partes) == 10, "El cuerpo debe tener diez páginas explícitas."
    paginas = Paginas()
    for numero, parte in enumerate(partes,1):
        paginas.nueva(principal=numero)
        paginas.markdown(parte)
    anexos(paginas,datos,muestras)
    paginas.c.save()
    paginas.memoria.seek(0)
    writer = PdfWriter()
    writer.append(PdfReader(paginas.memoria))
    writer.add_metadata({"/Title":"Informe Fase 2 - TLP02-2026 - Grupo 8", "/Author":"Grupo 8 - Carlo Guerra, Federico Calderón, Kelvin Iraheta, Allan López"})
    for nombre, data in datos.items():
        writer.add_attachment(Path(nombre).name, data)
    for nombre, data in datos.items():
        if nombre.startswith("anexos/"):
            ruta = DESTINO/nombre
            ruta.parent.mkdir(parents=True,exist_ok=True)
            ruta.write_bytes(data)
    with (DESTINO/"informe_fase2.pdf").open("wb") as f:
        writer.write(f)
    paquete(datos)
    print(f"PDF: {DESTINO/'informe_fase2.pdf'}")
    print(f"Páginas: 10 de informe + {paginas.numero-10} de anexos; {len(datos)} archivos adjuntos.")
    print(f"ZIP: {DESTINO/'entrega_fase2.zip'}")


if __name__ == "__main__":
    main()
