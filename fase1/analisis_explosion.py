"""P2 - Tarea 5: explosion de producciones y costo de concordancia.

Ejecutar desde la raiz del repositorio:
    python fase1/analisis_explosion.py
    python fase1/analisis_explosion.py --probar

No modifica gramatica_es.py, motor.py ni ningun archivo de P1.
Se cuentan como producciones las alternativas en las listas de GRAMATICA:
    "sn": [["det", "n"], ["det", "n", "adj"]] = 2 producciones.
Las alternativas vacias ([]) tambien cuentan como una produccion.
"""

import argparse
from collections import OrderedDict

from gramatica_es import GRAMATICA, INICIAL


# Instantanea de la tarea 2: se conserva aqui solo para hacer el estudio
# reproducible. La gramatica operativa SIGUE en gramatica_es.py.
GRAMATICA_BASE = {
    "oracion": [["sn", "sv"]],
    "sn": [["det", "n"], ["det", "n", "adj"]],
    "sv": [["v"], ["v", "sn"]],
    "det": [["el"], ["la"], ["los"], ["las"]],
    "n": [["perro"], ["perros"], ["gata"], ["gatas"], ["carne"]],
    "adj": [["negro"], ["negros"], ["negra"], ["negras"]],
    "v": [["come"], ["comen"], ["duerme"], ["duermen"]],
}


def contar_producciones(gramatica):
    return sum(len(alternativas) for alternativas in gramatica.values())


def terminales(gramatica):
    no_terminales = set(gramatica)
    return {
        simbolo
        for producciones in gramatica.values()
        for produccion in producciones
        for simbolo in produccion
        if simbolo not in no_terminales
    }


def normalizar_categoria(simbolo):
    """Elimina las distinciones de concordancia, NO las estructuras ni palabras.

    Mantiene sn (SN general) separado de sn_tipo (SN con rasgos antes
    de normalizar) para evitar una produccion circular sn -> sn.
    """
    if "_" not in simbolo:
        return simbolo

    tipo, sufijo = simbolo.rsplit("_", 1)
    if tipo in {"sn", "mod", "det", "n", "adj"} and sufijo in {"ms", "fs", "mp", "fp"}:
        return "sn_tipo" if tipo == "sn" else tipo
    if tipo in {"sv", "v", "vt"} and sufijo in {"s", "p"}:
        return tipo
    if tipo == "rel_suj" and sufijo in {"s", "p"}:
        return tipo
    return simbolo
def sin_concordancia(gramatica):
    """Contrafactual: mismas estructuras y vocabulario, sin rasgos.

    Fusiona categorias equivalentes y elimina producciones repetidas.
    No es el archivo de la tarea 2; es una variante de control obtenida
    automaticamente de la gramatica extendida.
    """
    resultado = {}
    for categoria, producciones in gramatica.items():
        destino = resultado.setdefault(normalizar_categoria(categoria), [])
        for produccion in producciones:
            opcion = [normalizar_categoria(simbolo) for simbolo in produccion]
            if opcion not in destino:
                destino.append(opcion)
    return resultado


def grupos(gramatica, fusionada=False):
    """Cuenta grupos funcionales para explicar de donde salen las reglas."""
    if fusionada:
        categorias = {
            "oracion": ["oracion"],
            "sintagma nominal": ["sn", "sn_tipo"],
            "modificadores nominales": ["mod"],
            "relativas": ["rel_suj", "rel_obj"],
            "sintagma verbal": ["sv"],
        }
    else:
        categorias = {
            "oracion": ["oracion"],
            "sintagma nominal": ["sn", "sn_ms", "sn_fs", "sn_mp", "sn_fp"],
            "modificadores nominales": ["mod_ms", "mod_fs", "mod_mp", "mod_fp"],
            "relativas": ["rel_suj_s", "rel_suj_p", "rel_obj"],
            "sintagma verbal": ["sv_s", "sv_p"],
        }

    salida = OrderedDict()
    incluidas = set()
    for nombre, miembros in categorias.items():
        faltantes = set(miembros) - set(gramatica)
        if faltantes:
            raise ValueError(f"Faltan categorias para '{nombre}': {sorted(faltantes)}")
        salida[nombre] = sum(len(gramatica[m]) for m in miembros)
        incluidas.update(miembros)
    salida["lexico, SP y adverbios"] = sum(
        len(producciones) for categoria, producciones in gramatica.items()
        if categoria not in incluidas
    )
    assert sum(salida.values()) == contar_producciones(gramatica)
    return salida


def comprobar_pruebas(base, control, completa):
    # Imports diferidos: el recuento principal solo necesita Python estandar.
    from motor import parsear
    from pruebas_base import PRUEBAS

    print("\nPRUEBAS DE CONTROL (20 ORACIONES ORIGINALES)")
    for nombre, gramatica in (
        ("Base", base),
        ("Ampliada sin concordancia", control),
        ("Extendida con concordancia", completa),
    ):
        aciertos = sum(
            (parsear(oracion, gramatica, INICIAL) is not None) == es_valida
            for oracion, es_valida in PRUEBAS
        )
        print(f"  {nombre:28} {aciertos}/{len(PRUEBAS)} clasificaciones correctas")


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--probar", action="store_true", help="Ejecutar tambien las 20 oraciones (requiere nltk)")
    args = argumentos.parse_args()

    base = GRAMATICA_BASE
    extendida = GRAMATICA
    control = sin_concordancia(extendida)

    assert contar_producciones(base) == 22, "La instantanea base fue alterada"
    assert terminales(control) == terminales(extendida), "La fusion altero el vocabulario"

    print("TAREA 5 - EXPLOSION DE REGLAS (ALTERNATIVAS DE PRODUCCION)")
    print(f"{'Version':36} {'No terminales':>14} {'Producciones':>14} {'Terminales':>12}")
    for nombre, g in (
        ("Tarea 2: base", base),
        ("Control: ampliada sin concordancia", control),
        ("Tarea 3: ampliada con concordancia", extendida),
    ):
        print(f"{nombre:36} {len(g):14} {contar_producciones(g):14} {len(terminales(g)):12}")

    b, s, e = [contar_producciones(g) for g in (base, control, extendida)]
    print(f"\nAmpliacion de estructuras y vocabulario: {s} - {b} = +{s-b} producciones")
    print(f"Costo de representar concordancia explicitamente: {e} - {s} = +{e-s} producciones")
    print(f"Aumento total: {e} - {b} = +{e-b}; factor {e/b:.2f}x")

    sin, con = grupos(control, True), grupos(extendida, False)
    print("\nDESGLOSE DEL COSTO DE CONCORDANCIA (MISMO VOCABULARIO Y ESTRUCTURAS)")
    print(f"{'Grupo':30} {'Sin rasgos':>12} {'Con rasgos':>12} {'Diferencia':>12}")
    for grupo in sin:
        print(f"{grupo:30} {sin[grupo]:12} {con[grupo]:12} {con[grupo]-sin[grupo]:+12}")
    assert sum(con[x]-sin[x] for x in sin) == e-s

    print("\nINTERPRETACION: son medidas de esta implementacion particular, no")
    print("un crecimiento obligatorio para toda CFG o todo el idioma espanol.")
    if args.probar:
        comprobar_pruebas(base, control, extendida)


if __name__ == "__main__":
    main()