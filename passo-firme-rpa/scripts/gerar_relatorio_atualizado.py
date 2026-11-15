"""Relatório técnico de RPA com evidências de contrato real (somente leitura) e simulação local."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether,Preformatted,HRFlowable
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/Relatorio_Tecnico_RPA_Atualizado.pdf'
real=json.loads((ROOT/'evidencias/diagnostico_azure_15-11-2026.json').read_text(encoding='utf-8'))
demo=json.loads((ROOT/'evidencias/demo_local_contrato_v0.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')
pdfmetrics.registerFont(TTFont('DejaVuMono','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
NAVY=colors.HexColor('#102B42'); BLUE=colors.HexColor('#1F628B'); TEAL=colors.HexColor('#087F6B');GRAY=colors.HexColor('#566675'); LIGHT=colors.HexColor('#EDF3F7'); GOLD=colors.HexColor('#F5E9C5'); LINE=colors.HexColor('#D5E0E7')
styles=getSampleStyleSheet()
for name,font,size,leading,color,space in [
 ('Kicker','DejaVuBold',9.2,13,TEAL,8),('TitlePF','DejaVuBold',23,29,NAVY,10),
 ('DeckPF','DejaVu',11,17,GRAY,12),('HeadPF','DejaVuBold',12,18,BLUE,6),
 ('BodyPF','DejaVu',9,14,NAVY,7),('SmallPF','DejaVu',7.9,11,GRAY,5),
 ('TablePF','DejaVu',8.1,12,NAVY,0),('BoldSmallPF','DejaVuBold',8.2,13,NAVY,4),
 ('MonoPF','DejaVuMono',7.1,10.9,NAVY,4)]:
 styles.add(ParagraphStyle(name=name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=space))
par=lambda s,sty='BodyPF':Paragraph(s,styles[sty])
S=[]
def h(n,t):S.append(par(f'{n:02d} &nbsp; {t}','HeadPF'))
def sp(n=.24):S.append(Spacer(1,n*cm))
def tbl(rows,colwidths):
 data=[[par(str(x),'TablePF') for x in row] for row in rows]
 t=Table(data,colWidths=colwidths,hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('LINEBELOW',(0,0),(-1,0),0.8,LINE),('LINEBELOW',(0,1),(-1,-1),0.35,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
 return t

def foot(c,d):
 c.saveState();w,h=A4;c.setStrokeColor(LINE);c.line(1.8*cm,1.35*cm,w-1.8*cm,1.35*cm)
 c.setFont('DejaVu',7);c.setFillColor(GRAY)
 c.drawString(1.8*cm,1.05*cm,'PASSO FIRME  ·  RPA  ·  GS 2026.2')
 c.drawRightString(w-1.8*cm,1.05*cm,f'{d.page}');c.restoreState()

# Cover
sp(.65);S.append(par('FIAP · GLOBAL SOLUTION 2026.2','Kicker'))
S.append(par('Passo Firme','TitlePF'))
S.append(par('Robotic Process Automation — triagem de barreiras em calçadas','DeckPF'))
S.append(HRFlowable(width='100%',thickness=1,color=LINE));sp(.28)
S.append(par('<b>Objetivo:</b> automatizar a validação e a priorização de relatos, identificar possíveis duplicados, consultar a orientação do assistente e encaminhar os registros por meio da API do MVP.'))
S.append(par('<b>Cidadãos beneficiados:</b> idosos, pessoas com deficiência e demais pedestres que dependem da segurança e acessibilidade das calçadas de São Paulo.'))
h(1,'Integrantes')
S.append(tbl([['Integrante','RM'],['David de Medeiros Pacheco Junior','551462'],['Kaique Maia Reis Silva','552112'],['Pedro Henrique Alves Guariente','550301'],['Orlando Akio Morii Cardoso*','98067*']], [11.2*cm,4.4*cm]))
S.append(par('*Quarto integrante identificado no README do repositório principal. Confirmar com a equipe antes de entregar a disciplina; o README do RPA tinha um nome/RM provisórios.','SmallPF'))
sp(.3)
h(2,'Estado comprovado em 15/11/2026')
S.append(tbl([['Frente','Resultado'],['API Azure / PostgreSQL','Health e banco OK (diagnóstico enviado pelo integrante)'],['Contrato GET /relatos e POST /assistente','Consultas validadas contra o endpoint público'],['Teste de automação','19 testes aprovados no ambiente de preparação'],['Fluxo de status ponta a ponta','5 relatos fictícios processados em API local simulada'],['PATCH no PostgreSQL real','Ainda NÃO comprovado; 0 escritas na Azure']], [6.2*cm,9.4*cm]))
sp(.22)
S.append(par('Atenção: este relatório diferencia observações da API pública e testes com dados fictícios. Não há protocolo oficial SP156 aberto pela automação.','SmallPF'))
S.append(PageBreak())

h(3,'Processo manual e automação proposta')
S.append(par('Antes, a triagem exigia conferir cada relato manualmente, comparar registros por posição e período, definir a urgência, consultar a orientação pertinente e atualizar o status. O RPA transforma esse processo em um lote auditável com regras determinísticas e desvio para revisão humana.'))
h(4,'Fluxograma BPMN')
S.append(par('O diagrama abaixo mostra entrada, validação, gateways, repetição, consulta ao assistente, escolha entre dry-run e atualização, além da auditoria. As saídas com erro são registradas e o lote continua.','SmallPF'))
img=Image(str(ROOT/'assets/fluxo-bpmn-atualizado.png'))
w0,h0=img.imageWidth,img.imageHeight  # Lazy load before sizing
img.drawHeight=20.3*cm;img.drawWidth=w0*img.drawHeight/h0
if img.drawWidth>14.8*cm:
    img.drawWidth=14.8*cm
    img.drawHeight=h0*img.drawWidth/w0
img.hAlign='CENTER';S.append(img)
S.append(par('Figura 1. Fluxo simplificado. O arquivo editável BPMN 2.0 está em docs/fluxo-bpmn-atualizado.bpmn.','SmallPF'))
S.append(PageBreak())

h(5,'Implementação em Python')
S.append(par('O robô usa a biblioteca padrão do Python, um cliente HTTP com timeout e retentativas, processamento de lotes, regras explícitas de negócio e auditoria JSONL. Executa em dry-run por padrão; alterações exigem o parâmetro --aplicar.'))
S.append(tbl([['Etapa','Regra / comportamento'],['Entrada','GET /relatos?status=recebido&amp;limite=200. Procura também relatos encaminhados/resolvidos para deduplicação.'],['Validação','Confere GPS, classe reconhecida, detecção e confiança. O GET real não expõe foto_url.'],['Duplicidade','Mesma classe, distância até 25 metros e intervalo de até 48 horas.'],['Decisão','Confiança inferior a 0,65 ou dados inconsistentes → revisão humana; duplicação → descartado.'],['Prioridade','Escala de 1 a 5: buraco 5; degrau/desnível 4; piso tátil 4; obstáculo 3; veículo na calçada 3; bônus de 1 para múltiplas detecções, limitado a 5.'],['Assistente','POST /assistente com pergunta e recebimento de resposta, fontes estruturadas e recusa.'],['Atualização','Se autorizada: recebido → em_triagem (com prioridade) → encaminhado (com responsável e base legal); revisão e descarte seguem as transições válidas.']], [4.1*cm,11.5*cm]))
sp(.18)
S.append(par('<b>Critérios de risco demonstrativos:</b> a pontuação é uma regra de negócio do protótipo, não uma escala de risco oficial nem decisão automática da Prefeitura.'))
h(6,'Lote, exceções e idempotência')
S.append(par('O robô percorre a lista de relatos e aplica regras de decisão. Falhas temporárias HTTP (429, 500, 502, 503 e 504, além de conectividade) geram novas tentativas com espera; erros por item são registrados sem interromper o restante do lote. A seleção por status recebido evita reprocessar relatos já concluídos. Uma falha entre os dois PATCHs pode deixar um item em_triagem: nesse caso, há necessidade de conciliação manual e registro de erro.'))
h(7,'Auditoria e LGPD')
S.append(par('Os eventos em logs/auditoria.jsonl guardam data/hora, ID técnico, ID da execução, status, motivo e contagens de sucesso/falha. O robô não copia nome do cidadão, descrição, foto, coordenadas ou token para os logs. O diagnóstico remoto também omite o conteúdo do relato; mostra apenas nomes de campos e resultados de contrato.'))
S.append(PageBreak())

h(8,'Evidência: integração com a API pública')
S.append(par('Em 15/11/2026, o integrante executou scripts/diagnostico_api.py apontando para o serviço publicado em Azure Container Apps. A resposta abaixo foi fornecida por ele, não é uma captura de tela.'))
url='https://ca-passofirme-api.lemonfield-b3da2f2c.brazilsouth.azurecontainerapps.io'
S.append(par(f'<b>Endpoint:</b> <link href="{url}" color="#1F628B">Azure Passo Firme</link>'))
S.append(tbl([['Campo observado','Resultado fornecido'],['saude / banco','ok / ok'],['get_relatos','lista_valida; ao menos um registro'],['Campos do relato','criado_em, descricao, deteccoes, distrito, id, lat, lon, prioridade, status'],['assistente','contrato_valido; recusa = false'],['fontes_estruturadas','true'],['escritas_realizadas','0']], [5.6*cm,10*cm]))
S.append(par('<b>Interpretação:</b> houve comunicação real com API e banco por meio de leitura, e a rota de assistência respondeu com o contrato esperado. Isso não comprova que o RPA tenha feito PATCH na base real, que YOLO ou LLM já sejam modelos definitivos, nem que o app tenha recebido o encaminhamento.'))
h(9,'Evidência: testes e demonstração local')
S.append(tbl([['Execução (dados sintéticos)','Resultado'],['Suite unittest - contrato v0','19 testes / OK no ambiente de revisão'],['Primeira rodada do robô','5 itens; 5 sucessos; 0 falhas'],['Encaminhados','2, com prioridade compatível (1 a 5)'],['Revisão humana','2'],['Descartados por duplicação','1'],['Segunda rodada','0 itens (sem reprocessamento)']], [8.8*cm,6.8*cm]))
S.append(par('Testes cobrem contrato de GET/POST/PATCH simulado, alteração de status válida, proteção por dry-run, retorno 503, interrupção do assistente, falha após em_triagem, validação GPS, raio temporal/espacial e logs sanitizados. O integrante confirmou separadamente que os 13 testes anteriores haviam passado no próprio computador.'))
S.append(par('<b>Arquivos associados:</b> evidencias/diagnostico_azure_15-11-2026.json; evidencias/testes_19_ambiente_de_revisao.txt; evidencias/demo_local_contrato_v0.json; evidencias/audit_demo_local.jsonl. Os prints da máquina do integrante devem ser acrescentados antes do envio.','SmallPF'))
S.append(PageBreak())

h(10,'Limites e riscos conhecidos')
S.append(tbl([['Ponto','Tratamento nesta versão'],['Writes na Azure','Não executados. É necessário autorização do grupo e controle de acesso. Não rodar --aplicar na URL pública.'],['Detecção e assistente','Conforme o código principal do grupo, api/app/servicos.py implementa respostas simuladas até a integração dos modelos finais.'],['Limite de relatos','A API oferece no máximo 200 registros por consulta; duplicação e cobertura do lote não são exaustivas acima do limite.'],['Falha entre PATCHs','Pode deixar relato em_triagem; a recuperação automática completa não está implementada.'],['Dados pessoais','Evitar registrar foto, GPS, descrições, identidades e tokens em logs ou capturas de tela.'],['Protocolo SP156','Nenhum chamado oficial é aberto; protocolos são exclusivamente simulados.']], [5.0*cm,10.6*cm]))
h(11,'Publicação e apresentação')
S.append(par('<b>Repositório principal do MVP:</b> <link href="https://github.com/predowss/passo-firme" color="#1F628B">github.com/predowss/passo-firme</link>'))
S.append(par('<b>API pública:</b> <link href="'+url+'/health" color="#1F628B">/health</link> &nbsp; · &nbsp; <link href="'+url+'/docs" color="#1F628B">/docs</link>'))
S.append(par('<b>Repositório RPA da disciplina:</b> [INSERIR LINK PUBLICADO]'))
S.append(par('<b>Vídeo demonstrativo de até 3 minutos:</b> [INSERIR LINK PÚBLICO OU NÃO LISTADO]'))
S.append(par('O vídeo deve apresentar o problema, o fluxograma, o diagnóstico em Azure, a execução local ponta a ponta, a decisão e o tratamento de falhas, deixando claro o que é simulado. O relatório e o vídeo precisam ser referenciados no GitHub e enviados na tarefa do Teams.'))
h(12,'Conclusão e status da entrega')
S.append(par('O RPA está implementado e testado em ambiente controlado: regras, lote, decisão, logs, falhas e atualização de status em API simulada contratualmente compatível. A conexão de leitura com a API Azure foi demonstrada pelo integrante. Para fechar a entrega, ainda restam os prints locais, o vídeo, os links definitivos e, idealmente, a homologação de escrita na API verdadeira em ambiente controlado.'))
sp(.22)
status=Table([[par('<b>ESTADO</b>','BoldSmallPF'),par('Relatório-base atualizado e verificável. Não afirmar integração completa de PATCH com produção enquanto o teste controlado não existir.','SmallPF')]], colWidths=[2.5*cm,13.1*cm])
status.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GOLD),('BOX',(0,0),(-1,-1),0.6,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11)]))
S.append(status)

pdf=SimpleDocTemplate(str(DEST),pagesize=A4,leftMargin=1.8*cm,rightMargin=1.8*cm,topMargin=1.72*cm,bottomMargin=1.8*cm,title='Passo Firme - RPA - Relatório técnico atualizado 15/11/2026',author='Equipe Passo Firme')
pdf.build(S,onFirstPage=foot,onLaterPages=foot)
print(DEST)
