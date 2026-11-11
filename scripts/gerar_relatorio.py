"""Relatório técnico PDF (modelo pronto para preencher os links e nomes do grupo)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "relatorio-tecnico-rpa.pdf"
DADOS = json.loads((ROOT / "assets" / "evidencia_demonstracao.json").read_text(encoding="utf-8"))

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVuBold", italic="DejaVu", boldItalic="DejaVuBold")

NAVY = colors.HexColor("#132B43")
BLUE = colors.HexColor("#135E9A")
TEAL = colors.HexColor("#008B77")
GRAY = colors.HexColor("#526477")
LIGHT = colors.HexColor("#EAF2F8")
LINE = colors.HexColor("#D9E2EA")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitlePF", fontName="DejaVuBold", fontSize=24, leading=32, textColor=NAVY, spaceAfter=13))
styles.add(ParagraphStyle(name="SubtitlePF", fontName="DejaVu", fontSize=12, leading=17, textColor=GRAY, spaceAfter=16))
styles.add(ParagraphStyle(name="H1PF", fontName="DejaVuBold", fontSize=12, leading=17, textColor=BLUE, spaceBefore=11, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyPF", fontName="DejaVu", fontSize=9, leading=14.0, spaceAfter=6))
styles.add(ParagraphStyle(name="SmallPF", fontName="DejaVu", fontSize=8, leading=12, spaceAfter=6))
styles.add(ParagraphStyle(name="SmallBoldPF", fontName="DejaVuBold", fontSize=8.2, leading=12, textColor=NAVY))
styles.add(ParagraphStyle(name="TablePF", fontName="DejaVu", fontSize=7.9, leading=11.5))
styles.add(ParagraphStyle(name="OverlinePF", fontName="DejaVuBold", fontSize=10, leading=16, textColor=TEAL, spaceAfter=7))
styles.add(ParagraphStyle(name="CalloutPF", fontName="DejaVu", fontSize=9, leading=15, textColor=NAVY))

story = []
p = lambda txt, style="BodyPF": Paragraph(txt, styles[style])

def H(num, title):
    story.append(p(f"{num:02d}  {title}", "H1PF"))


def footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.line(1.8*cm, 1.42*cm, width-1.8*cm, 1.42*cm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.8*cm, 1.09*cm, "Passo Firme  |  RPA  |  GS 2026.2")
    canvas.drawRightString(width - 1.8*cm, 1.09*cm, f"Página {doc.page}")
    canvas.restoreState()


def table(rows, widths, header=True):
    data = [[p(str(c), "TablePF") for c in row] for row in rows]
    result = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1 if header else 0)
    cmds = [("VALIGN", (0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),9),
            ("RIGHTPADDING",(0,0),(-1,-1),9), ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6), ("LINEBELOW",(0,0),(-1,-1),0.45,LINE)]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0),LIGHT), ("TEXTCOLOR",(0,0),(-1,0),NAVY)]
    result.setStyle(TableStyle(cmds))
    return result

story.append(Spacer(1, 1.2*cm))
story.append(p("RELATÓRIO TÉCNICO  /  ROBOTIC PROCESS AUTOMATION", "OverlinePF"))
story.append(p("Passo Firme", "TitlePF"))
story.append(p("Triagem automática de relatos de barreiras em calçadas", "SubtitlePF"))
story.append(Spacer(1, 0.4*cm))
status = Table([[p("ESCOPO IMPLEMENTADO", "SmallBoldPF"), p("Integração HTTP real com API fictícia local, processamento em lote, regras de decisão, auditoria e testes automatizados.", "CalloutPF")],
                [p("AINDA PENDENTE", "SmallBoldPF"), p("Conectar ao MVP público do grupo, preencher integrantes, publicar no GitHub e gravar o vídeo de até 3 minutos.", "CalloutPF")]],
               colWidths=[4.6*cm, 11.0*cm])
status.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT), ("BOX",(0,0),(-1,-1),0.8,LINE),
                            ("TOPPADDING",(0,0),(-1,-1),13),("BOTTOMPADDING",(0,0),(-1,-1),13),
                            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
                            ("VALIGN",(0,0),(-1,-1),"TOP")]))
story.append(status)
story.append(Spacer(1, 0.65*cm))
story.append(p("<b>Equipe:</b> [NOME COMPLETO / RM] — preencher todas as pessoas do grupo.", "BodyPF"))
story.append(p("<b>Disciplina:</b> Robotic Process Automation (RPA)<br/><b>Projeto CitizenTech:</b> Passo Firme<br/><b>Entrega da disciplina:</b> 19/11/2026 às 23h55, via Teams<br/><b>Data de elaboração:</b> novembro de 2026", "BodyPF"))
story.append(Spacer(1, 0.5*cm))
story.append(p("<b>Natureza da evidência:</b> protótipo executável e testes locais com dados totalmente sintéticos. Este documento não apresenta a API simulada como se fosse a aplicação em produção.", "SmallPF"))
story.append(PageBreak())

H(1, "Identificação da CitizenTech e problema")
story.append(p("O <b>Passo Firme</b> é uma proposta CitizenTech para facilitar o registro, a visualização e a priorização de barreiras em calçadas de São Paulo. O público beneficiado inclui idosos, pessoas com deficiência e pedestres que dependem de deslocamentos a pé. O projeto prevê aplicativo web acessível, API, detecção visual, assistente de orientação, RPA, processamento analítico e robô vistoriador."))
story.append(p("<b>Problema operacional:</b> no processo manual, um operador precisa ler relatos individualmente, verificar foto e localização, identificar duplicidades, estimar risco, consultar o encaminhamento cabível e atualizar o status. Essa rotina é repetitiva, sujeita a atrasos e inconsistências."))
H(2, "Objetivo da automação e benefício ao cidadão")
story.append(p("Automatizar a triagem de relatos recebidos, com critérios transparentes de validade, duplicação, confiança e prioridade, de forma que barreiras potencialmente graves sejam encaminhadas mais rapidamente à fila responsável. Casos incertos são enviados para revisão humana. O benefício esperado é reduzir retrabalho e padronizar a priorização, sem substituir a decisão final das autoridades."))
H(3, "Processo manual e processo automatizado")
story.append(table([
    ["Processo manual (AS-IS)", "Processo automatizado (TO-BE)"],
    ["Ler cada relato e conferir campos.", "GET /relatos busca o lote; validação automática de URL, GPS, classe e confiança."],
    ["Comparar relatos para encontrar duplicados.", "Heurística: mesma classe, até 25 m de distância e até 48 h."],
    ["Definir urgência e consultar orientação.", "Pontuação determinística e consulta ao POST /assistente."],
    ["Atualizar planilha/sistema manualmente.", "PATCH /relatos/{id}/status e JSON estruturado para canal simulado."],
    ["Anotar resultados e falhas sem padrão.", "Auditoria JSONL por item e por execução, inclusive falhas."],
], [7.8*cm, 7.8*cm]))
H(4, "Tecnologias utilizadas e justificativa")
story.append(p("<b>Python 3.10+</b> (biblioteca padrão) foi escolhido por simplicidade de implantação e integração via HTTP. O robô é independente do framework da API e pode conversar com o FastAPI/PostgreSQL previstos pelo grupo. <b>JSON</b> permite transferir informações estruturadas para a API e o painel. <b>unittest</b> testa regras e integrações, enquanto o <b>Graphviz</b> gera a representação visual do processo. O arquivo BPMN 2.0 é incluído separadamente."))
story.append(PageBreak())

story.append(p("05  Fluxo em BPMN — etapas, decisões, repetição e exceções", "H1PF"))
story.append(p("O fluxo representa os eventos de início e fim, as atividades automáticas, os gateways de decisão e o retorno para o próximo item do lote. A representação é simplificada; o arquivo <b>docs/fluxo-rpa.bpmn</b> contém os elementos editáveis do processo.", "SmallPF"))
img = Image(str(ROOT / "assets" / "fluxo-bpmn.png"))
img.drawWidth = 15.2*cm
img.drawHeight = img.imageHeight * img.drawWidth/img.imageWidth
if img.drawHeight > 21.8*cm:
    img.drawHeight = 21.8*cm
    img.drawWidth = img.imageWidth * img.drawHeight/img.imageHeight
img.hAlign = "CENTER"
story.append(img)
story.append(p("Fonte: diagrama elaborado para o protótipo do Passo Firme. O envio ao SP156 permanece simulado.", "SmallPF"))
story.append(PageBreak())

H(6, "Regras de negócio, decisões e processamento em lote")
story.append(table([
    ["Critério", "Decisão implementada"],
    ["Validade", "Foto com URL HTTP(S), latitude/longitude nos intervalos globais válidos, classe reconhecida e confiança entre 0 e 1."],
    ["Duplicidade", "Mesma classe, distância até 25 m e diferença temporal de até 48 h, comparada a casos aceitos anteriormente."],
    ["Confiança", "Se inferior a 0,65: revisão humana."],
    ["Prioridade", "Buraco 85; degrau ou desnível 75; piso tátil 65; obstáculo 55; veículo 50; +5 se houver múltiplas detecções."],
    ["Classificação", "Alta: 70 ou mais; média: 50 a 69; baixa: abaixo de 50."],
    ["IA", "Se o assistente recusar, revisão humana. Caso contrário, encaminhamento simulado com fontes retornadas."],
    ["Lote", "Itera por todos os relatos com status 'recebido'; uma segunda execução ignora os já concluídos."],
], [4.3*cm, 11.3*cm]))
story.append(p("<b>Observação metodológica:</b> limiares e pontuações foram definidos para demonstrar regras de decisão; não são regras oficiais da Prefeitura nem estimativas comprovadas de risco. A validação da presença física da imagem e a avaliação de sua qualidade pertencem ao MVP/detector."))
H(7, "Exceções e recuperação")
story.append(p("Falhas temporárias de conexão, HTTP 429 e erros de servidor são reexecutados até três vezes, com espera exponencial. Dados inválidos ou confiança baixa produzem revisão humana, sem interromper o restante do lote. Se o assistente ou o PATCH estiver indisponível após as tentativas, o erro é registrado e o relato fica pendente para uma próxima execução. Os resultados e os estados são consultáveis por API."))
H(8, "Logs e auditoria")
story.append(p("Cada linha de <b>logs/auditoria.jsonl</b> é um JSON com data/hora UTC, identificador da execução, identificador técnico do relato, resultado e motivo, ou código de falha. Ao final, há um resumo de itens, sucessos, falhas, revisões, descartes e encaminhamentos. Não são gravados GPS, URLs de fotos, nome do cidadão ou token de autenticação."))
story.append(PageBreak())

H(9, "Integração com o MVP")
story.append(p("O contrato do plano de grupo especifica <b>GET /relatos</b>, <b>POST /assistente</b> e <b>PATCH /relatos/{id}/status</b>. A integração local foi testada com chamadas HTTP a uma API fictícia. O PATCH grava os status e permite que outro componente os consulte. Para os casos encaminhados, arquivos JSON no diretório <b>outbox/</b> contêm ID, prioridade, distrito e indicação de canal simulado."))
story.append(p("<b>Pendente para a integração final:</b> validar os corpos JSON, credenciais, status, base legal e tratamento da orientação do assistente com os responsáveis pela API. Não foi realizada chamada real a SP156 nem comprovada a conexão à URL pública da equipe."))
H(10, "Testes e evidências de validação")
res = DADOS["primeira_execucao"]
rows = [
    ["Indicador", "Resultado observado na simulação local"],
    ["Itens processados", str(res["itens"])],
    ["Processamentos bem-sucedidos", str(res["sucessos"])],
    ["Encaminhados pelo canal simulado", str(res["encaminhados"])],
    ["Revisão humana", str(res["revisoes"])],
    ["Descartados como possível duplicado", str(res["descartados"])],
    ["Falhas na execução normal", str(res["falhas"])],
    ["Itens na segunda execução", str(DADOS["segunda_execucao_idempotente"]["itens"])],
]
story.append(table(rows, [9.8*cm, 5.8*cm]))
story.append(Spacer(1, 0.2*cm))
story.append(p("A suíte <b>unittest</b> contém <b>13 testes automatizados</b> cobrindo validações, distância, janela temporal, prioridade, confiança, lote integrado, idempotência, repetição após erro temporário de API, indisponibilidade do assistente, falha em PATCH e ausência de dados sensíveis nos logs. Todos passaram na execução local registrada em <b>assets/resultado-testes.txt</b>."))
story.append(p("<b>Cenários demonstrados:</b> (a) sucesso com dois encaminhamentos fictícios; (b) decisões com duas revisões e um descarte; (c) falhas simuladas, recuperadas ou registradas sem travar o lote. A API fictícia não substitui teste com o MVP público."))
H(11, "Segurança e LGPD")
story.append(p("O protótipo usa somente dados sintéticos, não coleta identificadores pessoais nos logs e limita o envio ao assistente ao tipo de barreira e distrito. A chave de API é lida de variável de ambiente e arquivos `.env` são ignorados pelo Git. Antes da produção, o time deve garantir HTTPS, autenticação, autorização, retenção e proteção dos dados no backend. O servidor HTTP de simulação não é apropriado para exposição pública."))
H(12, "Publicação, repositório, vídeo e conclusão")
story.append(p("<b>GitHub público:</b> [INSERIR LINK]  |  <b>Vídeo de até 3 minutos:</b> [INSERIR LINK]  |  <b>URL do MVP:</b> [INSERIR LINK]"))
story.append(p("<b>Conclusão:</b> a solução demonstra automação operacional com repetição, gateways de decisão, tratamento de falhas, integração HTTP local e auditoria reproduzível. O trabalho está tecnicamente pronto para a etapa de homologação com a API real, e o vídeo público deverá comprovar a execução no contexto do MVP."))

pdf = SimpleDocTemplate(str(DEST), pagesize=A4,
                        leftMargin=1.8*cm, rightMargin=1.8*cm,
                        topMargin=1.75*cm, bottomMargin=1.8*cm,
                        title="Passo Firme - Relatório técnico RPA",
                        author="Equipe Passo Firme - dados a preencher")
pdf.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Relatório criado: {DEST}")
