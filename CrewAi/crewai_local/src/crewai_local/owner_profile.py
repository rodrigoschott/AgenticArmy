"""
Perfil do Proprietário - Integração com Agentes

Extrai dados do questionário de auto-avaliação do Obsidian
e fornece contexto estruturado para os agentes.
"""

from typing import Dict, Any


def get_owner_profile() -> Dict[str, Any]:
    """
    Retorna o perfil do proprietário baseado no questionário preenchido.
    
    Fonte: Obsidian/Estrategia/00-Questionario-Auto-Avaliacao.md
    Data: 2025-10-30
    """
    return {
        # PARTE 1: MOTIVAÇÃO E OBJETIVOS
        "motivacao_principal": "estilo_de_vida",  # B) Estilo de vida
        "envolvimento_operacional": "hands_on_total",  # A) 7 dias/semana
        "horizonte_tempo": "longo_prazo",  # C) 10+ anos
        "metricas_sucesso": [
            {"metrica": "reputacao_nps", "prioridade": 1, "meta": "4.8+"},
            {"metrica": "estilo_vida", "prioridade": 2, "meta": "tempo_livre_baixo_estresse"},
            {"metrica": "margem_operacional", "prioridade": 3, "meta": "25-35%"},
            {"metrica": "payback", "prioridade": 4, "meta": "5-7 anos"},
            {"metrica": "impacto_local", "prioridade": 5}
        ],
        
        # PARTE 2: PERFIL DE RISCO E RESTRIÇÕES
        "perfil_risco": "moderado",  # B) Aceita volatilidade com upside
        "capital_investido_pct": 90,  # D) >90% do capital
        "budget_total": {
            "min": 2_700_000,
            "max": 3_000_000,
            "moeda": "BRL"
        },
        "capex_flexivel": True,
        "capex_deal_breaker": 500_000,  # Máximo R$500k
        "financiamento": {
            "interesse_inicial": False,
            "opcoes_backup": ["FUNGETUR"],
            "uso": "melhorias_emergencias"
        },
        "fluxo_negativo_tolerancia": "6_meses",  # A) Precisa break-even rápido
        
        # DEAL BREAKERS (não negociáveis)
        "deal_breakers": [
            "problemas_estruturais_graves",
            "impossibilidade_licencas",
            "restricoes_iphan_severas",
            "avaliacoes_ruins_lt_3.5",
            "localizacao_ruim_longe_atrativos",
            "capex_gt_500k"
        ],
        
        # PARTE 3: PREFERÊNCIAS ESTRATÉGICAS
        "tamanho_pousada": {
            "preferencia": "flexivel",
            "faixa_aceitavel": (8, 18),  # 8-18 quartos
            "criterio": "oportunidade_e_localizacao"
        },
        "localizacao_preferencia": [
            {"zona": "praia_jabaquara_pontal", "rank": 1},
            {"zona": "centro_historico", "rank": 2},
            {"zona": "zona_intermediaria", "rank": 3},
            {"zona": "area_rural", "rank": 4}
        ],
        "hospedes_alvo": [
            {"persona": "turistas_culturais", "prioridade": 1, "descricao": "FLIP, história, arte"},
            {"persona": "familias_criancas", "prioridade": 2, "descricao": "educacional, praia"},
            {"persona": "turistas_natureza", "prioridade": 3, "descricao": "trilhas, cachoeiras, mergulho"},
            {"persona": "estrangeiros", "prioridade": 4, "descricao": "internacionalização"}
        ],
        "nivel_servico": "mid_premium",  # B) Charme sem ostentação, R$280-400
        "diferenciais_ideais": [
            {"diferencial": "servico_personalizado", "rank": 1},
            {"diferencial": "localizacao_privilegiada", "rank": 2},
            {"diferencial": "design_arquitetura", "rank": 3}
        ],
        
        # PARTE 4: EXPECTATIVAS FINANCEIRAS
        "adr_esperado": {
            "alta_temporada": 500,  # Dez-Mar, FLIP
            "media_temporada": 300,  # Abr-Jun, Ago-Out
            "baixa_temporada": 250,  # Mai, Nov
            "status_validacao": "aguarda_validacao_mercado"
        },
        "ocupacao_ano1": {
            "estimativa": None,
            "status": "precisa_dados_mercado"
        },
        
        # PARTE 5: EXPERIÊNCIA E CONHECIMENTO
        "experiencia_hospitalidade": "nenhuma",
        "conhecimento_paraty": {
            "nivel": "residente",
            "vantagem": "conhecimento_local_profundo_network",
            "hospedagens_locais": False  # Nunca se hospedou em pousadas de Paraty
        },
        "preocupacoes_declaradas": [
            "pesquisa_mercado",
            "licencas_documentacoes_impostos",
            "planejamento_staff",
            "busca_diferenciais"
        ],
        
        # PARTE 6: DECISÕES CONTINGENTES
        "flexibilidade": {
            "ajuste_posicionamento": "negocia_meio_termo",  # D) Equilíbrio ideal/viável
            "aceita_fora_centro": True,  # Desde que localização seja boa
            "criterio_trade_off": "preco_potencial_capex"
        },
        
        # TENSÕES A RESOLVER (para orientar agentes)
        "tensoes_estrategicas": [
            {
                "tensao": "estilo_vida_vs_break_even",
                "descricao": "Quer qualidade de vida mas precisa break-even em 6 meses",
                "resolucao_sugerida": "operacao_eficiente_com_delegacao_gradual"
            },
            {
                "tensao": "servico_personalizado_vs_sem_experiencia",
                "descricao": "Diferencial em serviço mas zero experiência em hospitalidade",
                "resolucao_sugerida": "sops_detalhados_treinamento_intensivo_consultor"
            },
            {
                "tensao": "multiplos_publicos",
                "descricao": "4 personas diferentes pode diluir posicionamento",
                "resolucao_sugerida": "helena_deve_focar_1_2_personas_primarias"
            },
            {
                "tensao": "adr_alto_vs_mid_premium",
                "descricao": "R$500 alta temporada vs posicionamento mid-premium típico R$280-400",
                "resolucao_sugerida": "juliana_validar_mercado_suporta"
            },
            {
                "tensao": "investimento_concentrado",
                "descricao": ">90% capital + break-even 6 meses = pouca margem erro",
                "resolucao_sugerida": "ricardo_stress_test_viabilidade"
            }
        ],
        
        # VANTAGENS COMPETITIVAS NATURAIS
        "vantagens_naturais": [
            "mora_em_paraty_conhecimento_local",
            "comprometimento_total_hands_on_7_dias",
            "foco_qualidade_reputacao_sobre_retorno_rapido",
            "budget_adequado_2.7_3.0M",
            "flexibilidade_ajusta_dados_mercado"
        ]
    }


