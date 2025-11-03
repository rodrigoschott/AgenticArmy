"""
Sistema de Crews para o Projeto Paraty

Integra os 11 agentes consolidados (v2.0) em 3 workflows principais.
"""

import os
import json
from typing import Dict, Any
from itertools import cycle
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from crewai import LLM as CrewLLM
from dotenv import load_dotenv

from .crews.workflow_avaliacao import create_property_evaluation_crew
from .crews.workflow_posicionamento import create_positioning_crew
from .crews.workflow_abertura import create_opening_prep_crew
from .crews.workflow_planejamento_30dias import create_planning_30days_crew
from .crews.workflow_prospeccao import create_prospecting_crew
from .crews.workflow_screening import create_screening_crew
from .owner_profile import get_owner_profile, get_budget_range

load_dotenv()


class _CyclingStaticLLM:
    """LLM estático simples para permitir execução offline."""

    def __init__(self, responses):
        self._responses = cycle(responses)
        self.model = "static-local"

    def call(self, prompt: str, **kwargs: Any) -> str:
        return next(self._responses)

    async def acall(self, prompt: str, **kwargs: Any) -> str:
        return next(self._responses)


def _ollama_available(base_url: str) -> bool:
    """Verifica se o Ollama está disponível."""
    try:
        ping_url = urljoin(base_url if base_url.endswith("/") else base_url + "/", "api/tags")
        with urlopen(Request(ping_url, method="GET"), timeout=2) as response:
            return response.status == 200
    except (URLError, ValueError):
        return False


def _check_model_available(base_url: str, model_name: str) -> bool:
    """Verifica se um modelo específico está disponível no Ollama."""
    try:
        ping_url = urljoin(base_url if base_url.endswith("/") else base_url + "/", "api/tags")
        with urlopen(Request(ping_url, method="GET"), timeout=2) as response:
            if response.status == 200:
                import json
                data = json.loads(response.read().decode('utf-8'))
                models = [m['name'] for m in data.get('models', [])]
                # Verifica se o modelo existe (com ou sem :latest)
                return any(model_name in m for m in models)
    except Exception:
        pass
    return False


def _get_available_models(base_url: str) -> list:
    """Retorna lista de modelos disponíveis no Ollama."""
    try:
        ping_url = urljoin(base_url if base_url.endswith("/") else base_url + "/", "api/tags")
        with urlopen(Request(ping_url, method="GET"), timeout=2) as response:
            if response.status == 200:
                import json
                data = json.loads(response.read().decode('utf-8'))
                models = []
                for m in data.get('models', []):
                    name = m['name']
                    size = m.get('size', 0)
                    # Converter bytes para GB
                    size_gb = size / (1024**3) if size > 0 else 0
                    models.append({
                        'name': name,
                        'display_name': name,
                        'size_gb': size_gb
                    })
                return models
    except Exception:
        pass
    return []


def _select_model_interactive(base_url: str) -> str:
    """
    Permite ao usuário selecionar o modelo interativamente.
    
    Returns:
        Nome do modelo selecionado (ex: "qwen2.5:14b")
    """
    models = _get_available_models(base_url)
    
    if not models:
        print("⚠️  Nenhum modelo encontrado no Ollama")
        return None
    
    print("\n" + "="*70)
    print("🤖 MODELOS DISPONÍVEIS NO OLLAMA")
    print("="*70)
    
    # Modelos recomendados (em ordem de preferência)
    recommended = ["qwen2.5:14b", "glm-4.6:cloud", "llama3.2:latest", "gpt-oss:latest", "deepseek-coder:33b"]
    
    # Organizar modelos: recomendados primeiro, depois outros
    sorted_models = []
    other_models = []
    
    for model in models:
        name = model['name']
        if any(rec in name for rec in recommended):
            sorted_models.append(model)
        else:
            other_models.append(model)
    
    sorted_models.extend(other_models)
    
    # Exibir modelos
    for idx, model in enumerate(sorted_models, 1):
        name = model['name']
        size = model['size_gb']
        
        # Marcar recomendados
        is_recommended = any(rec in name for rec in recommended)
        marker = "⭐" if is_recommended else "  "
        
        print(f"{marker} {idx}. {name:<30} ({size:.1f} GB)")
    
    print("="*70)
    print("\n⭐ = Recomendado para este workflow")
    print("\n💡 Recomendações:")
    print("   • Qwen2.5 14B: Melhor para tool calling e análise complexa")
    print("   • GLM-4.6: Ótimo equilíbrio performance/qualidade")
    print("   • Llama3.2: Rápido e eficiente para tasks simples")
    print("\n⚠️  Modelos NÃO recomendados com CrewAI:")
    print("   • gpt-oss: Usa 'thinking mode' incompatível com CrewAI tools")
    print("     (Funciona standalone mas falha em workflows com ferramentas)")
    
    # Solicitar escolha
    while True:
        try:
            choice = input(f"\nEscolha um modelo (1-{len(sorted_models)}) [1]: ").strip()
            
            # Default para primeiro modelo (Qwen2.5 se disponível)
            if not choice:
                choice = "1"
            
            idx = int(choice)
            if 1 <= idx <= len(sorted_models):
                selected = sorted_models[idx - 1]
                print(f"\n✅ Modelo selecionado: {selected['name']}")
                return selected['name']
            else:
                print(f"❌ Escolha inválida. Digite um número entre 1 e {len(sorted_models)}")
        except ValueError:
            print("❌ Entrada inválida. Digite um número.")
        except KeyboardInterrupt:
            print("\n\n❌ Seleção cancelada.")
            return None


