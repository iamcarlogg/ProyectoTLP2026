"""Reanuda con pausas SOLO intentos HTTP 503 explícitos, sin cambiar el corredor.

python fase2/continuar_corrida.py --ejecutar
Máximo tres reintentos consecutivos sin progreso; no reintenta timeouts ni 429.
"""
import argparse
import json
import sys
import time

import llm_experimento as llm
from preparar_prompts import leer_entradas, leer_ejemplos, VARIANTES


def estado():
    total = 0
    errores = []
    for ruta in (llm.AQUI / "logs").glob("llm_*.json"):
        log = json.loads(ruta.read_text(encoding="utf-8"))
        hechos = {r["id"] for r in log["resultados"]}
        total += len(hechos)
        pendientes = {}
        for intento in log["intentos"]:
            if intento["id"] not in hechos:
                pendientes[intento["id"]] = intento
        errores.extend(pendientes.values())
    return total, errores


def correr():
    entradas = leer_entradas()
    leer_ejemplos()
    clave = llm.cargar_clave(llm.AQUI.parent / ".env")
    planes = []
    for variante in VARIANTES:
        ruta = llm.AQUI / "logs" / ("llm_" + variante.replace("-", "_") + ".json")
        config = llm.configuracion(variante, entradas)
        llm.cargar_log(ruta, config, entradas)  # Validar todo antes de enviar.
        planes.append((variante, ruta, config))
    with llm.bloqueo(llm.AQUI / "logs"):
        for variante, ruta, config in planes:
            log = llm.cargar_log(ruta, config, entradas)
            # No dejar que una entrada con 503 impida intentar las demás.
            # Todas siguen incluidas y cada llamada carece de historial.
            fallos = {}
            for intento in log["intentos"]:
                if intento.get("estado") == "error_api":
                    fallos[intento["id"]] = fallos.get(intento["id"], 0) + 1
            orden = sorted(entradas, key=lambda e: (fallos.get(e["id"], 0), e["id"]))
            llm.ejecutar(log, ruta, orden, variante, clave, reintentar=True, pausa=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true")
    args = parser.parse_args()
    if not args.ejecutar:
        print("Solo ayuda local. --ejecutar reanuda solicitudes reales con reintentos limitados de HTTP 503.")
        return
    sin_progreso = 0
    while True:
        antes, errores = estado()
        if any(i.get("estado") != "error_api" or i.get("codigo_error") != "HTTP_503:UNAVAILABLE"
               for i in errores):
            raise SystemExit("Existe un intento ambiguo o un error distinto de 503. Revisión manual requerida.")
        try:
            correr()
            return
        except (ValueError, KeyError):
            despues, errores = estado()
            if not errores or any(i.get("codigo_error") != "HTTP_503:UNAVAILABLE" for i in errores):
                raise SystemExit("Corrida detenida por un error distinto de HTTP 503; revisar logs.") from None
            sin_progreso = 1 if despues > antes else sin_progreso + 1
            if sin_progreso > 3:
                raise SystemExit("Tres reintentos sin progreso. Se conserva toda la evidencia.") from None
            demora = min(15 * sin_progreso, 45)
            print(f"HTTP 503; {despues}/120 guardadas. Espera de {demora} segundos antes de reanudar.", flush=True)
            time.sleep(demora)


if __name__ == "__main__":
    main()
