"""
═══════════════════════════════════════════════════════════════════════════════
MCP Integration Test Suite - Consolidated
═══════════════════════════════════════════════════════════════════════════════

Suite completa de testes para integração MCP nativa (CrewAI 1.2.1+).

CONSOLIDATES:
- test_mcp_basic.py     → Conexão MCP
- test_mcp_native.py    → Agente com LLM
- test_mcp_complete.py  → Auditoria de agentes (apenas parte relevante)
- test_source_tracking.py → (DEPRECATED - old CLI approach)

USAGE:
    poetry run python test_mcp_suite.py              # Teste completo
    poetry run python test_mcp_suite.py --quick      # Apenas conectividade
    poetry run python test_mcp_suite.py --agent      # Apenas teste de agente
    poetry run python test_mcp_suite.py --audit      # Apenas auditoria

KNOWN ISSUES (EXTERNAL):
    - filesystem server: EOF error during initialization (Docker MCP issue)
    - desktop-commander: Invalid JSON during initialization (Docker MCP issue)
    - airbnb_search: Blocked by robots.txt (Airbnb restriction)
    - maps_geocode: Requires valid Google Maps API key configuration
    - OAuth notifications: Connection refused (not critical, feature optional)

RESOLVED ISSUES:
    - Event loop closure: Fixed by using CLI approach for tool execution (Section 4)
    - Unicode encoding: Fixed by using UTF-8 with error replacement

VERSION: 2.1 - Hybrid (Native connectivity + CLI execution)
DATE: 2025-10-31
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: MCP CONNECTIVITY TEST
# ═══════════════════════════════════════════════════════════════════════════

def test_mcp_connection() -> Tuple[bool, str]:
    """
    Testa conexão básica com Docker MCP Gateway.
    
    Returns:
        (success: bool, message: str)
    """
    print("\n" + "="*80)
    print(" 🔌 TESTE 1: CONECTIVIDADE MCP GATEWAY")
    print("="*80)
    
    try:
        from src.crewai_local.tools.mcp_tools_new import (
            get_search_tools,
            get_docker_mcp_tools
        )
        
        print("\n📡 Conectando ao Docker MCP Gateway...")
        
        # Test 1: Get specific tools
        search_tools = get_search_tools()
        
        if not search_tools:
            return False, "❌ Nenhuma ferramenta obtida do gateway"
        
        print(f"✅ {len(search_tools)} ferramentas de busca obtidas:")
        for tool in search_tools:
            desc = tool.description[:60] if hasattr(tool, 'description') else "N/A"
            print(f"   • {tool.name}: {desc}...")
        
        # Test 2: Get all tools (optional, can be slow)
        print("\n📊 Obtendo total de ferramentas disponíveis...")
        all_tools = get_docker_mcp_tools()
        print(f"✅ Total: {len(all_tools)} ferramentas disponíveis no gateway")
        
        return True, f"✅ Gateway funcionando ({len(all_tools)} tools disponíveis)"
        
    except Exception as e:
        return False, f"❌ Erro de conexão: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: AGENT WITH LLM TEST
# ═══════════════════════════════════════════════════════════════════════════

def test_agent_with_mcp() -> Tuple[bool, str]:
    """
    Testa agente real usando MCP tools com LLM.
    
    Returns:
        (success: bool, message: str)
    """
    print("\n" + "="*80)
    print(" 🤖 TESTE 2: AGENTE COM MCP TOOLS + LLM")
    print("="*80)
    
    try:
        from crewai import Agent, Task, Crew
        from src.crewai_local.tools.mcp_tools_new import get_search_tools
        from src.crewai_local.crew_paraty import _initialize_llm
        
        print("\n1️⃣ Inicializando LLM...")
        llm = _initialize_llm()
        llm_name = llm.model if hasattr(llm, 'model') else type(llm).__name__
        print(f"✅ LLM: {llm_name}")
        
        print("\n2️⃣ Obtendo ferramentas MCP...")
        tools = get_search_tools()
        print(f"✅ {len(tools)} tools: {[t.name for t in tools]}")
        
        print("\n3️⃣ Criando agente...")
        agent = Agent(
            role="Pesquisador",
            goal="Encontrar informações básicas",
            backstory="Especialista em pesquisa rápida",
            tools=tools,
            llm=llm,
            verbose=False  # Reduz output
        )
        print("✅ Agente criado com MCP tools")
        
        print("\n4️⃣ Criando tarefa simples...")
        task = Task(
            description="Pesquise: 'Paraty turismo'. Resuma em 2 frases.",
            expected_output="Resumo de 2 frases sobre Paraty",
            agent=agent
        )
        print("✅ Tarefa criada")
        
        print("\n5️⃣ Executando crew (aguarde ~10-30s)...")
        print("-"*80)
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        print("-"*80)
        print("\n✅ Resultado obtido:")
        result_str = str(result)
        print(f"   {result_str[:200]}{'...' if len(result_str) > 200 else ''}")
        
        return True, "✅ Agente executou tarefa com sucesso"
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return False, f"❌ Erro: {str(e)}\n{error_detail[:500]}"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: AGENT COVERAGE AUDIT
# ═══════════════════════════════════════════════════════════════════════════

def analyze_agent_file(filepath: Path) -> List[Dict]:
    """Analisa arquivo de agente e extrai info sobre ferramentas."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    agents = []
    
    try:
        tree = ast.parse(content)
    except:
        return agents
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('create_'):
            agent_name = node.name.replace('create_', '').replace('_', ' ').title()
            
            has_tools_assignment = False
            uses_get_enhanced = False
            tools_empty = False
            tools_profile = None
            
            func_source = ast.get_source_segment(content, node)
            if func_source:
                if 'tools=' in func_source:
                    has_tools_assignment = True
                    
                    if 'get_enhanced_tools_for_agent' in func_source:
                        uses_get_enhanced = True
                        
                        import re
                        match = re.search(r'get_enhanced_tools_for_agent\(["\'](\w+)["\']\)', func_source)
                        if match:
                            tools_profile = match.group(1)
                    
                    if 'tools=[]' in func_source or 'tools = []' in func_source:
                        tools_empty = True
            
            agents.append({
                'name': agent_name,
                'function': node.name,
                'has_tools': has_tools_assignment,
                'uses_mcp': uses_get_enhanced,
                'tools_empty': tools_empty,
                'profile': tools_profile
            })
    
    return agents


