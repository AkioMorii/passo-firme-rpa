# Passo Firme — Robô de Triagem (RPA)

O Passo Firme é uma iniciativa para mapear e priorizar problemas nas calçadas de São Paulo. A ideia é facilitar o registro de barreiras como buracos, desníveis e obstáculos, especialmente para idosos e pessoas com deficiência. Nossa parte do projeto é um robô que automatiza a triagem desses relatos.

## Integrantes

- David de Medeiros Pacheco Junior — RM551462
- Kaique Maia Reis Silva — RM552112
- Pedro Henrique Alves Guariente — RM550301
- Orlando Akio Morii Cardoso — RM98067

## 1. Como o robô funciona

O robô busca relatos pendentes pela API do projeto, verifica a localização e as detecções, procura possíveis duplicatas e avalia a prioridade de atendimento. Quando necessário, consulta a rota do assistente para obter uma orientação e a respectiva fonte. Registros inválidos ou incertos vão para revisão humana.

A comunicação entre disciplinas acontece pela API FastAPI/PostgreSQL do projeto. Nesta versão, as rotas são `GET /relatos`, `POST /assistente` e `PATCH /relatos/{id}/status`.

A prioridade é de **1 a 5**, como exige o contrato da API. Um encaminhamento automático precisa seguir as transições `recebido → em_triagem → encaminhado`. Outros casos podem terminar em `revisao_humana` ou `descartado`.

As regras de distância (25 metros), tempo (48 horas) e confiança (0,65) são critérios demonstrativos deste MVP, não determinações oficiais da Prefeitura.

## 2. O que foi desenvolvido

- Processamento de vários relatos em um lote;
- Identificação de ocorrências possivelmente repetidas;
- Regras de negócio para priorizar e encaminhar;
- Tratamento de falhas e novas tentativas de conexão;
- Registro de auditoria com data, status e resultado, sem dados pessoais;
- Modo **dry-run** por padrão, que faz a triagem sem modificar os registros;
- API de demonstração local para testar os PATCHs com dados fictícios;
- 19 testes automatizados da versão atualizada, aprovados no Windows do integrante;
- Fluxograma BPMN, documentação e relatório técnico.

## 3. Como executar

Pré-requisito: Python 3.10 ou superior. Para executar o robô e os testes não é necessário instalar bibliotecas adicionais.

No terminal, dentro da pasta do projeto:

```powershell
python -m unittest discover -s tests -v
python scripts/demo.py
```

A demonstração usa um servidor local e dados fictícios. Na primeira execução, são processados cinco relatos (dois encaminhados, dois enviados para revisão humana e um descartado). A segunda execução não reprocessa os itens concluídos.

Para consultar a **API pública da Azure sem modificar registros**, execute:

```powershell
python scripts/diagnostico_api.py --base-url https://ca-passofirme-api.lemonfield-b3da2f2c.brazilsouth.azurecontainerapps.io
```

Para realizar apenas a triagem em modo seguro (dry-run) na Azure:

```powershell
python src/main.py --base-url https://ca-passofirme-api.lemonfield-b3da2f2c.brazilsouth.azurecontainerapps.io
```

**Não use `--aplicar` na API pública sem autorização do grupo e proteção de autenticação.** Para demonstrar escrita, utilize a API simulada local com `python scripts/demo.py`, ou a API verdadeira com Docker Compose e banco de testes isolado, com autorização da equipe.

## 4. Arquivos do projeto

- `src/`: código do robô, cliente HTTP e regras de negócio;
- `scripts/`: diagnóstico, demonstração, servidor simulado e geração do BPMN/relatório;
- `tests/`: testes automatizados;
- `docs/`: contrato da API, fluxograma BPMN, relatório e roteiro do vídeo;
- `evidencias/`: saídas da demonstração, testes e diagnóstico;
- `assets/`: diagrama em PNG e SVG;
- `logs/`: auditoria local (não publicar logs reais contendo informações de cidadãos).

## 5. Evidências de integração

Em 15/11/2026, o diagnóstico executado no computador de um integrante confirmou que a API Azure estava saudável, o PostgreSQL respondia e os endpoints `GET /relatos` e `POST /assistente` estavam retornando o formato esperado. O teste foi **somente de leitura** e realizou zero escritas.

A execução em Azure (dry-run, sem escrita) processou 51 relatos e calculou 5 encaminhamentos e 46 descartes, com 0 falhas. O percentual elevado de descartes deve ser revisado antes de qualquer execução com escrita. A demonstração local comprova a automação de ponta a ponta usando dados sintéticos. Ainda não foi comprovada a atualização por PATCH no PostgreSQL da API verdadeira.

As capturas do integrante ficam em `evidencias/` (`evidencia-json-teste.png`, `evidencia-api.png` e `evidencia-teste.png`). Veja o relatório em `docs/Relatorio_Tecnico_RPA_Atualizado.pdf`, o diagrama em `docs/fluxo-bpmn-atualizado.bpmn` e as instruções de finalização em `docs/Guia-de-entrega.md`.

## 6. Links

- [API e DevOps do Passo Firme](https://github.com/predowss/passo-firme)
- [Documentação Swagger publicada](https://ca-passofirme-api.lemonfield-b3da2f2c.brazilsouth.azurecontainerapps.io/docs)
- [Repositório RPA (branch de integração)](https://github.com/AkioMorii/passo-firme-rpa/tree/integracao)
- Vídeo demonstrativo de até 3 minutos: **[INSERIR LINK]**

O projeto utiliza dados fictícios na demonstração e não abre solicitações reais no serviço SP156.
