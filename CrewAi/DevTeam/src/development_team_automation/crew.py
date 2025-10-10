import os
from itertools import cycle
from typing import Any, Dict, Iterable, Protocol
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from crewai import Agent, Crew, LLM as CrewLLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

try:
    from crewai_tools import FileReadTool, SerperDevTool
except ImportError:  # pragma: no cover - ferramentas opcionais
    FileReadTool = None
    SerperDevTool = None

from dotenv import load_dotenv

load_dotenv()

_SERPER_AVAILABLE = bool(os.getenv("SERPER_API_KEY"))
_SERPER_WARNING_EMITTED = False


class SupportsCall(Protocol):
    model: str

    def call(self, prompt: str, **kwargs: Any) -> str: ...

    async def acall(self, prompt: str, **kwargs: Any) -> str: ...


class _CyclingStaticLLM:
    """LLM estático simples para permitir execução offline."""

    def __init__(self, responses: Iterable[str]):
        self._responses = cycle(responses)
        self.model = "static-local"

    def call(self, prompt: str, **kwargs: Any) -> str:
        return next(self._responses)

    async def acall(self, prompt: str, **kwargs: Any) -> str:
        return next(self._responses)


class _FallbackLLM:
    """Encapsula um LLM remoto com fallback seguro para execução offline."""

    def __init__(self, label: str, primary: SupportsCall | None, fallback: SupportsCall):
        self._label = label
        self._primary = primary
        self._fallback = fallback
        self._warned = False
        self.model = (primary.model if primary is not None else fallback.model)

    def _handle_failure(self, exc: Exception) -> None:
        if not self._warned:
            print(
                f"⚠️  Falha ao usar LLM '{self._label}' ({type(exc).__name__}: {exc}). "
                "Alternando para fallback estático."
            )
            self._warned = True
        self._primary = None
        self.model = self._fallback.model

    @staticmethod
    def _ensure_valid_response(result: Any) -> Any:
        if result is None:
            raise ValueError("Empty response from primary LLM")
        if isinstance(result, str) and not result.strip():
            raise ValueError("Empty response from primary LLM")
        return result

    def call(self, prompt: str, **kwargs: Any) -> str:
        if self._primary is not None:
            try:
                result = self._primary.call(prompt, **kwargs)
                return self._ensure_valid_response(result)
            except Exception as exc:  # pragma: no cover - erros da lib externa
                self._handle_failure(exc)
        return self._fallback.call(prompt, **kwargs)

    async def acall(self, prompt: str, **kwargs: Any) -> str:
        if self._primary is not None:
            try:
                result = await self._primary.acall(prompt, **kwargs)
                return self._ensure_valid_response(result)
            except Exception as exc:  # pragma: no cover - erros da lib externa
                self._handle_failure(exc)
        return await self._fallback.acall(prompt, **kwargs)


def _ollama_available(base_url: str) -> bool:
    try:
        ping_url = urljoin(base_url if base_url.endswith("/") else base_url + "/", "api/tags")
        with urlopen(Request(ping_url, method="GET"), timeout=2) as response:  # type: ignore[arg-type]
            return response.status == 200
    except (URLError, ValueError):
        return False