def get_owner_context_for_agent(agent_role: str) -> str:
    """
    Retorna contexto relevante do proprietário para um agente específico.
    
    Args:
        agent_role: Nome do agente (ex: 'Helena', 'Juliana', 'Ricardo')
    
    Returns:
        String formatada com contexto relevante para injetar no prompt
    """
    profile = get_owner_profile()
    
    contexts = {
        "Helena": f"""
CONTEXTO DO PROPRIETÁRIO (uso exclusivo para estratégia):

**Motivação:** Estilo de vida (não investimento puro)
**Prioridades:** 1) Reputação (NPS 4.8+), 2) Qualidade de vida, 3) Margem 25-35%
**Horizonte:** Longo prazo (10+ anos), operação hands-on (7 dias/semana)
**Experiência:** Nenhuma em hospitalidade, mas RESIDE EM PARATY (vantagem competitiva)

**Preferências:**
- Localização: 1º Praia (Jabaquara/Pontal), 2º Centro Histórico
- Tamanho: Flexível (8-18 quartos)
- Nível: Mid-premium (charme sem ostentação)
- Diferenciais: 1) Serviço personalizado, 2) Localização privilegiada, 3) Design

**Públicos-alvo declarados:** Culturais, Famílias, Natureza, Estrangeiros
⚠️ TENSÃO: 4 personas podem diluir posicionamento - RECOMENDE FOCAR EM 1-2 PRIMÁRIAS

**Restrições críticas:**
- Budget: R$2.7M-3.0M (>90% do capital investido)
- Tolerância fluxo negativo: 6 meses (break-even rápido obrigatório)
- CAPEX deal breaker: >R$500k

**Deal breakers:** Estrutura grave, sem licenças, IPHAN severo, reviews <3.5, longe de atrativos

**SUA MISSÃO:** Criar posicionamento que equilibre estilo de vida COM viabilidade financeira em 6 meses.
""",
        
        "Juliana": f"""
CONTEXTO DO PROPRIETÁRIO (análise de mercado):

**Expectativas ADR:**
- Alta temporada (Dez-Mar, FLIP): R$500/noite
- Média temporada: R$300/noite
- Baixa temporada: R$250/noite
⚠️ VALIDAR: R$500 é viável para mid-premium em Paraty? Típico é R$280-400.

**Posicionamento declarado:** Mid-premium (charme sem ostentação)
**Localização preferida:** 1º Praia (Jabaquara/Pontal), 2º Centro Histórico

**Públicos-alvo:** Culturais (FLIP), Famílias, Natureza, Estrangeiros
⚠️ ANALISAR: Esses 4 perfis frequentam as mesmas pousadas? Ou são segmentos distintos?

**Restrições financeiras:**
- Precisa break-even em 6 meses (fluxo negativo máximo)
- >90% do capital investido (pouca margem de erro)
- Budget total: R$2.7M-3.0M

**SUA MISSÃO:** 
1. Validar se ADR R$500 (alta) é realista para mid-premium
2. Mapear concorrentes na faixa R$280-400 (praia vs centro)
3. Recomendar mix de públicos que maximize ocupação SEM diluir posicionamento
4. Identificar gaps de mercado para break-even rápido
""",
        
        "Ricardo": f"""
CONTEXTO DO PROPRIETÁRIO (análise financeira):

**Situação financeira:**
- Budget total: R$2.7M - R$3.0M
- Investimento: >90% do capital (⚠️ ALTO RISCO - concentração extrema)
- CAPEX: Flexível, mas deal breaker se >R$500k
- Financiamento: Não inicialmente, mas aberto a FUNGETUR para emergências

**Restrições operacionais:**
- Tolerância fluxo negativo: 6 meses (break-even obrigatório)
- Experiência hospitalidade: ZERO (curva de aprendizado)
- Operação: Hands-on 7 dias/semana (proprietário residente)

**Expectativas ADR:**
- Alta: R$500, Média: R$300, Baixa: R$250
⚠️ VALIDAR: Viável para mid-premium com break-even 6 meses?

**Prioridades:**
1. Reputação (NPS 4.8+) - investe em qualidade
2. Qualidade de vida (baixo estresse)
3. Margem operacional 25-35%
4. Payback 5-7 anos (não é prioridade máxima)

**SUAS ANÁLISES OBRIGATÓRIAS:**
1. Stress test: Operação com 90%+ do capital + 6 meses break-even
2. Cenários conservador/base/otimista com ocupação/ADR real
3. CAPEX máximo viável sem comprometer fluxo 6 meses
4. Runway: Reserva emergencial mínima recomendada
5. Break-even real: Quantos quartos/ocupação/ADR para atingir em 6 meses
""",
        
        "Marcelo": f"""
CONTEXTO DO PROPRIETÁRIO (especialista Paraty):

**Vantagem competitiva:** RESIDE EM PARATY
- Conhecimento local profundo
- Network já estabelecido
- Familiaridade com sazonalidade, eventos, comunidade

**Públicos-alvo declarados:**
1. Turistas culturais (FLIP, história, arte)
2. Famílias com crianças (educacional, praia)
3. Turistas de natureza (trilhas, cachoeiras, mergulho)
4. Estrangeiros (internacionalização)

⚠️ VALIDAR: Esses 4 perfis têm interseção? Ou são segmentos distintos com necessidades conflitantes?

**Preferências localização:**
1º Praia (Jabaquara, Pontal)
2º Centro Histórico

**Diferencial desejado:** Serviço personalizado + Localização privilegiada

**SUA MISSÃO:**
1. Perfil detalhado de cada um dos 4 públicos em Paraty
2. Validar se esses públicos frequentam as mesmas pousadas ou não
3. Impacto de estar na praia vs centro histórico para cada persona
4. Recomendar 1-2 personas PRIMÁRIAS para foco (evitar diluição)
5. Rede de parceiros confiáveis para proprietário iniciante (curva aprendizado)
6. Experiências locais que atendem múltiplos perfis simultaneamente
""",
        
        "Gabriel": f"""
CONTEXTO DO PROPRIETÁRIO (crítica e stress test):

**Tensões identificadas para você questionar:**

1. **Estilo de vida vs Break-even rápido**
   - Quer: Qualidade de vida, tempo livre, baixo estresse
   - Mas: Precisa break-even em 6 meses
   - Pergunta: Como conciliar? É realista?

2. **Serviço personalizado vs Sem experiência**
   - Quer: Diferencial em serviço excepcional
   - Mas: Zero experiência em hospitalidade
   - Pergunta: Como entregar excelência sem experiência?

3. **Múltiplos públicos-alvo**
   - Quer: Atender culturais + famílias + natureza + estrangeiros
   - Risco: Diluição de posicionamento, operação complexa
   - Pergunta: É possível agradar todos? Qual o custo?

4. **ADR alto vs Mid-premium**
   - Quer: R$500 em alta temporada
   - Mas: Posicionamento "mid-premium" típico R$280-400
   - Pergunta: Mercado suporta? Ou expectativa inflada?

5. **Investimento concentrado vs Fluxo rápido**
   - Risco: >90% do capital + break-even 6 meses
   - Pergunta: E se não der certo? Margem de erro quase zero

**SUA MISSÃO:**
1. Desafiar TODAS as premissas dos outros agentes
2. Identificar riscos ocultos (o que pode dar errado?)
3. Questionar viabilidade do break-even em 6 meses
4. Provocar: "E se...?" para cada recomendação
5. Forçar escolhas difíceis (trade-offs)
"""
    }
    
    return contexts.get(agent_role, f"Perfil do proprietário: {profile}")


def get_deal_breakers() -> list:
    """Retorna lista de deal breakers não negociáveis."""
    return get_owner_profile()["deal_breakers"]


def get_budget_range() -> tuple:
    """Retorna faixa de budget (min, max)."""
    budget = get_owner_profile()["budget_total"]
    return (budget["min"], budget["max"])


def get_adr_expectations() -> dict:
    """Retorna expectativas de ADR por temporada."""
    return get_owner_profile()["adr_esperado"]


if __name__ == "__main__":
    # Teste: Imprimir contexto para Helena
    print("=" * 80)
    print("CONTEXTO PARA HELENA (ESTRATÉGIA)")
    print("=" * 80)
    print(get_owner_context_for_agent("Helena"))
    
    print("\n" + "=" * 80)
    print("DEAL BREAKERS")
    print("=" * 80)
    for db in get_deal_breakers():
        print(f"  ❌ {db}")
