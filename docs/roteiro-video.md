# Roteiro de vídeo (até 3 minutos)

**00:00-00:25 — Contexto.** Apresentar o Passo Firme, os relatos de buracos e obstáculos e o problema da triagem manual. Mostrar o processo manual versus o fluxograma BPMN.

**00:25-00:50 — Tecnologia.** Mostrar a estrutura do GitHub: `src/`, `tests/`, `docs/`, `logs/`, `assets/` e README. Dizer que o Python consulta `/relatos`, usa `/assistente` e atualiza `/relatos/{id}/status`.

**00:50-01:40 — Demonstração ponta a ponta.** Rodar `python scripts/demo.py`, mostrar contagens (2 encaminhados, 2 revisão humana e 1 descartado), abrir o JSON da evidência e o arquivo de saída. Mostrar o status retornado pela API local.

**01:40-02:10 — Decisão e lote.** Explicar distância de 25 m / 48 h, limite de confiança 0,65 e pontuação de risco. Mostrar 2ª execução com zero itens, indicando idempotência.

**02:10-02:35 — Falhas e auditoria.** Rodar `python -m unittest discover -s tests -v`; destacar o teste de API intermitente e de assistente indisponível. Abrir `logs/auditoria.jsonl`, sem dados pessoais.

**02:35-02:55 — Integração e encerramento.** Mostrar a ligação com o MVP via contrato da API e arquivos estruturados. Se houver API real integrada, demonstrá-la no vídeo; caso contrário, declarar que é uma simulação local e que a integração pública está pendente. Mostrar link do repositório e integrantes.

**Atenção:** não apresentar o mock como integração pública nem inventar protocolo oficial. Gravar tela e voz de verdade; este roteiro não substitui o vídeo solicitado pelo professor.
