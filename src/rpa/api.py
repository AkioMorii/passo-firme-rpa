"""Cliente HTTP simples, com retentativas limitadas e timeout."""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class APIError(Exception):
    """Falha de comunicação ou contrato com a API do MVP."""


class APIClient:
    def __init__(self, base_url: str, token: str = "", timeout: float = 5.0,
                 tentativas: int = 3, espera: float = 0.25):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.tentativas = max(1, tentativas)
        self.espera = max(0.0, espera)

    def _requisicao(self, metodo: str, caminho: str, payload: dict | None = None):
        corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        ultima_falha = ""
        for tentativa in range(1, self.tentativas + 1):
            req = Request(self.base_url + caminho, data=corpo, method=metodo, headers=headers)
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except HTTPError as erro:
                ultima_falha = f"HTTP_{erro.code}"
                if erro.code not in {429, 500, 502, 503, 504}:
                    raise APIError(ultima_falha) from None
            except (URLError, TimeoutError, OSError):
                ultima_falha = "conexao_indisponivel"
            except (ValueError, UnicodeDecodeError):
                raise APIError("resposta_json_invalida") from None
            if tentativa < self.tentativas:
                time.sleep(self.espera * (2 ** (tentativa - 1)))
        raise APIError(f"falha_apos_{self.tentativas}_tentativas:{ultima_falha}")

    def listar_relatos(self) -> list[dict]:
        # Consulta TODOS para detectar duplicatas contra relatos já encaminhados.
        resultado = self._requisicao("GET", "/relatos")
        dados = resultado if isinstance(resultado, list) else resultado.get("relatos") if isinstance(resultado, dict) else None
        if not isinstance(dados, list) or not all(isinstance(x, dict) for x in dados):
            raise APIError("contrato_relato_invalido")
        return dados

    def pedir_orientacao(self, classe: str, distrito: str) -> dict:
        # Não envia foto, GPS ou dados pessoais ao assistente.
        pergunta = f"Qual o encaminhamento administrativo recomendado para barreira do tipo {classe}?"
        payload = {"pergunta": pergunta, "contexto": {"tipo_barreira": classe, "distrito": distrito}}
        resposta = self._requisicao("POST", "/assistente", payload)
        if not isinstance(resposta, dict) or not isinstance(resposta.get("recusa"), bool):
            raise APIError("contrato_assistente_invalido")
        if not resposta["recusa"] and (not isinstance(resposta.get("resposta"), str) or not isinstance(resposta.get("fontes"), list)):
            raise APIError("contrato_assistente_invalido")
        return resposta

    def atualizar_relato(self, id_relato: int | str, dados: dict) -> dict:
        if not str(id_relato).isdigit():
            raise APIError("id_relato_invalido")
        resposta = self._requisicao("PATCH", f"/relatos/{id_relato}/status", dados)
        if not isinstance(resposta, dict):
            raise APIError("contrato_atualizacao_invalido")
        return resposta
