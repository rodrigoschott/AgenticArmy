"""
Teste para validar que o fix do event loop funciona.
"""

import sys
sys.path.insert(0, 'src')

from crewai import Agent, Task, Crew
from crewai_local.crew_paraty import _initialize_llm
from crewai_local.tools.mcp_tools_new import get_search_tools

print("="*80)
print("TESTE: Event Loop Fix para MCP Tools")
print("="*80)

try:
    # 1. Inicializar LLM
    print("\n1️⃣ Inicializando LLM...")
    llm = _initialize_llm()
    print(f"✅ LLM: {llm}")
    
    # 2. Obter MCP tools
    print("\n2️⃣ Obtendo ferramentas MCP...")
    tools = get_search_tools()
    print(f"✅ {len(tools)} tools obtidas")
    
    # 3. Criar agente
    print("\n3️⃣ Criando agente...")
    agent = Agent(
        role="Testador",
        goal="Testar ferramentas MCP",
        backstory="Expert em testes",
        llm=llm,
        tools=tools,
        verbose=True
    )
    print("✅ Agente criado")
    
    # 4. Criar tarefa simples
    print("\n4️⃣ Criando tarefa...")
    task = Task(
        description="Pesquise: 'Paraty turismo'. Resuma em 1 frase.",
        expected_output="Uma frase sobre turismo em Paraty",
        agent=agent
    )
    print("✅ Tarefa criada")
    
    # 5. Executar crew
    print("\n5️⃣ Executando crew...")
    print("-"*80)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    print("-"*80)
    
    # 6. Verificar resultado
    print("\n6️⃣ Resultado:")
    print(f"✅ {result}")
    
    print("\n" + "="*80)
    print("🎉 TESTE PASSOU! Event loop fix funcionando")
    print("="*80)

except Exception as e:
    print("\n" + "="*80)
    print(f"❌ TESTE FALHOU: {e}")
    print("="*80)
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    print("\n🧹 Teste concluído")
