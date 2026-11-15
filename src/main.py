"""CLI seguro: dry-run padrão; escrita só em localhost ou com liberação explícita."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from rpa.api import APIClient, APIError
from rpa.robot import RoboTriagem


def main():
    parser = argparse.ArgumentParser(description="Passo Firme | RPA integrado à API v0")
    parser.add_argument("--base-url", default=os.getenv("PASSO_FIRME_API_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--aplicar", action="store_true", help="permite PATCH, desativado por padrão")
    parser.add_argument("--permitir-remoto", action="store_true", help="confirma escrita em URL não local; apenas ambientes autorizados")
    parser.add_argument("--logs", type=Path, default=Path("logs"))
    parser.add_argument("--limiar", type=float, default=0.65)
    args = parser.parse_args()
    if not 0 <= args.limiar <= 1:
        parser.error("--limiar deve estar entre 0 e 1")
    url = urlparse(args.base_url)
    local = url.hostname in {"127.0.0.1", "localhost", "::1"}
    if args.aplicar and not local and not args.permitir_remoto:
        parser.error("Escrita em servidor remoto bloqueada. Use apenas um ambiente de testes autorizado com --permitir-remoto.")
    api = APIClient(args.base_url, token=os.getenv("PASSO_FIRME_API_TOKEN", ""))
    robo = RoboTriagem(api, args.logs, aplicar=args.aplicar, limiar=args.limiar)
    try:
        resultado = robo.executar()
    except APIError as exc:
        print(json.dumps({"erro": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 2 if resultado["falhas"] else 0


if __name__ == "__main__":
    sys.exit(main())
