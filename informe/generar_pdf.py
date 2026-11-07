"""P4 - Genera informe_fase1.pdf a partir de informe_fase1.html.

Requiere Playwright (no está en requirements.txt porque solo se usa aquí):
    pip install playwright
    playwright install chromium
Ejecutar desde la raíz: python informe/generar_pdf.py

Sin Playwright: abrir informe_fase1.html en Chrome o Edge → Imprimir →
Guardar como PDF, tamaño Carta, márgenes predeterminados y "Gráficos de fondo" activado.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

CARPETA = Path(__file__).parent
ORIGEN = CARPETA / "informe_fase1.html"
DESTINO = CARPETA / "informe_fase1.pdf"

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page()
    pagina.goto(ORIGEN.resolve().as_uri())
    pagina.pdf(path=str(DESTINO), format="Letter", print_background=True, prefer_css_page_size=True)
    navegador.close()

print(f"PDF generado: {DESTINO}")
