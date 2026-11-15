"""Cliente HTTP para FastAPI do Passo Firme, contrato de 15/11/2026 (GitHub main)."""
from __future__ import annotations
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class APIError(Exception):
    pass


class APIClient:
    def __init__(self, base_url: str, token: str = "", timeout=5.0, tentativas=3, espera=0.15):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.tentativas = max(1, tentativas)
        self.espera = max(0.0, espera)

    def _request(self, metodo: str, rota: str, body: dict | None = None):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        ultima = ""
        for n in range(self.tentativas):
            req = Request(self.base_url + rota, data=data, headers=headers, method=metodo)
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except HTTPError as exc:
                ultima = f"HTTP_{exc.code}"
                if exc.code not in {429, 500, 502, 503, 504}:
                    raise APIError(ultima) from None
            except (URLError, TimeoutError, OSError):
                ultima = "conexao_indisponivel"
            except (ValueError, UnicodeDecodeError):
                raise APIError("json_invalido") from None
            if n+1 < self.tentativas:
                time.sleep(self.espera * 2**n)
        raise APIError(f"{ultima}_apos_{self.tentativas}_tentativas")

    def listar(self, status: str | None = None, limite=200) -> list[dict]:
        params = {"limite": min(200, max(1, int(limite)))}
        if status:
            params["status"] = status
        resposta = self._request("GET", "/relatos?" + urlencode(params))
        if not isinstance(resposta, list) or not all(isinstance(r, dict) for r in resposta):
            raise APIError("formato_get_relatos_invalido")
        return resposta

    def perguntar(self, classe: str) -> dict:
        # A palavra 'calçada' ativa a base jurídica no assistente simulado da API.
        resposta = self._request("POST", "/assistente", {
            "pergunta": f"Quem é responsável por consertar a calçada quando há {classe.replace('_', ' ')}?"
        })
        if (not isinstance(resposta, dict) or not isinstance(resposta.get("recusa"), bool)
                or not isinstance(resposta.get("resposta"), str)
                or not isinstance(resposta.get("fontes"), list)):
            raise APIError("formato_assistente_invalido")
        return resposta

    def alterar(self, relato_id: int | str, status: str, prioridade: int | None = None,
                responsavel: str | None = None, base_legal: str | None = None) -> dict:
        if not str(relato_id).isdigit():
            raise APIError("id_invalido")
        dados = {"status": status}
        if prioridade is not None:
            dados["prioridade"] = prioridade
        if responsavel:
            dados["responsavel"] = responsavel
        if base_legal:
            dados["base_legal"] = base_legal[:200]
        resp = self._request("PATCH", f"/relatos/{relato_id}/status", dados)
        if not isinstance(resp, dict) or resp.get("status") != status:
            raise APIError("resposta_patch_invalida")
        return resp