def _initialize_llms() -> Dict[str, SupportsCall]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    if not base_url:
        base_url = "http://localhost:11434"

    project_manager_responses = [
        """# Plano de Projeto Inicial\n\n## Visão Geral\n- Projeto: Plataforma de automação completa\n- Objetivo: Entregar MVP em 8 semanas com foco em monitoramento inteligente.\n\n## Estrutura de Trabalho\n1. **Planejamento detalhado** (Semana 1)\n2. **Implementação incremental** (Semanas 2-5)\n3. **Teste e validação** (Semanas 5-6)\n4. **Documentação e entrega final** (Semanas 6-7)\n5. **Retrospectiva e ajustes finais** (Semana 8)\n\n## Distribuição de Tarefas\n- PM/Tech Lead: coordenação, revisões técnicas, gestão de riscos.\n- Dev Sênior: desenvolvimento backend/frontend e integrações.\n- QA: definição e execução de plano de testes, automação básica.\n- Documentação: guias de instalação, uso e referência técnica.\n\n## Riscos & Mitigações\n- Dependência de APIs externas → preparar mocks.\n- Capacitação da equipe na stack → criar sessões rápidas de alinhamento.\n\n## Comunicação\n- Daily stand-up (15 min).\n- Weekly checkpoint com stakeholders.\n- Kanban público com métricas de progresso.""",
        """# Relatório Final e Entrega\n\n## Resumo Executivo\nTodo o escopo planejado foi concluído: implementação, validação de qualidade e documentação aprovadas. A solução está pronta para handoff ao time de operações.\n\n## Checklist de Entrega\n- ✅ Código-fonte versionado e revisado.\n- ✅ Testes funcionais e regressão executados sem bloqueios.\n- ✅ Documentação técnica e de usuário publicada.\n- ✅ Riscos residuais monitorados (latência da API externa).\n\n## Retrospectiva\n- **Pontos fortes:** Comunicação fluida, divisão clara de responsabilidades, uso efetivo de automação.\n- **Melhorias futuras:** Expandir cobertura de testes de carga e preparar scripts de migração de dados.\n\n## Próximos Passos\n1. Monitorar métricas em produção por 2 semanas.\n2. Planejar backlog de melhorias contínuas.\n3. Formalizar treinamento dos usuários finais.""",
    ]

    developer_responses = [
        """## Relatório de Implementação\n\n- Stack: Python 3.11, FastAPI, PostgreSQL.\n- Principais módulos: autenticação JWT, ingestor de eventos, motor de análise assíncrono.\n- Padrões aplicados: arquitetura limpa, testes unitários com PyTest, logging estruturado.\n\n```python\n# main.py\nfrom fastapi import FastAPI\nfrom routes import sentiment\n\napp = FastAPI(title=\"Brand Pulse Monitor\")\napp.include_router(sentiment.router, prefix=\"/sentiment\")\n\nif __name__ == \"__main__\":\n    import uvicorn\n    uvicorn.run(app, host=\"0.0.0.0\", port=8000)\n```\n\n```python\n# sentiment.py\nfrom fastapi import APIRouter\nfrom schemas import SentimentRequest, SentimentResponse\n\nrouter = APIRouter()\n\n@router.post(\"/infer\", response_model=SentimentResponse)\ndef infer_sentiment(payload: SentimentRequest):\n    \"\"\"Mock de inferência usando Azure Text Analytics.\"\"\"\n    score = 0.82\n    label = \"positive\" if score >= 0.6 else \"neutral\"\n    return SentimentResponse(sentiment=label, score=score)\n```\n""",
    ]

    qa_responses = [
        """# Relatório de QA\n\n## Plano de Testes\n- Escopo: APIs REST, fluxos críticos do painel, integrações externas mockadas.\n- Abordagem: testes funcionais manuais + suíte automática de regressão (PyTest).\n\n## Execução\n| Caso | Resultado | Observações |\n| --- | --- | --- |\n| Autenticação | ✅ | Fluxo feliz e erro de credencial tratados |\n| Ingestão CSV | ✅ | Validação de schema e duplicidade |\n| Painel histórico | ⚠️ | Demora inicial de 3s (aceitável) |\n\n## Bugs\n- BA-104: mensagem de erro genérica → corrigido na sprint atual.\n\n## Conclusão\nSistema aprovado para go-live condicionado ao monitoramento da latência do painel histórico.""",
    ]

    documentation_responses = [
        """# Pacote de Documentação\n\n## Guia de Instalação\n1. Clone o repositório.\n2. Configure variáveis `DATABASE_URL` e `AZURE_TEXT_ANALYTICS_KEY`.\n3. Execute `make setup` para criar o ambiente local.\n\n## Guia do Usuário\n- Login com credenciais corporativas.\n- Acesse \"Sentimento em Tempo Real\" para os dashboards.\n- Configure alertas em *Configurações > Alertas*.\n\n## Referência Técnica\n- `/sentiment/infer`: POST com campo `text`.\n- `/reports/monthly`: GET retorna relatório consolidado em JSON.\n\n## Troubleshooting\n- Status 401: renovar token no IdP.\n- Latência >5s: validar saúde do serviço de filas.\n\nDocumentação alinhada com a release v1.0.0.""",
    ]

    fallback_llms = {
        "project_manager": _CyclingStaticLLM(project_manager_responses),
        "developer": _CyclingStaticLLM(developer_responses),
        "qa": _CyclingStaticLLM(qa_responses),
        "documentation": _CyclingStaticLLM(documentation_responses),
    }

    primary_llms: Dict[str, SupportsCall | None] = {
        "project_manager": None,
        "developer": None,
        "qa": None,
        "documentation": None,
    }

    if base_url and _ollama_available(base_url):
        primary_llms = {
            "project_manager": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
            "developer": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
            "qa": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
            "documentation": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
        }
    elif base_url:
        print(f"⚠️  Não foi possível conectar ao Ollama em {base_url}. Usando respostas estáticas.")

    friendly_labels = {
        "project_manager": "project_manager",
        "developer": "developer",
        "qa": "qa",
        "documentation": "documentation",
    }

    return {
        key: _FallbackLLM(
            label=friendly_labels[key],
            primary=primary_llms[key],
            fallback=fallback_llms[key],
        )
        for key in fallback_llms
    }


