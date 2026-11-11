# Regras, exceções e cuidados

## Processo manual anterior

1. Equipe abre relatos individualmente; 2. verifica imagem e localização; 3. procura ocorrências repetidas; 4. classifica a urgência; 5. confere referência normativa; 6. registra encaminhamento; 7. atualiza o painel. Repetições e falhas não ficam auditadas uniformemente.

## Processo automatizado

1. Buscar relatos de todos os status via `GET /relatos` e selecionar apenas `recebido`.
2. Validar URL da foto, faixas de latitude/longitude, classe e confiança.
3. Identificar duplicado: mesma classe, distância de até **25 m** e diferença temporal de até **48 h** em relação a outro relato válido já encaminhado ou aceito neste lote.
4. Se a confiança do detector for inferior a **0,65**, direcionar à revisão humana.
5. Pontuar prioridade: buraco 85, degrau/desnível 75, piso tátil 65, obstáculo 55, veículo 50. Múltiplas detecções recebem +5 pontos, com teto em 100. Alta >=70, média >=50, baixa abaixo de 50.
6. Buscar orientação na API de IA; se ela recusar, enviar à revisão humana.
7. Atualizar o status via PATCH e exportar um arquivo JSON de encaminhamento simulado.
8. Registrar evento e resumo em `logs/auditoria.jsonl` e prosseguir até o fim do lote.

Estas pontuações são **hipóteses do protótipo**, não resultados científicos de risco nem critérios legais oficiais.

## Resiliência

- Erros transitórios (429, 500, 502, 503, 504 e indisponibilidade) têm até três tentativas com backoff exponencial.
- Arquivo/URL de foto ou GPS inválido -> revisão humana, não quebra o lote.
- Duplicado -> `descartado` com justificativa; a pessoa pode revisar o critério.
- IA indisponível ou PATCH falhando -> erro registrado e relato permanece `recebido`, permitindo nova tentativa.
- Duas execuções seguidas não geram reencaminhamentos adicionais de casos concluídos, pois o filtro considera apenas `recebido`.
- Se a exportação local falhar após o PATCH, o erro é registrado: a entrega principal continua válida, mas o operador precisa reparar a exportação; não é garantida transação distribuída.

## LGPD, segurança e limites

- Dados **sintéticos** em demonstração; sem abrir chamado verdadeiro no SP156.
- Token da API apenas via variável de ambiente, nunca commitado.
- Logs registram apenas ID técnico, status, contagens e códigos de erro; sem GPS, fotos, nome ou texto livre.
- O assistente recebe somente categoria e distrito, não fotos ou coordenadas exatas.
- Em ambiente real, a API deve autenticar, autorizar, criptografar transporte (HTTPS), limitar requisições e aplicar política de retenção. O protótipo HTTP local não oferece essas proteções.
- A detecção de duplicidade é heurística: dois problemas diferentes no mesmo ponto podem exigir revisão; ocorrências distantes ou fora da janela não são agregadas.
