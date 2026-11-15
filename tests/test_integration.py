import sys
import tempfile
import threading
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from rpa.api import APIClient,APIError
from rpa.mock_api import criar_servidor
from rpa.robot import RoboTriagem, decidir_responsavel, sintetizar_fontes

class TestIntegracaoContratoReal(unittest.TestCase):
    def setUp(self):
        self.server,self.state=criar_servidor()
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.temp=tempfile.TemporaryDirectory()
        self.api=APIClient(f"http://127.0.0.1:{self.server.server_port}",tentativas=2,espera=.01,timeout=1)
    def tearDown(self):
        self.server.shutdown();self.thread.join(timeout=5);self.server.server_close();self.temp.cleanup()
    def robo(self,aplicar=False):
        return RoboTriagem(self.api,Path(self.temp.name)/"logs",aplicar=aplicar)
    def test_get_real_retorna_lista(self):
        self.assertEqual(len(self.api.listar(status="recebido")),5)
    def test_assistente_objetos_de_fonte(self):
        resp=self.api.perguntar("buraco")
        self.assertFalse(resp["recusa"])
        self.assertEqual(sintetizar_fontes(resp["fontes"]),"Lei Municipal 15.442/2011")
        self.assertEqual(decidir_responsavel(resp["resposta"]),"proprietario")
    def test_dry_run_nao_escreve(self):
        result=self.robo().executar()
        self.assertEqual(result["sucessos"],5)
        self.assertEqual(self.state.patch_calls,0)
        self.assertEqual(len(self.api.listar(status="recebido")),5)
    def test_transicoes_automaticas(self):
        result=self.robo(aplicar=True).executar()
        self.assertEqual((result["encaminhados"],result["revisoes"],result["descartados"]),(2,2,1))
        self.assertEqual(result["falhas"],0)
        self.assertEqual([r["status"] for r in self.state.relatos],
                         ["encaminhado","descartado","revisao_humana","revisao_humana","encaminhado"])
        self.assertEqual(self.state.relatos[0]["prioridade"],5)
        self.assertEqual(len(self.state.encaminhamentos),2)
    def test_segunda_execucao_idempotente(self):
        self.robo(aplicar=True).executar()
        self.assertEqual(self.robo(aplicar=True).executar()["itens"],0)
    def test_api_503_get_retenta(self):
        self.state.get_falhas=1
        result=self.robo(aplicar=True).executar()
        self.assertEqual(result["sucessos"],5)
        self.assertEqual(self.state.get_calls,4)
    def test_assistente_indisponivel_registra_erros(self):
        self.state.assistente_foradoar=True
        result=self.robo(aplicar=True).executar()
        self.assertEqual(result["falhas"],3)
        self.assertEqual(result["revisoes"],2)
        self.assertEqual(self.state.relatos[0]["status"],"recebido")
    def test_falha_posterior_em_triagem_identificada(self):
        self.state.patch_falha_status="encaminhado"
        result=self.robo(aplicar=True).executar()
        self.assertGreaterEqual(result["falhas"],1)
        self.assertEqual(self.state.relatos[0]["status"],"em_triagem")
    def test_logs_sem_gps(self):
        self.robo(aplicar=True).executar()
        log=(Path(self.temp.name)/"logs"/"auditoria.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("-23.5505",log)
        self.assertNotIn("Dados fictícios",log)
        self.assertIn("resumo_execucao",log)
    def test_status_direto_recebido_encaminhado_nao_permitido(self):
        with self.assertRaises(APIError) as ctx:
            self.api.alterar(101,"encaminhado",prioridade=5)
        self.assertIn("409",str(ctx.exception))
    def test_prioridade_escala_antiga_85_rejeitada(self):
        with self.assertRaises(APIError) as ctx:
            self.api.alterar(101,"em_triagem",prioridade=85)
        self.assertIn("422",str(ctx.exception))
