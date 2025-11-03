"""
Workflow A: Avaliar Propriedade Específica (AUTONOMOUS RESEARCH MODE)

Crew para avaliar uma propriedade específica e tomar decisão go/no-go.

NOVO: Modo de pesquisa autônoma - requer apenas nome OU link da propriedade.
Os agentes pesquisam e coletam automaticamente todos os dados necessários.

Agentes: Juliana (research), Marcelo, André, Fernando, Ricardo, Gabriel (6 agentes)
"""

from crewai import Crew, Process, Task
from ..agents.mercado import create_juliana_campos, create_marcelo_ribeiro
from ..agents.tecnico import create_andre_martins
from ..agents.juridico import create_fernando_costa
from ..agents.estrategia import create_ricardo_tavares
from ..agents.qualidade import create_gabriel_motta


def create_property_evaluation_crew(llm, property_data: dict) -> Crew:
    """
    Cria uma crew para avaliar uma propriedade específica (MODO AUTÔNOMO).

    NOVO: Agentes pesquisam automaticamente todos os dados necessários.

    Args:
        llm: Modelo de linguagem a ser usado pelos agentes
        property_data: Dict com informações mínimas da propriedade
            - property_name: Nome da propriedade (opcional se property_link fornecido)
            - property_link: Link da propriedade (opcional se property_name fornecido)
            - location_hint: Dica de localização (opcional)

    Returns:
        Crew configurada para avaliação autônoma
    """

    # Criar agentes
    juliana = create_juliana_campos(llm)  # NOVO: Research agent
    marcelo = create_marcelo_ribeiro(llm)
    andre = create_andre_martins(llm)
    fernando = create_fernando_costa(llm)
    ricardo = create_ricardo_tavares(llm)
    gabriel = create_gabriel_motta(llm)

    # Preparar dados de pesquisa
    property_identifier = property_data.get('property_link') or property_data.get('property_name', 'Propriedade')
    location_hint = property_data.get('location_hint', 'Paraty - RJ')

    # Task 0: RESEARCH - Coleta Autônoma de Dados da Propriedade
    task_research = Task(
        description=f"""MISSÃO CRÍTICA: Pesquise e colete TODOS os dados necessários sobre a propriedade para análise completa.

**ENTRADA FORNECIDA:**
- Identificador: {property_identifier}
- Dica de localização: {location_hint}

**ESTRATÉGIA DE PESQUISA (ANTI-BLOQUEIO COM PLAYWRIGHT):**

1. **Se um LINK foi fornecido** (Airbnb, Booking, OLX, imobiliária):

   **PASSO 1 - Tentativa Primária (fetch_url):**
   - Use: fetch_url(url)
   - Se retornar conteúdo válido: ÓTIMO! Extraia os dados e pule para análise de mercado
   - Se retornar erro (403, robots.txt): NORMAL! Vá IMEDIATAMENTE para PASSO 2

   **PASSO 2 - Playwright Fallback (PRIORIDADE ABSOLUTA):**
   - Se fetch falhou, use IMEDIATAMENTE: fetch_with_playwright_fallback(url)
   - Esta ferramenta tenta fetch primeiro, se falhar usa browser automático (Playwright)
   - Playwright renderiza JavaScript e bypassa maioria dos bloqueios
   - Mais lento (60s vs 30s) mas MUITO mais eficaz
   - Se retornar conteúdo: SUCESSO! Extraia dados e continue

   **PASSO 3 - Busca com Nome Específico (ÚLTIMO RECURSO):**
   - Use search_web APENAS se:
     * PASSO 1 (fetch) falhou E
     * PASSO 2 (Playwright) falhou E
     * Você conseguiu extrair o NOME da propriedade da URL
   - Se essas condições forem atendidas:
     * search_web("[nome_propriedade_específico] paraty")
     * Exemplo: "Pousada do Sandi Paraty preço" (com nome específico)
     * NÃO faça buscas genéricas como "pousada paraty venda"

   **PASSO 4 - Análise de Mercado (SEMPRE EXECUTAR):**
   - Independente do resultado acima, SEMPRE faça:
     * airbnb_search(location="Paraty - RJ", adults=2)
     * Objetivo: Benchmarks de ADR e ocupação regionais
     * Isto NÃO substitui o link direto, apenas complementa

   **PASSO 5 - Compilação e Estimativa:**
   - Compile TODOS os dados obtidos
   - Se preço não encontrado: estime baseado em comparáveis (R$/quarto)
   - Se quartos não encontrados: estime pelo tamanho típico regional
   - DOCUMENTE: "Dado via [fonte]" ou "Estimado via [método]"

2. **Se apenas NOME foi fornecido:**
   - PASSO 1: search_web("[nome_específico] paraty pousada")
     * Com o NOME específico fornecido pelo usuário
     * Objetivo: Encontrar link da propriedade
   - PASSO 2: Se encontrar link, use fetch_with_playwright_fallback(link)
   - PASSO 3: airbnb_search para benchmarks regionais
   - PASSO 4: Compilação e estimativa

3. **MENTALIDADE CRÍTICA - PRIORIDADE DE FERRAMENTAS:**
   - Link direto > busca genérica (SEMPRE)
   - Playwright > search_web (quando link está bloqueado)
   - fetch_with_playwright_fallback é sua MELHOR ferramenta para links
   - search_web é APENAS para nome específico em ÚLTIMO RECURSO
   - NÃO use search_web para "substituir" consulta de link direto
   - Benchmarks de mercado (airbnb_search) são COMPLEMENTO, não substituição

4. **REGRAS ABSOLUTAS:**
   - ✅ fetch_url → fetch_with_playwright_fallback → (se tiver nome) search_web
   - ❌ NUNCA pule Playwright para ir direto ao search_web
   - ❌ NUNCA faça buscas genéricas sem nome específico
   - ✅ Sempre documente: "Obtido via Playwright" ou "Estimado por comparáveis"
   - ✅ airbnb_search é para BENCHMARKS, execute sempre ao final

3. **DADOS OBRIGATÓRIOS A COLETAR:**

   a) **Identificação:**
      - Nome completo da propriedade
      - Endereço exato (rua, bairro, cidade)
      - Coordenadas/localização precisa

   b) **Características Físicas:**
      - Número de quartos/UHs
      - Área construída (m²)
      - Área do terreno (m²)
      - Estado de conservação (Excelente/Bom/Regular/Ruim)

   c) **Financeiro:**
      - Preço de venda/compra (R$)
      - Se não disponível: estime baseado em comparáveis da região

   d) **Mercado & Competição:**
      - Use airbnb_search para encontrar 5-10 pousadas similares na região
      - Colete ADR médio dos concorrentes (diária média)
      - Colete taxa de ocupação estimada do mercado
      - Identifique padrão de preços (alta/média/baixa temporada)

   e) **Condição & CAPEX:**
      - Avalie estado geral pelas fotos/descrição
      - Estime CAPEX necessário:
         * Excelente: 5-10% do valor
         * Bom: 15-20% do valor
         * Regular: 25-35% do valor
         * Ruim: 40-60% do valor

**FORMATO DE SAÍDA OBRIGATÓRIO (Markdown estruturado):**

## 1. IDENTIFICAÇÃO DA PROPRIEDADE
- Nome: [nome completo]
- Endereço: [endereço completo]
- Localização: [bairro/região]
- Link de referência: [se disponível]

## 2. CARACTERÍSTICAS FÍSICAS
- Quartos/UHs: [número]
- Área construída: [m² ou "não informado"]
- Área terreno: [m² ou "não informado"]
- Estado conservação: [Excelente/Bom/Regular/Ruim]

## 3. DADOS FINANCEIROS
- Preço venda/compra: R$ [valor]
- Fonte do preço: [listing/estimativa/comparáveis]
- CAPEX estimado: R$ [valor] ([%] do preço)
- Justificativa CAPEX: [baseado em estado + necessidades]

## 4. ANÁLISE DE MERCADO
### Concorrentes Analisados:
1. [Nome] - R$ [ADR] - [localização]
2. [Nome] - R$ [ADR] - [localização]
3. [Nome] - R$ [ADR] - [localização]
...

### Benchmarks de Mercado:
- ADR médio região: R$ [valor]
- ADR target recomendado: R$ [valor]
- Ocupação média mercado: [%]
- Ocupação target recomendada: [%]
- Sazonalidade: [alta/média/baixa + meses]

## 5. FONTES & CONFIABILIDADE
- Dados diretos: [lista de URLs usadas]
- Dados estimados: [lista do que foi estimado + método]
- Confiabilidade geral: [Alta/Média/Baixa]

**IMPORTANTE - RESILIÊNCIA E QUALIDADE:**
- Use TODAS as ferramentas disponíveis (search_web, fetch_url, airbnb_search)
- Se fetch_url falhar (robots.txt), use search_web como alternativa
- Se um dado não for encontrado diretamente, ESTIME baseado em comparáveis
- NUNCA deixe campos em branco - sempre forneça estimativa justificada
- Seja data-driven: cite fontes e links sempre que possível
- Documente claramente quando usar fontes alternativas ou estimativas""",

        expected_output="""Relatório estruturado em markdown com TODOS os dados coletados:
- Identificação completa da propriedade
- Características físicas detalhadas
- Preço de venda/compra (real ou estimado)
- CAPEX estimado com justificativa
- Análise de 5-10 concorrentes com ADR
- Benchmarks de mercado (ADR target, ocupação target)
- Lista de fontes e nível de confiabilidade dos dados
- Indicação de quais dados foram estimados (se aplicável)

CRITICAL: Este relatório será usado por todos os agentes seguintes. Dados faltantes inviabilizam a análise.
RESILIENCE: Se ferramentas falharem, use alternativas. Relatório completo com estimativas > dados faltantes.""",

        agent=juliana
    )

    # Task 1: Contexto Local + Experiências
    task_context = Task(
        description="""Com base nos DADOS PESQUISADOS da propriedade, forneça contexto completo sobre a localização em Paraty:

        **USE OS DADOS DO RELATÓRIO DE PESQUISA** (Task anterior) para:
        - Nome e localização exata da propriedade
        - Número de quartos (para dimensionar experiências)

        1. **Contexto Local:**
           - História e características do bairro/região específica
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
           - Regulações municipais específicas""",

        expected_output="""Relatório estruturado em markdown com:
        - Análise do contexto local específico da propriedade
        - Calendário anual de eventos com impacto em ocupação
        - Portfolio de 10-15 experiências autênticas com custos
        - Rede de parceiros locais recomendados
        - Restrições regulatórias a considerar""",

        agent=marcelo,
        context=[task_research]  # NOVO: Depende da pesquisa
    )
    
    # Task 2: Inspeção Técnica + CAPEX
    task_technical = Task(
        description="""Com base nos DADOS PESQUISADOS, realize avaliação técnica e refine estimativa de CAPEX:

        **USE OS DADOS DO RELATÓRIO DE PESQUISA:**
        - Nome e características da propriedade
        - Estado de conservação identificado (Excelente/Bom/Regular/Ruim)
        - CAPEX estimado inicial (refinar e detalhar)
        - Área construída e número de quartos

        1. **Inspeção Predial (baseada em dados disponíveis):**
           - Estrutura (fundações, paredes, lajes)
           - Sistemas hidráulicos (tubulação, reservatórios, esgoto)
           - Sistemas elétricos (fiação, quadros, aterramento)
           - Telhado (estrutura, telhas, calhas)
           - Acabamentos e conservação geral
           - Umidade, infiltrações, cupins

        2. **Estimativa DETALHADA de CAPEX:**
           - Parta do CAPEX estimado na pesquisa
           - Detalhe por categoria:
             * Reformas críticas (🔴 urgentes)
             * Reformas importantes (🟡 necessárias)
             * Melhorias desejáveis (🟢 diferenciais)
           - Contingência de 15-20% para surpresas
           - Total por ambiente/sistema

        3. **Considerações IPHAN:**
           - Restrições para fachada, janelas, cores
           - Aprovações necessárias
           - Limitações arquitetônicas

        4. **Timeline de Obras:**
           - Cronograma estimado por fase
           - Dependências críticas
           - Período mínimo realista""",

        expected_output="""Laudo técnico estruturado com:
        - Avaliação completa por sistema (estrutura, hidráulica, elétrica, telhado)
        - CAPEX DETALHADO por prioridade (crítico/importante/desejável)
        - Contingência de 15-20%
        - Restrições IPHAN aplicáveis
        - Cronograma de obras com timeline realista
        - Total de CAPEX consolidado e refinado""",

        agent=andre,
        context=[task_research]  # NOVO: Depende da pesquisa
    )
    
    # Task 3: Due Diligence Jurídica
    task_legal = Task(
        description="""Com base nos DADOS PESQUISADOS, conduza due diligence jurídica completa:

        **USE OS DADOS DO RELATÓRIO DE PESQUISA:**
        - Nome completo e endereço da propriedade
        - Preço de compra/venda
        - Localização específica (para verificar zoneamento)

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
        🟢 Acceptable - Situação regular""",

        expected_output="""Parecer jurídico estruturado com:
        - Checklist de due diligence com status de cada item
        - Red flags identificados (com sistema de cores)
        - Certidões necessárias e como obtê-las
        - Análise de zoneamento e restrições
        - Recomendação de estrutura de aquisição
        - Minutas de cláusulas contratuais protetivas
        - Conclusão: GO / NO-GO / GO COM RESSALVAS""",

        agent=fernando,
        context=[task_research]  # NOVO: Depende da pesquisa
    )
    
    # Task 4: Valuation e Modelagem Financeira
    task_financial = Task(
        description="""Com base nos DADOS PESQUISADOS e análises anteriores, realize valuation completo:

        **USE OS DADOS DO RELATÓRIO DE PESQUISA:**
        - Preço de compra/venda da propriedade
        - Número de quartos
        - ADR target recomendado (da análise de mercado)
        - Ocupação target recomendada (da análise de mercado)

        **USE OS DADOS DA ANÁLISE TÉCNICA:**
        - CAPEX refinado e detalhado do Eng. André

        1. **Inputs do Modelo:**
           - Preço de compra: [do relatório de pesquisa]
           - CAPEX: [do laudo técnico]
           - Quartos: [do relatório de pesquisa]
           - ADR target: [do benchmark de mercado]
           - Ocupação target: [do benchmark de mercado]

        2. **Projeção de Receitas (5 anos):**
           - Revenue por quarto por mês
           - Sazonalidade (alta/média/baixa)
           - Growth rate anual (0-5%)

        3. **Projeção de Custos:**
           - OPEX (operação): ~40-50% da receita
           - Staffing (usar guidelines padrão)
           - Manutenção, utilities, marketing
           - Impostos (Simples Nacional ~6-11%)

        4. **Três Cenários:**
           - 🔴 Conservador: ocupação -20%, ADR -10%
           - 🟡 Base: projeções do mercado
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
        context=[task_research, task_technical]  # NOVO: Depende de research + CAPEX
    )
    
    # Task 5: Stress Test e Devil's Advocate
    task_devil = Task(
        description="""Com base em TODAS as análises anteriores, desafie premissas e stress-teste a decisão:

        **USE OS DADOS DE TODAS AS ANÁLISES:**
        - Dados da propriedade (pesquisa)
        - Contexto local e experiências (Marcelo)
        - CAPEX e timeline de obras (André)
        - Due diligence jurídica (Fernando)
        - Modelo financeiro e valuation (Ricardo)

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

        Seja impiedosamente cético, mas construtivo.""",

        expected_output="""Relatório crítico estruturado com:
        - Lista de pressupostos questionáveis
        - 5-10 cenários adversos detalhados
        - Pre-mortem: 10 causas possíveis de fracasso
        - Perguntas desconfortáveis que precisam ser respondidas
        - Risk matrix completa (probabilidade × impacto)
        - Top 5 riscos críticos com sugestões de mitigação
        - Conclusão: Esta compra é robusta o suficiente para seguir?""",

        agent=gabriel,
        context=[task_research, task_context, task_technical, task_legal, task_financial]  # NOVO: Inclui research
    )
    
    # Criar Crew (ATUALIZADO: 6 agentes, 6 tasks)
    crew = Crew(
        agents=[juliana, marcelo, andre, fernando, ricardo, gabriel],  # NOVO: Juliana adicionada
        tasks=[task_research, task_context, task_technical, task_legal, task_financial, task_devil],  # NOVO: task_research primeiro
        process=Process.sequential,
        verbose=True
    )

    return crew
