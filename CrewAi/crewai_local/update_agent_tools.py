"""
Script para atualizar TODOS os agentes para usar ferramentas MCP
"""

import re
from pathlib import Path

# Mapeamento de arquivos e substituições
files_to_update = {
    "src/crewai_local/agents/tecnico.py": [
        {
            "old": 'tools=[],',
            "new": 'tools=tools_list,',
            "agent": "andre_martins"
        },
        {
            "old": '# Obter tools (pode ser None se DuckDuckGo não estiver disponível)\n    search_tool = get_search_tool()\n    tools_list = [search_tool] if search_tool else []',
            "new": '# Obter ferramentas estratégicas (busca + fetch para pesquisar normas técnicas)\n    tools_list = get_enhanced_tools_for_agent("estrategista")',
            "agent": "sofia_duarte"
        },
        {
            "old": '# Obter tools (pode ser None se DuckDuckGo não estiver disponível)\n    search_tool = get_search_tool()\n    tools_list = [search_tool] if search_tool else []',
            "new": '# Obter ferramentas estratégicas (busca + fetch para pesquisar operações)\n    tools_list = get_enhanced_tools_for_agent("estrategista")',
            "agent": "paula_andrade"
        }
    ]
}


def update_files():
    """Atualiza todos os arquivos."""
    print("=" * 80)
    print("🔧 ATUALIZANDO AGENTES PARA USAR FERRAMENTAS MCP")
    print("=" * 80)
    print()
    
    for filepath, replacements in files_to_update.items():
        file_path = Path(filepath)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {filepath}")
            continue
        
        print(f"📝 Processando: {filepath}")
        
        # Ler conteúdo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Aplicar substituições
        for repl in replacements:
            if repl['old'] in content:
                content = content.replace(repl['old'], repl['new'], 1)
                changes_made += 1
                print(f"  ✅ Atualizado: {repl['agent']}")
            else:
                print(f"  ⚠️  Não encontrado padrão para: {repl['agent']}")
        
        # Salvar se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  💾 Salvo com {changes_made} alterações")
        else:
            print(f"  ⏭️  Sem alterações necessárias")
        
        print()
    
    print("=" * 80)
    print("✅ ATUALIZAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print()
    print("📋 Próximos passos:")
    print("  1. Execute: poetry run python audit_agent_tools.py")
    print("  2. Verifique a cobertura de ferramentas MCP")
    print("  3. Execute: poetry run start")
    print()


if __name__ == "__main__":
    update_files()
