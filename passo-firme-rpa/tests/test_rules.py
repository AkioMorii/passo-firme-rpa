import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from rpa.mock_api import DADOS
from rpa.rules import principal, validar, prioridade, distancia_m, eh_duplicado

class TestRegrasContratoReal(unittest.TestCase):
    def test_sem_foto_url_retorna_valido(self):
        self.assertNotIn("foto_url", DADOS[0])
        self.assertEqual(validar(DADOS[0]), [])
    def test_sem_deteccao_revisar(self):
        self.assertIn("sem_deteccao", validar(DADOS[3]))
    def test_latitude_invalida(self):
        item=deepcopy(DADOS[0]); item["lat"]=-100
        self.assertIn("gps_invalido", validar(item))
    def test_classe_real_e_confianca(self):
        self.assertEqual(principal(DADOS[2]),("degrau_desnivel",.44))
    def test_pontuacao_1_a_5(self):
        self.assertEqual(prioridade(DADOS[0]),5)
        self.assertEqual(prioridade(DADOS[4]),3)
    def test_duplicado_menos_25m(self):
        self.assertLess(distancia_m(DADOS[0],DADOS[1]),25)
        self.assertTrue(eh_duplicado(DADOS[1],[DADOS[0]]))
    def test_duplicado_distante_nao_descarta(self):
        self.assertFalse(eh_duplicado(DADOS[4],[DADOS[0]]))
    def test_janela_48h(self):
        item=deepcopy(DADOS[0]); item["criado_em"]="2026-11-01T09:00:00-03:00"
        self.assertFalse(eh_duplicado(DADOS[1],[item]))
