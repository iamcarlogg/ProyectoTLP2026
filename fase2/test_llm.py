"""Pruebas sin red ni claves: python -m unittest discover -s fase2 -p test_llm.py -v"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import llm_experimento as llm
from preparar_prompts import leer_ejemplos, leer_entradas
from validar_respuesta_llm import interpretar


class Formato(unittest.TestCase):
    def test_ejemplos_y_arboles_esperados(self):
        for e in leer_ejemplos():
            r = interpretar(json.dumps(e["respuesta"]), e["oracion"])
            self.assertEqual(r["salida"], e["respuesta"]["salida"])
            if r["salida"] == "acepta":
                self.assertTrue(r["arbol_valido_cfg"])
        # Incluye epsilon y todos los árboles de referencia dentro de la CFG.
        import csv
        with (llm.AQUI / "corpus.csv").open(encoding="utf-8") as f:
            for e in csv.DictReader(f):
                if e["arbol_esperado"] and int(e["id"]) not in range(49, 53):
                    r = interpretar(json.dumps({"salida": "acepta", "arbol": e["arbol_esperado"]}), e["oracion"])
                    self.assertTrue(r["arbol_valido_cfg"], e["id"])

    def test_formatos_invalidos(self):
        for texto in ['```json\n{}\n```', '[]', '{}',
                      '{"salida":"acepta","arbol":null}',
                      '{"salida":"rechaza","arbol":"(x)"}',
                      '{"salida":"rechaza","salida":"acepta","arbol":null}',
                      '{"salida":"acepta","arbol":"(oracion"}']:
            self.assertEqual(interpretar(texto, "El perro duerme.")["salida"], "invalida")

    def test_error_gramatical_no_corrige_veredicto(self):
        r = interpretar('{"salida":"acepta","arbol":"(oracion (inventado hola))"}', "El perro duerme.")
        self.assertEqual(r["salida"], "acepta")
        self.assertFalse(r["arbol_valido_cfg"])
        self.assertEqual(interpretar('{"salida":"rechaza","arbol":null}', "El perro duerme.")["salida"], "rechaza")

    def test_truncamiento_es_invalida(self):
        r = interpretar('{"salida":"rechaza","arbol":null}', "x", "max_tokens")
        self.assertEqual(r["salida"], "invalida")

    def test_ambiguedad_acepta_otra_adjuncion(self):
        texto = '(oracion (sn_ms (det_ms el) (n_ms perro) (mod_ms)) (sv_s (vt_s come) (sn (sn_fs (det_fs la) (n_fs carne) (mod_fs))) (sp (p en) (sn (sn_fs (det_fs la) (n_fs casa) (mod_fs))))))'
        r = interpretar(json.dumps({"salida": "acepta", "arbol": texto}), 'El perro come la carne en la casa.')
        self.assertTrue(r["arbol_valido_cfg"])


class Corrida(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ruta = Path(self.temp.name) / "log.json"
        self.entradas = leer_entradas()[:2]
        self.config = llm.configuracion("zero-shot", self.entradas)
        self.log = llm.cargar_log(self.ruta, self.config, self.entradas)

    def enviar(self, clave, prompt):
        return json.dumps({"modelVersion": llm.MODELO, "usageMetadata": {},
                           "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": '{"salida":"rechaza","arbol":null}'}]}}]}), "prueba"

    def ejecutar(self, **kwargs):
        llm.ejecutar(self.log, self.ruta, self.entradas, "zero-shot", "clave_ficticia",
                     pausa=0, **kwargs)

    def test_reanudar_no_repite_y_guarda_bruto(self):
        with patch.object(llm, "guardar", wraps=llm.guardar) as guardar:
            self.ejecutar(enviar=self.enviar)
            self.assertTrue(any(c.args[1]["intentos"] for c in guardar.call_args_list))
        self.assertEqual(len(self.log["resultados"]), 2)
        self.assertTrue(self.log["metadatos"]["completo"])
        self.ejecutar(enviar=lambda *_: self.fail("Repetición de API"))
        self.assertEqual(len(self.log["resultados"]), 2)
        self.assertIn("respuesta_http", self.log["resultados"][0])
        self.assertNotIn("clave_ficticia", self.ruta.read_text(encoding="utf-8"))

    def test_respuesta_guardada_se_recupera_sin_api(self):
        with patch.object(llm, "registrar", side_effect=RuntimeError("interrupción simulada")):
            with self.assertRaises(RuntimeError):
                self.ejecutar(enviar=self.enviar)
        self.assertEqual(self.log["intentos"][0]["estado"], "recibido")
        self.entradas = self.entradas[:1]
        self.ejecutar(enviar=lambda *_: self.fail("Se repitió una respuesta recibida"))
        self.assertEqual(len(self.log["resultados"]), 1)

    def test_limite_de_llamadas_y_reanudacion(self):
        self.ejecutar(enviar=self.enviar, max_nuevas=1)
        self.assertEqual([r["id"] for r in self.log["resultados"]], [1])
        self.assertFalse(self.log["metadatos"]["completo"])
        self.ejecutar(enviar=self.enviar, max_nuevas=1)
        self.assertEqual([r["id"] for r in self.log["resultados"]], [1, 2])
        self.assertTrue(self.log["metadatos"]["completo"])

    def test_error_api_no_es_rechazo_ni_reintento_automatico(self):
        def falla(*_):
            raise llm.ErrorAPI("HTTP_429")
        with self.assertRaises(ValueError):
            self.ejecutar(enviar=falla)
        self.assertEqual(self.log["resultados"], [])
        with self.assertRaises(ValueError):
            self.ejecutar(enviar=lambda *_: self.fail("Reintento no autorizado"))
        self.ejecutar(enviar=self.enviar, reintentar=True)
        self.assertEqual(len(self.log["resultados"]), 2)

    def test_cambio_configuracion_y_duplicados_bloqueados(self):
        llm.guardar(self.ruta, self.log)
        otra = copy.deepcopy(self.config)
        otra["modelo"] = "otro"
        with self.assertRaises(ValueError):
            llm.cargar_log(self.ruta, otra, self.entradas)
        self.log["resultados"] = [self.entradas[0], self.entradas[0]]
        llm.guardar(self.ruta, self.log)
        with self.assertRaises(ValueError):
            llm.cargar_log(self.ruta, self.config, self.entradas)

    def test_clave_solo_en_archivo_temporal_y_prioridad_entorno(self):
        ruta = Path(self.temp.name) / ".env"
        ruta.write_text('GEMINI_API_KEY="valor_ficticio"\n', encoding="utf-8")
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(llm.cargar_clave(ruta), "valor_ficticio")
        with patch.dict("os.environ", {"GEMINI_API_KEY": "entorno_ficticio"}):
            self.assertEqual(llm.cargar_clave(ruta), "entorno_ficticio")

    def test_bloqueo_excluye_segunda_corrida(self):
        with llm.bloqueo(Path(self.temp.name)):
            with self.assertRaises(ValueError):
                with llm.bloqueo(Path(self.temp.name)):
                    self.fail("Dos corridas simultáneas")

    def test_peticion_gemini_independiente_y_parametros(self):
        from unittest.mock import MagicMock
        respuesta = MagicMock()
        respuesta.__enter__.return_value = respuesta
        respuesta.read.return_value = b'{"content": []}'
        respuesta.headers.get.return_value = "request-ficticio"
        with patch.object(llm, "urlopen", return_value=respuesta) as abrir:
            llm.solicitar("clave_ficticia", "prompt de prueba")
        peticion = abrir.call_args.args[0]
        cuerpo = json.loads(peticion.data)
        self.assertEqual(cuerpo["contents"], [{"role": "user", "parts": [{"text": "prompt de prueba"}]}])
        self.assertEqual(cuerpo["generationConfig"]["temperature"], 0)
        self.assertEqual(cuerpo["generationConfig"]["thinkingConfig"], {"thinkingLevel": "MINIMAL"})
        self.assertIn("gemini-3.1-flash-lite:generateContent", peticion.full_url)
        self.assertEqual(peticion.get_header("X-goog-api-key"), "clave_ficticia")
        self.assertNotIn("clave_ficticia", peticion.full_url)
        self.assertNotIn("clave_ficticia", peticion.data.decode())

    def test_plan_no_lee_clave_ni_crea_logs(self):
        with patch("sys.argv", ["llm_experimento.py"]), \
                patch.object(llm, "cargar_clave", side_effect=AssertionError("Leyó clave")), \
                patch.object(llm, "guardar", side_effect=AssertionError("Escribió log")), \
                patch.object(llm, "solicitar", side_effect=AssertionError("Usó red")):
            llm.main()

    def test_gemini_separa_pensamiento_y_conserva_respuesta_integra(self):
        def enviar(*_):
            return json.dumps({"modelVersion": llm.MODELO, "responseId": "simulado",
                               "usageMetadata": {"thoughtsTokenCount": 5},
                               "candidates": [{"finishReason": "STOP", "content": {"parts": [
                                   {"thought": True, "text": "pensamiento simulado"},
                                   {"text": '{"salida":"rechaza","arbol":null}'}]}}]}), None
        self.ejecutar(enviar=enviar, max_nuevas=1)
        resultado = self.log["resultados"][0]
        self.assertEqual(resultado["salida"], "rechaza")
        self.assertNotIn("pensamiento simulado", resultado["respuesta_completa"])
        self.assertIn("pensamiento simulado", resultado["respuesta_http"])
        self.assertEqual(resultado["uso_tokens"]["thoughtsTokenCount"], 5)

    def test_gemini_bloqueo_sin_candidatos_no_cuenta_como_rechazo(self):
        self.ejecutar(enviar=lambda *_: ('{"promptFeedback":{"blockReason":"SAFETY"}}', None),
                      max_nuevas=1)
        self.assertEqual(self.log["resultados"][0]["salida"], "invalida")


if __name__ == "__main__":
    unittest.main()
