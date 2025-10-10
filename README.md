# AgenticArmy Automation Stack

Este repositorio agrega tres solucoes complementares para construir automacao e agentes de IA em ambiente local:

| Pasta | Foco | Principais tecnologias |
|-------|------|------------------------|
| `Localn8n/self-hosted-ai-starter-kit` | Infraestrutura Docker para n8n, Ollama, Qdrant e PostgreSQL, com credenciais/workflows demo | Docker Compose, n8n, Ollama, Qdrant, PostgreSQL |
| `AwesomeN8n/awesome-n8n-templates` | Biblioteca de workflows n8n prontos para IA, integracoes e automacao | n8n (400+ integracoes), OpenAI, Gemini, Qdrant, Supabase, Notion etc. |
| `CrewAi` (`crewai_local` e `DevTeam`) | Agentes CrewAI personalizaveis para logica especializada, com fallback offline | Python 3.10+, CrewAI, Ollama (opcional), Poetry |

A combinacao permite subir um n8n local, importar workflows prontos e acionar agentes Python quando for preciso sair do low-code.

---

## 1. Localn8n: Stack self-hosted para n8n

- Docker Compose (`Localn8n/self-hosted-ai-starter-kit/docker-compose.yml`) sobe **n8n**, **PostgreSQL**, **Qdrant** e **Ollama** com volumes persistentes e rede interna `demo`.
- Targets proprios via perfis (`cpu`, `gpu-nvidia`, `gpu-amd`) e jobs `ollama-pull` para baixar `llama3.2` automaticamente.
- `.env` (baseado em `.env.example`) define credenciais do Postgres, chaves do n8n e opcionalmente `OLLAMA_HOST` para apontar para instancia local.
- Pasta `n8n/demo-data` carrega credenciais/workflows de exemplo ao iniciar (import job `n8n-import`).
- Volume `./shared -> /data/shared` permite compartilhar arquivos do host com o n8n.

**Como iniciar (PowerShell):**
```powershell
cd d:\Dev\py\AgenticArmy\Localn8n\self-hosted-ai-starter-kit
copy .env.example .env   # ajuste senhas antes de subir
# CPU por padrao
docker compose --profile cpu up -d
# Interface: http://localhost:5678
```

**Cuidados:** troque credenciais demo, verifique portas (5678, 11434, 6333) e monitore logs do Ollama ao baixar modelos grandes.

---

## 2. AwesomeN8n: Biblioteca de workflows

- Diretorio `AwesomeN8n/awesome-n8n-templates` agrupa centenas de workflows em JSON por categoria (AI, Forms, Slack, OpenAI, Telegram, WordPress etc.).
- `README.md` lista cada template com descricao e link direto para o arquivo correspondente.
- As categorias de IA incluem pipelines de **RAG**, agentes para **Telegram**, **Slack**, integracoes com **Qdrant**, **Supabase**, **Google Drive**, **Notion** e muito mais.

**Uso sugerido no n8n local:**
1. Suba o n8n com a stack Localn8n.
2. Em *Import > From file*, escolha um JSON da pasta desejada.
3. Revise credenciais (OpenAI, Gemini, Pinecone etc.) e ajuste para seus provedores (pode apontar para Ollama local quando aplicavel).

**Boas praticas:**
- Versione os workflows importados em um repositorio separado.
- Centralize credenciais no n8n (Settings > Credentials) e evite hardcode.
- Se usar RAG, considere apontar para o Qdrant local da stack.

---

## 3. CrewAi: Agentes Python orquestrados

### 3.1 `crewai_local`
- Projeto simples (`pyproject.toml`) com dependencia `crewai[tools] >=0.203.0` e `langchain-community`.
- `src/crewai_local/crew.py` define tres agentes (pesquisa, estrategia, dev) sequenciais, com **fallback estatico** se `OLLAMA_BASE_URL` nao estiver acessivel.
- `README.md` descreve setup com Poetry e comando `poetry run start`.

### 3.2 `DevTeam`
- Template completo do CrewAI "Development Team" adaptado para execucao local.
- Agents/tasks configurados via YAML (`config/agents.yaml`, `config/tasks.yaml`), base de conhecimento em `knowledge/`, e ferramentas opcionais (`Serper`, `FileReadTool`).
- `src/development_team_automation/crew.py` encapsula escolha de LLM (Ollama quando disponivel) com fallback deterministico `_FallbackLLM`.
- Comandos expostos em `pyproject.toml`: `run`, `train`, `replay`, `test` atraves de `poetry run python -m development_team_automation.main <verbo>`.

**Setup (PowerShell):**
```powershell
cd d:\Dev\py\AgenticArmy\CrewAi\DevTeam
poetry install
# executar
poetry run python -m development_team_automation.main run
```

**Integracao com n8n:**
- Use o n8n para acionar scripts via no **Execute Command** (`python -m crewai_local.main`) ou exponha um endpoint HTTP FastAPI nos projetos e consuma com **HTTP Request**.
- Defina variaveis como `OLLAMA_BASE_URL` e chaves em `.env` nas pastas de cada projeto.

---

## 4. Fluxo integrado sugerido

1. **Infraestrutura:** suba o stack Localn8n para ter n8n + Qdrant + Ollama.
2. **Workflows:** importe templates do AwesomeN8n alinhados ao seu caso de uso (p.ex. RAG para documentos internos, bots de mensageria, integracao com SaaS).
3. **Agentes especializados:** quando o workflow precisar de etapas complexas (planejamento, escrita de relatorios, geracao de codigo), invoque os agentes do CrewAi.
4. **Dados locais:** utilize o volume `shared` para trocar arquivos entre n8n e scripts Python, ou exponha APIs internas.
5. **Governanca:** monitore logs Docker para latencia dos modelos, configure backups dos volumes (`n8n_storage`, `postgres_storage`, `qdrant_storage`, `ollama_storage`).

---

## 5. Checklist rapido de configuracao

- [ ] Instalar Docker Desktop e habilitar WSL2.
- [ ] Revisar e preencher `Localn8n/self-hosted-ai-starter-kit/.env`.
- [ ] Executar `docker compose --profile cpu up -d` (ou perfil GPU desejado).
- [ ] Validar acesso em `http://localhost:5678`.
- [ ] Configurar credenciais n8n (OpenAI, Gemini, Pinecone, etc.).
- [ ] Criar ambientes Python com Poetry em `CrewAi/crewai_local` e `CrewAi/DevTeam`.
- [ ] Definir `OLLAMA_BASE_URL` se for usar modelos locais (default `http://localhost:11434`).
- [ ] Importar workflows do `AwesomeN8n` conforme necessidade.
- [ ] Vincular workflows do n8n aos agentes CrewAI (Execute Command ou HTTP).

---

## 6. Recursos adicionais

- Documentacao oficial n8n: <https://docs.n8n.io>
- Repositorio Self-hosted AI Starter Kit: <https://github.com/n8n-io/self-hosted-ai-starter-kit>
- CrewAI docs: <https://docs.crewai.com>
- Ollama: <https://ollama.com>

Com esta base voce consegue prototipar automacao e agentes de IA localmente, mantendo dados sob controle e evoluindo da prototipacao low-code para codigo Python especializado sempre que necessario.
