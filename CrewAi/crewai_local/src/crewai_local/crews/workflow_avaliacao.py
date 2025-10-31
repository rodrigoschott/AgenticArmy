"""
Workflow A: Avaliar Propriedade Específica

Crew para avaliar uma propriedade específica e tomar decisão go/no-go.
Agentes: Marcelo, André, Fernando, Ricardo, Gabriel (5 agentes)
"""

from crewai import Crew, Process, Task
from ..agents.mercado import create_marcelo_ribeiro
from ..agents.tecnico import create_andre_martins
from ..agents.juridico import create_fernando_costa
from ..agents.estrategia import create_ricardo_tavares
from ..agents.qualidade import create_gabriel_motta


def create_property_evaluation_crew(llm, property_data: dict) -> Crew:
    """
    Cria uma crew para avaliar uma propriedade específica.
    
    Args:
        llm: Modelo de linguagem a ser usado pelos agentes
        property_data: Dict com informações da propriedade
            - name: Nome da propriedade
            - location: Localização (Centro Histórico, Praia, etc)
            - price: Preço de compra (R$)
            - rooms: Número de quartos
            - capex_estimated: CAPEX estimado (R$)
            - adr_target: ADR projetado (R$)
            - occupancy_target: Ocupação projetada (%)
    
    Returns:
        Crew configurada para avaliação
    """
    
    # Criar agentes
    marcelo = create_marcelo_ribeiro(llm)
    andre = create_andre_martins(llm)
    fernando = create_fernando_costa(llm)
    ricardo = create_ricardo_tavares(llm)
    gabriel = create_gabriel_motta(llm)
    
    # Task 1: Contexto Local + Experiências
    task_context = Task(
        description=f"""Forneça contexto completo sobre {property_data['location']} em Paraty, incluindo:
        
        1. **Contexto Local:**
           - História e características do bairro/região
           - Fluxo turístico e perfil de visitantes
           - Proximidade de atrações principais
           - Infraestrutura (restaurantes, acesso, segurança)
        
        2. **Calendário de Eventos:**
           - FLIP (Festa Literária Internacional de Paraty) - impacto em ocupação e ADR
           - Festival da Cachaça, Bourbon Festival
           - Regatas e eventos náuticos
           - Feriados prolongados e alta temporada
           - Estimativa de impacto em ocupação por evento
        
        3. **Portfolio de Experiências Potenciais:**
           - 10-15 experiências autênticas que a pousada poderia oferecer
           - Parcerias necessárias (guias, restaurantes, barqueiros, artesãos)
           - Custo estimado por experiência
           - Diferenciais competitivos possíveis
        
        4. **Restrições Locais:**
           - IPHAN (tombamento histórico)
           - APA Cairuçu (área de proteção ambiental)
           - Regulações municipais específicas
        
        Propriedade: {property_data['name']}
        Localização: {property_data['location']}
        Quartos: {property_data['rooms']}""",
        
        expected_output="""Relatório estruturado em markdown com:
        - Análise do contexto local
        - Calendário anual de eventos com impacto em ocupação
        - Portfolio de 10-15 experiências autênticas com custos
        - Rede de parceiros locais recomendados
        - Restrições regulatórias a considerar""",
        
        agent=marcelo
    )
    
    # Task 2: Inspeção Técnica + CAPEX
    task_technical = Task(
        description=f"""Realize uma avaliação técnica detalhada da propriedade e estime o CAPEX total de reforma:
        
        1. **Inspeção Predial:**
           - Estrutura (fundações, paredes, lajes)
           - Sistemas hidráulicos (tubulação, reservatórios, esgoto)
           - Sistemas elétricos (fiação, quadros, aterramento)
           - Telhado (estrutura, telhas, calhas)
           - Acabamentos e conservação geral
           - Umidade, infiltrações, cupins
        
        2. **Estimativa de CAPEX:**
           - Reformas críticas (🔴 urgentes)
           - Reformas importantes (🟡 necessárias)
           - Melhorias desejáveis (🟢 diferenciais)
           - Contingência de 15-20% para surpresas
           - Total por ambiente/sistema
        
        3. **Considerações IPHAN:**
           - Restrições para fachada, janelas, cores
           - Aprovações necessárias
           - Limitações arquitetônicas
        
        4. **Timeline de Obras:**
           - Cronograma estimado por fase
           - Dependências críticas
           - Período mínimo realista
        
        Propriedade: {property_data['name']}
        CAPEX estimado inicial: R$ {property_data.get('capex_estimated', 'não informado')}""",
        
        expected_output="""Laudo técnico estruturado com:
        - Avaliação completa por sistema (estrutura, hidráulica, elétrica, telhado)
        - CAPEX detalhado por prioridade (crítico/importante/desejável)
        - Contingência de 15-20%
        - Restrições IPHAN aplicáveis
        - Cronograma de obras com timeline realista
        - Total de CAPEX consolidado""",
        
        agent=andre
    )
    
    # Task 3: Due Diligence Jurídica
    task_legal = Task(
        description=f"""Conduza uma due diligence jurídica completa da propriedade:
        
        1. **Análise de Matrícula:**
           - Proprietário atual e cadeia dominial
           - Ônus, gravames, hipotecas
           - Área registrada vs área real
           - Situação regular?
        
        2. **Zoneamento e Uso:**
           - Compatibilidade para uso hoteleiro
           - Restrições municipais
           - Tombamento IPHAN
           - APA Cairuçu (se aplicável)
        
        3. **Certidões Necessárias:**
           - Certidões negativas (federal, estadual, municipal, trabalhista)
           - IPTU em dia?
           - Débitos condominiais?
        
        4. **Passivos Ocultos:**
           - Processos judiciais envolvendo o imóvel
           - Passivos trabalhistas anteriores
           - Reclamações de vizinhos ou órgãos públicos
        
        5. **Estrutura de Aquisição:**
           - SPE vs pessoa física
           - Cláusulas contratuais protetivas
           - Contingências legais
        
        Use o sistema de alerta:
        🔴 Deal breaker - Impede a transação
        🟡 Negotiable - Pode ser negociado com vendedor
        🟢 Acceptable - Situação regular
        
        Propriedade: {property_data['name']}
        Preço: R$ {property_data['price']:,.2f}""",
        
        expected_output="""Parecer jurídico estruturado com:
        - Checklist de due diligence com status de cada item
        - Red flags identificados (com sistema de cores)
        - Certidões necessárias e como obtê-las
        - Análise de zoneamento e restrições
        - Recomendação de estrutura de aquisição
        - Minutas de cláusulas contratuais protetivas
        - Conclusão: GO / NO-GO / GO COM RESSALVAS""",
        
        agent=fernando
    )
    
    # Task 4: Valuation e Modelagem Financeira
    task_financial = Task(
        description=f"""Realize o valuation completo e crie modelo financeiro de 5 anos:
        
        1. **Inputs do Modelo:**
           - Preço de compra: R$ {property_data['price']:,.2f}
           - CAPEX: [usar estimativa do Eng. André]
           - Quartos: {property_data['rooms']}
           - ADR target: R$ {property_data.get('adr_target', 320)}
           - Ocupação target: {property_data.get('occupancy_target', 60)}%
        
        2. **Projeção de Receitas (5 anos):**
           - Revenue por quarto por mês
           - Sazonalidade (alta/média/baixa)
           - Growth rate anual (0-5%)
        
        3. **Projeção de Custos:**
           - OPEX (operação): ~40-50% da receita
           - Staffing (usar guidelines da Paula)
           - Manutenção, utilities, marketing
           - Impostos (Simples Nacional ~6-11%)
        
        4. **Três Cenários:**
           - 🔴 Conservador: ocupação -20%, ADR -10%
           - 🟡 Base: projeções fornecidas
           - 🟢 Otimista: ocupação +15%, ADR +10%
        
        5. **Métricas Financeiras:**
           - VPL (Valor Presente Líquido) - WACC 12%
           - TIR (Taxa Interna de Retorno)
           - Payback (tempo de retorno)
           - GOPPAR ano 5
           - Análise de sensibilidade (ocupação, ADR)
        
        6. **Análise de Caixa:**
           - Capital de giro necessário (6 meses)
           - Break-even point
           - "E se a ocupação cair 30%? Quanto tempo até falir?"
        
        Use o sistema de alerta:
        🔴 Red flag - Inviabilidade financeira
        🟡 Caution - Riscos a monitorar
        🟢 Acceptable - Dentro dos parâmetros""",
        
        expected_output="""Modelo financeiro completo contendo:
        - Projeção de 5 anos (receitas, custos, lucro)
        - Três cenários (conservador/base/otimista)
        - VPL, TIR, Payback para cada cenário
        - Análise de sensibilidade (tabelas)
        - Análise de caixa e capital de giro
        - Red flags financeiros identificados
        - Recomendação clara: COMPRAR / NÃO COMPRAR / RENEGOCIAR PREÇO
        - Se recomendar compra: preço máximo justificado""",
        
        agent=ricardo,
        context=[task_technical]  # Depende do CAPEX do André
    )
    
    # Task 5: Stress Test e Devil's Advocate
    task_devil = Task(
        description=f"""Desafie todas as premissas e stress-teste a decisão de compra:
        
        1. **Análise de Pressupostos:**
           - Revise todos os pressupostos otimistas
           - Identifique "achismos" sem dados
           - Questione projeções de ocupação e ADR
        
        2. **Cenários Adversos:**
           - E se a ocupação for 30% menor que o projetado?
           - E se a FLIP for cancelada 2 anos seguidos?
           - E se um concorrente forte abrir ao lado?
           - E se o CAPEX explodir em 50%?
           - E se houver uma crise econômica em 2026?
        
        3. **Pre-Mortem Analysis:**
           "É 2027. A pousada falhou completamente. Por quê?"
           - Liste 10 possíveis causas de fracasso
           - Avalie probabilidade (baixa/média/alta)
           - Avalie impacto (baixo/médio/alto/catastrófico)
        
        4. **Perguntas Desconfortáveis:**
           - O proprietário tem capital de giro para 12 meses de baixa?
           - Qual o plano B se tudo der errado?
           - Há estratégia de saída clara?
           - O mercado de Paraty está saturado?
        
        5. **Risk Matrix:**
           - Liste todos os riscos identificados
           - Classifique por probabilidade × impacto
           - Sugira mitigações para os top 5 riscos
        
        Seja impiedosamente cético, mas construtivo.
        
        Contexto:
        - Propriedade: {property_data['name']}
        - Investimento total: R$ {property_data['price'] + property_data.get('capex_estimated', 0):,.2f}""",
        
        expected_output="""Relatório crítico estruturado com:
        - Lista de pressupostos questionáveis
        - 5-10 cenários adversos detalhados
        - Pre-mortem: 10 causas possíveis de fracasso
        - Perguntas desconfortáveis que precisam ser respondidas
        - Risk matrix completa (probabilidade × impacto)
        - Top 5 riscos críticos com sugestões de mitigação
        - Conclusão: Esta compra é robusta o suficiente para seguir?""",
        
        agent=gabriel,
        context=[task_context, task_technical, task_legal, task_financial]
    )
    
    # Criar Crew
    crew = Crew(
        agents=[marcelo, andre, fernando, ricardo, gabriel],
        tasks=[task_context, task_technical, task_legal, task_financial, task_devil],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
