import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import DuckDuckGoSearchRun
from langchain_community.llms import Ollama
from dotenv import load_dotenv

load_dotenv()

# --- INICIALIZAÇÃO DOS MODELOS ESPECIALIZADOS ---
ollama_complex = Ollama(
  model='gpt-oss',
  base_url=os.getenv("OLLAMA_BASE_URL")
)
ollama_coder = Ollama(
  model='gpt-oss',
  base_url=os.getenv("OLLAMA_BASE_URL")
)

# --- FERRAMENTAS ---
search_tool = DuckDuckGoSearchRun()

# --- AGENTES ---
researcher = Agent(
  role='Pesquisador Sênior de Mercado',
  goal='Encontrar tecnologias de IA promissoras e relevantes para automação de marketing.',
  backstory="Com um olhar crítico, você identifica as tendências que realmente importam.",
  verbose=True, tools=[search_tool], llm=ollama_complex
)
strategist = Agent(
  role='Estrategista de Produto e Conteúdo',
  goal='Destilar a pesquisa técnica em um plano de ação e conceito de produto claro.',
  backstory="Você é a ponte entre o técnico e o negócio, transformando insights em estratégia.",
  verbose=True, llm=ollama_complex
)
coder = Agent(
  role='Desenvolvedor Python Sênior',
  goal='Escrever código Python limpo, funcional e bem documentado para criar um protótipo.',
  backstory="Você é um mestre do Python, capaz de traduzir especificações em código elegante.",
  verbose=True, llm=ollama_coder
)

# --- TAREFAS ---
task1 = Task(
  description="""Pesquise as 2 principais APIs de IA para análise de sentimento de texto.
  Avalie prós, contras e preços. Forneça os links para a documentação.""",
  expected_output="Um relatório detalhado comparando as duas APIs, com links para a documentação.",
  agent=researcher
)
task2 = Task(
  description="""Com base no relatório, escreva um resumo executivo para um novo produto
  que usa uma das APIs para monitorar o sentimento de uma marca.""",
  expected_output="Um resumo executivo formatado em markdown, com no máximo 3 parágrafos.",
  agent=strategist, context=[task1]
)
task3 = Task(
  description="""Usando o conceito do produto e a documentação da API recomendada,
  escreva um script Python simples que receba um texto e imprima o sentimento
  (pode usar uma chamada de API mock/falsa). Comente o código.""",
  expected_output="Um único arquivo de código Python (`sentiment_analyzer.py`) bem documentado.",
  agent=coder, context=[task1, task2]
)

# --- MONTAGEM DA EQUIPE (CREW) ---
def create_crew():
    return Crew(
        agents=[researcher, strategist, coder],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=2
    )
