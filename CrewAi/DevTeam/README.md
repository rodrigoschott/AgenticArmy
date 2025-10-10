# CompleteDevelopmentTeamAutomation Crew (offline friendly)

This project adapts the official crewAI "development team" template to run entirely on your machine. It keeps the original multi-agent workflow while prioritising local models, graceful fallbacks, and reproducible execution through Poetry.

## Requirements

- Python **3.10 – 3.13**
- [Poetry](https://python-poetry.org/docs/#installation) 1.8+
- (Optional) [Ollama](https://ollama.com/) running locally if you want to use your own models

All other dependencies are resolved through Poetry.

## Setup

```powershell
cd DevTeam
poetry install
```

The command above creates/updates Poetry's virtual environment and installs crewAI plus this project's extras. Each subsequent command should be executed with `poetry run …` to stay inside that environment.

## Running the crew

```powershell
poetry run python -m development_team_automation.main run
```

The entry point provides the same `run`, `train`, `replay`, and `test` helpers as the template. Replace `run` with any of those verbs if you need the alternative flows.

## Local LLM behaviour & fallbacks

- O arquivo `.env` deste projeto já define `OLLAMA_BASE_URL=http://localhost:11434`, o mesmo endpoint exposto pelo docker-compose de `Localn8n`. Ajuste esse valor apenas se seu serviço Ollama estiver em outra URL.
- Garanta que o modelo `gpt-oss` esteja disponível na instância dockerizada (`docker compose` já realiza o `ollama pull llama3.2`; instale `gpt-oss` se ainda não estiver presente).
- At start-up we probe the endpoint; if the check or the first generation fails, we automatically switch to deterministic static responses so the crew can finish offline.
- The Project Manager agent runs without the "reasoning" mode to avoid strict tool-calling assumptions that cloud models expect.
- A single warning is printed when the fallback kicks in so you know which agent switched.

## Optional integrations

| Integration | How to enable | What happens when missing |
|-------------|---------------|---------------------------|
| Serper search tool | Export `SERPER_API_KEY` in the environment before running | The developer agent disables the tool and continues with offline templates (no noisy stack traces). |
| `.env` variables | Place them alongside `pyproject.toml` or rely on your shell | We load them automatically via `python-dotenv`. |

## Customisation pointers

- Update `src/development_team_automation/config/agents.yaml` and `…/tasks.yaml` to change personalities and objectives.
- `src/development_team_automation/crew.py` centralises the agent wiring, local model selection, and fallback logic.
- `src/development_team_automation/main.py` keeps the CLI helpers; extend the `inputs` dict if you need richer prompts.

## Customize for your project

Follow this checklist to adapt the crew to a concrete project or task and supply domain documents as context.

### 1) Provide project inputs

Edit `src/development_team_automation/main.py` and set the `inputs` your crew will interpolate in prompts:

```python
inputs = {
		"project_name": "Brand Pulse Monitor",
		"project_requirements": "Real-time sentiment API, basic dashboard, Azure Text Analytics integration"
}
```

Tip: Add your own keys (e.g. `target_users`, `non_functional_requirements`) and reference them in YAML using `{your_key}`.

### 2) Tailor agents (roles, goals, tone)

Open `src/development_team_automation/config/agents.yaml` and customize:

- `role`: Title and scope of each agent
- `goal`: A crisp, outcome-oriented brief. Use inputs like `{project_name}`.
- `backstory`: Domain expertise, style, constraints (e.g., “prefer FastAPI + Postgres”).

Keep them specific to your context; agents perform better with clear constraints and examples.

### 3) Define tasks, outputs, and chaining

Edit `src/development_team_automation/config/tasks.yaml`:

- `description`: What to do, with any constraints and acceptance criteria
- `expected_output`: Concrete deliverables and format (e.g., “markdown with headings: …”)
- `agent`: Which agent executes the task
- `context`: Upstream tasks whose outputs are provided as context for this task

Example additions (fragment):

```yaml
software_development_implementation:
	description: >
		Implement the core API for {project_name}. Prior to coding, read the local
		requirements in "knowledge/requirements.md" and "knowledge/example_payloads.json".
		Use FastAPI and return Pydantic models. Include a quick-start section in the README.
	expected_output: >
		Source files under src/, a README excerpt, and a short rationale for key decisions.
	agent: senior_developer
	context:
	- project_planning_and_task_distribution
```

Notice how we mention specific file paths—this guides the agent to use the FileReadTool to ingest them.

### 4) Add documents as agent context

Use the existing `DevTeam/knowledge/` folder for your domain materials (requirements, APIs, examples, schemas). For best results:

1. Place files under `DevTeam/knowledge/` (text, Markdown, JSON, CSV). Keep names descriptive.
2. Reference the files explicitly in your task descriptions or agent goals, e.g.: “Read `knowledge/user_preference.txt` before planning.”
3. Ensure the FileReadTool is available:
	 - This project already wires `FileReadTool` when `crewai_tools` is installed.
	 - If you don’t have it, add the dependency and reinstall:

```powershell
poetry add crewai-tools
poetry install
```

4. Keep file paths relative to the DevTeam folder. Agents can open them directly via the tool.

Advanced: If you prefer reading entire directories, you can enable `DirectoryReadTool` by importing it and adding it to the agent tools in `crew.py` (requires `crewai-tools`).

### 5) Wire custom tools (optional)

Implement domain-specific actions in `src/development_team_automation/tools/custom_tool.py`—rename the class and fill `_run` with your logic (e.g., parse OpenAPI, query a local service, evaluate codegen). Then register it:

1. Import your tool in `src/development_team_automation/crew.py`.
2. Add an instance to the relevant agent’s `tools=[...]` list.
3. In the tool’s `description`, be explicit about when and how it should be used; agents rely on that text.

### 6) Encourage grounded reasoning (prompting tips)

- In task descriptions, explicitly say “Use the FileReadTool to read: …” and list the files.
- Ask for citations: “Quote snippets from the files you used with file path and line range.”
- For code tasks, request a brief “design-first” outline before implementation to reduce rework.

### 7) Re-run and iterate

```powershell
poetry run python -m development_team_automation.main run
```

Tweak YAML and inputs, run again, and compare outputs. Use the `context` links to pass real artefacts from earlier tasks to later ones.

### Optional: CLI or file-driven inputs

If you want to avoid editing `main.py` each time, you can extend it to load inputs from a JSON/YAML file (user-provided path) or parse command-line flags. Keep keys consistent with what your YAML references.

## Known limitations

- When running purely on static responses the crew outputs deterministic sample artefacts. Swap in local models to obtain dynamic content.
- The template still expects certain files (`sample_value`, etc.). If they are missing the agents will ask you to provide them; this mirrors the original behaviour.

## Support & references

- Official docs: <https://docs.crewai.com>
- GitHub issues: <https://github.com/joaomdmoura/crewai>
- Community Discord: <https://discord.com/invite/X4JWnZnxPb>

Enjoy hacking on your fully offline development crew!  
Feel free to extend it with new tools, local models, or additional agents as needed.
