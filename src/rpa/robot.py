"""Robô de triagem. Por padrão só planeja alterações (dry-run)."""
from __future__ import annotations
import json
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .api import APIClient, APIError
from .rules import eh_duplicado, principal, prioridade, validar


def normalizar(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def decidir_responsavel(resposta: str) -> str | None:
    """Somente sugestões explícitas do assistente; indefinição exige revisão humana."""
    texto = normalizar(resposta)
    if "proprietario" in texto:
        return "proprietario"
    if "concessionaria" in texto:
        return "concessionaria"
    if "prefeitura" in texto:
        return "prefeitura"
    return None


def sintetizar_fontes(fontes: list) -> str:
    titulos = []
    for fonte in fontes:
        if isinstance(fonte, dict) and isinstance(fonte.get("titulo"), str):
            titulos.append(fonte["titulo"].strip())
    return "; ".join(titulos)[:200]


class RoboTriagem:
    def __init__(self, api: APIClient, log_dir: Path, *, aplicar=False, limiar=.65):
        self.api = api
        self.aplicar = aplicar
        self.limiar = limiar
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.id_execucao = uuid.uuid4().hex[:12]

    def _log(self, **campos):
        # Sem foto, GPS, descrição, texto da IA ou token. IDs técnicos são os únicos identificadores.
        evento = {"momento": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "execucao_id": self.id_execucao, "aplicar": self.aplicar, **campos}
        with (self.log_dir / "auditoria.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    def executar(self):
        totais = {"itens": 0, "encaminhados": 0, "revisoes": 0, "descartados": 0,
                  "falhas": 0, "sucessos": 0}
        try:
            novos = self.api.listar(status="recebido", limite=200)
            enviados = self.api.listar(status="encaminhado", limite=200)
            concluidos = self.api.listar(status="resolvido", limite=200)
        except APIError as exc:
            self._log(evento="falha_lote", erro=str(exc))
            raise
        # A API entrega do mais novo ao mais antigo; inverter para deduplicar cronologicamente.
        novos.sort(key=lambda r: (str(r.get("criado_em", "")), str(r.get("id", ""))))
        anteriores = enviados + concluidos
        if len(novos) == 200:
            self._log(evento="aviso_limite_get", limite=200,
                      nota="Mais relatos podem estar pendentes; executar novo lote")
        for r in novos:
            totais["itens"] += 1
            ident = r.get("id")
            etapa = "inicio"
            try:
                erros = validar(r)
                classe, confianca = principal(r)
                ponto = None
                responsavel = None
                fonte = ""
                if erros:
                    destino, motivo = "revisao_humana", ",".join(erros)
                elif eh_duplicado(r, anteriores):
                    destino, motivo = "descartado", "possivel_duplicidade"
                elif confianca < self.limiar:
                    destino, motivo = "revisao_humana", "baixa_confianca"
                else:
                    ponto = prioridade(r)
                    resposta = self.api.perguntar(classe)
                    if resposta["recusa"]:
                        destino, motivo = "revisao_humana", "assistente_recusou"
                    else:
                        responsavel = decidir_responsavel(resposta["resposta"])
                        fonte = sintetizar_fontes(resposta["fontes"])
                        if not responsavel or not fonte:
                            destino, motivo = "revisao_humana", "responsabilidade_ou_fonte_indefinida"
                        else:
                            destino, motivo = "encaminhado", "triagem_automatica"
                if self.aplicar:
                    etapa = "patch"
                    if destino == "encaminhado":
                        # Transições permitidas: recebido -> em_triagem -> encaminhado.
                        self.api.alterar(ident, "em_triagem", prioridade=ponto)
                        etapa = "em_triagem_confirmada"
                        self.api.alterar(ident, "encaminhado", responsavel=responsavel, base_legal=fonte)
                    else:
                        self.api.alterar(ident, destino)
                totais["sucessos"] += 1
                if destino == "encaminhado":
                    totais["encaminhados"] += 1
                    anteriores.append(r)
                elif destino == "revisao_humana":
                    totais["revisoes"] += 1
                else:
                    totais["descartados"] += 1
                self._log(evento="relato_processado", relato_id=ident, resultado=destino,
                          motivo=motivo, prioridade=ponto)
            except (APIError, TypeError, KeyError, ValueError, OSError) as exc:
                totais["falhas"] += 1
                self._log(evento="erro_relato", relato_id=ident, etapa=etapa,
                          erro=str(exc) if isinstance(exc, APIError) else type(exc).__name__)
                # Se falhar após em_triagem, precisa de conciliação manual; não simular sucesso.
                continue
        self._log(evento="resumo_execucao", **totais)
        return {"execucao_id": self.id_execucao, "modo": "aplicar" if self.aplicar else "dry_run", **totais}
