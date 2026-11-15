"""Diagnóstico SEM ESCRITA do contrato do Passo Firme; não imprime relatos/PII."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rpa.api import APIClient, APIError


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico seguro de API para o RPA")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    api = APIClient(args.base_url, tentativas=2)
    try:
        saude = api._request("GET", "/health")
        relatos = api.listar(limite=1)
        assistente = api.perguntar("buraco")
        saida = {
            "base_url": args.base_url,
            "saude": saude.get("status") if isinstance(saude,dict) else "desconhecido",
            "banco": saude.get("banco") if isinstance(saude,dict) else "desconhecido",
            "get_relatos": "lista_valida",
            "amostra_encontrada": bool(relatos),
            "campos_do_primeiro_relato": sorted(relatos[0].keys()) if relatos else [],
            "assistente": "contrato_valido",
            "assistente_recusou": assistente["recusa"],
            "fontes_estruturadas": all(isinstance(f,dict) and "titulo" in f for f in assistente["fontes"]),
            "escritas_realizadas": 0,
        }
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return 0
    except APIError as exc:
        print(json.dumps({"erro": str(exc), "escritas_realizadas": 0}), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
