"""
Teste rápido das ferramentas CLI
"""

from src.crewai_local.tools.web_tools import (
    print_available_tools,
    get_enhanced_tools_for_agent,
    mcp_search_cli
)

print("\n" + "="*70)
print("🧪 TESTE RÁPIDO - CLI TOOLS")
print("="*70)

# 1. Testar função de diagnóstico
print("\n1️⃣ TESTANDO DIAGNÓSTICO:")
print_available_tools()

# 2. Testar obtenção de ferramentas por perfil
print("\n2️⃣ TESTANDO GET_ENHANCED_TOOLS_FOR_AGENT:")
profiles = ["estrategista", "mercado", "localizacao", "marketing", "tecnico"]
for profile in profiles:
    tools = get_enhanced_tools_for_agent(profile)
    print(f"   • {profile:15} → {len(tools)} tools: {[t.name for t in tools]}")

# 3. Testar uma chamada CLI direta
print("\n3️⃣ TESTANDO CHAMADA CLI DIRETA:")
print("   Executando: mcp_search_cli('Paraty Brazil')...")
result = mcp_search_cli("Paraty Brazil")
if "Error" in result:
    print(f"   ❌ FALHOU: {result[:200]}")
else:
    print(f"   ✅ PASSOU: {len(result)} chars retornados")
    print(f"   Primeiros 150 chars: {result[:150]}...")

print("\n" + "="*70)
print("✅ TESTE CONCLUÍDO")
print("="*70 + "\n")
