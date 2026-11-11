import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rpa.mock_api import DADOS_EXEMPLO
from rpa.rules import calcular_prioridade, classe_principal, distancia_m, duplicado, validar


class TestRegras(unittest.TestCase):
    def test_relato_valido(self):
        self.assertEqual(validar(DADOS_EXEMPLO[0]), [])

    def test_foto_e_gps_invalidos(self):
        self.assertIn("foto_ausente_ou_url_invalida", validar(DADOS_EXEMPLO[3]))
        self.assertIn("gps_fora_de_faixa", validar(DADOS_EXEMPLO[3]))

    def test_menor_que_25_metros_e_mesma_classe_duplicado(self):
        self.assertLess(distancia_m(DADOS_EXEMPLO[0], DADOS_EXEMPLO[1]), 25)
        self.assertTrue(duplicado(DADOS_EXEMPLO[1], [DADOS_EXEMPLO[0]]))

    def test_distantes_nao_duplicados(self):
        self.assertFalse(duplicado(DADOS_EXEMPLO[4], [DADOS_EXEMPLO[0]]))

    def test_prazo_maior_que_48_horas_nao_duplicado(self):
        antigo = deepcopy(DADOS_EXEMPLO[0]); antigo["criado_em"] = "2026-11-01T09:00:00-03:00"
        self.assertFalse(duplicado(DADOS_EXEMPLO[1], [antigo]))

    def test_prioridade_buraco_alta(self):
        self.assertEqual(calcular_prioridade(DADOS_EXEMPLO[0]), (85, "alta"))

    def test_prioridade_obstaculo_media(self):
        self.assertEqual(calcular_prioridade(DADOS_EXEMPLO[4]), (55, "media"))

    def test_confianca_baixa_detectada(self):
        self.assertLess(classe_principal(DADOS_EXEMPLO[2])[1], 0.65)


if __name__ == "__main__":
    unittest.main()