def _initialize_llm(interactive: bool = True, model_name: str = None):
    """
    Inicializa o LLM.

    Args:
        interactive: Se True, permite seleção interativa do modelo
        model_name: Nome específico do modelo a ser usado (sobrescreve interactive)

    Returns:
        Instância do LLM configurado
    
    Priority order:
        1. model_name parameter (explicit override)
        2. DEFAULT_MODEL environment variable
        3. Interactive selection (if interactive=True)
        4. Auto-selection fallback (qwen2.5:14b -> glm-4.6 -> gpt-oss)
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    if not _ollama_available(base_url):
        print(f"⚠️  Ollama não disponível em {base_url}")
        print(f"⚠️  Usando modo demonstração (respostas estáticas).")

        # Fallback estático com respostas genéricas
        static_responses = [
            "Análise realizada com base nos dados fornecidos.",
            "Recomendação: Prosseguir com cautela, considerando os riscos identificados.",
            "Relatório técnico completo disponível nos arquivos de saída."
        ]

        return _CyclingStaticLLM(static_responses)

    print(f"✅ Conectado ao Ollama em {base_url}")

    # PRIORITY 1: Explicit model_name parameter (API calls, testing overrides)
    if model_name:
        selected_model = model_name
        print(f"🚀 Usando modelo especificado: {selected_model}")
    # PRIORITY 2: DEFAULT_MODEL environment variable (automation, tests, default config)
    elif os.getenv("DEFAULT_MODEL"):
        selected_model = os.getenv("DEFAULT_MODEL")
        print(f"🚀 Usando modelo padrão (DEFAULT_MODEL): {selected_model}")
    # PRIORITY 3: Interactive selection (manual execution)
    elif interactive:
        selected_model = _select_model_interactive(base_url)
        
        if selected_model:
            print(f"🚀 Iniciando com modelo: {selected_model}")
            
            # ⚠️ ALERTA: gpt-oss tem formato de resposta incompatível com CrewAI
            if "gpt-oss" in selected_model.lower():
                print("⚠️  AVISO: gpt-oss usa 'thinking mode' que pode causar problemas com CrewAI")
                print("⚠️  Recomendação: Use qwen2.5:14b, glm-4.6:cloud ou llama3.2:latest")
                print("\n💡 gpt-oss funciona bem standalone mas não com ferramentas CrewAI")
                print("   Motivo: CrewAI espera respostas diretas, mas gpt-oss retorna:")
                print("   'Thinking... [raciocínio] ...done thinking. [resposta]'")
                
                cont = input("\n❓ Continuar mesmo assim? (pode falhar) [y/N]: ").strip().lower()
                if cont != 'y':
                    print("\n🔄 Por favor, escolha outro modelo.")
                    return _initialize_llm(interactive=True)
            
            return CrewLLM(model=f"ollama/{selected_model}", base_url=base_url)
    # PRIORITY 4: Auto-selection fallback (no env var, non-interactive mode)
    else:
        # Prioridade 1: Qwen2.5 14B (128k contexto, tool calling excelente)
        if _check_model_available(base_url, "qwen2.5:14b"):
            selected_model = "qwen2.5:14b"
            print(f"🚀 Usando modelo: Qwen2.5 14B (auto-selecionado)")
        # Prioridade 2: GLM-4.6 (melhor performance, contexto longo)
        elif _check_model_available(base_url, "glm-4.6"):
            selected_model = "glm-4.6:cloud"
            print(f"🔄 Usando: GLM-4.6 (auto-selecionado)")
        # Fallback: gpt-oss (modelo original)
        else:
            selected_model = "gpt-oss"
            print(f"⚠️  Usando: gpt-oss (fallback)")
        
        return CrewLLM(model=f"ollama/{selected_model}", base_url=base_url)
    
    # Build and return the LLM instance
    return CrewLLM(model=f"ollama/{selected_model}", base_url=base_url)


def generate_comprehensive_report(property_data: Dict[str, Any], final_result: str, task_outputs: list) -> str:
    """
    Gera relatório completo com outputs de todos os agentes da cadeia.

    Args:
        property_data: Dados da propriedade (name, link, location_hint)
        final_result: Resultado final da crew (executive summary)
        task_outputs: Lista de dicts com outputs individuais de cada task
            [{task_number: int, agent: str, output: str}, ...]

    Returns:
        String formatada em markdown com relatório completo
    """
    report_lines = []

    # Cabeçalho
    report_lines.append("# Avaliação Completa de Propriedade - Todos os Agentes\n")
    report_lines.append("=" * 70)
    report_lines.append("\n")

    # Identificação da propriedade
    report_lines.append("## 📋 Identificação da Propriedade\n")
    if property_data.get('property_link'):
        report_lines.append(f"**Link:** {property_data['property_link']}\n")
    if property_data.get('property_name'):
        report_lines.append(f"**Nome:** {property_data['property_name']}\n")
    if property_data.get('location_hint'):
        report_lines.append(f"**Localização:** {property_data['location_hint']}\n")
    report_lines.append("\n---\n\n")

    # Executive Summary (final result)
    report_lines.append("## 🎯 Executive Summary (Conclusão Final)\n")
    report_lines.append(final_result)
    report_lines.append("\n\n---\n\n")

    # Outputs individuais de cada task/agent
    report_lines.append("## 📊 Outputs Detalhados por Agente\n")
    report_lines.append("\n")

    # Mapear número da task para nome descritivo
    task_names = {
        0: "🔍 Task 0: Pesquisa e Coleta de Dados (Juliana Campos)",
        1: "🏛️ Task 1: Análise de Localização e Contexto (Marcelo Ribeiro)",
        2: "🔧 Task 2: Análise Técnica e Estimativa CAPEX (André Costa)",
        3: "⚖️ Task 3: Due Diligence Jurídica (Fernando Luz)",
        4: "💰 Task 4: Modelagem Financeira e Viabilidade (Ricardo Tavares)",
        5: "🎲 Task 5: Stress Test e Recomendação Final (Gabriel Santos)"
    }

    for task_output in task_outputs:
        task_num = task_output.get('task_number', -1)
        agent_role = task_output.get('agent', 'Agente Desconhecido')
        output_text = task_output.get('output', '[Output não disponível]')

        # Obter nome descritivo da task
        task_title = task_names.get(task_num, f"Task {task_num}: {agent_role}")

        report_lines.append(f"### {task_title}\n")
        report_lines.append("\n")
        report_lines.append(output_text)
        report_lines.append("\n\n---\n\n")

    # Metadata
    import datetime
    report_lines.append("## 📝 Metadata\n")
    report_lines.append(f"**Data de Geração:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"**Total de Agentes:** {len(task_outputs)}\n")
    report_lines.append(f"**Workflow:** Avaliação de Propriedade (Workflow A)\n")
    report_lines.append("\n")
    report_lines.append("---\n")
    report_lines.append("*Relatório gerado automaticamente pelo sistema CrewAI Local*\n")

    return "".join(report_lines)


def create_output_directory(workflow_name: str) -> str:
    """
    Cria diretório outputs/{workflow_name}/{YYYY-MM-DD}/.

    Args:
        workflow_name: Nome do workflow (ex: "property_evaluation", "positioning_strategy")

    Returns:
        Caminho completo do diretório criado
    """
    import os
    from datetime import date

    today = date.today().strftime("%Y-%m-%d")
    output_dir = os.path.join("outputs", workflow_name, today)
    os.makedirs(output_dir, exist_ok=True)

    return output_dir


def generate_summary_report(property_data: Dict[str, Any], final_result: str) -> str:
    """
    Gera relatório executivo (apenas summary, sem outputs individuais).

    Args:
        property_data: Dados da propriedade/projeto
        final_result: Resultado final da crew (executive summary)

    Returns:
        String formatada em markdown com relatório executivo
    """
    import datetime

    report_lines = []

    # Cabeçalho
    report_lines.append("# Relatório Executivo\n")
    report_lines.append("=" * 70)
    report_lines.append("\n\n")

    # Identificação (se disponível)
    if property_data.get('property_link'):
        report_lines.append(f"**Link:** {property_data['property_link']}\n")
    if property_data.get('property_name'):
        report_lines.append(f"**Nome:** {property_data['property_name']}\n")
    if property_data.get('location_hint') or property_data.get('location'):
        location = property_data.get('location_hint') or property_data.get('location')
        report_lines.append(f"**Localização:** {location}\n")

    report_lines.append("\n---\n\n")

    # Resultado executivo
    report_lines.append(final_result)
    report_lines.append("\n\n---\n\n")

    # Metadata
    report_lines.append("## 📝 Metadata\n")
    report_lines.append(f"**Data de Geração:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("\n")
    report_lines.append("*Relatório gerado automaticamente pelo sistema CrewAI Local*\n")

    return "".join(report_lines)


def save_workflow_outputs(workflow_name: str, identifier: str, property_data: Dict,
                         final_result: str, task_outputs: list):
    """
    Salva tanto o relatório completo quanto o sumário executivo em pastas organizadas.

    Args:
        workflow_name: Nome do workflow (ex: "property_evaluation")
        identifier: Identificador para o nome do arquivo (ex: nome da propriedade)
        property_data: Dados do projeto/propriedade
        final_result: Resultado final da crew
        task_outputs: Lista de outputs individuais das tasks

    Saves:
        outputs/{workflow_name}/{date}/{workflow}_{identifier}_completo.md
        outputs/{workflow_name}/{date}/{workflow}_{identifier}_summary.md
    """
    # Criar diretório
    output_dir = create_output_directory(workflow_name)

    # Sanitizar identificador para nome de arquivo
    safe_id = identifier.replace('https://', '').replace('http://', '') \
                        .replace('/', '_').replace(' ', '_').replace(':', '-')[:50]

    # Nome base dos arquivos
    base_name = f"{workflow_name}_{safe_id}"

    # Gerar relatório completo
    comprehensive_report = generate_comprehensive_report(
        property_data=property_data,
        final_result=final_result,
        task_outputs=task_outputs
    )

    # Gerar relatório sumário
    summary_report = generate_summary_report(
        property_data=property_data,
        final_result=final_result
    )

    # Salvar relatório completo
    completo_path = os.path.join(output_dir, f"{base_name}_completo.md")
    with open(completo_path, 'w', encoding='utf-8') as f:
        f.write(comprehensive_report)

    # Salvar relatório sumário
    summary_path = os.path.join(output_dir, f"{base_name}_summary.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_report)

    print(f"\n💾 Relatórios salvos em: {output_dir}/")
    print(f"   📊 Completo: {base_name}_completo.md ({len(task_outputs)} agentes)")
    print(f"   📄 Sumário:  {base_name}_summary.md (executive only)")

    return completo_path, summary_path


def run_property_evaluation(llm=None, property_data=None):
    """
    Executa o Workflow A: Avaliação de Propriedade (MODO AUTÔNOMO).

    NOVO: Apenas nome OU link da propriedade necessário.
    Agentes: Juliana (research), Marcelo, André, Fernando, Ricardo, Gabriel (6 agentes)

    Args:
        llm: LLM pré-inicializado (opcional, para uso via API)
        property_data: Dados da propriedade (opcional, para uso via API)
            - property_name: Nome da propriedade
            - property_link: Link da propriedade
            - location_hint: Dica de localização

    Returns:
        Resultado da crew (para uso via API) ou None (modo interativo)
    """

    # Modo API: parâmetros fornecidos
    if llm is not None and property_data is not None:
        crew = create_property_evaluation_crew(llm, property_data)
        result = crew.kickoff()

        # Coletar outputs individuais de cada task/agent
        task_outputs = []
        for i, task in enumerate(crew.tasks):
            if hasattr(task, 'output') and task.output:
                task_outputs.append({
                    'task_number': i,
                    'agent': task.agent.role if hasattr(task, 'agent') else 'Unknown',
                    'output': task.output.raw if hasattr(task.output, 'raw') else str(task.output)
                })

        # Salvar outputs usando sistema organizado
        final_result_text = result.raw if hasattr(result, 'raw') else str(result)
        property_identifier = property_data.get('property_name') or property_data.get('property_link', 'propriedade')

        save_workflow_outputs(
            workflow_name="property_evaluation",
            identifier=property_identifier,
            property_data=property_data,
            final_result=final_result_text,
            task_outputs=task_outputs
        )

        return result

    # Modo interativo: CLI
    print("\n" + "=" * 70)
    print("🔍 MODO DE PESQUISA AUTÔNOMA")
    print("=" * 70)
    print("Os agentes vão pesquisar AUTOMATICAMENTE todos os dados necessários.")
    print("Você precisa fornecer apenas:")
    print("  • Nome da propriedade OU")
    print("  • Link direto (Airbnb, Booking, OLX, imobiliária, etc.)")
    print("=" * 70)

    print("\n📋 IDENTIFICAÇÃO DA PROPRIEDADE")
    print("-" * 70)

    # Perguntar qual tipo de input
    print("\nVocê tem um link direto da propriedade? (S/N)")
    has_link = input("> ").strip().upper() == 'S'

    property_data = {}

    if has_link:
        # Modo link
        print("\n📎 Cole o link da propriedade:")
        print("   (Airbnb, Booking.com, OLX, site de imobiliária, etc.)")
        property_link = input("> ").strip()

        if not property_link:
            print("\n❌ Link não pode estar vazio!")
            return

        property_data['property_link'] = property_link
        property_data['property_name'] = None

        print("\n💡 Dica de localização (opcional, pressione Enter para pular):")
        print("   Ex: 'Paraty - RJ', 'Centro Histórico', etc.")
        location_hint = input("> ").strip()
        property_data['location_hint'] = location_hint if location_hint else None

    else:
        # Modo nome
        print("\n🏨 Nome da propriedade:")
        property_name = input("> ").strip()

        if not property_name:
            print("\n❌ Nome não pode estar vazio!")
            return

        property_data['property_name'] = property_name
        property_data['property_link'] = None

        print("\n📍 Localização/região (recomendado para melhor pesquisa):")
        print("   Ex: 'Paraty - RJ', 'Centro Histórico de Paraty', etc.")
        location_hint = input("> ").strip()
        property_data['location_hint'] = location_hint if location_hint else 'Paraty - RJ'

    # Resumo dos dados
    print("\n" + "=" * 70)
    print("📊 DADOS PARA PESQUISA:")
    print("=" * 70)
    if property_data.get('property_link'):
        print(f"  🔗 Link: {property_data['property_link']}")
    else:
        print(f"  🏨 Nome: {property_data['property_name']}")
    if property_data.get('location_hint'):
        print(f"  📍 Localização: {property_data['location_hint']}")
    print("=" * 70)

    print("\n⏳ Os agentes vão agora:")
    print("  1️⃣  Pesquisar dados da propriedade (preço, quartos, condição)")
    print("  2️⃣  Analisar concorrentes (ADR, ocupação)")
    print("  3️⃣  Estimar CAPEX necessário")
    print("  4️⃣  Realizar análises técnica, jurídica e financeira")
    print("  5️⃣  Fazer stress test e recomendação final")
    print("\n⏱️  Duração estimada: 15-25 minutos")
    print("-" * 70)

    print("\n🚀 Iniciando avaliação com 6 agentes especializados...")
    print("-" * 70)

    llm = _initialize_llm()
    crew = create_property_evaluation_crew(llm, property_data)

    result = crew.kickoff()

    print("\n\n" + "=" * 70)
    print("✅ AVALIAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print(result)

    # Coletar outputs individuais de cada task/agent
    task_outputs = []
    for i, task in enumerate(crew.tasks):
        if hasattr(task, 'output') and task.output:
            task_outputs.append({
                'task_number': i,
                'agent': task.agent.role if hasattr(task, 'agent') else 'Unknown',
                'output': task.output.raw if hasattr(task.output, 'raw') else str(task.output)
            })

    # Salvar outputs usando sistema organizado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    property_identifier = property_data.get('property_name') or property_data.get('property_link', 'propriedade')

    save_workflow_outputs(
        workflow_name="property_evaluation",
        identifier=property_identifier,
        property_data=property_data,
        final_result=result_text,
        task_outputs=task_outputs
    )


def run_positioning_strategy():
    """
    Executa o Workflow B: Estratégia de Posicionamento.
    
    Agentes: Juliana, Marcelo, Helena, Beatriz (4 agentes)
    """
    
    print("\n📋 DADOS DO PROJETO")
    print("-" * 70)
    
    project_data = {
        'location': input("Localização: ") or 'Paraty - Centro Histórico',
        'rooms': int(input("Número de quartos: ") or 12),
        'target_audience': input("Público-alvo: ") or 'Casais 35-55 anos, alta renda'
    }
    
    print("\n🚀 Desenvolvendo estratégia de posicionamento...")
    print("-" * 70)
    
    llm = _initialize_llm()
    crew = create_positioning_crew(llm, project_data)

    result = crew.kickoff()

    print("\n\n" + "=" * 70)
    print("✅ ESTRATÉGIA DESENVOLVIDA!")
    print("=" * 70)
    print(result)

    # Coletar outputs individuais de cada task/agent
    task_outputs = []
    for i, task in enumerate(crew.tasks):
        if hasattr(task, 'output') and task.output:
            task_outputs.append({
                'task_number': i,
                'agent': task.agent.role if hasattr(task, 'agent') else 'Unknown',
                'output': task.output.raw if hasattr(task.output, 'raw') else str(task.output)
            })

    # Salvar outputs usando sistema organizado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    identifier = project_data.get('location', 'paraty')

    save_workflow_outputs(
        workflow_name="positioning_strategy",
        identifier=identifier,
        property_data=project_data,
        final_result=result_text,
        task_outputs=task_outputs
    )


def run_opening_preparation():
    """
    Executa o Workflow C: Preparação para Abertura.
    
    Agentes: Paula, Patrícia, Sofia, Renata (4 agentes)
    """
    
    print("\n📋 DADOS DA ABERTURA")
    print("-" * 70)
    
    opening_data = {
        'opening_date': input("Data prevista de abertura (YYYY-MM-DD): ") or '2026-06-01',
        'rooms': int(input("Número de quartos: ") or 12),
        'staff_size': int(input("Tamanho da equipe: ") or 8)
    }
    
    print("\n🚀 Preparando para abertura...")
    print("-" * 70)
    
    llm = _initialize_llm()
    crew = create_opening_prep_crew(llm, opening_data)

    result = crew.kickoff()

    print("\n\n" + "=" * 70)
    print("✅ PLANO DE ABERTURA COMPLETO!")
    print("=" * 70)
    print(result)

    # Coletar outputs individuais de cada task/agent
    task_outputs = []
    for i, task in enumerate(crew.tasks):
        if hasattr(task, 'output') and task.output:
            task_outputs.append({
                'task_number': i,
                'agent': task.agent.role if hasattr(task, 'agent') else 'Unknown',
                'output': task.output.raw if hasattr(task.output, 'raw') else str(task.output)
            })

    # Salvar outputs usando sistema organizado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    identifier = opening_data.get('opening_date', '2026-06-01')

    save_workflow_outputs(
        workflow_name="opening_preparation",
        identifier=identifier,
        property_data=opening_data,
        final_result=result_text,
        task_outputs=task_outputs
    )


def run_planning_30days():
    """
    Executa o Workflow D: Planejamento Inicial (30 dias).
    
    Agentes: Helena, Ricardo, Juliana, Marcelo (4 agentes)
    """
    
    print("\n" + "=" * 70)
    print("🗓️  WORKFLOW D: PLANEJAMENTO INICIAL (30 DIAS)")
    print("=" * 70)
    
    # Carregar perfil do proprietário
    profile = get_owner_profile()
    budget_min, budget_max = get_budget_range()
    
    print("\n📊 PERFIL DO PROPRIETÁRIO")
    print("-" * 70)
    print(f"Motivação: {profile['motivacao_principal']}")
    print(f"Budget: R${budget_min:,.0f} - R${budget_max:,.0f}")
    print(f"Horizonte: {profile['horizonte_tempo']}")
    print(f"Break-even máximo: {profile['fluxo_negativo_tolerancia']}")
    print(f"Experiência hospitalidade: {profile['experiencia_hospitalidade']}")
    print(f"Conhecimento Paraty: {profile['conhecimento_paraty']['nivel']}")
    
    print("\n📋 TAREFAS DO PLANO 30 DIAS")
    print("-" * 70)
    print("✓ T-1001: Proposta de valor (Helena)")
    print("✓ T-1010: Mapa competitivo (Juliana)")
    print("✓ T-1011: Calendário eventos (Marcelo)")
    print("✓ T-1003: Envelope financeiro (Ricardo)")
    print("✓ Síntese final (Helena)")
    
    confirma = input("\n▶️  Iniciar execução? (S/n): ").strip().lower()
    if confirma == 'n':
        print("❌ Execução cancelada.")
        return
    
    print("\n🚀 Iniciando análise estratégica...")
    print("-" * 70)
    
    llm = _initialize_llm()
    
    # Dados do projeto (mínimos necessários)
    project_data = {
        'localizacao': 'Paraty',
        'preferencias_localizacao': ['praia', 'centro_historico'],
        'tamanho_flexivel': True,
        'faixa_quartos': (8, 18)
    }
    
    crew = create_planning_30days_crew(llm, project_data)

    result = crew.kickoff()

    print("\n\n" + "=" * 70)
    print("✅ PLANO DE 30 DIAS COMPLETO!")
    print("=" * 70)
    print(result)

    # Coletar outputs individuais de cada task/agent
    task_outputs = []
    for i, task in enumerate(crew.tasks):
        if hasattr(task, 'output') and task.output:
            task_outputs.append({
                'task_number': i,
                'agent': task.agent.role if hasattr(task, 'agent') else 'Unknown',
                'output': task.output.raw if hasattr(task.output, 'raw') else str(task.output)
            })

    # Salvar outputs usando sistema organizado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    identifier = project_data.get('localizacao', 'paraty')

    save_workflow_outputs(
        workflow_name="planning_30days",
        identifier=identifier,
        property_data=project_data,
        final_result=result_text,
        task_outputs=task_outputs
    )

    print("\n📌 Próximo passo: Revisar documento e tomar Decision Point 1")
    print("   (Aprovar posicionamento e iniciar Fase 3: Pipeline)")


def run_property_prospecting():
    """
    Executa o Workflow E: Prospecção de Propriedades.

    Agente: Marina (1 agente, 3 tasks)
    Output: JSON com lista de pousadas à venda qualificadas
    """

    print("\n" + "=" * 70)
    print("🔍 WORKFLOW E: PROSPECÇÃO DE PROPRIEDADES")
    print("=" * 70)
    print("Este workflow busca pousadas À VENDA em Paraty e compila JSON de leads.")
    print("=" * 70)

    # Coletar constraints do usuário
    print("\n📋 FILTROS DE BUSCA (opcional - Enter para pular)")
    print("-" * 70)

    constraints = {}

    # Price range
    print("\n💰 Faixa de Preço:")
    price_min_input = input("   Preço mínimo (R$) [Enter para sem limite]: ").strip()
    price_max_input = input("   Preço máximo (R$) [Enter para sem limite]: ").strip()

    try:
        constraints['price_min'] = int(price_min_input.replace(',', '').replace('.', '')) if price_min_input else None
    except ValueError:
        constraints['price_min'] = None

    try:
        constraints['price_max'] = int(price_max_input.replace(',', '').replace('.', '')) if price_max_input else None
    except ValueError:
        constraints['price_max'] = None

    # Location
    print("\n📍 Localização Preferida:")
    print("   1. Praia")
    print("   2. Centro Histórico")
    print("   3. Qualquer localização")
    location_choice = input("   Escolha (1/2/3) [3]: ").strip() or "3"

    location_filter = []
    if location_choice == "1":
        location_filter = ["praia"]
    elif location_choice == "2":
        location_filter = ["centro_historico"]
    # else: location_filter stays empty (any location)

    constraints['location_filter'] = location_filter

    # Room count
    print("\n🛏️  Número de Quartos:")
    rooms_min_input = input("   Mínimo de quartos [Enter para sem limite]: ").strip()
    rooms_max_input = input("   Máximo de quartos [Enter para sem limite]: ").strip()

    try:
        constraints['rooms_min'] = int(rooms_min_input) if rooms_min_input else None
    except ValueError:
        constraints['rooms_min'] = None

    try:
        constraints['rooms_max'] = int(rooms_max_input) if rooms_max_input else None
    except ValueError:
        constraints['rooms_max'] = None

    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS FILTROS:")
    print("=" * 70)
    if constraints['price_min'] or constraints['price_max']:
        price_min_fmt = f"R${constraints['price_min']:,.0f}" if constraints['price_min'] else "sem limite"
        price_max_fmt = f"R${constraints['price_max']:,.0f}" if constraints['price_max'] else "sem limite"
        print(f"  💰 Preço: {price_min_fmt} - {price_max_fmt}")
    else:
        print(f"  💰 Preço: sem limite")

    if location_filter:
        print(f"  📍 Localização: {', '.join(location_filter)}")
    else:
        print(f"  📍 Localização: qualquer")

    if constraints['rooms_min'] or constraints['rooms_max']:
        rooms_min_fmt = constraints['rooms_min'] if constraints['rooms_min'] else "sem limite"
        rooms_max_fmt = constraints['rooms_max'] if constraints['rooms_max'] else "sem limite"
        print(f"  🛏️  Quartos: {rooms_min_fmt} - {rooms_max_fmt}")
    else:
        print(f"  🛏️  Quartos: sem limite")
    print("=" * 70)

    print("\n⏳ Iniciando prospecção...")
    print("  1️⃣  Buscar listagens em sites imobiliários")
    print("  2️⃣  Extrair e validar dados de cada propriedade")
    print("  3️⃣  Compilar JSON com leads qualificados")
    print("\n⏱️  Duração estimada: 10-20 minutos")
    print("-" * 70)

    confirma = input("\n▶️  Iniciar prospecção? (S/n): ").strip().lower()
    if confirma == 'n':
        print("❌ Prospecção cancelada.")
        return

    llm = _initialize_llm()
    crew = create_prospecting_crew(llm, constraints)

    result = crew.kickoff()

    print("\n\n" + "=" * 70)
    print("✅ PROSPECÇÃO CONCLUÍDA!")
    print("=" * 70)

    # Parse JSON from result
    import json
    from datetime import datetime

    try:
        # Result should be JSON string from task 3
        result_text = result.raw if hasattr(result, 'raw') else str(result)

        # Try to extract JSON from markdown code fence if present
        if '```json' in result_text:
            json_start = result_text.find('```json') + 7
            json_end = result_text.find('```', json_start)
            json_str = result_text[json_start:json_end].strip()
        elif '```' in result_text:
            json_start = result_text.find('```') + 3
            json_end = result_text.find('```', json_start)
            json_str = result_text[json_start:json_end].strip()
        else:
            json_str = result_text.strip()

        # Parse JSON
        leads_data = json.loads(json_str)

        # Save to file
        output_dir = create_output_directory("property_prospecting")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pousadas_paraty_leads_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(leads_data, f, ensure_ascii=False, indent=2)

        # Print summary
        metadata = leads_data.get('metadata', {})
        properties = leads_data.get('properties', [])

        print(f"\n📊 RESULTADOS:")
        print(f"   • Total encontrado: {metadata.get('total_found', 0)}")
        print(f"   • Total qualificado: {metadata.get('total_qualified', 0)}")
        print(f"   • Fontes consultadas: {', '.join(metadata.get('sources', []))}")
        print(f"\n💾 Arquivo salvo em:")
        print(f"   {filepath}")
        print(f"\n📄 Propriedades no arquivo: {len(properties)}")

        # Show first 3 properties as preview
        if properties:
            print(f"\n🏨 PREVIEW (primeiras 3 propriedades):")
            for i, prop in enumerate(properties[:3], 1):
                print(f"\n   {i}. {prop.get('name', 'N/A')}")
                print(f"      Preço: {prop.get('price_formatted', 'N/A')}")
                print(f"      Quartos: {prop.get('rooms', 'N/A')}")
                print(f"      Localização: {prop.get('location_type', 'N/A')}")
                print(f"      URL: {prop.get('listing_url', 'N/A')[:60]}...")

        print("\n✨ Próximo passo: Usar Workflow A (Avaliação) com estas propriedades!")

    except json.JSONDecodeError as e:
        print(f"\n⚠️  Erro ao processar JSON: {str(e)}")
        print(f"   Resultado bruto salvo em: outputs/property_prospecting/raw_result.txt")

        # Save raw result for debugging
        output_dir = create_output_directory("property_prospecting")
        with open(os.path.join(output_dir, "raw_result.txt"), 'w', encoding='utf-8') as f:
            f.write(result_text)
    except Exception as e:
        print(f"\n❌ Erro ao salvar resultados: {str(e)}")
        print(result)


def run_batch_evaluation():
    """
    Executa o Workflow F: Batch Property Screening + Selective Deep Dive.

    FASE 1: Screening rápido de TODAS as propriedades do JSON (5-10 min)
    FASE 2: Deep dive seletivo com Workflow A nas top N escolhidas (N × 20 min)

    Workflow: Sofia Mendes (screening) → Workflow A (avaliação profunda das selecionadas)
    """

    print("\n" + "=" * 70)
    print("🔢 WORKFLOW F: BATCH PROPERTY EVALUATION")
    print("=" * 70)
    print("Screening rápido + avaliação profunda seletiva")
    print("=" * 70)

    # FASE 0: Localizar arquivo JSON do Workflow E
    print("\n📁 FASE 0: SELECIONAR ARQUIVO JSON")
    print("-" * 70)
    print("Este workflow processa propriedades do Workflow E (Prospecção).")
    print()

    # Listar JSONs recentes em outputs/property_prospecting/
    import glob
    from pathlib import Path

    json_pattern = os.path.join("outputs", "property_prospecting", "*", "*.json")
    json_files = sorted(glob.glob(json_pattern), key=os.path.getmtime, reverse=True)

    if json_files:
        print("📋 Arquivos JSON encontrados (mais recentes primeiro):")
        for i, filepath in enumerate(json_files[:5], 1):  # Mostrar os 5 mais recentes
            filename = os.path.basename(filepath)
            date_folder = os.path.basename(os.path.dirname(filepath))
            filesize_kb = os.path.getsize(filepath) / 1024
            print(f"   {i}. {filename} ({date_folder}, {filesize_kb:.1f} KB)")
        print()

        choice = input("Digite o número do arquivo OU caminho completo [1]: ").strip() or "1"

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= min(5, len(json_files)):
                json_path = json_files[choice_num - 1]
            else:
                print(f"❌ Número inválido. Use 1-{min(5, len(json_files))}")
                return
        except ValueError:
            # Caminho completo fornecido
            json_path = choice
            if not os.path.exists(json_path):
                print(f"❌ Arquivo não encontrado: {json_path}")
                return
    else:
        print("⚠️  Nenhum arquivo JSON encontrado em outputs/property_prospecting/")
        print()
        json_path = input("Digite o caminho completo do arquivo JSON: ").strip()
        if not os.path.exists(json_path):
            print(f"❌ Arquivo não encontrado: {json_path}")
            return

    # Carregar e validar JSON
    print(f"\n📖 Carregando: {os.path.basename(json_path)}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")
        return
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return

    # Validar estrutura
    if 'data' not in json_data or 'properties' not in json_data['data']:
        print("❌ JSON inválido: estrutura esperada é {'data': {'properties': [...]}}")
        return

    properties = json_data['data']['properties']
    total_properties = len(properties)

    if total_properties == 0:
        print("❌ JSON não contém propriedades para analisar")
        return

    print(f"✅ JSON válido: {total_properties} propriedades encontradas")

    # Extrair constraints originais (se disponíveis no JSON)
    metadata = json_data.get('metadata', {})
    constraints = metadata.get('constraints', {})

    if constraints:
        print(f"\n📊 Constraints originais (Workflow E):")
        if constraints.get('price_min') or constraints.get('price_max'):
            print(f"   • Preço: R${constraints.get('price_min', 0):,.0f} - R${constraints.get('price_max', 999999999):,.0f}")
        if constraints.get('location_filter'):
            print(f"   • Localização: {', '.join(constraints['location_filter'])}")
        if constraints.get('rooms_min') or constraints.get('rooms_max'):
            print(f"   • Quartos: {constraints.get('rooms_min', 'sem limite')} - {constraints.get('rooms_max', 'sem limite')}")

    # FASE 1: Screening
    print("\n" + "=" * 70)
    print("🔍 FASE 1: SCREENING RÁPIDO (5-10 minutos)")
    print("=" * 70)
    print(f"Analisando {total_properties} propriedades com scoring multi-dimensional...")
    print()
    print("Critérios:")
    print("  • Price/Room Ratio (30%): R$/quarto vs benchmark R$100k-200k")
    print("  • Location (25%): praia=10, centro_historico=9, outras=6")
    print("  • Data Quality (15%): complete=10, partial=7, minimal=4")
    print("  • Condition (20%): excelente=10, bom=8, regular=6")
    print("  • Investment Fit (10%): alinhamento com budget")
    print()

    top_n = input("Quantas propriedades top deseja no ranking? [10]: ").strip() or "10"
    try:
        top_n = int(top_n)
        if top_n < 1 or top_n > total_properties:
            print(f"⚠️  Ajustado para {min(10, total_properties)} (mín: 1, máx: {total_properties})")
            top_n = min(10, total_properties)
    except ValueError:
        print("⚠️  Valor inválido, usando 10")
        top_n = 10

    print(f"\n⏳ Iniciando screening de {total_properties} propriedades...")
    print("-" * 70)

    llm = _initialize_llm()
    screening_crew = create_screening_crew(llm, json_data, constraints, top_n)

    screening_result = screening_crew.kickoff()

    # Parse do resultado
    result_text = screening_result.raw if hasattr(screening_result, 'raw') else str(screening_result)

    # Remover markdown code fences se presentes
    if '```json' in result_text:
        json_start = result_text.find('```json') + 7
        json_end = result_text.find('```', json_start)
        json_str = result_text[json_start:json_end].strip()
    elif '```' in result_text:
        json_start = result_text.find('```') + 3
        json_end = result_text.find('```', json_start)
        json_str = result_text[json_start:json_end].strip()
    else:
        json_str = result_text.strip()

    try:
        screening_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"\n❌ Erro ao parsear JSON de screening: {e}")
        print("\n📝 Salvando resultado bruto para debug...")
        debug_dir = create_output_directory("batch_screening")
        debug_path = os.path.join(debug_dir, "screening_raw_output.txt")
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"💾 Salvo em: {debug_path}")
        return

    # Salvar JSON de screening
    from datetime import datetime
    output_dir = create_output_directory("batch_screening")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_filename = os.path.splitext(os.path.basename(json_path))[0]
    screening_json_path = os.path.join(output_dir, f"screening_{source_filename}_{timestamp}.json")

    with open(screening_json_path, 'w', encoding='utf-8') as f:
        json.dump(screening_data, f, ensure_ascii=False, indent=2)

    # Exibir tabela de resultados
    ranked = screening_data.get('ranked_properties', [])

    print("\n" + "=" * 70)
    print(f"📊 RESULTADOS DO SCREENING (TOP {len(ranked)})")
    print("=" * 70)
    print()
    print(f"{'Rank':<5} {'ID':<10} {'Score':<6} {'Preço':<12} {'Quartos':<8} {'R$/Qt':<10} {'Location':<15} {'Rec':<15}")
    print("-" * 70)

    for prop in ranked:
        rank = prop['rank']
        prop_id = prop['property_id']
        score = prop['scores']['final_score']
        price = f"R${prop['price']/1_000_000:.1f}M" if prop.get('price') else "N/A"
        bedrooms = prop.get('bedrooms', 'N/A')
        price_per_room_val = prop['scores'].get('price_per_room_value', 0)
        price_per_room = f"R${price_per_room_val/1000:.0f}k" if price_per_room_val > 0 else "N/A"
        location = prop.get('location_type', 'N/A')[:13]
        rec = prop['recommendation'][:13]

        print(f"{rank:<5} {prop_id:<10} {score:<6.1f} {price:<12} {bedrooms:<8} {price_per_room:<10} {location:<15} {rec:<15}")

    print()
    print(f"💾 Screening completo salvo em:")
    print(f"   {screening_json_path}")

    # FASE 2: Selective Deep Dive
    print("\n" + "=" * 70)
    print("🔬 FASE 2: SELECTIVE DEEP DIVE")
    print("=" * 70)
    print("Escolha propriedades para análise profunda com Workflow A (6 agentes).")
    print(f"Duração estimada: ~20 minutos por propriedade")
    print()

    num_to_analyze = input(f"Quantas propriedades deseja analisar em profundidade? (0-{len(ranked)}) [0 para pular]: ").strip() or "0"

    try:
        num_to_analyze = int(num_to_analyze)
        if num_to_analyze < 0 or num_to_analyze > len(ranked):
            print(f"❌ Número inválido. Use 0-{len(ranked)}")
            return
    except ValueError:
        print("❌ Número inválido")
        return

    if num_to_analyze == 0:
        print("\n✅ Screening concluído. Nenhuma análise profunda solicitada.")
        return

    # Coletar IDs para análise
    print(f"\nDigite os IDs das propriedades separados por vírgula")
    print(f"Exemplo: PROP-001,PROP-005,PROP-009")
    print(f"OU pressione Enter para analisar automaticamente as top {num_to_analyze}")
    print()

    ids_input = input("> ").strip()

    if ids_input:
        # IDs fornecidos manualmente
        selected_ids = [id.strip() for id in ids_input.split(',')]
    else:
        # Selecionar automaticamente top N
        selected_ids = [prop['property_id'] for prop in ranked[:num_to_analyze]]

    # Validar IDs
    valid_ids = {prop['property_id']: prop for prop in ranked}
    properties_to_analyze = []

    for prop_id in selected_ids:
        if prop_id in valid_ids:
            properties_to_analyze.append(valid_ids[prop_id])
        else:
            print(f"⚠️  ID não encontrado no ranking: {prop_id} (pulando)")

    if not properties_to_analyze:
        print("\n❌ Nenhuma propriedade válida selecionada")
        return

    print(f"\n🚀 Iniciando análise profunda de {len(properties_to_analyze)} propriedades...")
    print(f"⏱️  Tempo estimado total: ~{len(properties_to_analyze) * 20} minutos")
    print("-" * 70)

    # Loop de análise profunda
    analyzed_count = 0
    failed_count = 0

    for i, prop in enumerate(properties_to_analyze, 1):
        prop_id = prop['property_id']
        prop_name = prop['name']
        prop_url = prop.get('url', '')

        print(f"\n[{i}/{len(properties_to_analyze)}] Analisando: {prop_id} - {prop_name}")
        print(f"    Score: {prop['scores']['final_score']} | {prop['recommendation']}")
        print(f"    URL: {prop_url}")
        print("-" * 70)

        # Preparar property_data para Workflow A
        property_data_for_eval = {
            'property_name': prop_name,
            'property_link': prop_url if prop_url else None,
            'location_hint': f"{prop.get('location_type', 'Paraty')} - Paraty, RJ"
        }

        try:
            # Chamar Workflow A
            eval_result = run_property_evaluation(llm, property_data_for_eval)
            analyzed_count += 1
            print(f"✅ Análise concluída para {prop_id}")
        except Exception as e:
            print(f"❌ Erro ao analisar {prop_id}: {str(e)}")
            failed_count += 1

            # Perguntar se deseja continuar
            if i < len(properties_to_analyze):
                continue_choice = input("\n   Continuar com próximas propriedades? (S/N) [S]: ").strip().upper() or "S"
                if continue_choice != 'S':
                    print("\n⚠️  Análise interrompida pelo usuário")
                    break

    # Resumo final
    print("\n" + "=" * 70)
    print("🎯 WORKFLOW F CONCLUÍDO")
    print("=" * 70)
    print(f"\n📊 FASE 1 - Screening:")
    print(f"   • {total_properties} propriedades analisadas")
    print(f"   • Top {len(ranked)} ranqueadas")
    print(f"   • Arquivo: {screening_json_path}")
    print()
    print(f"🔬 FASE 2 - Deep Dive:")
    print(f"   • {analyzed_count} propriedades analisadas com sucesso")
    if failed_count > 0:
        print(f"   • {failed_count} falharam")
    print(f"   • Relatórios salvos em: outputs/property_evaluation/{datetime.now().strftime('%Y-%m-%d')}/")
    print()
    print("✅ Batch evaluation concluída!")


# Mantém compatibilidade com código antigo
def create_crew():
    """Função de compatibilidade - usa workflow de avaliação por padrão."""
    llm = _initialize_llm()
    
    property_data = {
        'name': 'Pousada Exemplo',
        'location': 'Centro Histórico',
        'price': 2_000_000,
        'rooms': 10,
        'capex_estimated': 250_000,
        'adr_target': 300,
        'occupancy_target': 55
    }
    
    return create_property_evaluation_crew(llm, property_data)