llms = _initialize_llms()


@CrewBase
class CompleteDevelopmentTeamAutomationCrew:
    """CompleteDevelopmentTeamAutomation crew"""

    @agent
    def project_manager_and_tech_lead(self) -> Agent:
        tools = []
        if FileReadTool is not None:
            tools.append(FileReadTool())

        return Agent(
            config=self.agents_config["project_manager_and_tech_lead"],
            tools=tools,
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llms["project_manager"],
        )

    @agent
    def senior_developer(self) -> Agent:
        tools = []
        global _SERPER_WARNING_EMITTED
        if SerperDevTool is not None and _SERPER_AVAILABLE:
            tools.append(SerperDevTool())
        elif SerperDevTool is not None and not _SERPER_WARNING_EMITTED:
            print("ℹ️  SERPER_API_KEY não encontrado. Ferramenta de busca desabilitada.")
            _SERPER_WARNING_EMITTED = True

        return Agent(
            config=self.agents_config["senior_developer"],
            tools=tools,
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llms["developer"],
        )

    @agent
    def qa_engineer_and_tester(self) -> Agent:
        tools = []
        if FileReadTool is not None:
            tools.append(FileReadTool())

        return Agent(
            config=self.agents_config["qa_engineer_and_tester"],
            tools=tools,
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llms["qa"],
        )

    @agent
    def documentation_expert(self) -> Agent:
        tools = []
        if FileReadTool is not None:
            tools.append(FileReadTool())

        return Agent(
            config=self.agents_config["documentation_expert"],
            tools=tools,
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=llms["documentation"],
        )

    @task
    def project_planning_and_task_distribution(self) -> Task:
        return Task(
            config=self.tasks_config["project_planning_and_task_distribution"],
            markdown=False,
        )

    @task
    def software_development_implementation(self) -> Task:
        return Task(
            config=self.tasks_config["software_development_implementation"],
            markdown=False,
        )

    @task
    def quality_assurance_and_testing(self) -> Task:
        return Task(
            config=self.tasks_config["quality_assurance_and_testing"],
            markdown=False,
        )

    @task
    def documentation_creation(self) -> Task:
        return Task(
            config=self.tasks_config["documentation_creation"],
            markdown=False,
        )

    @task
    def project_review_and_final_delivery(self) -> Task:
        return Task(
            config=self.tasks_config["project_review_and_final_delivery"],
            markdown=False,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CompleteDevelopmentTeamAutomation crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
