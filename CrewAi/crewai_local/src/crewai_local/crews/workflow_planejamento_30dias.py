"""
Workflow D: Planejamento Inicial (30 Dias)

Executa as 5 tarefas críticas do plano de 30 dias:
- T-1001: Proposta de valor
- T-1003: Envelope financeiro
- T-1010: Mapa competitivo
- T-1011: Calendário eventos
- T-1021.2: Pipeline ativo

Agentes: Helena, Ricardo, Juliana, Marcelo (4 agentes)
"""

from crewai import Agent, Task, Crew
from ..agents.estrategia import create_helena_andrade
from ..agents.mercado import create_juliana_campos, create_marcelo_ribeiro
from ..agents.estrategia import create_ricardo_tavares
from ..owner_profile import get_owner_context_for_agent, get_budget_range, get_adr_expectations


def create_planning_30days_crew(llm, project_data: dict = None) -> Crew:
    """
    Cria o crew de Planejamento Inicial (30 dias).
    
    Args:
        llm: Instância do LLM
        project_data: Dados opcionais do projeto (localização, preferências, etc.)
    
    Returns:
        Crew configurado para planejamento inicial
    """
    
    # Agentes (com contexto do proprietário injetado)
    helena = create_helena_andrade(llm)
    ricardo = create_ricardo_tavares(llm)
    juliana = create_juliana_campos(llm)
    marcelo = create_marcelo_ribeiro(llm)
    
    # Contexto do projeto
    localizacao = project_data.get('localizacao', 'Paraty') if project_data else 'Paraty'
    budget_min, budget_max = get_budget_range()
    adr_expectations = get_adr_expectations()
    
    # TAREFA 1: Proposta de Valor (Helena)
    task1_proposta_valor = Task(
        description=f"""
        ## TAREFA: T-1001 - Proposta de Valor e Posicionamento
        
        **Contexto do Proprietário:**
{get_owner_context_for_agent("Helena")}
        
        **Objetivo:**
        Desenvolver a Tese do Projeto (2-3 páginas) com:
        1. Promessa central (1 frase)
        2. Personas prioritárias (MÁXIMO 2, não 4)
        3. Diferenciais competitivos (5-7 pontos)
        4. Anti-posicionamento (o que NÃO somos)
        
        **Restrições críticas:**
        - Budget: R${budget_min:,.0f} - R${budget_max:,.0f}
        - Break-even: 6 meses (não negociável)
        - Experiência proprietário: ZERO em hospitalidade
        - Localização preferida: 1º Praia, 2º Centro Histórico
        
        **ATENÇÃO:**
        O proprietário listou 4 personas (culturais, famílias, natureza, estrangeiros).
        Você DEVE recomendar focar em 1-2 primárias para evitar diluição.
        
        **Prazo:** 7 dias
        **Esforço:** 8-12 horas
        """,
        expected_output="""
        # TESE DO PROJETO - POUSADA PARATY
        
        ## 1. PROMESSA CENTRAL
        [Escreva aqui UMA frase que captura a essência do posicionamento]
        
        ## 2. PERSONAS PRIMÁRIAS (MÁXIMO 2)
        **Persona 1:** [Nome do perfil]
        - Por que escolhemos: [Justificativa baseada em dados de mercado]
        - Necessidades principais: [3-5 pontos]
        - Potencial de receita: [Alto/Médio]
        
        **Persona 2 (opcional):** [Nome do perfil]
        - Por que escolhemos: [Justificativa]
        - Sinergia com Persona 1: [Como se complementam]
        
        ## 3. DIFERENCIAIS COMPETITIVOS (5-7)
        1. [Diferencial 1 - específico e mensurável]
        2. [Diferencial 2]
        3. [Diferencial 3]
        4. [Diferencial 4]
        5. [Diferencial 5]
        
        ## 4. ANTI-POSICIONAMENTO (O que NÃO somos)
        - NÃO somos: [Tipo 1]
        - NÃO somos: [Tipo 2]
        - NÃO somos: [Tipo 3]
        
        ## 5. LOCALIZAÇÃO RECOMENDADA
        **Recomendação:** [Praia OU Centro Histórico]
        **Justificativa:** [Baseada nas personas escolhidas e viabilidade]
        
        ## 6. ALERTAS E RISCOS
        ⚠️ Break-even 6 meses com zero experiência: [Análise de viabilidade]
        ⚠️ [Outros riscos identificados]
        
        **FORMATO OBRIGATÓRIO:** Retorne SOMENTE o conteúdo estruturado acima.
        NÃO retorne "Thought:", "Action:", "Input:" ou formato de raciocínio.
        Este é o DOCUMENTO FINAL que será usado pelas próximas tarefas.
        """,
        agent=helena
    )
    
    # TAREFA 2: Análise de Mercado (Juliana) - PARALELA com T3
    task2_mapa_competitivo = Task(
        description=f"""
        ## TAREFA: T-1010 - Mapa Competitivo (15 concorrentes)
        
        **Contexto do Proprietário:**
{get_owner_context_for_agent("Juliana")}
        
        **Objetivo:**
        Mapear 15 concorrentes em Paraty (mid-premium, R$280-400 ADR) e validar:
        
        1. **Validação ADR:** 
           - Proprietário espera R$500 (alta), R$300 (média), R$250 (baixa)
           - Isso é viável para "mid-premium"? Ou está em zona "premium"?
        
        2. **Segmentação:**
           - Concorrentes praia vs centro histórico
           - Quais atendem culturais? Famílias? Natureza? Estrangeiros?
           - Algum concorrente atende 4 perfis? Ou especializam em 1-2?
        
        3. **Break-even 6 meses:**
           - Ocupação média dos concorrentes no primeiro ano
           - É possível atingir break-even em 6 meses? Benchmarks reais?
        
        **Fontes:** Booking, Airbnb, TripAdvisor (foco em notas 4.5+)
        
        **⚠️ OBRIGATÓRIO - RASTREAMENTO DE FONTES:**
        - SEMPRE cite as fontes de cada informação
        - Formato: "Segundo [Fonte] em [Data]: [Informação]"
        - Exemplo: "Segundo DuckDuckGo em 2025-10-31: Casa das Areias R$450/noite alta temporada"
        - Exemplo: "Segundo Airbnb em 2025-10-31 - Paraty: 23 propriedades disponíveis"
        - Se usar tool MCP: Copie o timestamp fornecido no cabeçalho da resposta
        - Se for conhecimento próprio: Indique claramente "Baseado em conhecimento prévio"
        
        **Prazo:** 10 dias (paralelo com Marcelo)
        **Esforço:** 15-20 horas
        """,
        expected_output="""
        # MAPA COMPETITIVO - PARATY MID-PREMIUM
        
        ## 1. CONCORRENTES IDENTIFICADOS (15 POUSADAS)
        
        ### Categoria Praia:
        1. [Nome] - [Localização] - [Quartos] - ADR: Alta R$X / Média R$Y / Baixa R$Z - Nota: X.X
        2. [Nome] - [Localização] - [Quartos] - ADR: Alta R$X / Média R$Y / Baixa R$Z - Nota: X.X
        [... listar 7-8 pousadas de praia]
        
        ### Categoria Centro Histórico:
        1. [Nome] - [Localização] - [Quartos] - ADR: Alta R$X / Média R$Y / Baixa R$Z - Nota: X.X
        2. [Nome] - [Localização] - [Quartos] - ADR: Alta R$X / Média R$Y / Baixa R$Z - Nota: X.X
        [... listar 7-8 pousadas de centro]
        
        ## 2. VALIDAÇÃO ADR
        **ADR Esperado pelo proprietário:**
        - Alta temporada: R$500
        - Média temporada: R$300
        - Baixa temporada: R$250
        
        **Análise de Viabilidade:**
        [É realista para mid-premium? Ou está em zona premium? Dados do mercado]
        
        **Recomendação de ajuste:** [Manter / Ajustar para R$X,Y,Z]
        
        ## 3. SEGMENTAÇÃO DE CONCORRENTES
        **Especialistas (1-2 personas):**
        - [Nome pousada]: Foco em [Persona X]
        - [Nome pousada]: Foco em [Persona Y]
        
        **Generalistas (3-4 personas):**
        - [Nome pousada]: Atende [Personas A, B, C, D]
        
        **Insight:** [Especialistas performam melhor? Ou generalistas têm ocupação maior?]
        
        ## 4. BENCHMARKING OCUPAÇÃO
        **Ano 1 (inauguração):** XX-XX% ocupação média
        **Ano 2:** XX-XX% ocupação média
        **Estabilizado (Ano 3+):** XX-XX% ocupação média
        
        **Fontes:** [Listar fontes específicas com datas]
        
        ## 5. GAPS DE MERCADO
        1. [Gap 1 - oportunidade não explorada]
        2. [Gap 2 - nicho descoberto]
        3. [Gap 3 - diferenciação possível]
        
        ## 6. ALERTAS
        ⚠️ Proprietários experientes vs iniciantes: [Diferença de performance em %]
        ⚠️ Break-even 6 meses: [Viável segundo benchmarks? Sim/Não/Talvez]
        
        **FORMATO OBRIGATÓRIO:** Retorne SOMENTE o conteúdo estruturado acima.
        NÃO retorne "Thought:", "Action:", "Input:" ou formato de raciocínio.
        """,
        agent=juliana
    )
    
    # TAREFA 3: Calendário e Sazonalidade (Marcelo) - PARALELA com T2
    task3_calendario_eventos = Task(
        description=f"""
        ## TAREFA: T-1011 - Calendário de Eventos e Sazonalidade
        
        **Contexto do Proprietário:**
{get_owner_context_for_agent("Marcelo")}
        
        **Objetivo:**
        Criar calendário anual 2025-2026 com impacto em pricing e ocupação.
        
        **Análise obrigatória:**
        1. **FLIP:** Impacto em ADR, min-stay, perfil de hóspedes
        2. **Feriados prolongados:** Carnaval, Semana Santa, Corpus Christi, etc.
        3. **Eventos locais:** Festivais, temporada alta/média/baixa
        
        **Validação de personas:**
        - Culturais (FLIP): Quando vêm? Quanto pagam? Perfil?
        - Famílias: Férias escolares, feriados
        - Natureza: Melhor clima para trilhas/cachoeiras
        - Estrangeiros: Sazonalidade diferente de brasileiros?
        
        **PERGUNTA CRÍTICA:**
        Esses 4 públicos têm picos de demanda nos MESMOS períodos?
        Ou se complementam (um grupo vem quando outro não vem)?
        
        **Prazo:** 3 dias (paralelo com Juliana)
        **Esforço:** 4-6 horas
        """,
        expected_output="""
        # CALENDÁRIO EVENTOS & SAZONALIDADE - PARATY 2025-2026
        
        ## 1. CALENDÁRIO ANUAL
        
        ### Jan-Mar 2025
        - **Janeiro:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        - **Fevereiro:** [Alta/Média/Baixa] - Eventos: Carnaval - ADR: R$X - Min-stay: X noites
        - **Março:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        
        ### Abr-Jun 2025
        - **Abril:** [Alta/Média/Baixa] - Eventos: Semana Santa - ADR: R$X - Min-stay: X noites
        - **Maio:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        - **Junho:** [Alta/Média/Baixa] - Eventos: Corpus Christi - ADR: R$X - Min-stay: X noites
        
        ### Jul-Set 2025
        - **Julho:** [Alta/Média/Baixa] - Eventos: FLIP, Férias - ADR: R$X - Min-stay: X noites
        - **Agosto:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        - **Setembro:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        
        ### Out-Dez 2025
        - **Outubro:** [Alta/Média/Baixa] - Eventos: [Lista] - ADR: R$X - Min-stay: X noites
        - **Novembro:** [Alta/Média/Baixa] - Eventos: Proclamação - ADR: R$X - Min-stay: X noites
        - **Dezembro:** [Alta/Média/Baixa] - Eventos: Natal, Réveillon - ADR: R$X - Min-stay: X noites
        
        ## 2. ESTRATÉGIA DE TARIFAS
        
        **Justificativa ADR:**
        - **R$500 (Alta):** [Por que este valor? Baseado em quais concorrentes/eventos?]
        - **R$300 (Média):** [Justificativa]
        - **R$250 (Baixa):** [Justificativa]
        
        ## 3. ANÁLISE DE PERSONAS POR TEMPORADA
        
        **Culturais (FLIP):**
        - Período: [Meses]
        - ADR médio: R$X
        - Ocupação esperada: XX%
        
        **Famílias:**
        - Períodos: [Férias escolares, feriados]
        - ADR médio: R$X
        - Ocupação esperada: XX%
        
        **Natureza:**
        - Melhor clima: [Meses]
        - ADR médio: R$X
        - Ocupação esperada: XX%
        
        **Estrangeiros:**
        - Picos: [Meses diferentes de brasileiros?]
        - ADR médio: R$X
        - Ocupação esperada: XX%
        
        ## 4. INTERSEÇÃO vs COMPLEMENTARIDADE
        
        **Análise crítica:** [Esses 4 públicos competem pelos mesmos períodos? Ou se complementam?]
        
        **Recomendação:** Focar em [Persona 1] e [Persona 2] porque [justificativa baseada em sazonalidade]
        
        **FORMATO OBRIGATÓRIO:** Retorne SOMENTE o conteúdo estruturado acima.
        NÃO retorne "Thought:", "Action:", "Input:" ou formato de raciocínio.
        """,
        agent=marcelo
    )
    
    # TAREFA 4: Envelope Financeiro (Ricardo) - DEPENDE de T1, T2, T3
    task4_envelope_financeiro = Task(
        description=f"""
        ## TAREFA: T-1003 - Envelope Financeiro + Contas PJ
        
        **Contexto do Proprietário:**
{get_owner_context_for_agent("Ricardo")}
        
        **Inputs necessários:**
        - Tese do Projeto (Helena): Posicionamento, personas, diferenciais
        - Mapa Competitivo (Juliana): ADR validado, ocupação benchmarks
        - Calendário (Marcelo): Sazonalidade, pricing por período
        
        **Objetivo:**
        Criar plano financeiro completo e validar viabilidade do break-even em 6 meses.
        
        **Análises obrigatórias:**
        
        1. **CAPEX (por ambiente):**
           - Estimativa por quarto, áreas comuns, TI, segurança
           - MÁXIMO: R$500k (deal breaker do proprietário)
           - Contingência: 12-15%
        
        2. **OPEX (18 meses):**
           - Folha + encargos (considerar curva aprendizado)
           - Utilidades, lavanderia, amenities
           - Comissões OTAs (12-18%)
           - Marketing inicial
           - TI, contabilidade
        
        3. **CENÁRIOS (3):**
           - Conservador: Ocupação 40%, ADR 80% do esperado
           - Base: Ocupação 55%, ADR conforme planejado
           - Otimista: Ocupação 70%, ADR 110%
        
        4. **BREAK-EVEN 6 MESES:**
           - ⚠️ CRÍTICO: Validar se é POSSÍVEL com >90% capital investido
           - Quantos quartos ocupados/mês necessários?
           - Qual ocupação mínima por temporada?
           - Margem de segurança (runway)?
        
        5. **STRESS TEST:**
           - E se ocupação for 30% nos 3 primeiros meses?
           - E se CAPEX estourar 20%?
           - Reserva emergencial mínima recomendada?
        
        **Prazo:** 10 dias (após receber inputs de Helena, Juliana, Marcelo)
        **Esforço:** 12-16 horas
        """,
        expected_output="""
        # ANÁLISE FINANCEIRA - VIABILIDADE POUSADA PARATY
        
        ## 1. ALOCAÇÃO DE CAPITAL (Budget Total: R$2.7M-3.0M)
        
        **Distribuição:**
        - Aquisição imóvel: R$X,XXX,XXX (XX%)
        - CAPEX (reformas/mobília): R$XXX,XXX (XX%)
        - Capital de giro (18 meses): R$XXX,XXX (XX%)
        - Reserva emergencial: R$XXX,XXX (XX%)
        - **TOTAL:** R$X,XXX,XXX
        
        ## 2. CAPEX DETALHADO (MÁXIMO R$500K)
        
        **Por ambiente:**
        - X quartos @ R$XX,XXX cada: R$XXX,XXX
        - Áreas comuns (recepção, café, piscina): R$XXX,XXX
        - Cozinha comercial: R$XX,XXX
        - Infraestrutura TI/segurança: R$XX,XXX
        - Contingência 12-15%: R$XX,XXX
        - **TOTAL CAPEX:** R$XXX,XXX ✅ Dentro do limite R$500k
        
        ## 3. OPEX MENSAL (18 meses)
        
        **Fixo:**
        - Folha de pagamento + encargos: R$XX,XXX
        - Utilidades (água, luz, gás): R$X,XXX
        - Seguros: R$X,XXX
        - Contabilidade/jurídico: R$X,XXX
        - TI/software: R$X,XXX
        
        **Variável:**
        - Lavanderia/amenities: R$XX por quarto ocupado
        - Comissões OTAs (15%): % sobre receita
        - Marketing: R$X,XXX (maior nos primeiros 6 meses)
        
        **TOTAL OPEX MENSAL:** R$XX,XXX (mínimo) + variável
        
        ## 4. CENÁRIOS DE VIABILIDADE
        
        ### CONSERVADOR (Pessimista)
        - Ocupação média: 40%
        - ADR médio: R$320 (80% do planejado)
        - Receita mensal: R$XX,XXX
        - OPEX mensal: R$XX,XXX
        - **Break-even:** Mês XX (⚠️ FORA do prazo 6 meses)
        
        ### BASE (Realista)
        - Ocupação média: 55%
        - ADR médio: R$400 (conforme planejado)
        - Receita mensal: R$XX,XXX
        - OPEX mensal: R$XX,XXX
        - **Break-even:** Mês 6-7 ✅ Dentro do prazo
        
        ### OTIMISTA
        - Ocupação média: 70%
        - ADR médio: R$440 (110% do planejado)
        - Receita mensal: R$XX,XXX
        - OPEX mensal: R$XX,XXX
        - **Break-even:** Mês 4 ✅ Antecipado
        
        ## 5. ANÁLISE BREAK-EVEN 6 MESES
        
        **Para atingir break-even no mês 6:**
        - Ocupação mínima necessária: XX%
        - Quartos ocupados/mês: XX de XX disponíveis
        - ADR mínimo: R$XXX
        - Receita mensal mínima: R$XX,XXX
        
        **⚠️ ALERTA CRÍTICO:**
        [Análise de viabilidade: É possível com >90% capital investido e zero experiência?]
        [Margem de segurança: Quantos meses de runway com reserva emergencial?]
        
        ## 6. STRESS TEST
        
        **Cenário 1: Ocupação 30% nos primeiros 3 meses**
        - Impacto caixa: -R$XX,XXX
        - Runway restante: X meses
        - Ação necessária: [Mitigação]
        
        **Cenário 2: CAPEX estoura 20% (R$600k)**
        - Impacto capital de giro: -R$XXX,XXX
        - Viabilidade: [Análise]
        
        **Cenário 3: ADR médio 20% abaixo do planejado**
        - Break-even adiado para: Mês XX
        - Ação necessária: [Mitigação]
        
        ## 7. RECOMENDAÇÕES
        
        1. **Reserva emergencial mínima:** R$XXX,XXX (X meses de OPEX)
        2. **Ocupação target Mês 1-3:** XX% mínimo
        3. **Ocupação target Mês 4-6:** XX% para break-even
        4. **Backup FUNGETUR:** [Analisar se aplicável como contingência]
        5. **Conta PJ:** [Documentar processo de abertura]
        
        **FORMATO OBRIGATÓRIO:** Retorne SOMENTE o conteúdo estruturado acima com NÚMEROS REAIS.
        NÃO retorne "Thought:", "Action:", "Input:" ou formato de raciocínio.
        Faça os cálculos e preencha todos os valores marcados como R$XXX.
        """,
        agent=ricardo,
        context=[task1_proposta_valor, task2_mapa_competitivo, task3_calendario_eventos]
    )
    
    # TAREFA 5: Síntese e Próximos Passos (Helena) - FINAL
    task5_sintese_30dias = Task(
        description=f"""
        ## TAREFA: Síntese do Plano de 30 Dias
        
        **Objetivo:**
        Consolidar todos os outputs em uma apresentação executiva de 10 slides.
        
        **Inputs:**
        - Tese do Projeto (sua autoria)
        - Mapa Competitivo (Juliana)
        - Calendário e Sazonalidade (Marcelo)
        - Envelope Financeiro (Ricardo)
        
        **Estrutura da apresentação:**
        
        Slide 1: Executive Summary
        - Go/No-Go recomendação
        - 3 principais achados
        - 3 principais riscos
        
        Slides 2-3: Posicionamento Validado
        - Promessa central
        - 1-2 personas PRIMÁRIAS (ajustadas após dados de mercado)
        - Diferenciais competitivos
        
        Slide 4: Mercado Paraty
        - Top 5 concorrentes
        - Gaps de oportunidade
        - ADR validado (ajustado se necessário)
        
        Slide 5: Sazonalidade e Pricing
        - Calendário visual (alta/média/baixa)
        - Estratégia de tarifas por temporada
        
        Slides 6-7: Viabilidade Financeira
        - Budget alocado (pizza chart)
        - Cenário base: Ocupação/ADR/Break-even
        - ⚠️ Alerta: Viabilidade 6 meses
        
        Slide 8: Riscos e Mitigações
        - Top 5 riscos
        - Plano de mitigação para cada um
        
        Slide 9: Próximos Passos (Semana 5-8)
        - Pipeline ativo: Prospecção 10-15 imóveis
        - Visitas anônimas: 2-3 pousadas
        - NDA e scorecard prontos
        
        Slide 10: Decisão Requerida
        - Aprovar posicionamento?
        - Aprovar budget?
        - Iniciar prospecção ativa?
        
        **Prazo:** 2 dias (após receber todos os inputs)
        """,
        expected_output="""
        # PLANO 30 DIAS - EXECUTIVE SUMMARY
        
        ## SLIDE 1: EXECUTIVE SUMMARY
        
        ### Recomendação: [GO ✅ / NO-GO ❌ / AJUSTAR ⚠️]
        
        ### 3 Principais Achados:
        1. [Achado 1 - baseado em dados concretos]
        2. [Achado 2 - insight do mercado]
        3. [Achado 3 - oportunidade identificada]
        
        ### 3 Principais Riscos:
        1. [Risco 1 - com probabilidade e impacto]
        2. [Risco 2]
        3. [Risco 3]
        
        ---
        
        ## SLIDES 2-3: POSICIONAMENTO VALIDADO
        
        ### Promessa Central:
        "[Frase única que captura a essência - da Task 1]"
        
        ### Personas Primárias:
        1. **[Persona 1]**: [Por que escolhemos - dados de sazonalidade e mercado]
        2. **[Persona 2]**: [Complementaridade com Persona 1]
        
        ### Diferenciais Competitivos (Top 5):
        1. [Diferencial 1]
        2. [Diferencial 2]
        3. [Diferencial 3]
        4. [Diferencial 4]
        5. [Diferencial 5]
        
        ---
        
        ## SLIDE 4: MERCADO PARATY
        
        ### Top 5 Concorrentes:
        1. [Nome] - ADR R$XXX - Ocupação XX% - Nota X.X
        2. [Nome] - ADR R$XXX - Ocupação XX% - Nota X.X
        3. [Nome] - ADR R$XXX - Ocupação XX% - Nota X.X
        4. [Nome] - ADR R$XXX - Ocupação XX% - Nota X.X
        5. [Nome] - ADR R$XXX - Ocupação XX% - Nota X.X
        
        ### Gaps de Oportunidade:
        - [Gap 1]
        - [Gap 2]
        - [Gap 3]
        
        ### ADR Validado:
        - Alta temporada: R$XXX (ajustado de R$500)
        - Média temporada: R$XXX (ajustado de R$300)
        - Baixa temporada: R$XXX (ajustado de R$250)
        
        ---
        
        ## SLIDE 5: SAZONALIDADE E PRICING
        
        ### Calendário Visual:
        - **Alta:** Jan, Fev, Jul, Dez (ADR R$XXX)
        - **Média:** Abr, Jun, Set, Nov (ADR R$XXX)
        - **Baixa:** Mar, Mai, Ago, Out (ADR R$XXX)
        
        ### Eventos-Chave:
        - FLIP (Julho): ADR R$XXX, min-stay X noites
        - Carnaval (Fevereiro): ADR R$XXX, min-stay X noites
        - Réveillon (Dezembro): ADR R$XXX, min-stay X noites
        
        ---
        
        ## SLIDES 6-7: VIABILIDADE FINANCEIRA
        
        ### Budget Alocado (R$X.XM total):
        - Aquisição: XX%
        - CAPEX: XX%
        - Giro: XX%
        - Reserva: XX%
        
        ### Cenário Base:
        - Ocupação média: XX%
        - ADR médio: R$XXX
        - Receita mensal: R$XX,XXX
        - OPEX mensal: R$XX,XXX
        - **Break-even: Mês X**
        
        ### ⚠️ ALERTA VIABILIDADE 6 MESES:
        [Análise crítica: Possível? Margem de segurança? Runway?]
        
        ---
        
        ## SLIDE 8: RISCOS E MITIGAÇÕES
        
        ### Top 5 Riscos:
        1. **[Risco 1]**
           - Mitigação: [Plano específico]
        
        2. **[Risco 2]**
           - Mitigação: [Plano específico]
        
        3. **[Risco 3]**
           - Mitigação: [Plano específico]
        
        4. **[Risco 4]**
           - Mitigação: [Plano específico]
        
        5. **[Risco 5]**
           - Mitigação: [Plano específico]
        
        ---
        
        ## SLIDE 9: PRÓXIMOS PASSOS (SEMANAS 5-8)
        
        ### Pipeline Ativo:
        - Prospecção: 10-15 imóveis (praia + centro)
        - Critérios: [Lista específica baseada em posicionamento]
        
        ### Visitas Anônimas:
        - 2-3 pousadas concorrentes
        - Checklist de observação pronto
        
        ### Documentos Prontos:
        - ✅ NDA modelo
        - ✅ Scorecard de avaliação
        - ✅ Checklist due diligence
        
        ---
        
        ## SLIDE 10: DECISÃO REQUERIDA
        
        ### Pergunta 1: Aprovar posicionamento?
        [Sim / Não / Ajustar - com justificativa]
        
        ### Pergunta 2: Aprovar budget alocação?
        [Sim / Não / Ajustar - com justificativa]
        
        ### Pergunta 3: Iniciar prospecção ativa?
        [Sim / Não / Aguardar - com justificativa]
        
        ### Condições para Prosseguir:
        1. [Condição 1]
        2. [Condição 2]
        3. [Condição 3]
        
        ---
        
        ## PRÓXIMOS PASSOS
        
        1. Revisar recomendações de posicionamento
        2. Validar viabilidade financeira (break-even 6 meses)
        3. Decidir: Iniciar prospecção ativa?
        
        **FORMATO OBRIGATÓRIO:** Retorne SOMENTE o conteúdo estruturado acima, consolidando TODOS os outputs das tarefas anteriores.
        NÃO retorne "Thought:", "Action:", "Input:" ou formato de raciocínio.
        Este é o DOCUMENTO FINAL que será salvo em plano_30_dias_resultado.md.
        Preencha TODOS os [colchetes] com dados reais das tarefas anteriores.
        """,
        agent=helena,
        context=[task1_proposta_valor, task2_mapa_competitivo, task3_calendario_eventos, task4_envelope_financeiro]
    )
    
    # Criar crew
    crew = Crew(
        agents=[helena, ricardo, juliana, marcelo],
        tasks=[
            task1_proposta_valor,
            task2_mapa_competitivo,
            task3_calendario_eventos,
            task4_envelope_financeiro,
            task5_sintese_30dias
        ],
        verbose=True,
        process="sequential",  # Ordem: T1 → (T2 || T3) → T4 → T5
        max_rpm=None,  # Sem limite de requisições por minuto
        manager_llm=llm  # LLM para o manager (se necessário)
    )
    
    return crew
