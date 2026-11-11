"""Demonstração ponta a ponta local, gerando evidências reais em assets/ e logs/."""
from __future__ import annotations
import json
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rpa.api import APIClient
from rpa.mock_api import criar_servidor
from rpa.robot import RoboTriagem


def main():
    servidor, estado = criar_servidor(port=0)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        root_logs = ROOT / "logs"
        root_saida = ROOT / "outbox"
        (ROOT / "assets").mkdir(exist_ok=True)
        cliente = APIClient(f"http://127.0.0.1:{servidor.server_port}", tentativas=3, espera=0.01)
        robot = RoboTriagem(cliente, root_logs, root_saida)
        resumo = robot.executar()
        segunda_rodada = RoboTriagem(cliente, root_logs, root_saida).executar()
        status = [{"id": v["id"], "status": v["status"], "prioridade": v.get("prioridade")}
                  for v in estado.relatos]
        evidencia = {
            "nota": "Demonstração local com dados inteiramente fictícios. Não comprova integração no MVP público.",
            "primeira_execucao": resumo,
            "segunda_execucao_idempotente": segunda_rodada,
            "status_apos_execucao": status,
            "quantidade_chamadas_assistente": estado.quantidade_assistente,
        }
        (ROOT / "assets" / "evidencia_demonstracao.json").write_text(
            json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
    finally:
        servidor.shutdown()
        thread.join(timeout=3)
        servidor.server_close()


if __name__ == "__main__":
    main()
