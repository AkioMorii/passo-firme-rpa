# Passo Firme — Robô de Triagem (RPA)

**Integrantes:**

David de Medeiros Pacheco Junior, RM551462;
Kaique Maia Reis Silva, RM552112;
Orlando Akio Morii Cardoso, RM98067;
Pedro Henrique Alves Guariente, RM550301;

## 1. Ficha Técnica do MVP

- **Produto:** Passo Firme.
- **Público:** idosos, pessoas com deficiência e demais pedestres em um distrito piloto de São Paulo.
- **Problema:** Buracos, degraus e obstáculos nas calçadas são riscos sem mapa e triagem centralizados.
- **Solução:** Cidadão registra foto e local; detector visual classifica; assistente orienta; RPA deduplica, prioriza e encaminha; painel exibe status.
- **Arquitetura prevista pelo grupo:** PWA, API FastAPI e PostgreSQL, YOLO, LLM local/RAG, Airflow/Databricks, RPA Python, robô vistoriador, Azure e CI/CD.
- **RPA entrega:** Automação de triagem via `GET /relatos`, `POST /assistente` e `PATCH /relatos/{id}/status`, evidência em `outbox/` e audit trail em `logs/`.
- **ODS:** Visamos atender as ODS, 11 (11.2, 11.7), 10 (10.2), 3 e 9 (9.1), por mobilidade segura, inclusão e priorização de infraestrutura.

## 2. Pré-requisitos

Python **3.10 ou superior**. **Para executar o RPA** não é necessário `pip install`. Scripts opcionais para regenerar o diagrama e o PDF exigem, respectivamente, Graphviz instalado e `reportlab`. Testado localmente com dados fictícios, sem banco e sem credenciais reais.

## 3. Como executar

Terminal 1, na raiz do projeto:

```bash
python scripts/mock_api.py
```

Terminal 2, na raiz do projeto:

```bash
python src/main.py --base-url http://127.0.0.1:8765
```

Alternativa **em um único comando**, sem iniciar o servidor manualmente:

```bash
python scripts/demo.py
```

A demonstração salva `assets/evidencia_demonstracao.json`, `logs/auditoria.jsonl` e os arquivos consumíveis em `outbox/`.

### Testes

```bash
python -m unittest discover -s tests -v
```

### Execuções periódicas (exemplo)

- Windows: agendar `python C:\\caminho\\passo-firme-rpa\\src\\main.py` no Agendador de Tarefas, definindo o diretório de trabalho na raiz e as variáveis de ambiente.
- Linux: cron `*/30 * * * * cd /caminho/passo-firme-rpa && /usr/bin/python3 src/main.py`.
- Não faça `git commit` de `.env` ou logs reais. Nunca use relatórios sintéticos em sistemas de atendimento público.

## 4. Estrutura

```text
src/main.py            entrada do robô
src/rpa/api.py         HTTP com retries, timeout e contratos
src/rpa/rules.py       regras determinísticas e deduplicação
src/rpa/robot.py       processamento em lote, logs, exportação
src/rpa/mock_api.py    API de desenvolvimento local
scripts/mock_api.py    inicialização do mock
scripts/demo.py        demonstração ponta a ponta + evidências
tests/                 testes unitários e de integração
assets/                fluxograma e evidências sem PII
docs/                  contratos, regras, BPMN e roteiro do vídeo
logs/                  auditoria JSONL (gerada localmente)
outbox/                dados JSON para consumo simulado pelo MVP
```

## 5. Fluxo operacional e critérios

Mapeamento manual e automatizado, fluxograma BPMN, regras de negócio, respostas a falhas e cuidados com LGPD estão em [`docs/regras-e-seguranca.md`](docs/regras-e-seguranca.md) e [`docs/fluxo-rpa.bpmn`](docs/fluxo-rpa.bpmn). O fluxograma legível está em `assets/fluxo-bpmn.png`.

- URL da foto e coordenadas inválidas -> revisão humana.
- Ocorrências da mesma classe a <=25 m e <=48 h -> duplicadas.
- Confiança do detector <0,65 -> revisão humana.
- Prioridades 50 a 85 definidas por tipo de obstáculo, com acréscimo de 5 para múltiplas detecções.
- Encaminhamentos **simulados**, nunca abertos no SP156.
- Falha de API -> retry exponencial e registro do erro; lote prossegue quando possível.

## 6. Evidências e limites de integração

A API de demonstração é **fictícia**, mas o cliente faz requisições HTTP reais na máquina local e testa o contrato proposto. A API pública do grupo **ainda não foi verificada neste projeto**. Para conectá-la, acordar os JSONs em [`docs/contrato-api.md`](docs/contrato-api.md), seguir o [`docs/guia-integracao-mvp.md`](docs/guia-integracao-mvp.md), definir `PASSO_FIRME_API_URL` e token, testar o GET e PATCH e registrar evidências reais.
