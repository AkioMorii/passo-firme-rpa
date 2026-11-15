# Origem das evidências (15/11/2026)

- `diagnostico_azure_15-11-2026.json`: transcrição fiel do resultado que o integrante forneceu depois de executar `scripts/diagnostico_api.py` em seu computador contra a API pública. É **evidência de conectividade e contrato de leitura**; não demonstra PATCH ou alteração de dados. Para uma imagem real, fazer captura de tela no computador do integrante.
- `testes_19_ambiente_de_revisao.txt`: saída real dos 19 testes executados no ambiente de preparação deste pacote, com código correspondente. O integrante havia confirmado os 13 testes da versão original no próprio computador; ainda precisa registrar um print dos **19 testes atualizados** na sua máquina.
- `demo_local_contrato_v0.json`: execução com 5 registros inventados e servidor local simulado, incluindo PATCH no servidor fictício. Nunca representar como alteração na Azure.
- `audit_demo_local.jsonl`: auditoria gerada com dados inventados. Nenhuma informação identificadora real.
