"""Orquestração de lote, decisão, integração e trilha de auditoria."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .api import APIClient, APIError
from .rules import calcular_prioridade, classe_principal, duplicado, validar


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RoboTriagem:
    def __init__(self, cliente: APIClient, pasta_logs: Path, pasta_saida: Path, limite_confianca: float = 0.65):
        self.cliente = cliente
        self.pasta_logs = Path(pasta_logs)
        self.pasta_saida = Path(pasta_saida)
        self.limite_confianca = limite_confianca
        self.pasta_logs.mkdir(parents=True, exist_ok=True)
        self.pasta_saida.mkdir(parents=True, exist_ok=True)
        self.execucao_id = uuid.uuid4().hex[:12]

    def _auditar(self, **campos):
        # Nunca incluir nome, texto livre do cidadão, foto, posição ou token.
        registro = {"momento": agora_iso(), "execucao_id": self.execucao_id, **campos}
        with (self.pasta_logs / "auditoria.jsonl").open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    def _registrar_saida(self, relato: dict, faixa: str, pontuacao: int, fontes: list):
        # Arquivo estruturado consumível por outro componente, sem dados pessoais.
        saida = {
            "relato_id": relato["id"], "status": "encaminhado",
            "prioridade": pontuacao, "faixa_prioridade": faixa,
            "distrito": str(relato.get("distrito", "nao_informado")),
            "fontes_assistente": fontes,
            "canal": "simulado", "integracao": "arquivo_estruturado",
            "protocolo_simulado": f"DEMO-{relato['id']}",
        }
        caminho = self.pasta_saida / f"relato_{relato['id']}.json"
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
        temporario.replace(caminho)

    def executar(self) -> dict:
        contagem = {"itens": 0, "sucessos": 0, "falhas": 0,
                    "encaminhados": 0, "revisoes": 0, "descartados": 0}
        try:
            todos = self.cliente.listar_relatos()
        except APIError as erro:
            self._auditar(evento="erro_lote", codigo=str(erro))
            raise
        # Os relatos novos são processados cronologicamente; idempotência por status.
        novos = [x for x in todos if str(x.get("status", "")).lower() == "recebido"]
        novos.sort(key=lambda x: (str(x.get("criado_em", "")), str(x.get("id", ""))))
        aceitos = [x for x in todos if x.get("status") in {"encaminhado", "resolvido"}]
        for relato in novos:
            contagem["itens"] += 1
            relato_id = relato.get("id")
            try:
                problemas = validar(relato)
                classe, confianca = classe_principal(relato)
                if problemas:
                    status, motivo = "revisao_humana", ",".join(problemas)
                    payload = {"status": status, "prioridade": None, "motivo": motivo}
                elif duplicado(relato, aceitos):
                    status, motivo = "descartado", "possivel_duplicidade_espacial_temporal"
                    payload = {"status": status, "prioridade": None, "motivo": motivo}
                elif confianca < self.limite_confianca:
                    status, motivo = "revisao_humana", "baixa_confianca"
                    payload = {"status": status, "prioridade": None, "motivo": motivo}
                else:
                    pontuacao, faixa = calcular_prioridade(relato)
                    resposta = self.cliente.pedir_orientacao(classe, str(relato.get("distrito", "nao_informado")))
                    if resposta["recusa"]:
                        status, motivo = "revisao_humana", "assistente_recusou"
                        payload = {"status": status, "prioridade": None, "motivo": motivo}
                    else:
                        status, motivo = "encaminhado", "triagem_automatica"
                        payload = {
                            "status": status, "prioridade": pontuacao,
                            "faixa_prioridade": faixa, "motivo": motivo,
                            "encaminhamento": {
                                "canal": "simulado", "protocolo_simulado": f"DEMO-{relato_id}",
                                "base_legal": resposta["fontes"],
                                "orientacao": resposta["resposta"],
                            },
                        }
                self.cliente.atualizar_relato(relato_id, payload)
                contagem["sucessos"] += 1
                if status == "encaminhado":
                    contagem["encaminhados"] += 1
                    aceitos.append(relato)
                    # Produção adicional opcional de arquivo para o painel / consumidor.
                    # Se falhar, o PATCH continua válido; o erro fica registrado para reparo.
                    try:
                        self._registrar_saida(relato, faixa, pontuacao, resposta["fontes"])
                    except OSError:
                        self._auditar(evento="erro_exportacao", relato_id=relato_id, codigo="falha_gravacao_arquivo")
                elif status == "revisao_humana":
                    contagem["revisoes"] += 1
                else:
                    contagem["descartados"] += 1
                self._auditar(evento="relato_processado", relato_id=relato_id,
                              resultado=status, motivo=motivo)
            except (APIError, KeyError, TypeError, ValueError, OSError) as erro:
                contagem["falhas"] += 1
                self._auditar(evento="erro_item", relato_id=relato_id,
                              codigo=str(erro) if isinstance(erro, APIError) else type(erro).__name__)
                # Não marca relato como concluído se a atualização falhar.
                continue
        self._auditar(evento="resumo_execucao", **contagem)
        return {"execucao_id": self.execucao_id, **contagem}
