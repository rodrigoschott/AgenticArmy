"""
Exemplos de uso do Sistema Multi-Agente Paraty

Este arquivo demonstra como usar os 3 workflows principais.
"""

from crewai_local.crew_paraty import (
    _initialize_llm,
    create_property_evaluation_crew,
    create_positioning_crew,
    create_opening_prep_crew
)


def exemplo_avaliacao_propriedade():
    """
    Exemplo: Avaliar Pousada Vista Mar no Centro Histórico
    
    Workflow A - 5 agentes:
    - Marcelo: Contexto local + experiências
    - André: Avaliação técnica + CAPEX
    - Fernando: Due diligence jurídica
    - Ricardo: Valuation financeiro
    - Gabriel: Stress test e riscos
    """
    
    print("=" * 70)
    print("EXEMPLO 1: AVALIAÇÃO DE PROPRIEDADE")
    print("=" * 70)
    
    # Dados da propriedade a ser avaliada
    property_data = {
        'name': 'Pousada Vista Mar',
        'location': 'Centro Histórico de Paraty',
        'price': 2_200_000,  # R$ 2.2 milhões
        'rooms': 12,
        'capex_estimated': 280_000,  # R$ 280 mil de reforma
        'adr_target': 320,  # Taxa média diária de R$ 320
        'occupancy_target': 60  # 60% de ocupação
    }
    
    print("\n📋 Propriedade:")
    print(f"   Nome: {property_data['name']}")
    print(f"   Localização: {property_data['location']}")
    print(f"   Preço: R$ {property_data['price']:,.2f}")
    print(f"   Quartos: {property_data['rooms']}")
    print(f"   CAPEX estimado: R$ {property_data['capex_estimated']:,.2f}")
    print(f"   ADR target: R$ {property_data['adr_target']}")
    print(f"   Ocupação target: {property_data['occupancy_target']}%")
    
    print("\n🚀 Iniciando avaliação com 5 agentes especializados...\n")
    
    # Inicializar LLM e criar crew
    llm = _initialize_llm()
    crew = create_property_evaluation_crew(llm, property_data)
    
    # Executar workflow
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("✅ AVALIAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(result)
    
    # Salvar resultado
    with open("exemplo_avaliacao.md", 'w', encoding='utf-8') as f:
        f.write(f"# Avaliação: {property_data['name']}\n\n")
        f.write(result)
    
    print("\n💾 Resultado salvo em: exemplo_avaliacao.md")


def exemplo_estrategia_posicionamento():
    """
    Exemplo: Desenvolver estratégia para nova pousada boutique
    
    Workflow B - 4 agentes:
    - Juliana: Análise competitiva
    - Marcelo: Perfil turista + experiências
    - Helena: Posicionamento estratégico
    - Beatriz: Naming + identidade de marca
    """
    
    print("\n\n" + "=" * 70)
    print("EXEMPLO 2: ESTRATÉGIA DE POSICIONAMENTO")
    print("=" * 70)
    
    # Dados do projeto
    project_data = {
        'location': 'Paraty - Centro Histórico',
        'rooms': 12,
        'target_audience': 'Casais 35-55 anos, alta renda, cultura e gastronomia'
    }
    
    print("\n📋 Projeto:")
    print(f"   Localização: {project_data['location']}")
    print(f"   Quartos: {project_data['rooms']}")
    print(f"   Público-alvo: {project_data['target_audience']}")
    
    print("\n🚀 Desenvolvendo estratégia com 4 agentes...\n")
    
    # Inicializar LLM e criar crew
    llm = _initialize_llm()
    crew = create_positioning_crew(llm, project_data)
    
    # Executar workflow
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("✅ ESTRATÉGIA DESENVOLVIDA")
    print("=" * 70)
    print(result)
    
    # Salvar resultado
    with open("exemplo_posicionamento.md", 'w', encoding='utf-8') as f:
        f.write("# Estratégia de Posicionamento\n\n")
        f.write(result)
    
    print("\n💾 Resultado salvo em: exemplo_posicionamento.md")


def exemplo_preparacao_abertura():
    """
    Exemplo: Preparar pousada para soft opening
    
    Workflow C - 4 agentes:
    - Paula: SOPs e operações
    - Patrícia: Licenciamento + compliance trabalhista
    - Sofia: Design e ambientação
    - Renata: Auditoria de experiência + processos
    """
    
    print("\n\n" + "=" * 70)
    print("EXEMPLO 3: PREPARAÇÃO PARA ABERTURA")
    print("=" * 70)
    
    # Dados da abertura
    opening_data = {
        'opening_date': '2026-06-01',  # Início da alta temporada
        'rooms': 12,
        'staff_size': 8  # Equipe inicial
    }
    
    print("\n📋 Abertura:")
    print(f"   Data prevista: {opening_data['opening_date']}")
    print(f"   Quartos: {opening_data['rooms']}")
    print(f"   Equipe: {opening_data['staff_size']} funcionários")
    
    print("\n🚀 Preparando abertura com 4 agentes...\n")
    
    # Inicializar LLM e criar crew
    llm = _initialize_llm()
    crew = create_opening_prep_crew(llm, opening_data)
    
    # Executar workflow
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("✅ PLANO DE ABERTURA COMPLETO")
    print("=" * 70)
    print(result)
    
    # Salvar resultado
    with open("exemplo_abertura.md", 'w', encoding='utf-8') as f:
        f.write("# Plano de Abertura\n\n")
        f.write(result)
    
    print("\n💾 Resultado salvo em: exemplo_abertura.md")


if __name__ == "__main__":
    # Executar todos os exemplos
    
    print("🏨 SISTEMA MULTI-AGENTE PARATY - EXEMPLOS DE USO\n")
    
    # Exemplo 1: Avaliar propriedade
    exemplo_avaliacao_propriedade()
    
    # Exemplo 2: Estratégia de posicionamento
    exemplo_estrategia_posicionamento()
    
    # Exemplo 3: Preparação para abertura
    exemplo_preparacao_abertura()
    
    print("\n\n" + "=" * 70)
    print("🎉 TODOS OS EXEMPLOS CONCLUÍDOS!")
    print("=" * 70)
    print("\nArquivos gerados:")
    print("  - exemplo_avaliacao.md")
    print("  - exemplo_posicionamento.md")
    print("  - exemplo_abertura.md")
