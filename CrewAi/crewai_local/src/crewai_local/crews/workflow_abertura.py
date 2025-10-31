"""
Workflow C: Preparação para Abertura

Crew para preparar a pousada para soft opening com conformidade total.
Agentes: Paula, Patrícia, Sofia, Renata (4 agentes)
"""

from crewai import Crew, Process, Task
from ..agents.tecnico import create_paula_andrade, create_sofia_duarte
from ..agents.juridico import create_patricia_lemos
from ..agents.qualidade import create_renata_silva


def create_opening_prep_crew(llm, opening_data: dict = None) -> Crew:
    """
    Cria uma crew para preparar a abertura da pousada.
    
    Args:
        llm: Modelo de linguagem a ser usado pelos agentes
        opening_data: Dict opcional com dados da abertura
    
    Returns:
        Crew configurada para preparação de abertura
    """
    
    if opening_data is None:
        opening_data = {
            'opening_date': '2026-06-01',
            'rooms': 12,
            'staff_size': 8
        }
    
    # Criar agentes
    paula = create_paula_andrade(llm)
    patricia = create_patricia_lemos(llm)
    sofia = create_sofia_duarte(llm)
    renata = create_renata_silva(llm)
    
    # Task 1: SOPs Completos
    task_operations = Task(
        description=f"""Desenvolva SOPs (Standard Operating Procedures) completos:
        
        1. **SOPs de Operação:**
           - Check-in (welcome drink, tour, explicações)
           - Housekeeping (limpeza diária, troca de roupa, amenities)
           - Café da manhã (montagem, reposição, timing)
           - Atendimento ao hóspede (<5min response time)
           - Check-out (despedida, feedback, follow-up)
           - Emergências (médicas, segurança, mau tempo)
        
        2. **Organograma e Staffing:**
           - Estrutura organizacional
           - Descrição de cargos e responsabilidades
           - Escalas de trabalho (turnos, folgas)
           - Sizing: {opening_data['rooms']} quartos = quantos funcionários?
        
        3. **Tech Stack:**
           - PMS (Property Management System) recomendado
           - Channel Manager (integração OTAs)
           - Booking Engine (reservas diretas)
           - WhatsApp Business
           - Sistemas de pagamento
        
        4. **Checklists Operacionais:**
           - Daily checklist (recepção, housekeeping, cozinha)
           - Weekly checklist (manutenção, estoques)
           - Monthly checklist (auditoria, treinamento)
        
        5. **Políticas de Atendimento:**
           - Tempos de resposta
           - Padrões de qualidade
           - Tratamento de reclamações
        
        Data de abertura: {opening_data['opening_date']}
        Quartos: {opening_data['rooms']}""",
        
        expected_output="""Manual operacional completo contendo:
        - SOPs detalhados para todas as operações
        - Organograma com descrições de cargos
        - Staffing sizing e escalas
        - Tech stack recomendado com custos
        - Checklists diários/semanais/mensais
        - Políticas de atendimento e qualidade
        - Timeline de treinamento pré-abertura""",
        
        agent=paula
    )
    
    # Task 2: Roadmap de Licenciamento + Compliance Trabalhista
    task_compliance = Task(
        description=f"""Crie roadmap completo de licenciamento e compliance trabalhista:
        
        1. **Roadmap de Licenças:**
           - AVCB (Bombeiros): prazos, requisitos, custos
           - Licença Sanitária: documentos, vistoria, aprovação
           - Alvará de Funcionamento: dependências, timeline
           - Cadastur (MTur): processo online, documentos
           - Cronograma integrado com dependências
        
        2. **Contatos Estratégicos:**
           - Prefeitura de Paraty (responsável, telefone)
           - Corpo de Bombeiros RJ
           - Vigilância Sanitária
           - IPHAN (se aplicável)
        
        3. **Compliance Trabalhista:**
           - Modelos de contratos CLT por cargo
           - Cálculo de custo total por função (1.7x salário)
           - eSocial: eventos obrigatórios e prazos
           - FGTS, INSS: cronograma de recolhimentos
           - Convenção coletiva: sindicato dos hotéis RJ
        
        4. **Obrigações Mensais:**
           - eSocial (até dia 15)
           - FGTS (até dia 7)
           - INSS (até dia 20)
           - Folha de pagamento (5º dia útil)
        
        5. **Documentos Obrigatórios:**
           - PGR (Programa de Gerenciamento de Riscos)
           - PCMSO (Controle Médico de Saúde Ocupacional)
           - Registros de ponto
        
        Staff planejado: {opening_data.get('staff_size', 8)} funcionários
        Abertura: {opening_data['opening_date']}""",
        
        expected_output="""Roadmap de compliance contendo:
        - Cronograma de licenciamento (Gantt chart em markdown)
        - Checklist de documentos por licença
        - Contatos de órgãos fiscalizadores
        - Modelos de contratos CLT
        - Cálculo de custo total por cargo
        - Calendário de obrigações trabalhistas mensais
        - Documentos obrigatórios (PGR, PCMSO)
        - Timeline crítico até a abertura""",
        
        agent=patricia
    )
    
    # Task 3: Walkthrough de Design e Ambientação
    task_design = Task(
        description=f"""Realize walkthrough final de design e ambientação:
        
        1. **Guest Journey Mapping:**
           - Arrival (primeira impressão, estacionamento)
           - Check-in (lobby, conforto)
           - Circulação (wayfinding, fluxos)
           - Quarto (layout, conforto, funcionalidade)
           - Áreas comuns (sala, piscina, jardim)
           - Café da manhã (ambiente, vista)
           - Check-out (despedida memorável)
        
        2. **Checklist de Design:**
           - Iluminação (natural e artificial)
           - Ventilação e climatização
           - Sinalização e wayfinding
           - Acessibilidade (NBR 9050)
           - Materiais locais (autenticidade)
           - Pontos instagramáveis
        
        3. **Ambientação:**
           - Mobiliário (especificação, fornecedores)
           - Decoração (arte local, plantas, texturas)
           - Amenities (roupa de cama, toalhas, sabonetes)
           - Música ambiente
           - Aromas característicos
        
        4. **Ajustes Finais:**
           - Lista de melhorias pré-abertura
           - Priorização (crítico/importante/desejável)
           - Orçamento de ajustes finais
        
        Quartos: {opening_data['rooms']}
        Abertura: {opening_data['opening_date']}""",
        
        expected_output="""Relatório de design final contendo:
        - Guest journey completo com pontos de atenção
        - Checklist de design por ambiente
        - Especificação de ambientação (mobília, decoração, amenities)
        - Lista de ajustes finais priorizados
        - Orçamento de melhorias pré-abertura
        - Recomendações de pontos instagramáveis
        - Timeline de implementação""",
        
        agent=sofia
    )
    
    # Task 4: Auditoria Completa (Experiência + Processos)
    task_audit = Task(
        description=f"""Realize auditoria completa de experiência e processos:
        
        1. **Mystery Guest Simulation:**
           - Simule a jornada completa do hóspede
           - Avalie cada touchpoint (1-10)
           - Identifique gaps de qualidade
           - Compare com padrões internacionais
        
        2. **Auditoria de Processos:**
           - Mapeie todos os processos operacionais
           - Identifique gargalos e ineficiências
           - Calcule tempos (check-in, housekeeping, atendimento)
           - Analise produtividade da equipe
        
        3. **Benchmarking:**
           - Compare com Michelin, Forbes, Relais & Châteaux
           - Onde estamos vs onde precisamos estar?
           - Gaps críticos a endereçar
        
        4. **Plano de Melhoria:**
           - 🟢 Quick wins (alto impacto, baixo esforço)
           - 🟡 Estratégico (alto impacto, alto esforço)
           - 🔵 Fill-ins (baixo impacto, baixo esforço)
           - Priorização por impacto na experiência
        
        5. **KPIs de Performance:**
           - Tempo de check-in (meta: <5min)
           - Response time (meta: <10min)
           - NPS esperado
           - Taxa de retorno projetada
        
        Abertura em: {opening_data['opening_date']}
        Padrão objetivo: 4.8+ rating""",
        
        expected_output="""Relatório de auditoria contendo:
        - Mystery guest report completo (nota por touchpoint)
        - Mapeamento de processos (fluxogramas)
        - Identificação de gargalos e ineficiências
        - Comparação com benchmarks internacionais
        - Plano de melhoria priorizado (quick wins + estratégico)
        - KPIs de performance com metas
        - Checklist final pré-abertura
        - Recomendação: PRONTO PARA ABRIR? (sim/não/com ressalvas)""",
        
        agent=renata,
        context=[task_operations, task_compliance, task_design]
    )
    
    # Criar Crew
    crew = Crew(
        agents=[paula, patricia, sofia, renata],
        tasks=[task_operations, task_compliance, task_design, task_audit],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
