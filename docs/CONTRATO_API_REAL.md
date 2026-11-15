# Ajustes da API real (main do repositório predowss/passo-firme consultada em 15/11/2026)

- GET /relatos?status=recebido&limite=200 -> **lista** de `RelatoOut`, com `deteccoes` (cada detecção `classe, confianca, caixa`). Não tem `foto_url` no DTO público.
- Classes: `buraco`, `degrau_desnivel`, `obstaculo`, `veiculo_na_calcada`, `piso_tatil`.
- POST /assistente recebe somente `{"pergunta":"..."}`. Retorna `resposta`, `fontes` lista de objetos `{titulo, trecho}`, `recusa`, `modelo`.
- PATCH /relatos/{id}/status recebe `status`, `prioridade` **inteiro 1..5**, `responsavel` em `proprietario | prefeitura | concessionaria` e `base_legal` até 200 caracteres. Campos `motivo`, `encaminhamento` e `faixa_prioridade` **não fazem parte do schema**.
- Transições automáticas: `recebido -> em_triagem -> encaminhado`; inválidos `recebido -> revisao_humana`; duplicados `recebido -> descartado`.
- A API mantém `encaminhamento` com protocolo simulado dentro do banco, mas o `RelatoOut` não inclui esses dados.
- `GET /relatos` atualmente tem limite máximo de 200 e não possui paginação por `offset` ou cursor. Um único lote pode não cobrir o histórico completo; solicite paginação ao time de Produto.
- `log_rpa` está definido no banco mas não existe endpoint para gravar logs; esta versão registra o arquivo JSONL localmente.
- Não há proteção de autenticação explícita no endpoint PATCH em `api/app/main.py`. O modo remoto de escrita requer autorização da equipe e deveria esperar autenticação da API.
- A foto não é exposta no GET por desenho de privacidade; sem `deteccoes`, o RPA envia para revisão humana. Não use ausência de `foto_url` para acusar erro.
- O detector e o assistente no GitHub permanecem simulados em `api/app/servicos.py`; a integração com os modelos finais depende dos respectivos responsáveis.
- A atualização de dois PATCH não é transação atômica; em caso de falha depois de `em_triagem`, a ocorrência precisa de conciliação com o grupo. Não a marque como encaminhada automaticamente.
- A heurística de duplicatas e a prioridade de 1..5 são **propostas acadêmicas**, não regras oficiais. Foto, GPS e tipo de obstáculo podem não bastar para descartar um relato com segurança; validar manualmente falsos positivos antes de produção.

## Fontes verificadas
- https://github.com/predowss/passo-firme/blob/main/api/app/main.py
- https://github.com/predowss/passo-firme/blob/main/api/app/servicos.py
- https://github.com/predowss/passo-firme/blob/main/api/app/db.py
- https://github.com/predowss/passo-firme/blob/main/api/tests/test_api.py
