"""Regras da triagem compatíveis com o contrato v0 da API Passo Firme."""
from __future__ import annotations
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt

# Hipóteses de triagem para o protótipo, NÃO critérios oficiais.
PRIORIDADES = {
    "buraco": 5,
    "degrau_desnivel": 4,
    "piso_tatil": 4,
    "obstaculo": 3,
    "veiculo_na_calcada": 3,
}


def principal(relato: dict) -> tuple[str | None, float | None]:
    """Seleciona a detecção mais confiante, conforme RelatoOut.deteccoes."""
    itens = relato.get("deteccoes")
    if not isinstance(itens, list):
        return None, None
    candidatos = []
    for item in itens:
        if not isinstance(item, dict):
            continue
        try:
            conf = float(item["confianca"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= conf <= 1:
            candidatos.append((str(item.get("classe", "")).strip().lower(), conf))
    return max(candidatos, key=lambda par: par[1]) if candidatos else (None, None)


def validar(relato: dict) -> list[str]:
    """A API não retorna foto_url; validamos os campos disponíveis, inclusive detecção."""
    erros = []
    try:
        lat, lon = float(relato["lat"]), float(relato["lon"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            erros.append("gps_invalido")
    except (KeyError, TypeError, ValueError):
        erros.append("gps_invalido")
    classe, confianca = principal(relato)
    if classe is None:
        erros.append("sem_deteccao")
    elif classe not in PRIORIDADES:
        erros.append("classe_nao_reconhecida")
    if confianca is None:
        erros.append("confianca_invalida")
    return erros


def instante(valor: str | None) -> datetime | None:
    if not isinstance(valor, str):
        return None
    try:
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return data.astimezone(timezone.utc)
    except ValueError:
        return None


def distancia_m(a: dict, b: dict) -> float:
    lat1, lon1 = radians(float(a["lat"])), radians(float(a["lon"]))
    lat2, lon2 = radians(float(b["lat"])), radians(float(b["lon"]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    hav = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 2 * 6_371_000 * asin(min(1, sqrt(hav)))


def eh_duplicado(relato: dict, anteriores: list[dict], raio_m=25, janela_horas=48) -> bool:
    data = instante(relato.get("criado_em"))
    if data is None or validar(relato):
        return False
    classe, _ = principal(relato)
    for outro in anteriores:
        if str(relato.get("id")) == str(outro.get("id")):
            continue
        if validar(outro) or principal(outro)[0] != classe:
            continue
        anterior_data = instante(outro.get("criado_em"))
        if anterior_data is None:
            continue
        if abs((data - anterior_data).total_seconds()) > janela_horas*3600:
            continue
        if distancia_m(relato, outro) <= raio_m:
            return True
    return False


def prioridade(relato: dict) -> int:
    """Escala 1..5, conforme MudancaStatus da API real."""
    classe, _ = principal(relato)
    base = PRIORIDADES[classe]
    det = relato.get("deteccoes")
    bonus = 1 if isinstance(det, list) and len(det) > 1 else 0
    return min(5, base + bonus)
