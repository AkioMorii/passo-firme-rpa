import sys
import tempfile
import threading
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rpa.api import APIClient
from rpa.mock_api import criar_servidor
from rpa.robot import RoboTriagem


class TestIntegracao(unittest.TestCase):
    def setUp(self):
        self.servidor, self.estado = criar_servidor(port=0)
        self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.temp = tempfile.TemporaryDirectory()
        self.cliente = APIClient(f"http://127.0.0.1:{self.servidor.server_port}",
                                 tentativas=2, espera=0.001, timeout=1)

    def tearDown(self):
        self.servidor.shutdown()
        self.thread.join(timeout=3)
        self.servidor.server_close()
        self.temp.cleanup()

    def robo(self):
        return RoboTriagem(self.cliente, Path(self.temp.name) / "logs", Path(self.temp.name) / "outbox")

    def test_lote_completo_e_idempotencia(self):
        r = self.robo().executar()
        self.assertEqual(r["itens"], 5)
        self.assertEqual(r["sucessos"], 5)
        self.assertEqual(r["falhas"], 0)
        self.assertEqual(r["encaminhados"], 2)
        self.assertEqual(r["revisoes"], 2)
        self.assertEqual(r["descartados"], 1)
        self.assertEqual([x["status"] for x in self.estado.relatos],
                         ["encaminhado", "descartado", "revisao_humana", "revisao_humana", "encaminhado"])
        self.assertTrue((Path(self.temp.name) / "outbox" / "relato_101.json").exists())
        self.assertEqual(self.robo().executar()["itens"], 0)

    def test_api_intermitente_tenta_novamente(self):
        self.estado.falhar_get_vezes = 1
        r = self.robo().executar()
        self.assertEqual(r["sucessos"], 5)
        self.assertEqual(self.estado.quantidade_get, 2)

    def test_assistente_fora_do_ar_nao_interrompe_lote(self):
        self.estado.falhar_assistente = True
        r = self.robo().executar()
        self.assertEqual(r["falhas"], 3)  # relatos válidos 101, 102 e 105 falham na consulta
        self.assertEqual(r["revisoes"], 2)  # invalidos/confiança baixa continuam tratados
        self.assertEqual(self.estado.relatos[0]["status"], "recebido")
        self.assertGreaterEqual(self.estado.quantidade_assistente, 1)

    def test_patch_com_falha_nao_interrompe_outros(self):
        self.estado.falhar_patch_ids.add(101)
        r = self.robo().executar()
        self.assertEqual(r["falhas"], 1)
        self.assertEqual(r["sucessos"], 4)
        self.assertEqual(self.estado.relatos[0]["status"], "recebido")

    def test_logs_nao_contem_gps_ou_urls(self):
        self.robo().executar()
        texto = (Path(self.temp.name) / "logs" / "auditoria.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("-23.550500", texto)
        self.assertNotIn("example.org", texto)
        self.assertIn("resumo_execucao", texto)


if __name__ == "__main__":
    unittest.main()
