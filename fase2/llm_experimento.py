"""Gemini por API. Sin --ejecutar solo muestra un plan local, sin leer .env.

python fase2/llm_experimento.py
python fase2/llm_experimento.py --ejecutar
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid

from preparar_prompts import AQUI, VARIANTES, construir_prompt, leer_ejemplos, leer_entradas
from validar_respuesta_llm import interpretar

MODELO = "gemini-3.1-flash-lite"
VERSION_API = "v1beta"
PARAMETROS = {"temperature": 0, "maxOutputTokens": 2048,
              "thinkingConfig": {"thinkingLevel": "MINIMAL"}}
ENDPOINT = f"https://generativelanguage.googleapis.com/{VERSION_API}/models/{MODELO}:generateContent"


def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def guardar(ruta, dato):
    temporal = ruta.with_suffix(".json.tmp")
    with temporal.open("w", encoding="utf-8", newline="\n") as archivo:
        json.dump(dato, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")
        archivo.flush()
        os.fsync(archivo.fileno())
    temporal.replace(ruta)


def cargar_clave(ruta):
    clave = os.environ.get("GEMINI_API_KEY", "").strip()
    if not clave and ruta.exists():
        for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
            nombre, separador, valor = linea.strip().removeprefix("export ").partition("=")
            if separador and nombre.strip() == "GEMINI_API_KEY":
                valor = valor.strip()
                if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                    valor = valor[1:-1]
                clave = valor.strip()
                break
    if not clave or any(c.isspace() for c in clave):
        raise ValueError("Falta una GEMINI_API_KEY válida en el entorno o .env.")
    return clave


def configuracion(variante, entradas):
    fuentes = ["corpus.csv", "gramatica_es.txt", "gramatica_es.py", "prompts/base.txt",
               "prompts/few_shot.json", "preparar_prompts.py", "validar_respuesta_llm.py",
               "llm_experimento.py"]
    return {"version": 1, "variante": variante, "modelo": MODELO,
            "api_version": VERSION_API, "parametros": PARAMETROS,
            "endpoint": ENDPOINT, "ids": [e["id"] for e in entradas],
            "sha256_fuentes": {f: hashlib.sha256((AQUI / f).read_bytes()).hexdigest()
                               for f in fuentes}}


def cargar_log(ruta, config, entradas):
    if not ruta.exists():
        return {"metadatos": {"enfoque": "llm_" + config["variante"].replace("-", "_"),
                              "fecha": ahora(), "proveedor": "Google", "modelo": MODELO,
                              "temperatura": 0, "max_tokens": PARAMETROS["maxOutputTokens"],
                              "parametros": PARAMETROS, "api_version": VERSION_API,
                              "python": platform.python_version(), "corpus": "fase2/corpus.csv",
                              "oraciones": len(entradas), "completo": False,
                              "configuracion": config}, "resultados": [], "intentos": []}
    log = json.loads(ruta.read_text(encoding="utf-8"))
    if log["metadatos"].get("configuracion") != config:
        raise ValueError("El log pertenece a otra configuración. No se pueden mezclar corridas.")
    esperadas = {e["id"]: e["oracion"] for e in entradas}
    ids = [r["id"] for r in log["resultados"]]
    if len(ids) != len(set(ids)) or any(
            r["id"] not in esperadas or r["oracion"] != esperadas[r["id"]]
            for r in log["resultados"]):
        raise ValueError("Log con resultados duplicados o ajenos al corpus.")
    return log


class ErrorAPI(Exception):
    def __init__(self, codigo):
        self.codigo = codigo
        super().__init__(codigo)


def solicitar(clave, prompt):
    cuerpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
              "generationConfig": PARAMETROS}
    peticion = Request(ENDPOINT, data=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
                       headers={"Content-Type": "application/json", "x-goog-api-key": clave},
                       method="POST")
    try:
        with urlopen(peticion, timeout=120) as respuesta:
            contenido = respuesta.read().decode("utf-8")
            request_id = respuesta.headers.get("x-request-id") or respuesta.headers.get("x-goog-request-id")
        return contenido, request_id
    except HTTPError as error:
        codigo = "HTTP_" + str(error.code)
        try:
            dato = json.loads(error.read().decode("utf-8"))
            tipo = dato.get("error", {}).get("status")
            if tipo in {"INVALID_ARGUMENT", "UNAUTHENTICATED", "PERMISSION_DENIED", "NOT_FOUND",
                        "RESOURCE_EXHAUSTED", "INTERNAL", "UNAVAILABLE", "FAILED_PRECONDITION"}:
                codigo += ":" + tipo
            mensaje = str(dato.get("error", {}).get("message", "")).lower()
            if "credit balance" in mensaje or "insufficient credit" in mensaje:
                codigo += ":saldo_insuficiente"
        except (ValueError, AttributeError, OSError):
            pass
        raise ErrorAPI(codigo) from None
    except (URLError, TimeoutError, OSError):
        raise ErrorAPI("conexion_o_timeout") from None


def registrar(log, intento):
    api = json.loads(intento["respuesta_http"])
    candidatos = api.get("candidates", [])
    candidato = candidatos[0] if candidatos else {}
    texto = "".join(b.get("text", "") for b in candidato.get("content", {}).get("parts", [])
                    if not b.get("thought"))
    fin = candidato.get("finishReason")
    resultado = {k: intento[k] for k in ("id", "oracion", "prompt", "timestamp", "timestamp_fin",
                                       "intento_id", "request_id", "respuesta_http", "tiempo_ms")}
    resultado.update(respuesta_completa=texto, modelo_devuelto=api.get("modelVersion"),
                     uso_tokens=api.get("usageMetadata"), stop_reason=fin,
                     response_id=api.get("responseId"))
    resultado.update(interpretar(texto, intento["oracion"], "end_turn" if fin == "STOP" else fin))
    log["resultados"].append(resultado)
    intento["estado"] = "registrado"


def ejecutar(log, ruta, entradas, variante, clave, reintentar=False, enviar=solicitar, pausa=1,
             max_nuevas=None):
    # Recupera respuestas guardadas antes de una interrupción, sin consultar la API.
    hechos = {r["id"] for r in log["resultados"]}
    for intento in log["intentos"]:
        if intento["estado"] == "recibido" and intento["id"] not in hechos:
            registrar(log, intento)
            hechos.add(intento["id"])
            guardar(ruta, log)
    nuevas = 0
    for entrada in entradas:
        identificador = entrada["id"]
        if identificador in hechos:
            continue
        if max_nuevas is not None and nuevas >= max_nuevas:
            break
        anteriores = [i for i in log["intentos"] if i["id"] == identificador]
        if anteriores and not reintentar:
            raise ValueError("Hay un intento sin resultado. Revisar antes de usar --reintentar-errores.")
        intento = {**entrada, "intento_id": str(uuid.uuid4()), "timestamp": ahora(),
                   "prompt": construir_prompt(entrada["oracion"], variante), "estado": "enviado"}
        log["intentos"].append(intento)
        guardar(ruta, log)
        inicio = time.perf_counter()
        try:
            raw, request_id = enviar(clave, intento["prompt"])
        except ErrorAPI as error:
            intento.update(estado="error_api", codigo_error=error.codigo, timestamp_fin=ahora())
            guardar(ruta, log)
            raise ValueError("API detenida: " + error.codigo + ". No se reintentó automáticamente.") from None
        intento.update(respuesta_http=raw, request_id=request_id, estado="recibido",
                       timestamp_fin=ahora(), tiempo_ms=round((time.perf_counter()-inicio)*1000, 3))
        guardar(ruta, log)  # Evidencia íntegra antes de interpretar.
        nuevas += 1
        registrar(log, intento)
        hechos.add(identificador)
        log["metadatos"].update(completo=len(hechos) == len(entradas), actualizado=ahora())
        guardar(ruta, log)
        print(f"{variante}: {len(hechos)}/{len(entradas)} (id {identificador})", flush=True)
        if pausa:
            time.sleep(pausa)
    log["metadatos"].update(completo=len(hechos) == len(entradas), actualizado=ahora())
    guardar(ruta, log)
    return nuevas


@contextmanager
def bloqueo(carpeta):
    ruta = carpeta / ".llm.lock"
    try:
        descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError("Existe .llm.lock: hay otra corrida o una interrupción pendiente de revisar.") from None
    try:
        os.close(descriptor)
        yield
    finally:
        ruta.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="Envía solicitudes de pago.")
    parser.add_argument("--variante", choices=(*VARIANTES, "ambas"), default="ambas")
    parser.add_argument("--max-nuevas", type=int,
                        help="Máximo de llamadas nuevas en total; no cambia la configuración experimental.")
    parser.add_argument("--reintentar-errores", action="store_true",
                        help="Autoriza repetir intentos sin respuesta local; podrían haberse cobrado.")
    args = parser.parse_args()
    if args.max_nuevas is not None and args.max_nuevas < 1:
        parser.error("--max-nuevas debe ser positivo.")
    entradas = leer_entradas()
    leer_ejemplos()
    variantes = VARIANTES if args.variante == "ambas" else (args.variante,)
    planes = []
    # Valida todos los logs seleccionados antes de la primera llamada.
    for variante in variantes:
        ruta = AQUI / "logs" / ("llm_" + variante.replace("-", "_") + ".json")
        log = cargar_log(ruta, configuracion(variante, entradas), entradas)
        pendientes = len(entradas) - len(log["resultados"])
        print(f"{variante}: {pendientes} resultados pendientes; modelo {MODELO}; max_tokens 2048.")
        planes.append((variante, ruta, log))
    if not args.ejecutar:
        print("Solo plan local. No se leyó .env, no se escribieron logs ni se usó la API.")
        return
    clave = cargar_clave(AQUI.parent / ".env")
    (AQUI / "logs").mkdir(exist_ok=True)
    with bloqueo(AQUI / "logs"):
        restantes = args.max_nuevas
        for variante, ruta, log in planes:
            if restantes == 0:
                break
            log = cargar_log(ruta, configuracion(variante, entradas), entradas)
            usadas = ejecutar(log, ruta, entradas, variante, clave, args.reintentar_errores,
                              max_nuevas=restantes)
            if restantes is not None:
                restantes -= usadas


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError):
        # Mensajes de excepciones de terceros podrían contener cabeceras o credenciales.
        raise SystemExit("Corrida detenida. Revise configuración e intentos guardados; no hay reintentos automáticos.") from None
