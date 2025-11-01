"""
Sistema de Crews para o Projeto Paraty

Integra os 11 agentes consolidados (v2.0) em 3 workflows principais.
"""

import os
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


def run_property_evaluation():
    """
    Executa o Workflow A: Avaliação de Propriedade.
    
    Agentes: Marcelo, André, Fernando, Ricardo, Gabriel (5 agentes)
    """
    
    print("\n📋 DADOS DA PROPRIEDADE")
    print("-" * 70)
    
    # Exemplo de propriedade (em produção, viria de input do usuário)
    property_data = {
        'name': input("Nome da propriedade: ") or 'Pousada Vista Mar',
        'location': input("Localização (Centro Histórico/Praia/etc): ") or 'Centro Histórico',
        'price': float(input("Preço de compra (R$): ") or 2_200_000),
        'rooms': int(input("Número de quartos: ") or 12),
        'capex_estimated': float(input("CAPEX estimado (R$): ") or 280_000),
        'adr_target': float(input("ADR projetado (R$): ") or 320),
        'occupancy_target': float(input("Ocupação projetada (%): ") or 60)
    }
    
    print("\n🚀 Iniciando avaliação com 5 agentes especializados...")
    print("-" * 70)
    
    llm = _initialize_llm()
    crew = create_property_evaluation_crew(llm, property_data)
    
    result = crew.kickoff()
    
    print("\n\n" + "=" * 70)
    print("✅ AVALIAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print(result)
    
    # Salvar resultado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    output_file = f"avaliacao_{property_data['name'].replace(' ', '_')}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Avaliação: {property_data['name']}\n\n")
        f.write(result_text)
    
    print(f"\n💾 Resultado salvo em: {output_file}")


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
    
    # Salvar resultado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    with open("estrategia_posicionamento.md", 'w', encoding='utf-8') as f:
        f.write("# Estratégia de Posicionamento\n\n")
        f.write(result_text)
    
    print("\n💾 Resultado salvo em: estrategia_posicionamento.md")


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
    
    # Salvar resultado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    with open("plano_abertura.md", 'w', encoding='utf-8') as f:
        f.write("# Plano de Abertura\n\n")
        f.write(result_text)
    
    print("\n💾 Resultado salvo em: plano_abertura.md")


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
    
    # Salvar resultado
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    with open("plano_30_dias_resultado.md", 'w', encoding='utf-8') as f:
        f.write("# Plano de 30 Dias - Resultado\n\n")
        f.write("**Data:** " + str(__import__('datetime').date.today()) + "\n\n")
        f.write("## Executive Summary\n\n")
        f.write(result_text)
        f.write("\n\n## Próximos Passos\n\n")
        f.write("1. Revisar recomendações de posicionamento\n")
        f.write("2. Validar viabilidade financeira (break-even 6 meses)\n")
        f.write("3. Decidir: Iniciar prospecção ativa?\n")
    
    print("\n💾 Resultado salvo em: plano_30_dias_resultado.md")
    print("\n📌 Próximo passo: Revisar documento e tomar Decision Point 1")
    print("   (Aprovar posicionamento e iniciar Fase 3: Pipeline)")


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
