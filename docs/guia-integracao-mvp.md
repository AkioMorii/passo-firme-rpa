# Checklist de homologação com a API pública do grupo

O robô funciona no mock local, mas só estará integrado ao MVP quando os testes abaixo forem realizados contra a API real. **Não use dados de cidadãos reais durante a homologação sem autorização e medidas de proteção.**

## Solicitar à equipe de Produto/IA

1. URL HTTPS da API e mecanismo de autenticação; não compartilhar tokens em repositório.
2. Exemplo real (anônimo) do JSON de `GET /relatos`: incluir `id`, `status`, `criado_em`, `lat`, `lon`, `foto_url`, `distrito` e `deteccoes` (ou informar formato equivalente).
3. Exemplo do request e response de `POST /assistente`, com `resposta`, `fontes` e `recusa`.
4. Exemplo aceito de `PATCH /relatos/{id}/status`, incluindo `prioridade`, `motivo` e `encaminhamento`, sem envio à prefeitura real.
5. Confirmação de valores para estados `recebido`, `revisao_humana`, `descartado`, `encaminhado`.

## Executar o teste no Windows

No PowerShell, na pasta do projeto, configurar somente valores aprovados para testes:

```powershell
$env:PASSO_FIRME_API_URL = 'https://URL-REAL-DO-MVP'
$env:PASSO_FIRME_API_TOKEN = 'TOKEN-DE-TESTE'
python src/main.py
```

O código atualmente aceita `--base-url` e lê o token por variável de ambiente. Se o JSON não corresponder ao contrato proposto, alterar os métodos de `src/rpa/api.py` e atualizar `docs/contrato-api.md` e os testes. **Não alterar silenciosamente a API compartilhada nem enviar POSTs reais ao SP156**.

## Evidências mínimas

- Print da execução do robô contra o ambiente integrado (omitindo URLs internas e tokens, se necessário).
- Print do mesmo relato exibido no MVP com status e prioridade atualizados.
- Log `resumo_execucao` (sem dados pessoais).
- Cenário simulado de erro (assistente 503 ou input inválido) com tratamento demonstrado.
- Registrar no PDF o status efetivo da integração, os endpoints confirmados e o responsável pela homologação.
