# Prompt — Geração da Apresentação Executiva

Prompt utilizado no **GitHub Copilot Chat** com o modelo **Opus**, acessado via **Microsoft Outlook**, para gerar o arquivo `reconciliacao_edd_v8.html`.

---

## Como usar

1. Abra o GitHub Copilot Chat no Outlook
2. Selecione o modelo **Opus**
3. Cole o prompt abaixo, substituindo os campos `[INFORME]` pelos números da carga atual antes de enviar
4. Após receber o Markdown, execute `python scripts/07_gerar_pdf.py` para gerar o PDF atualizado
5. A saída gerada é o documento HTML de apresentação executiva

---

## Prompt

```
Você é um especialista em documentação técnica e automação de processos de telecomunicações.
Preciso que você gere um documento de apresentação executiva em Markdown para um projeto de automação chamado

O documento deve ser adequado para apresentação a um gerente de operações de rede e deve conter:
1. Título e contexto (área, objetivo)
2. Descrição do problema original (dificuldades do processo manual)
3. Descrição da solução desenvolvida (pipeline Python automatizado)
4. Tabela de resultados com números reais do processamento
5. Tabela de problemas técnicos encontrados e soluções implementadas
6. Fluxo simplificado do pipeline (ASCII)
7. Tecnologias utilizadas
8. Lista de entregáveis do projeto
9. Seção de reusabilidade (como usar nas próximas cargas)

Use os seguintes dados reais do projeto:
- Circuitos EDD processados: [INFORME O TOTAL]
- Equipamentos já na planta (filtrados): [INFORME]
- Centros já no GRC (filtrados): [INFORME]
- Novos centros a cadastrar: [INFORME]
- Novos equipamentos a cadastrar: [INFORME]
- Lotes de 500 linhas gerados: [INFORME]

Linguagem: português brasileiro, objetiva e profissional.
Formato: Markdown compatível com GitHub, com tabelas e blocos de código.
Tom: técnico mas acessível para gestores não-técnicos.

Gere o documento completo agora.
```

---

## Dicas de uso

- Antes de rodar o prompt, execute o pipeline completo para ter os números reais de cada etapa
- Os campos `[INFORME]` devem ser preenchidos com os totais dos CSVs gerados nos `output/passo*/`
- Para atualizar apenas uma seção do documento já gerado, informe no chat: *"Atualize apenas a seção X com: [novos dados]"*
