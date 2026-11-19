"""Interpreta formato sin corregir decisiones o derivaciones del modelo."""
import json
import re

from gramatica_es import GRAMATICA, INICIAL
from preparar_prompts import normalizar


def leer_arbol(texto):
    tokens = re.findall(r"\(|\)|[^\s()]+", texto)
    posicion = 0

    def nodo():
        nonlocal posicion
        if posicion >= len(tokens) or tokens[posicion] != "(":
            raise ValueError("Se esperaba un nodo.")
        posicion += 1
        if posicion >= len(tokens) or tokens[posicion] in ("(", ")"):
            raise ValueError("Falta etiqueta.")
        etiqueta = tokens[posicion]
        posicion += 1
        hijos = []
        while posicion < len(tokens) and tokens[posicion] != ")":
            if tokens[posicion] == "(":
                hijos.append(nodo())
            else:
                hijos.append(tokens[posicion])
                posicion += 1
        if posicion >= len(tokens):
            raise ValueError("Falta cierre.")
        posicion += 1
        return etiqueta, hijos

    raiz = nodo()
    if posicion != len(tokens):
        raise ValueError("Contenido después del árbol.")
    return raiz


def comprobar_derivacion(arbol, oracion):
    errores, hojas = [], []

    def recorrer(nodo):
        etiqueta, hijos = nodo
        produccion = [h[0] if isinstance(h, tuple) else h for h in hijos]
        if etiqueta not in GRAMATICA or produccion not in GRAMATICA[etiqueta]:
            errores.append("produccion")
        for hijo in hijos:
            if isinstance(hijo, tuple):
                recorrer(hijo)
            else:
                hojas.append(hijo)

    if arbol[0] != INICIAL:
        errores.append("raiz")
    recorrer(arbol)
    if hojas != normalizar(oracion):
        errores.append("hojas")
    return sorted(set(errores))


def sin_duplicados(pares):
    objeto = {}
    for clave, valor in pares:
        if clave in objeto:
            raise ValueError("Clave JSON repetida.")
        objeto[clave] = valor
    return objeto


def interpretar(respuesta, oracion, stop_reason="end_turn"):
    invalida = {"salida": "invalida", "arbol": None,
                "arbol_valido_cfg": None, "errores_arbol": []}
    try:
        if stop_reason != "end_turn":
            raise ValueError("Respuesta incompleta o interrumpida: " + str(stop_reason))
        dato = json.loads(respuesta, object_pairs_hook=sin_duplicados)
        if not isinstance(dato, dict) or set(dato) != {"salida", "arbol"}:
            raise ValueError("Se requieren exactamente salida y arbol.")
        if dato["salida"] not in ("acepta", "rechaza"):
            raise ValueError("Veredicto desconocido.")
        if dato["salida"] == "rechaza":
            if dato["arbol"] is not None:
                raise ValueError("Un rechazo requiere arbol null.")
            return {**dato, "arbol_valido_cfg": None, "errores_arbol": [], "error_formato": None}
        if not isinstance(dato["arbol"], str) or not dato["arbol"].strip():
            raise ValueError("Una aceptación requiere un árbol.")
        errores = comprobar_derivacion(leer_arbol(dato["arbol"]), oracion)
        return {**dato, "arbol_valido_cfg": not errores,
                "errores_arbol": errores, "error_formato": None}
    except (ValueError, TypeError, RecursionError):
        # No incluir texto libre del servidor en diagnósticos operativos.
        return {**invalida, "error_formato": "Respuesta fuera del contrato o incompleta."}
