# API Reference

This repository contains multiple subprojects. This document catalogs all public entry points, functions, classes, configuration, and CLI usage relevant to developers integrating or extending the projects.

- CrewAI local demo (`CrewAi/crewai_local`)
- CrewAI development team automation (`CrewAi/DevTeam`)
- n8n self-hosted kit and templates are operational assets; they expose no Python API but have CLI/Docker usage.

---

## CrewAI Local Demo (`CrewAi/crewai_local`)

### Installation
- Python 3.11
- Install with Poetry inside the `CrewAi/crewai_local` folder.

```bash
cd CrewAi/crewai_local
poetry install
```

### Environment
- Optional: `OLLAMA_BASE_URL` (default `http://localhost:11434`) to use a local model.
- Fallback static responses are used if the endpoint is unavailable.

### Public Modules
- `crewai_local.main`
- `crewai_local.crew`

### CLI Entrypoint
- Script: `poetry run start`
- Invokes `crewai_local.main:run`

#### Usage
```bash
cd CrewAi/crewai_local
poetry run start
```

### Functions

#### `crewai_local.main.run()`
Runs the crew and prints the final result to stdout.

Example:
```python
from crewai_local.main import run

if __name__ == "__main__":
    run()
```

#### `crewai_local.crew.create_crew() -> crewai.Crew`
Constructs and returns a sequential `Crew` with three agents and three tasks.

Example:
```python
from crewai_local.crew import create_crew

crew = create_crew()
result = crew.kickoff()
print(result)
```

### Classes

#### `crewai_local.crew.SupportsCall` (typing.Protocol)
- Attributes: `model: str`
- Methods: `call(prompt: str, **kwargs) -> str`, `acall(prompt: str, **kwargs) -> str`

#### `_CyclingStaticLLM`
- Minimal static LLM used for offline fallback. Implements `call` and `acall` returning deterministic values.

### Environment Variables
- `OLLAMA_BASE_URL`: Base URL of the local Ollama instance. If reachable, a live model is used; otherwise, static responses are served.

---

## CrewAI Development Team (`CrewAi/DevTeam`)

### Installation
```bash
cd CrewAi/DevTeam
poetry install
```

### Environment
- Optional: `SERPER_API_KEY` to enable the Serper search tool.
- Optional: `OLLAMA_BASE_URL` to use local models; otherwise deterministic fallbacks are used.

### Public Modules
- `development_team_automation.main`
- `development_team_automation.crew`
- `development_team_automation.tools.custom_tool`
- Configuration files:
  - `src/development_team_automation/config/agents.yaml`
  - `src/development_team_automation/config/tasks.yaml`

### CLI Entrypoints
Defined in `pyproject.toml`:
- `development_team_automation` -> `development_team_automation.main:run`
- `run_crew` -> `development_team_automation.main:run`
- `train` -> `development_team_automation.main:train`
- `replay` -> `development_team_automation.main:replay`
- `test` -> `development_team_automation.main:test`

#### Usage
```bash
cd CrewAi/DevTeam
poetry run python -m development_team_automation.main run
poetry run python -m development_team_automation.main train 5 out.json
poetry run python -m development_team_automation.main replay <task_id>
poetry run python -m development_team_automation.main test 3 gpt-oss
```

### Functions (development_team_automation.main)

#### `run()`
Runs the crew with default `inputs` keys: `project_name`, `project_requirements`.

Example:
```python
from development_team_automation.main import run

run()
```

#### `train()`
Trains the crew for a given number of iterations.

- Args (from CLI): `n_iterations: int`, `filename: str`

Example:
```bash
poetry run python -m development_team_automation.main train 10 training_log.json
```

#### `replay()`
Replays the crew execution from a specific task.

- Args (from CLI): `task_id: str`

Example:
```bash
poetry run python -m development_team_automation.main replay task_2
```

#### `test()`
Tests the crew execution.

- Args (from CLI): `n_iterations: int`, `openai_model_name: str`

Example:
```bash
poetry run python -m development_team_automation.main test 3 gpt-oss
```

### Functions & Classes (development_team_automation.crew)

#### `CompleteDevelopmentTeamAutomationCrew` (CrewBase)
Creates a Crew with four agents and five tasks; wires local model selection and graceful fallbacks.

- Agents (decorated methods):
  - `project_manager_and_tech_lead() -> Agent`
  - `senior_developer() -> Agent`
  - `qa_engineer_and_tester() -> Agent`
  - `documentation_expert() -> Agent`

- Tasks (decorated methods):
  - `project_planning_and_task_distribution() -> Task`
  - `software_development_implementation() -> Task`
  - `quality_assurance_and_testing() -> Task`
  - `documentation_creation() -> Task`
  - `project_review_and_final_delivery() -> Task`

- Crew assembly:
  - `crew() -> Crew`

- Helper classes:
  - `SupportsCall` (typing.Protocol)
  - `_CyclingStaticLLM` (offline static LLM)
  - `_FallbackLLM` (wraps a primary LLM with deterministic fallback)

Example:
```python
from development_team_automation.crew import CompleteDevelopmentTeamAutomationCrew

crew = CompleteDevelopmentTeamAutomationCrew().crew()
result = crew.kickoff(inputs={
    'project_name': 'Brand Pulse Monitor',
    'project_requirements': 'Realtime sentiment API, dashboard'
})
print(result)
```

### Custom Tooling

#### `development_team_automation.tools.custom_tool.MyCustomTool`
A template `BaseTool` for custom actions.

- Args schema: `MyCustomToolInput` with field `argument: str`
- Implement logic in `_run(self, argument: str) -> str`

Example registration snippet (edit your agent wiring):
```python
from development_team_automation.tools.custom_tool import MyCustomTool

# inside an agent factory
custom_tool = MyCustomTool()
Agent(config=..., tools=[custom_tool])
```

### Configuration
- `config/agents.yaml`: Roles, goals, backstories
- `config/tasks.yaml`: Task descriptions, expected outputs, task chaining

Example usage in YAML (fragment):
```yaml
software_development_implementation:
  description: Implement the core API for {project_name}.
  expected_output: Source files and short rationale.
  agent: senior_developer
  context:
    - project_planning_and_task_distribution
```

### Environment Variables
- `SERPER_API_KEY`: Enables `SerperDevTool` for search (optional)
- `OLLAMA_BASE_URL`: If set and reachable, use live models; otherwise fall back to static responses

---

## n8n Assets
- `Localn8n/self-hosted-ai-starter-kit`: Docker Compose stack for n8n, Postgres, Qdrant, Ollama.
- `AwesomeN8n/awesome-n8n-templates`: JSON workflow templates categorized by domain.

These do not expose Python APIs; use Docker and the n8n UI for operation.

### Quick start (n8n stack)
```bash
cd Localn8n/self-hosted-ai-starter-kit
cp .env.example .env
# choose a profile as needed
docker compose --profile cpu up -d
```

---

## Versioning and Scripts

### CrewAI Local Demo
- Script: `start` -> `crewai_local.main:run`

### DevTeam
- Scripts: `development_team_automation`, `run_crew`, `train`, `replay`, `test`

---

## Troubleshooting
- If `OLLAMA_BASE_URL` is unreachable, both CrewAI projects switch to deterministic static outputs. This is expected and ensures local/offline runs.
- To enable extra tools like search, install `crewai-tools` and set `SERPER_API_KEY`.
