"""
Sistema Multi-Agente para Avaliação de Pousadas em Paraty

Este sistema oferece 6 workflows principais:
1. Planejamento Inicial (30 Dias)
2. Prospecção de Propriedades (Lead Generation)
3. Avaliação em Lote (Batch Screening + Deep Dive) - NOVO!
4. Avaliação de Propriedade (go/no-go decision)
5. Estratégia de Posicionamento (marca e diferenciação)
6. Preparação para Abertura (compliance e operações)
"""

import os
import sys
from dotenv import load_dotenv

from crewai_local.crew_paraty import (
    run_planning_30days,
    run_property_evaluation,
    run_positioning_strategy,
    run_opening_preparation,
    run_property_prospecting,
    run_batch_evaluation
)
from crewai_local.config.logging_config import setup_logging, get_logger
from crewai_local.config.env_validator import (
    validate_environment,
    check_docker_mcp_available
)

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(console=True, colored_console=True)


def startup_validation() -> bool:
    """
    Run startup validation checks.

    Returns:
        True if all validations pass, False otherwise
    """
    logger.info("Running startup validation...")

    # Skip validation if requested (for testing)
    if os.getenv("SKIP_STARTUP_VALIDATION") == "true":
        logger.warning("Startup validation SKIPPED (SKIP_STARTUP_VALIDATION=true)")
        return True

    # Validate environment variables
    print("\n🔍 Validating environment configuration...")
    env_valid = validate_environment(show_report=True, show_warnings=True)

    # Check Docker MCP availability (optional check)
    skip_docker_check = os.getenv("SKIP_DOCKER_CHECK") == "true"
    if not skip_docker_check:
        print("\n🐳 Checking Docker MCP Gateway...")
        docker_available, docker_message = check_docker_mcp_available()

        if docker_available:
            print(f"   ✅ {docker_message}")
            logger.info(docker_message)
        else:
            print(f"   ⚠️  {docker_message}")
            print(f"   💡 MCP tools will not be available. Agents will have limited capabilities.")
            logger.warning(docker_message)

            # Ask user if they want to continue without Docker
            response = input("\n   Continue without Docker MCP? (y/N): ").strip().lower()
            if response != 'y':
                print("\n   👋 Please start Docker Desktop and try again.")
                logger.info("User chose to exit due to missing Docker")
                return False
    else:
        logger.warning("Docker check SKIPPED (SKIP_DOCKER_CHECK=true)")

    # Check for Google Maps API key (optional)
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("\n   ⚠️  Google Maps API key not configured")
        print("   💡 Location-based tools will not work (maps_geocode, maps_search_places)")
        logger.warning("Google Maps API key not configured")

    print("\n✅ Startup validation complete!")
    return True


def main():
    """Menu principal do sistema."""

    print("=" * 70)
    print("🏨 SISTEMA DE AVALIAÇÃO DE POUSADAS - PARATY v2.4")
    print("=" * 70)

    # Run startup validation
    if not startup_validation():
        sys.exit(1)

    print("\nWorkflows disponíveis:")
    print()
    print("🗓️  D. Planejamento Inicial (30 Dias) ⭐ RECOMENDADO PARA INICIAR")
    print("    └─ Validação estratégica antes de prospectar imóveis")
    print()
    print("🔎 E. Prospectar Propriedades (Lead Generation)")
    print("    └─ Busca e qualifica pousadas à venda em Paraty")
    print()
    print("🔢 F. Avaliar Lote de Propriedades (Batch) 🆕 NOVO!")
    print("    └─ Screening rápido + deep dive seletivo")
    print()
    print("🔍 A. Avaliar Propriedade Específica (Go/No-Go)")
    print("    └─ Due diligence completa - apenas nome/link necessário!")
    print()
    print("🎯 B. Desenvolver Estratégia de Posicionamento")
    print("    └─ Definir marca, público-alvo e diferenciação")
    print()
    print("🚀 C. Preparar para Abertura (Soft Opening)")
    print("    └─ SOPs, licenças e lançamento operacional")
    print()
    print("0. Sair")
    print()

    choice = input("Escolha um workflow (D/E/F/A/B/C/0): ").strip().upper()
    
    if choice == "D":
        print("\n🗓️  WORKFLOW D: PLANEJAMENTO INICIAL (30 DIAS)")
        print("-" * 70)
        print("Este workflow executa as 5 tarefas críticas do seu plano:")
        print("  ✓ Proposta de valor e posicionamento")
        print("  ✓ Envelope financeiro")
        print("  ✓ Mapa competitivo (15 concorrentes)")
        print("  ✓ Calendário de eventos e sazonalidade")
        print("  ✓ Síntese e recomendação go/no-go")
        print()
        run_planning_30days()

    elif choice == "E":
        print("\n🔎 WORKFLOW E: PROSPECÇÃO DE PROPRIEDADES")
        print("-" * 70)
        print("Este workflow:")
        print("  1️⃣  Busca pousadas À VENDA em sites imobiliários")
        print("  2️⃣  Extrai dados estruturados (preço, quartos, localização)")
        print("  3️⃣  Valida contra seus critérios de investimento")
        print("  4️⃣  Gera JSON com leads qualificados")
        print()
        run_property_prospecting()

    elif choice == "F":
        print("\n🔢 WORKFLOW F: BATCH PROPERTY EVALUATION")
        print("-" * 70)
        print("Este workflow:")
        print("  1️⃣  Faz screening rápido de TODAS as propriedades (5-10 min)")
        print("  2️⃣  Rankeia top 10 por múltiplos critérios")
        print("  3️⃣  Permite escolher 3-5 para análise profunda")
        print("  4️⃣  Executa Workflow A apenas nas selecionadas")
        print()
        print("💡 Ideal para processar o JSON do Workflow E")
        print()
        run_batch_evaluation()

    elif choice == "A" or choice == "1":
        print("\n🔍 WORKFLOW A: AVALIAÇÃO DE PROPRIEDADE (MODO AUTÔNOMO)")
        print("-" * 70)
        run_property_evaluation()
        
    elif choice == "B" or choice == "2":
        print("\n🎯 WORKFLOW B: ESTRATÉGIA DE POSICIONAMENTO")
        print("-" * 70)
        run_positioning_strategy()
        
    elif choice == "C" or choice == "3":
        print("\n🚀 WORKFLOW C: PREPARAÇÃO PARA ABERTURA")
        print("-" * 70)
        run_opening_preparation()
        
    elif choice == "0":
        print("\n👋 Até logo!")
        return
        
    else:
        print("\n❌ Opção inválida. Tente novamente.")
        main()


def run():
    """Mantém compatibilidade com poetry run start."""
    main()


if __name__ == "__main__":
    main()
