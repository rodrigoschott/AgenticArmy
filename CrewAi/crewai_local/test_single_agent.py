"""
Teste de um agente individual usando CLI tools
"""

from crewai import Agent, Task, Crew
from src.crewai_local.tools.web_tools import get_enhanced_tools_for_agent
from src.crewai_local.crew_paraty import _initialize_llm

print("\n" + "="*70)
print("🧪 TESTE DE AGENTE INDIVIDUAL - CLI TOOLS")
print("="*70)

# Criar LLM
print("\n1️⃣ Inicializando LLM...")
llm = _initialize_llm()
print(f"   ✅ LLM criado: {llm.model_name if hasattr(llm, 'model_name') else 'LLM'}")

# Criar agente com ferramentas CLI
print("\n2️⃣ Criando agente de teste...")
tools = get_enhanced_tools_for_agent("estrategista")
print(f"   📋 Ferramentas: {[t.name for t in tools]}")

agent = Agent(
    role="Test Agent - Estrategista",
    goal="Test CLI tools by searching for information about Paraty",
    backstory="You are a test agent validating that MCP CLI tools work correctly.",
    tools=tools,
    llm=llm,
    verbose=True
)
print(f"   ✅ Agente criado: {agent.role}")

# Criar task simples
print("\n3️⃣ Criando tarefa...")
task = Task(
    description="""
    Search the web for information about Paraty tourism.
    Use the search_web tool to find relevant information.
    Return a brief summary (2-3 sentences) about Paraty as a tourist destination.
    """,
    expected_output="A brief summary about Paraty tourism in 2-3 sentences",
    agent=agent
)
print(f"   ✅ Tarefa criada")

# Executar crew
print("\n4️⃣ Executando crew...")
print("   ⏳ Aguardando execução (pode demorar ~10-30s)...\n")
print("-" * 70)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

try:
    result = crew.kickoff()
    
    print("-" * 70)
    print("\n5️⃣ RESULTADO:")
    print(f"\n{result}\n")
    
    print("="*70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("   ✓ Agente criado")
    print("   ✓ Ferramentas CLI funcionaram")
    print("   ✓ Task executada sem 'Event loop is closed'")
    print("   ✓ Resultado obtido")
    print("="*70 + "\n")
    
except Exception as e:
    print("-" * 70)
    print("\n❌ ERRO NA EXECUÇÃO:")
    print(f"   {str(e)}\n")
    print("="*70 + "\n")
    raise
