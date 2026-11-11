"""CLI: python src/main.py --base-url http://127.0.0.1:8765"""
import argparse
import json
import os
import sys
from pathlib import Path

from rpa.api import APIClient, APIError
from rpa.robot import RoboTriagem


def main() -> int:
    parser = argparse.ArgumentParser(description="Robô de triagem - Passo Firme")
    parser.add_argument("--base-url", default=os.getenv("PASSO_FIRME_API_URL", "http://127.0.0.1:8765"))
    parser.add_argument("--timeout", type=float, default=float(os.getenv("RPA_TIMEOUT", "3")))
    parser.add_argument("--tentativas", type=int, default=int(os.getenv("RPA_TENTATIVAS", "3")))
    parser.add_argument("--limiar", type=float, default=float(os.getenv("RPA_LIMIAR_CONFIANCA", "0.65")))
    parser.add_argument("--logs", type=Path, default=Path(os.getenv("RPA_LOG_DIR", "logs")))
    parser.add_argument("--saida", type=Path, default=Path(os.getenv("RPA_OUTPUT_DIR", "outbox")))
    args = parser.parse_args()
    if not 0 <= args.limiar <= 1:
        parser.error("--limiar deve estar entre 0 e 1")
    cliente = APIClient(base_url=args.base_url, token=os.getenv("PASSO_FIRME_API_TOKEN", ""),
                        timeout=args.timeout, tentativas=args.tentativas)
    robo = RoboTriagem(cliente, args.logs, args.saida, args.limiar)
    try:
        resultado = robo.executar()
    except APIError as erro:
        print(json.dumps({"erro": str(erro), "sucesso": False}), file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["falhas"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