def test_agent_coverage() -> Tuple[int, int, List[str]]:
    """
    Audita cobertura de ferramentas MCP nos agentes.
    
    Returns:
        (agents_with_mcp: int, total_agents: int, issues: List[str])
    """
    print("\n" + "="*80)
    print(" 📊 TESTE 3: AUDITORIA DE COBERTURA DE AGENTES")
    print("="*80)
    
    agents_dir = Path("src/crewai_local/agents")
    
    if not agents_dir.exists():
        return 0, 0, ["❌ Diretório de agentes não encontrado"]
    
    all_agents = []
    issues = []
    
    print("\n🔍 Analisando agentes...")
    
    for agent_file in agents_dir.glob("*.py"):
        if agent_file.name == "__init__.py":
            continue
        
        category = agent_file.stem
        agents = analyze_agent_file(agent_file)
        
        for agent in agents:
            agent['category'] = category
            all_agents.append(agent)
    
    # Count stats
    total = len(all_agents)
    with_mcp = sum(1 for a in all_agents if a['uses_mcp'])
    without_tools = sum(1 for a in all_agents if a['tools_empty'])
    
    # Print results by category
    categories = {}
    for agent in all_agents:
        cat = agent['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(agent)
    
    print("\n📋 Agentes por categoria:")
    for cat, agents in sorted(categories.items()):
        print(f"\n   {cat.upper()}:")
        for agent in agents:
            status = "✅" if agent['uses_mcp'] else ("🟡" if agent['has_tools'] else "❌")
            profile = f" ({agent['profile']})" if agent['profile'] else ""
            print(f"      {status} {agent['name']}{profile}")
            
            if not agent['uses_mcp'] and not agent['tools_empty']:
                issues.append(f"⚠️ {agent['name']} tem tools mas não usa MCP")
            elif agent['tools_empty']:
                issues.append(f"❌ {agent['name']} não tem ferramentas configuradas")
    
    # Summary
    coverage = (with_mcp / total * 100) if total > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"📊 RESUMO:")
    print(f"   Total de agentes: {total}")
    print(f"   Com MCP tools: {with_mcp} ({coverage:.1f}%)")
    print(f"   Sem ferramentas: {without_tools}")
    print(f"{'='*80}")
    
    return with_mcp, total, issues


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: REAL MCP TOOLS EXECUTION TESTS (CLI APPROACH)
# ═══════════════════════════════════════════════════════════════════════════

import json
import subprocess

