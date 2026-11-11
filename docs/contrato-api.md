# Contrato da integração com o MVP (versão de trabalho)

O plano original do grupo define as rotas, mas **não define o corpo exato dos JSONs**. Os formatos abaixo são uma proposta operacional que **precisa ser validada com quem desenvolve a API** antes de conectar ao ambiente real.

## GET /relatos

Retornar todos os relatos, inclusive encaminhados/resolvidos, para verificar duplicatas históricas. Resposta aceita pelo cliente: array puro ou `{"relatos": [...]}`.

```json
{"relatos":[{"id":101,"criado_em":"2026-11-10T09:00:00-03:00","foto_url":"https://example.org/101.jpg","lat":-23.5505,"lon":-46.6333,"distrito":"Distrito Exemplo","status":"recebido","deteccoes":[{"classe":"buraco","confianca":0.95}]}]}
```

Se a API real retornar detecções em tabela separada, sugerimos incluí-las no GET para evitar uma rota não prevista no planejamento.

## POST /assistente

Requisição sem GPS, foto ou identificação do cidadão:

```json
{"pergunta":"Qual o encaminhamento administrativo recomendado para barreira do tipo buraco?","contexto":{"tipo_barreira":"buraco","distrito":"Distrito Exemplo"}}
```

Resposta esperada:

```json
{"resposta":"Orientação a ser validada com fontes oficiais.","fontes":["Referência confirmada pelo serviço de IA"],"recusa":false}
```

O serviço IA **é responsável por responder com fontes verdadeiras**. A API de exemplo em `src/rpa/mock_api.py` retorna texto marcadamente fictício.

## PATCH /relatos/{id}/status

```json
{"status":"encaminhado","prioridade":85,"faixa_prioridade":"alta","motivo":"triagem_automatica","encaminhamento":{"canal":"simulado","protocolo_simulado":"DEMO-101","base_legal":["Fonte da IA"],"orientacao":"Texto gerado pelo assistente"}}
```

Para revisão: `{"status":"revisao_humana","prioridade":null,"motivo":"baixa_confianca"}`.
Para duplicado: `{"status":"descartado","prioridade":null,"motivo":"possivel_duplicidade_espacial_temporal"}`.

O PATCH deve ser **atômico** e rejeitar operações repetidas com `409 Conflict` quando o relato já tiver saído de `recebido`. Uma futura melhoria é oferecer `Idempotency-Key` para tolerar falhas de rede após gravação.

## Limitações e pontos pendentes

- `revisao_humana` e `descartado` são representações técnicas dos desvios descritos no plano. Os valores exatos do banco precisam ser acordados.
- Campos `motivo`, `encaminhamento`, `faixa_prioridade` e resposta do assistente não foram fechados no contrato v0.
- A imagem é validada pela **presença de URL bem formada**, não por download, existência do arquivo ou qualidade da imagem. A validação da foto real pertence à API e ao detector YOLO.
- O cálculo de prioridade é um **critério do protótipo**, não da Prefeitura de São Paulo.
- A integração operacional com a API pública só pode ser considerada comprovada após executar os mesmos testes contra a URL real do grupo.
