"""
Workflow B: Estratégia de Posicionamento

Crew para desenvolver estratégia de posicionamento e marca.
Agentes: Juliana, Marcelo, Helena, Beatriz (4 agentes)
"""

from crewai import Crew, Process, Task
from ..agents.mercado import create_juliana_campos, create_marcelo_ribeiro
from ..agents.estrategia import create_helena_andrade
from ..agents.marketing import create_beatriz_moura


def create_positioning_crew(llm, project_data: dict = None) -> Crew:
    """
    Cria uma crew para desenvolver estratégia de posicionamento e marca.
    
    Args:
        llm: Modelo de linguagem a ser usado pelos agentes
        project_data: Dict opcional com contexto do projeto
    
    Returns:
        Crew configurada para estratégia de posicionamento
    """
    
    if project_data is None:
        project_data = {
            'location': 'Paraty - Centro Histórico',
            'rooms': 12,
            'target_audience': 'Casais 35-55 anos, alta renda'
        }
    
    # Criar agentes
    juliana = create_juliana_campos(llm)
    marcelo = create_marcelo_ribeiro(llm)
    helena = create_helena_andrade(llm)
    beatriz = create_beatriz_moura(llm)
    
    # Task 1: Análise Competitiva
    task_market = Task(
        description=f"""Realize análise competitiva completa de pousadas em Paraty:
        
        1. **Benchmark de 15 propriedades similares:**
           - Nome, localização, categoria
           - Número de quartos
           - ADR por temporada (alta/média/baixa)
           - Rating (Booking, Airbnb, TripAdvisor)
           - Principais amenities
           - Pontos fortes e fracos (baseado em reviews)
        
        2. **Análise de Pricing:**
           - Range de ADR por categoria
           - Pricing strategies (premium, mid-range, budget)
           - Yield management (sazonalidade)
        
        3. **Gaps de Mercado:**
           - Segmentos mal atendidos
           - Oportunidades de diferenciação
           - Blue oceans potenciais
        
        4. **Recomendações:**
           - ADR target por temporada
           - Posicionamento de preço recomendado
        
        Contexto: {project_data['location']}, {project_data['rooms']} quartos""",
        
        expected_output="""Relatório competitivo contendo:
        - Matriz comparativa de 15 propriedades
        - Análise de pricing por temporada
        - Identificação de gaps de mercado
        - Recomendação de ADR target e posicionamento de preço""",
        
        agent=juliana
    )
    
    # Task 2: Perfil do Turista + Experiências
    task_local = Task(
        description="""Defina o perfil do turista de Paraty e experiências diferenciadas:
        
        1. **Segmentação de Turistas:**
           - Perfis demográficos (idade, renda, origem)
           - Motivações de viagem (lazer, cultura, aventura, romance)
           - Duração média de estadia
           - Gastos médios por categoria
        
        2. **Portfolio de Experiências Autênticas:**
           - 10-15 experiências exclusivas por perfil
           - Parcerias locais necessárias
           - Precificação sugerida
           - Diferenciais vs concorrência
        
        3. **Calendário de Oportunidades:**
           - Eventos que geram demanda premium
           - Períodos de baixa ocupação (como preencher?)
        
        4. **Posicionamento Local:**
           - História/cultura que pode ser explorada
           - Autenticidade vs turistificação""",
        
        expected_output="""Relatório de segmentação e experiências contendo:
        - 3-4 personas detalhadas de turistas
        - Portfolio de 10-15 experiências autênticas
        - Calendário de oportunidades sazonais
        - Recomendações de posicionamento cultural""",
        
        agent=marcelo
    )
    
    # Task 3: Posicionamento Estratégico
    task_strategy = Task(
        description=f"""Desenvolva o posicionamento estratégico da pousada:
        
        1. **Análise SWOT:**
           - Strengths (forças internas)
           - Weaknesses (fraquezas internas)
           - Opportunities (oportunidades externas)
           - Threats (ameaças externas)
        
        2. **Proposta de Valor:**
           - Para quem? (público-alvo primário e secundário)
           - Que problema resolvemos?
           - Como somos únicos? (moat competitivo)
           - Por que acreditar em nós?
        
        3. **Posicionamento:**
           - Apresente 2-3 opções estratégicas
           - Para cada uma: prós, contras, investimento necessário
           - Recomendação final com justificativa
        
        4. **Frameworks:**
           - Use Value Proposition Canvas
           - Porter's Five Forces
           - Blue Ocean (eliminar-reduzir-elevar-criar)
        
        Contexto: {project_data.get('target_audience', 'a definir')}
        
        Baseie-se na análise de mercado e perfil de turistas.""",
        
        expected_output="""Tese de posicionamento estratégico contendo:
        - Análise SWOT completa
        - Value Proposition Canvas
        - 2-3 opções de posicionamento (com trade-offs)
        - Recomendação final justificada
        - Moat competitivo identificado
        - Segmento-alvo primário e secundário""",
        
        agent=helena,
        context=[task_market, task_local]
    )
    
    # Task 4: Naming e Identidade de Marca
    task_brand = Task(
        description="""Desenvolva naming e diretrizes de identidade de marca:
        
        1. **Naming:**
           - 3-5 opções de nome inspiradas em Paraty
           - Para cada uma: significado, tom, disponibilidade
           - Verificar disponibilidade .com.br
           - Checklist para registro INPI
        
        2. **Brand Platform:**
           - Propósito (por que existimos?)
           - Promessa (o que garantimos?)
           - Posicionamento (como somos únicos?)
           - Personalidade (como nos expressamos?)
        
        3. **Tom de Voz:**
           - Atributos de comunicação (3-5)
           - Exemplos de frases "somos/não somos"
        
        4. **Diretrizes Visuais (conceito):**
           - Paleta de cores sugerida (inspirada em Paraty)
           - Mood board (descrição de referências)
           - Elementos de identidade local
        
        5. **Touchpoints Prioritários:**
           - Site, Instagram, OTAs
           - Sinalização física
           - Amenities e papelaria
        
        Baseie-se no posicionamento estratégico definido.""",
        
        expected_output="""Plataforma de marca contendo:
        - 3-5 opções de nome (com análise e recomendação)
        - Brand platform completo (propósito, promessa, posicionamento, personalidade)
        - Tom de voz com exemplos práticos
        - Diretrizes visuais conceituais
        - Roadmap de implementação nos touchpoints
        - Próximos passos (registro INPI, design, fotografia)""",
        
        agent=beatriz,
        context=[task_strategy]
    )
    
    # Criar Crew
    crew = Crew(
        agents=[juliana, marcelo, helena, beatriz],
        tasks=[task_market, task_local, task_strategy, task_brand],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
