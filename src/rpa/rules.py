"""Regras determinísticas de triagem, auditáveis e independentes da API."""
from __future__ import annotations

from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlparse

SEVERIDADE = {
    "buraco": 85,
    "degrau": 75,
    "desnivel": 75,
    "desnível": 75,
    "piso_tatil": 65,
    "piso tátil": 65,
    "obstaculo": 55,
    "obstáculo": 55,
    "veiculo": 50,
    "veículo": 50,
}


def classe_principal(relato: dict) -> tuple[str | None, float | None]:
    """Seleciona a detecção mais confiante, ou os campos simplificados do contrato."""
    deteccoes = relato.get("deteccoes")
    if isinstance(deteccoes, list) and deteccoes:
        candidatas = []
        for det in deteccoes:
            if not isinstance(det, dict):
                continue
            try:
                candidatos_conf = float(det.get("confianca"))
            except (TypeError, ValueError):
                continue
            if 0 <= candidatos_conf <= 1:
                candidatas.append((str(det.get("classe", "")).strip().lower(), candidatos_conf))
        if candidatas:
            return max(candidatas, key=lambda v: v[1])
    classe = relato.get("classe")
    try:
        confianca = float(relato.get("confianca"))
    except (TypeError, ValueError):
        return (str(classe).strip().lower() if classe is not None else None), None
    return (str(classe).strip().lower() if classe is not None else None), confianca


def validar(relato: dict) -> list[str]:
    """Retorna códigos, sem copiar dados pessoais aos registros de auditoria."""
    problemas = []
    foto = relato.get("foto_url")
    parsed = urlparse(str(foto or ""))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        problemas.append("foto_ausente_ou_url_invalida")
    try:
        lat, lon = float(relato["lat"]), float(relato["lon"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            problemas.append("gps_fora_de_faixa")
    except (KeyError, TypeError, ValueError):
        problemas.append("gps_ausente_ou_invalido")
    classe, confianca = classe_principal(relato)
    if classe not in SEVERIDADE:
        problemas.append("classe_ausente_ou_desconhecida")
    if confianca is None or not 0 <= confianca <= 1:
        problemas.append("confianca_invalida")
    return problemas


def parse_horario(valor: str | None) -> datetime | None:
    if not valor or not isinstance(valor, str):
        return None
    try:
        hora = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if hora.tzinfo is None:
            hora = hora.replace(tzinfo=timezone.utc)
        return hora.astimezone(timezone.utc)
    except ValueError:
        return None


def distancia_m(a: dict, b: dict) -> float:
    """Distância geodésica aproximada em metros, via Haversine."""
    lat1, lon1 = radians(float(a["lat"])), radians(float(a["lon"]))
    lat2, lon2 = radians(float(b["lat"])), radians(float(b["lon"]))
    dif_lat, dif_lon = lat2 - lat1, lon2 - lon1
    hav = sin(dif_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dif_lon / 2) ** 2
    return 2 * 6_371_000 * asin(min(1, sqrt(hav)))


def duplicado(relato: dict, anteriores: list[dict], raio_m: float = 25, janela_horas: float = 48) -> bool:
    classe, _ = classe_principal(relato)
    horario = parse_horario(relato.get("criado_em"))
    if horario is None or validar(relato):
        return False
    for outro in anteriores:
        if str(outro.get("id")) == str(relato.get("id")):
            continue
        if validar(outro) or classe_principal(outro)[0] != classe:
            continue
        horario_outro = parse_horario(outro.get("criado_em"))
        if horario_outro is None or abs((horario - horario_outro).total_seconds()) > janela_horas * 3600:
            continue
        if distancia_m(relato, outro) <= raio_m:
            return True
    return False


def calcular_prioridade(relato: dict) -> tuple[int, str]:
    """Pontuação de risco demonstrativa. Não é critério oficial da prefeitura."""
    classe, _ = classe_principal(relato)
    base = SEVERIDADE[classe]
    deteccoes = relato.get("deteccoes", [])
    bonus = 5 if isinstance(deteccoes, list) and len(deteccoes) > 1 else 0
    pontuacao = min(100, base + bonus)
    faixa = "alta" if pontuacao >= 70 else "media" if pontuacao >= 50 else "baixa"
    return pontuacao, faixa
