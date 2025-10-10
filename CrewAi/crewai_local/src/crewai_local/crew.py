import os
from itertools import cycle
from typing import Any, Dict, Iterable, Protocol
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from crewai import Agent, Crew, LLM as CrewLLM, Process, Task
try:
    from crewai_tools import DuckDuckGoSearchRun
except ImportError:  # DuckDuckGo tool pode não estar disponível
    DuckDuckGoSearchRun = None
from dotenv import load_dotenv

load_dotenv()


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

    if base_url and _ollama_available(base_url):
        return {
            "researcher": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
            "strategist": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
            "coder": CrewLLM(model="ollama/gpt-oss", base_url=base_url),
        }

    if base_url:
        print(f"⚠️  Não foi possível conectar ao Ollama em {base_url}. Usando respostas estáticas.")

    researcher_responses = [
        """### Comparativo de APIs de Análise de Sentimento\n\n| API | Pontos Fortes | Pontos Fracos | Preço | Documentação |\n| --- | --- | --- | --- | --- |\n| Google Cloud Natural Language | Alta precisão, suporte multilíngue, boa integração com GCP | Custo cresce rapidamente em alto volume | A partir de ~US$1.00 por 1000 unidades | https://cloud.google.com/natural-language/docs |\n| Azure Text Analytics | Integração com ecossistema Azure, dashboards, GDPR-ready | Requer configuração no Azure Portal | A partir de ~US$1.00 por 1000 chamadas | https://learn.microsoft.com/azure/cognitive-services/text-analytics/ |\n\n**Recomendação:** Adotar Azure Text Analytics pelo equilíbrio entre custo, segurança corporativa e facilidade de integração em pipelines de monitoramento de marca."""
    ]

    strategist_responses = [
        """## Resumo Executivo\n\nCriamos o *Brand Pulse Monitor*, uma solução SaaS que acompanha o sentimento em tempo real sobre marcas utilizando Azure Text Analytics. O produto integra dados de reviews, redes sociais e tickets de suporte para gerar alertas e relatórios executivos.\n\n### Por que agora\n- Crescimento de canais digitais dispersos dificulta a leitura rápida do sentimento.\n- Equipes de marketing precisam priorizar ações com base em métricas confiáveis.\n\n### Proposta de Valor\n- Painel centralizado com notas de sentimento, tópicos emergentes e variação histórica.\n- Alertas automáticos quando o sentimento cair abaixo de thresholds configuráveis.\n- Baseado em tecnologia Azure, garantindo compliance corporativa e escalabilidade."""
    ]

    coder_responses = [
        '''"""sentiment_analyzer.py"""\n"""Script de exemplo que simula uma chamada à API Azure Text Analytics."""\n\nimport json\nfrom typing import Literal\n\nSentiment = Literal['positive', 'neutral', 'negative']\n\nMOCK_RESPONSES: dict[str, Sentiment] = {\n    'excelente': 'positive',\n    'ruim': 'negative',\n}\n\n\ndef analyze_sentiment(text: str) -> Sentiment:\n    """Retorna o sentimento estimado para `text` usando dados mockados."""\n    text_lower = text.lower()\n    for keyword, sentiment in MOCK_RESPONSES.items():\n        if keyword in text_lower:\n            return sentiment\n    return 'neutral'\n\n\nif __name__ == '__main__':\n    sample = 'O atendimento foi excelente, recomendo muito'\n    result = analyze_sentiment(sample)\n    print(json.dumps({'input': sample, 'sentiment': result}, ensure_ascii=False, indent=2))\n'''
    ]

    return {
        "researcher": _CyclingStaticLLM(researcher_responses),
        "strategist": _CyclingStaticLLM(strategist_responses),
        "coder": _CyclingStaticLLM(coder_responses),
    }


llms = _initialize_llms()

researcher_llm = llms["researcher"]
strategist_llm = llms["strategist"]
coder_llm = llms["coder"]

# --- FERRAMENTAS ---
search_tool = DuckDuckGoSearchRun() if DuckDuckGoSearchRun is not None else None
researcher_tools = [search_tool] if search_tool else []

# --- AGENTES ---
researcher = Agent(
    role='Pesquisador Sênior de Mercado',
    goal='Encontrar tecnologias de IA promissoras e relevantes para automação de marketing.',
    backstory="Com um olhar crítico, você identifica as tendências que realmente importam.",
    verbose=True,
    tools=researcher_tools,
    llm=researcher_llm,
)
strategist = Agent(
    role='Estrategista de Produto e Conteúdo',
    goal='Destilar a pesquisa técnica em um plano de ação e conceito de produto claro.',
    backstory="Você é a ponte entre o técnico e o negócio, transformando insights em estratégia.",
    verbose=True,
    llm=strategist_llm,
)
coder = Agent(
    role='Desenvolvedor Python Sênior',
    goal='Escrever código Python limpo, funcional e bem documentado para criar um protótipo.',
    backstory="Você é um mestre do Python, capaz de traduzir especificações em código elegante.",
    verbose=True,
    llm=coder_llm,
)

# --- TAREFAS ---
task1 = Task(
    description="""Pesquise as 2 principais APIs de IA para análise de sentimento de texto.\n  Avalie prós, contras e preços. Forneça os links para a documentação.""",
    expected_output="Um relatório detalhado comparando as duas APIs, com links para a documentação.",
    agent=researcher,
)
task2 = Task(
    description="""Com base no relatório, escreva um resumo executivo para um novo produto\n  que usa uma das APIs para monitorar o sentimento de uma marca.""",
    expected_output="Um resumo executivo formatado em markdown, com no máximo 3 parágrafos.",
    agent=strategist,
    context=[task1],
)
task3 = Task(
    description="""Usando o conceito do produto e a documentação da API recomendada,\n  escreva um script Python simples que receba um texto e imprima o sentimento\n  (pode usar uma chamada de API mock/falsa). Comente o código.""",
    expected_output="Um único arquivo de código Python (`sentiment_analyzer.py`) bem documentado.",
    agent=coder,
    context=[task1, task2],
)


# --- MONTAGEM DA EQUIPE (CREW) ---
def create_crew() -> Crew:
    return Crew(
        agents=[researcher, strategist, coder],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=True,
    )
