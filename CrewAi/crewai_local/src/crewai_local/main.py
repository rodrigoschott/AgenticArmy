"""
Sistema Multi-Agente para Avaliação de Pousadas em Paraty

Este sistema oferece 4 workflows principais:
1. Planejamento Inicial (30 Dias) - NOVO!
2. Avaliação de Propriedade (go/no-go decision)
3. Estratégia de Posicionamento (marca e diferenciação)
4. Preparação para Abertura (compliance e operações)
"""

import os
from crewai_local.crew_paraty import (
    run_planning_30days,
    run_property_evaluation,
    run_positioning_strategy,
    run_opening_preparation
)


def main():
    """Menu principal do sistema."""
    
    print("=" * 70)
    print("🏨 SISTEMA DE AVALIAÇÃO DE POUSADAS - PARATY v2.1")
    print("=" * 70)
    print("\nWorkflows disponíveis:")
    print()
    print("🗓️  D. Planejamento Inicial (30 Dias) ⭐ RECOMENDADO PARA INICIAR")
    print("    └─ Validação estratégica antes de prospectar imóveis")
    print()
    print("🔍 A. Avaliar Propriedade Específica (Go/No-Go)")
    print("    └─ Due diligence completa de um imóvel candidato")
    print()
    print("🎯 B. Desenvolver Estratégia de Posicionamento")
    print("    └─ Definir marca, público-alvo e diferenciação")
    print()
    print("🚀 C. Preparar para Abertura (Soft Opening)")
    print("    └─ SOPs, licenças e lançamento operacional")
    print()
    print("0. Sair")
    print()
    
    choice = input("Escolha um workflow (D/A/B/C/0): ").strip().upper()
    
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
        
    elif choice == "A" or choice == "1":
        print("\n🔍 WORKFLOW A: AVALIAÇÃO DE PROPRIEDADE")
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
