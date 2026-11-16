"""P1 - ¿Qué gramáticas son LL(1)? Calcula FIRST, FOLLOW y la tabla LL(1).

Usa el mismo formato de gramática que motor.py: diccionario con
no terminal -> lista de producciones; [] es epsilon; lo que no es clave
es terminal. Una gramática es LL(1) si ninguna celda de la tabla tiene
más de una producción (sin conflictos).

    python fase1/analisis_ll1.py            # resumen de las tres gramáticas
    python fase1/analisis_ll1.py --tabla    # además, la tabla LL(1) de mini-C
"""
import sys

from analisis_explosion import GRAMATICA_BASE
from gramatica_es import GRAMATICA, INICIAL

EPS = "ε"
FIN = "$"

# Mini-C en BNF: la EBNF de parser_formal.py sin *, ? ni paréntesis.
# Cada repetición ( ... )* se vuelve un no terminal recursivo por la derecha.
MINIC = {
    "programa":       [["sentencias", "EOF"]],
    "sentencias":     [["sentencia", "sentencias"], []],
    "sentencia":      [["declaracion"], ["asignacion"], ["si"], ["mientras"], ["bloque"]],
    "declaracion":    [["tipo", "ID", "inicializacion", ";"]],
    "inicializacion": [["=", "expr"], []],
    "tipo":           [["int"], ["float"]],
    "asignacion":     [["ID", "=", "expr", ";"]],
    "si":             [["if", "(", "condicion", ")", "sentencia", "sino"]],
    "sino":           [["else", "sentencia"], []],
    "mientras":       [["while", "(", "condicion", ")", "sentencia"]],
    "bloque":         [["{", "sentencias", "}"]],
    "condicion":      [["expr", "OP_REL", "expr"]],
    "expr":           [["termino", "expr_resto"]],
    "expr_resto":     [["+", "termino", "expr_resto"], ["-", "termino", "expr_resto"], []],
    "termino":        [["factor", "termino_resto"]],
    "termino_resto":  [["*", "factor", "termino_resto"], ["/", "factor", "termino_resto"], []],
    "factor":         [["NUM"], ["ID"], ["(", "expr", ")"]],
}


def first_de_secuencia(simbolos, first, gramatica):
    """FIRST de una secuencia de símbolos; incluye EPS si toda la secuencia puede ser vacía."""
    resultado = set()
    for s in simbolos:
        if s not in gramatica:          # terminal: él mismo y se acabó
            resultado.add(s)
            return resultado
        resultado |= first[s] - {EPS}
        if EPS not in first[s]:
            return resultado
    resultado.add(EPS)                  # todos podían ser vacíos
    return resultado


def calcular_first(gramatica):
    first = {a: set() for a in gramatica}
    cambio = True
    while cambio:                       # se repite hasta que nada crezca (punto fijo)
        cambio = False
        for a, producciones in gramatica.items():
            for prod in producciones:
                nuevo = first_de_secuencia(prod, first, gramatica)
                if not nuevo <= first[a]:
                    first[a] |= nuevo
                    cambio = True
    return first


def calcular_follow(gramatica, inicial, first):
    follow = {a: set() for a in gramatica}
    follow[inicial].add(FIN)
    cambio = True
    while cambio:
        cambio = False
        for a, producciones in gramatica.items():
            for prod in producciones:
                for i, b in enumerate(prod):
                    if b not in gramatica:
                        continue
                    resto = first_de_secuencia(prod[i + 1:], first, gramatica)
                    nuevo = resto - {EPS}
                    if EPS in resto:            # lo que sigue puede desaparecer
                        nuevo |= follow[a]
                    if not nuevo <= follow[b]:
                        follow[b] |= nuevo
                        cambio = True
    return follow


def tabla_ll1(gramatica, inicial):
    """Devuelve la tabla {(no_terminal, terminal): [producciones]}."""
    first = calcular_first(gramatica)
    follow = calcular_follow(gramatica, inicial, first)
    tabla = {}
    for a, producciones in gramatica.items():
        for prod in producciones:
            f = first_de_secuencia(prod, first, gramatica)
            destinos = (f - {EPS}) | (follow[a] if EPS in f else set())
            for t in destinos:
                tabla.setdefault((a, t), []).append(prod)
    return tabla


def conflictos(tabla):
    return {celda: prods for celda, prods in tabla.items() if len(prods) > 1}


def texto(prod):
    return " ".join(prod) if prod else EPS


def resumen(nombre, gramatica, inicial):
    tabla = tabla_ll1(gramatica, inicial)
    choques = conflictos(tabla)
    no_terminales = sorted({a for a, _ in choques})
    print(f"\n{nombre}: {sum(map(len, gramatica.values()))} producciones, "
          f"{len(choques)} celdas en conflicto en {len(no_terminales)} no terminales")
    print("  LL(1):", "sí" if not choques else "no")
    for (a, t), prods in sorted(choques.items())[:8]:
        print(f"  [{a}, {t}] -> " + "  |  ".join(texto(p) for p in prods))
    if len(choques) > 8:
        print(f"  ... y {len(choques) - 8} más")
    return choques


def imprimir_tabla_minic():
    tabla = tabla_ll1(MINIC, "programa")
    print("\nTabla LL(1) de mini-C (solo celdas con producción):")
    for a in MINIC:
        celdas = sorted((t, prods) for (x, t), prods in tabla.items() if x == a)
        print(f"  {a}: " + "; ".join(f"{t} -> {' | '.join(texto(p) for p in prods)}"
                                      for t, prods in celdas))


if __name__ == "__main__":
    # Comprobaciones: el único conflicto de mini-C es el else colgante,
    # y las dos gramáticas del español no son LL(1).
    assert set(resumen("Mini-C (BNF)", MINIC, "programa")) == {("sino", "else")}
    assert resumen("Español base", GRAMATICA_BASE, INICIAL)
    assert resumen("Español extendida", GRAMATICA, INICIAL)
    if "--tabla" in sys.argv:
        imprimir_tabla_minic()
