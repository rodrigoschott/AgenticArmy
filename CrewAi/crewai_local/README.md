# CrewAI Local Demo

Este projeto demonstra uma equipe de agentes CrewAI trabalhando sequencialmente para:

1. Pesquisar APIs de análise de sentimento.
2. Destilar os achados em um resumo executivo.
3. Gerar um protótipo Python `sentiment_analyzer.py` usando a API recomendada (mockada).

## Requisitos

- Python 3.11
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências
- Opcional: [Ollama](https://ollama.com/) rodando com o modelo `gpt-oss`

## Configuração

1. Instale as dependências:

   ```powershell
   poetry install
   ```

2. (Opcional) Ajuste a URL base do Ollama caso seu serviço não esteja no padrão do docker-compose (`http://localhost:11434`). O repositório já inclui esse valor no arquivo `.env`, então basta garantir que a stack `Localn8n` esteja em execução.

   ```powershell
   setx OLLAMA_BASE_URL http://localhost:11434
   ```

   Se o endpoint não responder, o projeto usa respostas estáticas de fallback para permitir execução offline.

3. Crie um arquivo `.env` na raiz, se desejar sobrescrever variáveis adicionais (opcional).

## Execução

Inicie a missão da equipe:

```powershell
poetry run start
```

O comando:

- Carrega os agentes definidos em `crewai_local/crew.py`.
- Executa as três tarefas em sequência.
- Exibe o relatório final no terminal.

## Estrutura

```
src/
  crewai_local/
    crew.py      # definição dos agentes, tarefas e fallback offline
    main.py      # ponto de entrada exposto por poetry run start
```

## Notas

- Para produção, substitua o fallback estático conectando o Ollama (ou outro LLM) com os modelos desejados.
- `DuckDuckGoSearchRun` está disponível para pesquisas, mas o fallback estático retorna respostas pré-determinadas quando os LLMs reais não estão ativos.
