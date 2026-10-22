"""Motor genérico: analiza oraciones con CUALQUIER gramática escrita como diccionario.

Es descendente recursivo con vuelta atrás (backtracking): prueba cada producción en
orden y, si un camino no funciona, regresa y prueba el siguiente. Devuelve TODOS los
árboles posibles, así se puede ver cuándo una oración es ambigua.

Reglas para escribir la gramática:
- Clave = no terminal; valor = lista de producciones (cada una, lista de símbolos).
- Lo que no es clave se trata como palabra. Ningún no terminal puede llamarse
  igual que una palabra.
- [] es una producción vacía (ε).
- Sin recursión por la izquierda (a → a ...): provoca RecursionError.
"""
from nltk import Tree


def _analizar(simbolo, palabras, i, gramatica):
    """Genera (arbol, j) por cada forma en que `simbolo` cubre palabras[i:j]."""
    if simbolo not in gramatica:                  # no tiene reglas: es una palabra
        if i < len(palabras) and palabras[i] == simbolo:
            yield simbolo, i + 1
        return
    for produccion in gramatica[simbolo]:         # prueba cada opción de la regla
        for hijos, j in _secuencia(produccion, palabras, i, gramatica):
            yield Tree(simbolo, hijos), j


def _secuencia(simbolos, palabras, i, gramatica):
    """Genera (lista_de_hijos, j) para una lista de símbolos seguidos."""
    if not simbolos:
        yield [], i
        return
    primero, resto = simbolos[0], simbolos[1:]
    for arbol, j in _analizar(primero, palabras, i, gramatica):
        for otros, k in _secuencia(resto, palabras, j, gramatica):
            yield [arbol] + otros, k


def todos_los_arboles(oracion, gramatica, inicial):
    """Lista de árboles que cubren la oración completa. Lista vacía = rechazada."""
    palabras = oracion.lower().replace(".", "").replace(",", "").split()
    return [arbol for arbol, j in _analizar(inicial, palabras, 0, gramatica)
            if j == len(palabras)]


def parsear(oracion, gramatica, inicial):
    """El primer árbol encontrado, o None si la oración no cumple la gramática."""
    arboles = todos_los_arboles(oracion, gramatica, inicial)
    return arboles[0] if arboles else None


if __name__ == "__main__":
    from gramatica_es import GRAMATICA, INICIAL

    oraciones = [
        "El perro negro come la carne",
        "La perro come",
        "Los perros duermen",
        "El perro duermen",
    ]
    for oracion in oraciones:
        arbol = parsear(oracion, GRAMATICA, INICIAL)
        print(oracion, "->", arbol if arbol else "RECHAZADA")
        print()
