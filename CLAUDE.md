# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

AgenticArmy is a local automation stack combining three complementary solutions for building AI agents and automation workflows. The project is structured into three main components:

- **Skynet**: Docker infrastructure for n8n, Ollama, Qdrant, and PostgreSQL
- **AwesomeN8n/awesome-n8n-templates**: Library of 400+ pre-built n8n workflow templates
- **CrewAi**: Python-based multi-agent systems with offline fallback capabilities

## Common Development Commands

### Docker Infrastructure (Skynet)

Navigate to: `Skynet`

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

## Docker Compose Services

The Skynet stack uses Docker Compose with multiple profiles for different hardware configurations:
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
   - **crewai_local**: 13 specialized agents for boutique hotel evaluation (Strategy, Market, Legal, Technical, Marketing, Quality)

### Configuration Files

**DevTeam Project:**
- **agents.yaml**: Defines agent roles, goals, and backstories
- **tasks.yaml**: Defines tasks with descriptions, expected outputs, and agent assignments

**crewai_local Project:**
- Agents and tasks defined in Python code (no YAML files)
- Agent definitions: `src/crewai_local/agents/` directory
- Workflow definitions: `src/crewai_local/crews/` directory

**Both Projects:**
- **.env**: Environment variables (OLLAMA_BASE_URL, API keys, database credentials)

## Key Technical Details

### Environment Variables

Create `.env` files from `.env.example` templates. Critical variables:

```
# Skynet
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
- Host: `./Skynet/shared`
- n8n container: `/data/shared`

### Workflow Import

To use n8n templates:
1. Navigate to n8n UI (http://localhost:5678)
2. Go to Import > From file
3. Select JSON from `AwesomeN8n/awesome-n8n-templates/<category>`
4. Configure credentials (OpenAI, Gemini, etc.)
5. Adjust to use local Ollama when applicable

## CrewAI_Local Workflows

The `crewai_local` project provides 4 specialized workflows for boutique hotel (pousada) evaluation and strategy:

### Workflow A: Property Evaluation (AUTONOMOUS RESEARCH MODE) ⭐ NEW

**Location:** `CrewAi/crewai_local/src/crewai_local/crews/workflow_avaliacao.py`

**Purpose:** Go/No-Go decision for property acquisition with autonomous data gathering

**Agents:** 6 agents (Juliana, Marcelo, André, Fernando, Ricardo, Gabriel)
**Duration:** 15-25 minutes (includes research phase)

**NEW FEATURE - Autonomous Research:**
- Only requires **property name OR property link** as input
- Agents automatically research and gather all necessary data
- Supports multiple property sources: Airbnb, Booking.com, OLX, real estate listings
- **Robots.txt Bypass:** fetch_url ignores blocking for legitimate research purposes
- **3-Tier Fallback:** If fetch blocked → search_web → airbnb_search → estimates

**Input (API):**
```json
{
  "property_name": "Pousada Vista Mar",
  "location_hint": "Paraty - RJ"
}

OR

{
  "property_link": "https://www.airbnb.com.br/rooms/12345678"
}
```

**Workflow Steps:**
1. **Task 0 - Property Research** (Juliana Campos - Market Analyst)
   - Researches property details from name/link
   - Gathers: price, rooms, condition, location
   - Analyzes 5-10 competitors for ADR/occupancy benchmarks
   - Estimates CAPEX needs based on condition
   - Output: Complete property intelligence report

2. **Task 1 - Local Context** (Marcelo Ribeiro - Paraty Expert)
   - FLIP events, cultural calendar
   - 10-15 authentic experiences
   - IPHAN/APA restrictions

3. **Task 2 - Technical Evaluation** (André Martins - Engineer)
   - Refines CAPEX estimation
   - Timeline and phasing
   - IPHAN compliance

4. **Task 3 - Legal Due Diligence** (Fernando Costa - Lawyer)
   - Property title, zoning
   - Licenses and certifications
   - Risk assessment

5. **Task 4 - Financial Modeling** (Ricardo Tavares - Financial Analyst)
   - 5-year projections (3 scenarios)
   - VPL, TIR, Payback
   - Buy/Don't Buy recommendation

6. **Task 5 - Stress Testing** (Gabriel Motta - Devil's Advocate)
   - Pre-mortem analysis
   - Risk matrix
   - Final robustness check

**Output:** Complete evaluation report with go/no-go recommendation

**API Endpoints:**
- Sync: `POST /workflows/property-evaluation`
- Async: `POST /workflows/property-evaluation/async`

### Workflow B: Positioning Strategy
**Agents:** 4 (Juliana, Marcelo, Helena, Beatriz)
**Duration:** 8-15 minutes
**Purpose:** Brand positioning and market strategy

### Workflow C: Opening Preparation
**Agents:** 4 (Paula, Patrícia, Sofia, Renata)
**Duration:** 10-18 minutes
**Purpose:** Soft opening preparation with compliance

### Workflow D: 30-Day Planning
**Agents:** 4 (Helena, Ricardo, Juliana, Marcelo)
**Duration:** 2-3 hours (ALWAYS use async mode!)
**Purpose:** Complete strategic analysis before property search

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
└── Skynet/
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
