"""API local de demonstração. Dados fictícios; não abre chamados reais."""
from __future__ import annotations

import json
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

DADOS_EXEMPLO = [
    {"id": 101, "criado_em": "2026-11-10T09:00:00-03:00", "foto_url": "https://example.org/fotos/ficticias/101.jpg",
     "lat": -23.550500, "lon": -46.633300, "distrito": "Distrito Exemplo", "status": "recebido",
     "deteccoes": [{"classe": "buraco", "confianca": 0.95}]},
    {"id": 102, "criado_em": "2026-11-10T09:10:00-03:00", "foto_url": "https://example.org/fotos/ficticias/102.jpg",
     "lat": -23.550508, "lon": -46.633305, "distrito": "Distrito Exemplo", "status": "recebido",
     "deteccoes": [{"classe": "buraco", "confianca": 0.91}]},
    {"id": 103, "criado_em": "2026-11-10T09:20:00-03:00", "foto_url": "https://example.org/fotos/ficticias/103.jpg",
     "lat": -23.552000, "lon": -46.633300, "distrito": "Distrito Exemplo", "status": "recebido",
     "deteccoes": [{"classe": "degrau", "confianca": 0.44}]},
    {"id": 104, "criado_em": "2026-11-10T09:30:00-03:00", "foto_url": "",
     "lat": -123.0, "lon": -46.63000, "distrito": "Distrito Exemplo", "status": "recebido",
     "deteccoes": [{"classe": "obstaculo", "confianca": 0.90}]},
    {"id": 105, "criado_em": "2026-11-10T09:40:00-03:00", "foto_url": "https://example.org/fotos/ficticias/105.jpg",
     "lat": -23.553500, "lon": -46.634200, "distrito": "Distrito Exemplo", "status": "recebido",
     "deteccoes": [{"classe": "obstaculo", "confianca": 0.88}]},
]


class EstadoAPI:
    def __init__(self, dados=None):
        self.relatos = deepcopy(DADOS_EXEMPLO if dados is None else dados)
        self.falhar_assistente = False
        self.falhar_patch_ids = set()
        self.falhar_get_vezes = 0
        self.quantidade_get = 0
        self.quantidade_assistente = 0


def criar_servidor(host="127.0.0.1", port=8765, estado=None):
    estado = estado or EstadoAPI()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            return

        def _responder(self, codigo, dados):
            corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def _ler_json(self):
            try:
                tamanho = int(self.headers.get("Content-Length", "0"))
                if tamanho > 1024 * 1024:
                    return None
                return json.loads(self.rfile.read(tamanho).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return None

        def do_GET(self):
            if urlsplit(self.path).path == "/relatos":
                estado.quantidade_get += 1
                if estado.falhar_get_vezes:
                    estado.falhar_get_vezes -= 1
                    return self._responder(503, {"erro": "temporariamente_indisponivel"})
                return self._responder(200, {"relatos": estado.relatos})
            return self._responder(404, {"erro": "rota_nao_encontrada"})

        def do_POST(self):
            if urlsplit(self.path).path != "/assistente":
                return self._responder(404, {"erro": "rota_nao_encontrada"})
            payload = self._ler_json()
            if not isinstance(payload, dict) or "pergunta" not in payload:
                return self._responder(400, {"erro": "requisicao_invalida"})
            estado.quantidade_assistente += 1
            if estado.falhar_assistente:
                return self._responder(503, {"erro": "assistente_indisponivel"})
            # Resposta sintética. Não afirma uma interpretação jurídica verdadeira.
            return self._responder(200, {
                "resposta": "Orientacao demonstrativa: encaminhar para triagem administrativa; confirmar a responsabilidade com fonte oficial.",
                "fontes": ["Base demonstrativa: verificar Lei Municipal 15.442/2011 e servico SP156"],
                "recusa": False,
            })

        def do_PATCH(self):
            caminho = urlsplit(self.path).path.strip("/").split("/")
            if len(caminho) != 3 or caminho[0] != "relatos" or caminho[2] != "status":
                return self._responder(404, {"erro": "rota_nao_encontrada"})
            try:
                id_relato = int(caminho[1])
            except ValueError:
                return self._responder(400, {"erro": "id_invalido"})
            if id_relato in estado.falhar_patch_ids:
                return self._responder(503, {"erro": "falha_simulada_patch"})
            payload = self._ler_json()
            if not isinstance(payload, dict) or payload.get("status") not in {"revisao_humana", "descartado", "encaminhado"}:
                return self._responder(400, {"erro": "status_invalido"})
            for relato in estado.relatos:
                if relato.get("id") == id_relato:
                    if relato["status"] != "recebido":
                        return self._responder(409, {"erro": "relato_ja_processado"})
                    relato.update(payload)
                    return self._responder(200, {"id": id_relato, "status": relato["status"]})
            return self._responder(404, {"erro": "relato_nao_encontrado"})

    server = ThreadingHTTPServer((host, port), Handler)
    return server, estado
