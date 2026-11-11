"""Inicie a API fictícia: python scripts/mock_api.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rpa.mock_api import criar_servidor

if __name__ == "__main__":
    servidor, _ = criar_servidor()
    print("API fictícia ativa em http://127.0.0.1:8765 - Ctrl+C para parar", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
