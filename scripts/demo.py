"""Demo local que executa dois lotes, verifica as transições e salva evidência."""
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
    servidor, estado = criar_servidor()
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        api = APIClient(f"http://127.0.0.1:{servidor.server_port}", espera=.01)
        primeiro = RoboTriagem(api, ROOT/"logs", aplicar=True).executar()
        segundo = RoboTriagem(api, ROOT/"logs", aplicar=True).executar()
        resultado = {"api": "mock-v0-contratual", "aviso": "DADOS FICTÍCIOS: não comprova integração Azure",
                     "primeira_execucao":primeiro,"segunda_execucao":segundo,
                     "status_finais":[{"id":r["id"],"status":r["status"],"prioridade":r.get("prioridade")} for r in estado.relatos],
                     "encaminhamentos_simulados":estado.encaminhamentos}
        (ROOT/"assets").mkdir(exist_ok=True)
        (ROOT/"assets"/"evidencia-api-v0.json").write_text(json.dumps(resultado,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps(resultado,indent=2,ensure_ascii=False))
    finally:
        servidor.shutdown()
        thread.join(timeout=5)
        servidor.server_close()

if __name__ == "__main__":
    main()