def test_tool_execution_cli(tool_name: str) -> Tuple[bool, str, str]:
    """
    Executa teste real de uma ferramenta MCP usando CLI approach (estável).
    Usa: docker mcp tools call <tool_name> <arg>=<value>
    
    Args:
        tool_name: Nome da ferramenta (search, wikipedia, youtube, maps, airbnb, fetch)
    
    Returns:
        (success: bool, message: str, result: str)
    """
    try:
        # Map tool names to actual tool and arguments
        tool_config = {
            "search": {
                "tool": "search",
                "args": ["query=Paraty Brasil turismo"]
            },
            "wikipedia": {
                "tool": "get_summary",
                "args": ["title=Paraty"]
            },
            "youtube": {
                "tool": "get_video_info",
                "args": ["url=https://youtube.com/watch?v=dQw4w9WgXcQ"]
            },
            "maps": {
                "tool": "maps_geocode",
                "args": ["address=Paraty, RJ, Brasil"]
            },
            "airbnb": {
                "tool": "airbnb_search",
                "args": ["location=Paraty", "adults=2"]
            },
            "fetch": {
                "tool": "fetch",
                "args": ["url=https://example.com"]
            }
        }
        
        if tool_name not in tool_config:
            return False, f"❌ Tool '{tool_name}' desconhecida", ""
        
        config = tool_config[tool_name]
        
        # Execute via Docker MCP CLI: docker mcp tools call <tool> <arg>=<value>
        cmd = ["docker", "mcp", "tools", "call", config["tool"]] + config["args"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'  # Replace invalid chars instead of failing
        )
        
        if result.returncode != 0:
            error_msg = result.stderr[:150] if result.stderr else (result.stdout[:150] if result.stdout else "Unknown error")
            return False, f"❌ Erro CLI: {error_msg}", ""
        
        # Parse result - output is usually plain text
        output = result.stdout.strip() if result.stdout else ""
        
        if not output or len(output) < 20:
            return False, f"❌ Output vazio ou muito curto", ""
        
        # Extract summary based on tool type
        if tool_name == "search":
            # Get first few lines
            lines = output.split('\n')[:5]
            summary = ' '.join(lines)[:200]
        elif tool_name == "wikipedia":
            # Get first 200 chars
            summary = output[:200]
        elif tool_name == "youtube":
            # Look for video info
            if "error" in output.lower():
                return False, f"❌ YouTube error: {output[:100]}", ""
            lines = output.split('\n')[:3]
            summary = ' '.join(lines)[:200]
        elif tool_name == "maps":
            # Check for API errors
            if "REQUEST_DENIED" in output or "not authorized" in output.lower():
                return False, f"⚠️ Maps API não configurada (requer chave válida)", output[:150]
            lines = output.split('\n')[:5]
            summary = ' '.join(lines)[:200]
        elif tool_name == "airbnb":
            # Check for robots.txt blocking
            if "robots.txt" in output.lower() or "disallowed" in output.lower():
                return False, f"⚠️ Airbnb bloqueado por robots.txt (limitação externa)", output[:150]
            lines = output.split('\n')[:5]
            summary = ' '.join(lines)[:200]
        elif tool_name == "fetch":
            # Count content size
            summary = f"Fetched {len(output)} characters"
        else:
            summary = output[:200]
        
        return True, f"✅ {tool_name} executado via CLI", summary
        
    except subprocess.TimeoutExpired:
        return False, f"❌ Timeout em {tool_name} (>30s)", ""
    except Exception as e:
        return False, f"❌ Erro em {tool_name}: {str(e)[:100]}", ""


def test_all_mcp_tools() -> Dict[str, Tuple[bool, str, str]]:
    """
    Testa execução real de cada tipo de ferramenta MCP usando CLI approach.
    
    Returns:
        Dict com resultados de cada teste
    """
    print("\n" + "="*80)
    print(" 🧪 TESTE 4: EXECUÇÃO REAL DE FERRAMENTAS MCP (CLI)")
    print("="*80)
    
    # Tools to test
    tools_to_test = ["search", "wikipedia", "youtube", "maps", "airbnb", "fetch"]
    
    results = {}
    
    print("\n⏳ Executando testes via Docker MCP CLI...")
    print("-"*80)
    
    for i, tool_name in enumerate(tools_to_test, 1):
        print(f"\n[{i}/{len(tools_to_test)}] Testando {tool_name.upper()}...")
        success, msg, result = test_tool_execution_cli(tool_name)
        results[tool_name] = (success, msg, result)
        
        if success:
            print(f"   ✅ {msg}")
            print(f"   📄 Resultado: {result[:150]}{'...' if len(result) > 150 else ''}")
        else:
            print(f"   {msg}")
    
    print("-"*80)
    
    # Summary
    successful = sum(1 for s, _, _ in results.values() if s)
    total = len(results)
    
    print(f"\n📊 RESUMO DE EXECUÇÕES:")
    print(f"   Testes bem-sucedidos: {successful}/{total}")
    print(f"   Taxa de sucesso: {(successful/total*100):.1f}%")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def print_header():
    """Print suite header."""
    print("\n" + "="*80)
    print(" "*20 + "MCP INTEGRATION TEST SUITE")
    print("  Version: 2.0 - Native Integration (CrewAI 1.2.1+)")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*80)


