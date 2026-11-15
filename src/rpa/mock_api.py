"""Simula o contrato público EXATO da API FastAPI v0, sem PostgreSQL ou nuvem."""
from __future__ import annotations
import json
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

DADOS = [
    {"id":101,"criado_em":"2026-11-10T09:00:00-03:00","lat":-23.5505,"lon":-46.6333,"distrito":"Exemplo","descricao":"Dados fictícios", "status":"recebido","prioridade":None,"deteccoes":[{"classe":"buraco","confianca":.95,"caixa":[.1,.1,.2,.2]}]},
    {"id":102,"criado_em":"2026-11-10T09:10:00-03:00","lat":-23.5505,"lon":-46.6333,"distrito":"Exemplo","descricao":"Dados fictícios", "status":"recebido","prioridade":None,"deteccoes":[{"classe":"buraco","confianca":.91,"caixa":[.1,.1,.2,.2]}]},
    {"id":103,"criado_em":"2026-11-10T09:20:00-03:00","lat":-23.5520,"lon":-46.6333,"distrito":"Exemplo","descricao":"Dados fictícios", "status":"recebido","prioridade":None,"deteccoes":[{"classe":"degrau_desnivel","confianca":.44,"caixa":[.1,.1,.2,.2]}]},
    {"id":104,"criado_em":"2026-11-10T09:30:00-03:00","lat":-23.5530,"lon":-46.6323,"distrito":"Exemplo","descricao":"Dados fictícios", "status":"recebido","prioridade":None,"deteccoes":[]},
    {"id":105,"criado_em":"2026-11-10T09:40:00-03:00","lat":-23.5550,"lon":-46.6350,"distrito":"Exemplo","descricao":"Dados fictícios", "status":"recebido","prioridade":None,"deteccoes":[{"classe":"obstaculo","confianca":.88,"caixa":[.1,.1,.2,.2]}]},
]
TRANSICOES = {
    "recebido": {"em_triagem", "revisao_humana", "descartado"},
    "em_triagem": {"encaminhado", "revisao_humana", "descartado"},
    "revisao_humana": {"em_triagem", "encaminhado", "descartado"},
    "encaminhado": {"resolvido"}, "resolvido": set(), "descartado": set(),
}

class Estado:
    def __init__(self, dados=None):
        self.relatos = deepcopy(DADOS if dados is None else dados)
        self.encaminhamentos = []
        self.assistente_foradoar = False
        self.get_falhas = 0
        self.patch_falha_status = None
        self.get_calls = 0
        self.patch_calls = 0


def criar_servidor(host="127.0.0.1", port=0, estado=None):
    estado = estado or Estado()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def responder(self, status, obj):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def corpo(self):
            try:
                n = int(self.headers.get("Content-Length", 0))
                if n > 10_000:
                    return None
                return json.loads(self.rfile.read(n).decode("utf-8"))
            except (TypeError, ValueError, UnicodeDecodeError):
                return None

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path == "/health":
                return self.responder(200, {"status":"ok","banco":"ok","versao":"simulado"})
            if parsed.path != "/relatos":
                return self.responder(404, {"detail":"Not Found"})
            estado.get_calls += 1
            if estado.get_falhas:
                estado.get_falhas -= 1
                return self.responder(503, {"detail":"indisponivel"})
            q = parse_qs(parsed.query)
            filtro = q.get("status", [None])[0]
            try:
                limite = int(q.get("limite", ["50"])[0])
            except ValueError:
                return self.responder(422, {"detail":"limite invalido"})
            if not 1 <= limite <= 200 or (filtro and filtro not in TRANSICOES):
                return self.responder(422, {"detail":"parametro invalido"})
            items = [r for r in estado.relatos if not filtro or r["status"] == filtro]
            items.sort(key=lambda r:r["criado_em"], reverse=True)
            return self.responder(200, items[:limite])

        def do_POST(self):
            if urlsplit(self.path).path != "/assistente":
                return self.responder(404, {"detail":"Not Found"})
            body = self.corpo()
            if not isinstance(body, dict) or not isinstance(body.get("pergunta"), str):
                return self.responder(422, {"detail":"pergunta invalida"})
            if estado.assistente_foradoar:
                return self.responder(503, {"detail":"indisponivel"})
            if "calçada" in body["pergunta"].lower():
                return self.responder(200, {"resposta":"Em São Paulo, a manutenção da calçada cabe ao proprietário do imóvel.",
                    "fontes":[{"titulo":"Lei Municipal 15.442/2011", "trecho":"Responsabilidade pela calçada"}],
                    "recusa":False,"modelo":"simulado-v0"})
            return self.responder(200, {"resposta":"Não encontrei resposta.","fontes":[],"recusa":True,"modelo":"simulado-v0"})

        def do_PATCH(self):
            partes = urlsplit(self.path).path.strip("/").split("/")
            if len(partes)!=3 or partes[0]!="relatos" or partes[2]!="status" or not partes[1].isdigit():
                return self.responder(404, {"detail":"Not Found"})
            body = self.corpo()
            if not isinstance(body,dict):
                return self.responder(422, {"detail":"JSON invalido"})
            status = body.get("status")
            p = body.get("prioridade")
            if (status not in TRANSICOES or (p is not None and (not isinstance(p, int) or not 1 <= p <= 5))
                    or any(k not in {"status","prioridade","responsavel","base_legal"} for k in body)):
                return self.responder(422,{"detail":"payload invalido"})
            ident = int(partes[1]); relato = next((r for r in estado.relatos if r["id"] == ident), None)
            if relato is None:
                return self.responder(404,{"detail":"Relato não encontrado"})
            if status != relato["status"] and status not in TRANSICOES[relato["status"]]:
                return self.responder(409,{"detail":"Transição não permitida"})
            estado.patch_calls += 1
            if estado.patch_falha_status == status:
                return self.responder(503,{"detail":"indisponivel"})
            if p is not None:
                relato["prioridade"] = p
            if status == "encaminhado" and body.get("responsavel"):
                estado.encaminhamentos.append({"relato_id":ident,"responsavel":body["responsavel"],
                                              "base_legal":body.get("base_legal"), "protocolo_simulado":f"SIM-{ident}"})
            relato["status"] = status
            return self.responder(200, relato)
    return ThreadingHTTPServer((host, port), Handler), estado
