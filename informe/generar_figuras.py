"""P4 - Genera la figura SVG del informe en informe/figuras/.

- figura1_arbol_a.svg y figura1_arbol_b.svg: los dos árboles de la CFG para
  «El perro come la carne en la casa» (ambigüedad estructural).

Ejecutar desde la raíz, antes de generar_pdf.py:  python informe/generar_figuras.py
"""
import re
import sys
from pathlib import Path

CARPETA = Path(__file__).parent
sys.path.insert(0, str(CARPETA.parent / "fase1"))

from nltk.tree import Tree, TreePrettyPrinter        # noqa: E402

from gramatica_es import GRAMATICA, INICIAL         # noqa: E402
from motor import todos_los_arboles                 # noqa: E402

SALIDA = CARPETA / "figuras"
SALIDA.mkdir(exist_ok=True)


def sin_vacios(arbol):
    """Quita los nodos ε (p. ej. mod_fs sin hijos) para que el dibujo sea legible."""
    if isinstance(arbol, str):
        return arbol
    hijos = [sin_vacios(h) for h in arbol if isinstance(h, str) or len(h) > 0]
    return Tree(arbol.label(), hijos)


# Figura 1: los dos árboles de la oración ambigua.
arboles = todos_los_arboles("El perro come la carne en la casa", GRAMATICA, INICIAL)
assert len(arboles) == 2, "se esperaban 2 árboles"
for letra, arbol in zip("ab", arboles):
    compacto = sin_vacios(arbol)
    compacto.collapse_unary(collapsePOS=False, joinChar="/")   # sn → sn_fs se dibuja como "sn/sn_fs"
    svg = TreePrettyPrinter(compacto).svg(nodecolor="#1f2a5a", leafcolor="#b03a2e")
    # nltk pone el tamaño en "em" con otra proporción que el viewBox; se usa el del
    # viewBox para que el dibujo no tenga márgenes en blanco y el PDF lo mida bien.
    _, _, ancho, alto = re.search(r'viewBox="([^"]*)"', svg).group(1).split()
    svg = re.sub(r'width="[^"]*em" height="[^"]*em"', f'width="{ancho}" height="{alto}"', svg, count=1)
    (SALIDA / f"figura1_arbol_{letra}.svg").write_text(svg, encoding="utf-8")


print(f"Figuras generadas en {SALIDA}")