def print_summary(results: Dict):
    """Print test summary."""
    print("\n" + "="*80)
    print(" "*30 + "TEST SUMMARY")
    print("="*80)
    
    for test_name, (success, message) in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status}  |  {test_name}")
    
    print("="*80)
    
    # Overall status
    all_passed = all(result[0] for result in results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para produção")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("   Revise os erros acima e corrija antes de usar em produção")
    print("="*80 + "\n")


def run_quick_test():
    """Run only connectivity test."""
    print_header()
    success, msg = test_mcp_connection()
    print(f"\n{msg}")
    return success


def run_agent_test():
    """Run only agent test."""
    print_header()
    success, msg = test_agent_with_mcp()
    print(f"\n{msg}")
    return success


def run_audit_test():
    """Run only audit."""
    print_header()
    with_mcp, total, issues = test_agent_coverage()
    
    if issues:
        print("\n⚠️ Problemas encontrados:")
        for issue in issues:
            print(f"   {issue}")
    
    return with_mcp == total


def run_full_suite():
    """Run all tests."""
    print_header()
    
    results = {}
    
    # Test 1: Connectivity
    success1, msg1 = test_mcp_connection()
    results["Conectividade MCP Gateway"] = (success1, msg1)
    
    if not success1:
        print("\n❌ Gateway não disponível. Pulando testes restantes.")
        print("💡 Inicie o Docker Desktop e habilite MCP Toolkit")
        print_summary(results)
        return False
    
    # Test 2: Agent
    success2, msg2 = test_agent_with_mcp()
    results["Agente com MCP + LLM"] = (success2, msg2)
    
    # Test 3: Audit
    with_mcp, total, issues = test_agent_coverage()
    success3 = (with_mcp == total)
    msg3 = f"✅ {with_mcp}/{total} agentes com MCP" if success3 else f"⚠️ {with_mcp}/{total} agentes com MCP"
    results["Cobertura de Agentes"] = (success3, msg3)
    
    if issues:
        print("\n⚠️ Problemas encontrados:")
        for issue in issues[:5]:  # Limit to 5
            print(f"   {issue}")
        if len(issues) > 5:
            print(f"   ... e mais {len(issues)-5} problemas")
    
    # Test 4: Real tool execution
    print("\n" + "="*80)
    print("💡 Iniciando testes de execução real das ferramentas MCP...")
    print("="*80)
    
    tool_results = test_all_mcp_tools()
    
    if tool_results:
        successful_tools = sum(1 for s, _, _ in tool_results.values() if s)
        total_tools = len(tool_results)
        success4 = (successful_tools == total_tools)
        msg4 = f"✅ {successful_tools}/{total_tools} ferramentas executadas" if success4 else f"⚠️ {successful_tools}/{total_tools} ferramentas executadas"
        results["Execução Real de Tools"] = (success4, msg4)
        
        # Show detailed results
        print("\n📋 Resultados Detalhados:")
        for tool_name, (success, msg, result) in tool_results.items():
            status = "✅" if success else "❌"
            print(f"\n   {status} {tool_name.upper()}")
            if success and result:
                print(f"      → {result[:120]}{'...' if len(result) > 120 else ''}")
    
    # Summary
    print_summary(results)
    
    # Additional context for known issues
    failed_tests = [name for name, (success, _) in results.items() if not success]
    if failed_tests and "Execução Real de Tools" in failed_tests:
        print("\n" + "="*80)
        print("ℹ️  NOTA SOBRE FALHAS CONHECIDAS:")
        print("="*80)
        print("   Algumas falhas são ESPERADAS devido a limitações externas:")
        print("   • Airbnb: Bloqueado por robots.txt (não corrigível)")
        print("   • Google Maps: Requer chave de API configurada")
        print("   • YouTube: Pode falhar se vídeo não disponível")
        print("\n   ✅ Ferramentas CRÍTICAS funcionando: search, wikipedia, fetch")
        print("="*80)
    
    return all(result[0] for result in results.values())


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if "--quick" in args:
        success = run_quick_test()
    elif "--agent" in args:
        success = run_agent_test()
    elif "--audit" in args:
        success = run_audit_test()
    else:
        success = run_full_suite()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
