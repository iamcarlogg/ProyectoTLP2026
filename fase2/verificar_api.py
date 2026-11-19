"""Cuenta tokens de cuatro prompts representativos; no genera respuestas.

python fase2/verificar_api.py --consultar
"""
import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import llm_experimento as llm
from preparar_prompts import construir_prompt, leer_entradas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consultar", action="store_true")
    args = parser.parse_args()
    if not args.consultar:
        print("Use --consultar para enviar cuatro prompts al contador de tokens de Google.")
        return
    clave = llm.cargar_clave(llm.AQUI.parent / ".env")
    entradas = leer_entradas()
    larga = max(entradas, key=lambda e: len(e["oracion"]))
    mediciones = []
    for variante in ["zero-shot", "few-shot"]:
        for entrada in [entradas[0], larga]:
            prompt = construir_prompt(entrada["oracion"], variante)
            cuerpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            peticion = Request(llm.ENDPOINT.replace(":generateContent", ":countTokens"),
                               data=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
                               headers={"Content-Type": "application/json", "x-goog-api-key": clave},
                               method="POST")
            try:
                with urlopen(peticion, timeout=30) as respuesta:
                    dato = json.loads(respuesta.read())
            except HTTPError as error:
                raise SystemExit("Conteo detenido: HTTP " + str(error.code)) from None
            except (URLError, TimeoutError, OSError):
                raise SystemExit("Conteo detenido por conexión o timeout; no se generaron respuestas.") from None
            medicion = {"variante": variante, "id": entrada["id"], "caracteres": len(prompt),
                        "input_tokens_estimados": dato["totalTokens"]}
            mediciones.append(medicion)
            print(json.dumps(medicion, ensure_ascii=False), flush=True)
    # Rango de una muestra: no es una cota matemática para los otros prompts.
    muestras = [m["input_tokens_estimados"] for m in mediciones]
    entrada_estimada = sum(muestras) / len(muestras) * 120
    reporte = {"fecha": llm.ahora(), "modelo": llm.MODELO, "api_version": llm.VERSION_API,
               "fuente_precios": "https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite",
               "usd_millon_entrada": 0.25, "usd_millon_salida": 1.50,
               "nota": "Costo de tarifa de pago. Puede ser cero con cuota gratuita disponible; no comprueba facturación ni créditos.",
               "metodo": "Muestra de 4 prompts: no es conteo exacto de las 120 entradas.",
               "mediciones": mediciones, "entrada_tokens_estimada": entrada_estimada,
               "costo_entrada_estimado_usd": entrada_estimada * 0.25 / 1000000,
               "tope_salida_tokens": 120 * llm.PARAMETROS["maxOutputTokens"],
               "tope_costo_solo_salida_usd": 120 * llm.PARAMETROS["maxOutputTokens"] * 1.50 / 1000000}
    llm.guardar(llm.AQUI / "documentacion/06_verificacion_gemini.json", reporte)
    print("Conteo completado. No se generaron respuestas del experimento.")


if __name__ == "__main__":
    main()
