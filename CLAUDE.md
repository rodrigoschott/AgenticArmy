# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

AgenticArmy is a local automation stack combining three complementary solutions for building AI agents and automation workflows. The project is structured into three main components:

- **Localn8n/self-hosted-ai-starter-kit**: Docker infrastructure for n8n, Ollama, Qdrant, and PostgreSQL
- **AwesomeN8n/awesome-n8n-templates**: Library of 400+ pre-built n8n workflow templates
- **CrewAi**: Python-based multi-agent systems with offline fallback capabilities

## Common Development Commands

### Docker Infrastructure (Localn8n)

Navigate to: `Localn8n/self-hosted-ai-starter-kit`

```powershell
# Start the stack (CPU profile)
docker compose --profile cpu up -d

# Start with GPU support (NVIDIA)
docker compose --profile gpu-nvidia up -d

# Start with GPU support (AMD)
docker compose --profile gpu-amd up -d

# Stop the stack
docker compose down

# View logs
docker compose logs -f
```

Services will be available at:
- n8n: http://localhost:5678
- Ollama: http://localhost:11434
- Qdrant: http://localhost:6333

### CrewAI Projects

#### DevTeam Project

Navigate to: `CrewAi/DevTeam`

```powershell
# Install dependencies
poetry install

# Run the crew
poetry run python -m development_team_automation.main run

# Train the crew
poetry run python -m development_team_automation.main train <iterations> <filename>

# Replay a specific task
poetry run python -m development_team_automation.main replay <task_id>

# Test the crew
poetry run python -m development_team_automation.main test <iterations> <model_name>

# Run tests
poetry run pytest
```

#### crewai_local Project

Navigate to: `CrewAi/crewai_local`

```powershell
# Install dependencies
poetry install

# Run the crew
poetry run start

# Run tests
poetry run pytest
```

## Architecture

### Docker Stack Architecture

The Localn8n stack uses Docker Compose with multiple profiles for different hardware configurations:
- **Networks**: Internal `demo` network for service communication
- **Volumes**: Persistent storage for n8n, PostgreSQL, Qdrant, and Ollama
- **Shared Volume**: `./shared -> /data/shared` for file exchange between host and n8n
- **Import Job**: `n8n-import` automatically loads demo credentials and workflows from `n8n/demo-data` on startup

### CrewAI Agent Architecture

Both CrewAI projects implement a sophisticated fallback system for offline operation:

