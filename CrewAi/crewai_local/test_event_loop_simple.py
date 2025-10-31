"""
Teste simples para validar fix do event loop.
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
    print("\n1. Inicializando LLM...")
    llm = _initialize_llm()
    print(f"OK LLM: {llm}")
    
    # 2. Obter MCP tools
    print("\n2. Obtendo ferramentas MCP...")
    tools = get_search_tools()
    print(f"OK {len(tools)} tools obtidas")
    
    #3. Criar agente
    print("\n3. Criando agente...")
    agent = Agent(
        role="Testador",
        goal="Testar ferramentas MCP",
        backstory="Expert em testes",
        llm=llm,
        tools=tools,
        verbose=False
    )
    print("OK Agente criado")
    
    # 4. Criar tarefa simples
    print("\n4. Criando tarefa...")
    task = Task(
        description="Pesquise: 'Paraty turismo'. Resuma em 1 frase.",
        expected_output="Uma frase sobre turismo em Paraty",
        agent=agent
    )
    print("OK Tarefa criada")
    
    # 5. Executar crew
    print("\n5. Executando crew...")
    print("-"*80)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False
    )
    
    result = crew.kickoff()
    print("-"*80)
    
    # 6. Verificar resultado
    print("\n6. Resultado:")
    print(f"OK {result}")
    
    print("\n" + "="*80)
    print("TESTE PASSOU! Event loop fix funcionando")
    print("="*80)

except Exception as e:
    print("\n" + "="*80)
    print(f"TESTE FALHOU: {e}")
    print("="*80)
    import traceback
    traceback.print_exc()

finally:
    print("\nTeste concluido")