1. **LLM Selection Logic** (`crew.py`):
   - Attempts to connect to Ollama at `OLLAMA_BASE_URL` (default: http://localhost:11434)
   - Uses `/api/tags` endpoint to check availability
   - Falls back to static responses if Ollama is unavailable

2. **Fallback Pattern** (`_FallbackLLM` class):
   - Primary LLM: Ollama with `gpt-oss` model
   - Fallback LLM: Static cycling responses (`_CyclingStaticLLM`)
   - Automatic switching on failure with warning message
   - Preserves model interface for seamless operation

3. **Agent Roles**:
   - **DevTeam**: Project Manager, Senior Developer, QA Engineer, Documentation Expert
   - **crewai_local**: Researcher, Strategist, Coder

### Configuration Files

- **agents.yaml**: Defines agent roles, goals, and backstories
- **tasks.yaml**: Defines tasks with descriptions, expected outputs, and agent assignments
- **.env**: Environment variables (OLLAMA_BASE_URL, API keys, database credentials)

## Key Technical Details

### Environment Variables

Create `.env` files from `.env.example` templates. Critical variables:

```
# Localn8n
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=n8n
N8N_ENCRYPTION_KEY=<generate_random_key>
N8N_USER_MANAGEMENT_JWT_SECRET=<generate_random_key>
OLLAMA_HOST=ollama:11434

# CrewAI projects
OLLAMA_BASE_URL=http://localhost:11434
SERPER_API_KEY=<optional_for_web_search>
```

### Python Version Requirements

- **DevTeam**: Python >=3.10, <3.14
- **crewai_local**: Python >=3.11, <3.12

### Dependencies

- **DevTeam**: crewai[tools] >=0.177.0, <1.0.0
- **crewai_local**: crewai[tools] >=0.203.0, <0.204.0, langchain-community, python-dotenv

### Optional Tools

CrewAI tools are loaded conditionally:
- `FileReadTool`: For reading local files
- `SerperDevTool`: For web search (requires SERPER_API_KEY)
- `DuckDuckGoSearchRun`: Alternative search tool

## Integration Patterns

### n8n to CrewAI Integration

Two approaches:

1. **Execute Command Node**: Call Python scripts directly
   ```
   cd D:\Dev\py\AgenticArmy\CrewAi\crewai_local && poetry run start
   ```

2. **HTTP Request Node**: Expose CrewAI as FastAPI endpoints and call via HTTP

### Data Exchange

Use the shared volume for file exchange:
- Host: `./Localn8n/self-hosted-ai-starter-kit/shared`
- n8n container: `/data/shared`

### Workflow Import

To use n8n templates:
1. Navigate to n8n UI (http://localhost:5678)
2. Go to Import > From file
3. Select JSON from `AwesomeN8n/awesome-n8n-templates/<category>`
4. Configure credentials (OpenAI, Gemini, etc.)
5. Adjust to use local Ollama when applicable

## Common Patterns

### Adding New CrewAI Agents

1. Define agent in `config/agents.yaml` with role, goal, and backstory
2. Add agent method in `crew.py` with `@agent` decorator
3. Configure LLM and tools in agent initialization
4. Add corresponding tasks in `config/tasks.yaml`
5. Create task method in `crew.py` with `@task` decorator
6. Update crew composition in `@crew` method

### Ollama Model Management

```bash
# List installed models
curl http://localhost:11434/api/tags

# Pull new model
docker exec ollama ollama pull <model_name>

# Check model availability in Python
# Uses _ollama_available() function in crew.py
```

### Testing Offline Mode

1. Stop Ollama service: `docker compose stop ollama-cpu`
2. Run CrewAI project - should show fallback warning
3. Verify static responses are used
4. Restart Ollama: `docker compose start ollama-cpu`

## Project Structure

```
AgenticArmy/
├── AwesomeN8n/
│   └── awesome-n8n-templates/  # 400+ workflow templates organized by category
├── CrewAi/
│   ├── DevTeam/
│   │   ├── src/development_team_automation/
│   │   │   ├── config/          # agents.yaml, tasks.yaml
│   │   │   ├── tools/           # custom_tool.py
│   │   │   ├── knowledge/       # user_preference.txt
│   │   │   ├── crew.py          # Agent and task definitions
│   │   │   └── main.py          # CLI entry points
│   │   └── pyproject.toml
│   └── crewai_local/
│       ├── src/crewai_local/
│       │   ├── crew.py          # Simple 3-agent setup
│       │   └── main.py
│       └── pyproject.toml
└── Localn8n/
    └── self-hosted-ai-starter-kit/
        ├── docker-compose.yml
        ├── n8n/demo-data/       # Credentials and workflows
        └── shared/              # Host-container file exchange
```

## Troubleshooting

### Ollama Connection Issues

Check Ollama status:
```bash
curl http://localhost:11434/api/tags
```

If unreachable:
- Verify Docker container is running: `docker ps | grep ollama`
- Check OLLAMA_BASE_URL environment variable
- Review Docker logs: `docker logs ollama`

### n8n Import Failures

- Ensure PostgreSQL is healthy before n8n starts
- Check `docker compose logs n8n-import` for errors
- Verify credentials files in `n8n/demo-data/credentials`

### Poetry Dependency Conflicts

```powershell
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall
poetry install --no-cache
```

### CrewAI Static Responses

If seeing repeated static responses:
- Verify Ollama is running and accessible
- Check OLLAMA_BASE_URL points to correct endpoint
- Ensure `gpt-oss` model is pulled: `docker exec ollama ollama pull gpt-oss`

## Notes

- All commands assume PowerShell on Windows (paths use `\`)
- The project is in Portuguese (README, comments, static responses)
- n8n workflows support 400+ integrations including OpenAI, Gemini, Qdrant, Supabase, Notion
- CrewAI agents run sequentially by default (Process.sequential)
- Static fallback responses are domain-specific and provide realistic project artifacts
