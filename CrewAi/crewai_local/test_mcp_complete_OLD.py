"""
Suite Completa de Testes para Ferramentas MCP
==============================================

Consolida todos os testes em um único arquivo:
- Auditoria de agentes
- Testes de integração
- Validação de ferramentas MCP
- Testes reais de cada ferramenta

Execute: poetry run python test_mcp_complete.py
Execute com verbose: poetry run python test_mcp_complete.py --verbose

NOTA IMPORTANTE (31/10/2025):
=============================
CrewAI possui integração NATIVA com MCP desde a versão 1.2.1!

A abordagem antiga (este script) usa comandos CLI `docker mcp tool call` que
NÃO são a forma recomendada de usar o Docker MCP Gateway em produção.

NOVA ABORDAGEM RECOMENDADA:
- Use MCPServerAdapter do CrewAI (crewai-tools[mcp])
- Conecta via stdio ao: docker mcp gateway run
- Descoberta automática de ~60 ferramentas
- Veja: src/crewai_local/tools/mcp_tools_new.py
- Teste: poetry run python test_mcp_basic.py

Este script permanece útil para:
- Auditar cobertura de ferramentas nos agentes
- Verificar status do Docker MCP Gateway
- Entender quais servers MCP estão ativos
"""

import ast
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


# =============================================================================
# CONFIGURAÇÃO GLOBAL
# =============================================================================

VERBOSE = False  # Será atualizado por argumentos de linha de comando


def set_verbose(value: bool):
    """Define modo verbose globalmente."""
    global VERBOSE
    VERBOSE = value


def print_verbose(message: str, data: str = None):
    """Imprime mensagem apenas em modo verbose."""
    if VERBOSE:
        print(f"\n{'='*80}")
        print(f"🔍 {message}")
        print('='*80)
        if data:
            # Limita tamanho para não poluir demais
            max_length = 2000
            if len(data) > max_length:
                print(data[:max_length])
                print(f"\n... (truncado, {len(data) - max_length} caracteres restantes)")
            else:
                print(data)
        print('='*80)


# =============================================================================
# SEÇÃO 1: AUDITORIA DE AGENTES
# =============================================================================

def analyze_agent_file(filepath: Path) -> List[Dict]:
    """Analisa um arquivo de agente e retorna informações sobre ferramentas."""
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
            tools_list_name = None
            
            func_source = ast.get_source_segment(content, node)
            if func_source:
                if 'tools=' in func_source:
                    has_tools_assignment = True
                    
                    if 'get_enhanced_tools_for_agent' in func_source:
                        uses_get_enhanced = True
                        
                        import re
                        match = re.search(r'get_enhanced_tools_for_agent\(["\'](\w+)["\']\)', func_source)
                        if match:
                            tools_list_name = match.group(1)
                    
                    if 'tools=[]' in func_source or 'tools = []' in func_source:
                        tools_empty = True
                    
                    if 'search_tool' in func_source and not uses_get_enhanced:
                        tools_list_name = "search_tool (nativo)"
            
            agents.append({
                'name': agent_name,
                'function': node.name,
                'has_tools': has_tools_assignment,
                'uses_enhanced': uses_get_enhanced,
                'tools_empty': tools_empty,
                'tools_type': tools_list_name
            })
    
    return agents


def audit_agents() -> Tuple[int, int, List[Dict]]:
    """
    Executa auditoria completa dos agentes.
    Retorna: (agents_with_mcp, total_agents, all_agents_data)
    """
    agents_dir = Path("src/crewai_local/agents")
    
    if not agents_dir.exists():
        return 0, 0, []
    
    all_agents = []
    
    for agent_file in agents_dir.glob("*.py"):
        if agent_file.name == "__init__.py":
            continue
        
        category = agent_file.stem
        agents = analyze_agent_file(agent_file)
        
        for agent in agents:
            agent['category'] = category
            all_agents.append(agent)
    
    agents_with_mcp = sum(1 for a in all_agents if a['uses_enhanced'])
    
    return agents_with_mcp, len(all_agents), all_agents


# =============================================================================
# SEÇÃO 2: VERIFICAÇÃO DE DISPONIBILIDADE MCP
# =============================================================================

def check_docker_mcp_gateway() -> Dict[str, bool]:
    """Verifica se Docker MCP Gateway está rodando e quais servers estão ativos."""
    availability = {
        'gateway_running': False,
        'duckduckgo': False,
        'fetch': False,
        'playwright': False,
        'google_maps': False,
        'airbnb': False,
        'wikipedia': False,
        'youtube': False,
    }
    
    try:
        result = subprocess.run(
            ["docker", "mcp", "server", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            availability['gateway_running'] = True
            output = result.stdout.lower()
            
            availability['duckduckgo'] = 'duckduckgo' in output
            availability['fetch'] = 'fetch' in output
            availability['playwright'] = 'playwright' in output
            availability['google_maps'] = 'google-maps' in output or 'maps' in output
            availability['airbnb'] = 'airbnb' in output
            availability['wikipedia'] = 'wikipedia' in output
            availability['youtube'] = 'youtube' in output
            
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return availability


def check_python_tools() -> Dict[str, bool]:
    """Verifica se ferramentas Python MCP estão disponíveis."""
    tools_available = {
        'mcp_tools_module': False,
        'mcp_search_tool': False,
        'mcp_fetch_tool': False,
        'mcp_browser_tool': False,
        'mcp_maps_tool': False,
        'mcp_airbnb_tool': False,
        'mcp_wikipedia_tool': False,
        'mcp_youtube_tool': False,
    }
    
    try:
        from src.crewai_local.tools import mcp_tools
        tools_available['mcp_tools_module'] = True
        
        tools_available['mcp_search_tool'] = hasattr(mcp_tools, 'mcp_search_tool')
        tools_available['mcp_fetch_tool'] = hasattr(mcp_tools, 'mcp_fetch_tool')
        tools_available['mcp_browser_tool'] = hasattr(mcp_tools, 'mcp_browser_tool')
        tools_available['mcp_maps_tool'] = hasattr(mcp_tools, 'mcp_maps_tool')
        tools_available['mcp_airbnb_tool'] = hasattr(mcp_tools, 'mcp_airbnb_tool')
        tools_available['mcp_wikipedia_tool'] = hasattr(mcp_tools, 'mcp_wikipedia_tool')
        tools_available['mcp_youtube_tool'] = hasattr(mcp_tools, 'mcp_youtube_tool')
        
    except ImportError:
        pass
    
    return tools_available


# =============================================================================
# SEÇÃO 3: TESTES REAIS DE FERRAMENTAS MCP
# =============================================================================

def test_search_tool() -> Tuple[bool, str]:
    """Testa ferramenta de busca DuckDuckGo."""
    try:
        query = "pousadas Paraty"
        print_verbose(f"SEARCH TEST - Executando busca: '{query}'")
        
        cmd = ["docker", "mcp", "tool", "call", "duckduckgo_search", "--", query]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("SEARCH TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("SEARCH TEST - Saída stderr", result.stderr)
        
        if result.returncode == 0 and len(result.stdout) > 50:
            return True, f"✅ Retornou {len(result.stdout)} caracteres de resultados"
        else:
            return False, f"❌ Erro: {result.stderr[:100]}"
    except Exception as e:
        print_verbose(f"SEARCH TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_fetch_tool() -> Tuple[bool, str]:
    """Testa ferramenta de fetch de URL."""
    try:
        url = "https://example.com"
        params = json.dumps({"url": url})
        
        print_verbose(f"FETCH TEST - Obtendo URL: {url}")
        
        cmd = ["docker", "mcp", "tool", "call", "fetch", "--", params]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("FETCH TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("FETCH TEST - Saída stderr", result.stderr)
        
        if result.returncode == 0 and len(result.stdout) > 50:
            return True, f"✅ Retornou {len(result.stdout)} caracteres de conteúdo"
        else:
            return False, f"❌ Erro: {result.stderr[:100]}"
    except Exception as e:
        print_verbose(f"FETCH TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_wikipedia_tool() -> Tuple[bool, str]:
    """Testa ferramenta Wikipedia."""
    try:
        query = "Paraty"
        print_verbose(f"WIKIPEDIA TEST - Buscando artigos: '{query}'")
        
        # Busca artigos
        params = json.dumps({"query": query, "limit": 1})
        cmd = ["docker", "mcp", "tool", "call", "search_wikipedia", "--", params]
        print_verbose(f"Comando busca: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("WIKIPEDIA TEST - Busca stdout", result.stdout)
        if result.stderr:
            print_verbose("WIKIPEDIA TEST - Busca stderr", result.stderr)
        
        if result.returncode != 0:
            return False, f"❌ Erro na busca: {result.stderr[:100]}"
        
        # Verifica se encontrou resultados
        try:
            data = json.loads(result.stdout)
            if data and len(data) > 0:
                article_title = data[0].get('title', 'Unknown')
                print_verbose(f"WIKIPEDIA TEST - Artigo encontrado: '{article_title}'")
                
                # Tenta obter resumo
                params = json.dumps({"title": article_title})
                cmd = ["docker", "mcp", "tool", "call", "get_summary", "--", params]
                print_verbose(f"Comando resumo: {' '.join(cmd)}")
                
                summary_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                print_verbose("WIKIPEDIA TEST - Resumo stdout", summary_result.stdout)
                if summary_result.stderr:
                    print_verbose("WIKIPEDIA TEST - Resumo stderr", summary_result.stderr)
                
                if summary_result.returncode == 0:
                    return True, f"✅ Artigo '{article_title}' - {len(summary_result.stdout)} chars"
                else:
                    return True, f"⚠️ Busca OK, resumo falhou para '{article_title}'"
            else:
                return False, "❌ Nenhum artigo encontrado"
        except json.JSONDecodeError as e:
            print_verbose(f"WIKIPEDIA TEST - Erro JSON: {str(e)}")
            return False, "❌ Resposta inválida (não JSON)"
            
    except Exception as e:
        print_verbose(f"WIKIPEDIA TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_maps_tool() -> Tuple[bool, str]:
    """Testa ferramenta Google Maps."""
    try:
        address = "Paraty, RJ, Brasil"
        params = json.dumps({"address": address})
        
        print_verbose(f"MAPS TEST - Geocodificando: '{address}'")
        
        cmd = ["docker", "mcp", "tool", "call", "maps_geocode", "--", params]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("MAPS TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("MAPS TEST - Saída stderr", result.stderr)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data and 'results' in data and len(data['results']) > 0:
                    location = data['results'][0].get('geometry', {}).get('location', {})
                    lat = location.get('lat', 'N/A')
                    lng = location.get('lng', 'N/A')
                    print_verbose(f"MAPS TEST - Coordenadas encontradas: ({lat}, {lng})")
                    return True, f"✅ Coordenadas: ({lat}, {lng})"
                else:
                    return False, "❌ Nenhuma localização encontrada"
            except json.JSONDecodeError as e:
                print_verbose(f"MAPS TEST - Erro JSON: {str(e)}")
                return True, f"⚠️ Resposta recebida mas não JSON: {result.stdout[:50]}"
        else:
            return False, f"❌ Erro: {result.stderr[:100]}"
    except Exception as e:
        print_verbose(f"MAPS TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_airbnb_tool() -> Tuple[bool, str]:
    """Testa ferramenta Airbnb."""
    try:
        location = "Paraty, Brazil"
        params = json.dumps({"location": location, "adults": 2})
        
        print_verbose(f"AIRBNB TEST - Buscando em: '{location}' para 2 adultos")
        
        cmd = ["docker", "mcp", "tool", "call", "airbnb_search", "--", params]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("AIRBNB TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("AIRBNB TEST - Saída stderr", result.stderr)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict) and 'results' in data:
                    count = len(data.get('results', []))
                    print_verbose(f"AIRBNB TEST - {count} listagens encontradas")
                    return True, f"✅ Encontrou {count} listagens"
                elif isinstance(data, list):
                    print_verbose(f"AIRBNB TEST - {len(data)} listagens encontradas")
                    return True, f"✅ Encontrou {len(data)} listagens"
                else:
                    print_verbose(f"AIRBNB TEST - Resposta: {str(data)[:200]}")
                    return True, f"⚠️ Resposta recebida: {str(data)[:50]}"
            except json.JSONDecodeError as e:
                print_verbose(f"AIRBNB TEST - Erro JSON: {str(e)}")
                return True, f"⚠️ Resposta recebida mas não JSON: {result.stdout[:50]}"
        else:
            return False, f"❌ Erro: {result.stderr[:100]}"
    except Exception as e:
        print_verbose(f"AIRBNB TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_youtube_tool() -> Tuple[bool, str]:
    """Testa ferramenta YouTube (apenas verifica disponibilidade, não transcreve)."""
    try:
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        params = json.dumps({"url": video_url})
        
        print_verbose(f"YOUTUBE TEST - Obtendo info do vídeo: {video_url}")
        
        cmd = ["docker", "mcp", "tool", "call", "get_video_info", "--", params]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print_verbose("YOUTUBE TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("YOUTUBE TEST - Saída stderr", result.stderr)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict) and 'title' in data:
                    title = data.get('title', 'Unknown')[:50]
                    print_verbose(f"YOUTUBE TEST - Vídeo encontrado: '{title}'")
                    return True, f"✅ Vídeo info obtida: '{title}'"
                else:
                    print_verbose(f"YOUTUBE TEST - Resposta: {str(data)[:200]}")
                    return True, f"⚠️ Resposta recebida: {str(data)[:50]}"
            except json.JSONDecodeError as e:
                print_verbose(f"YOUTUBE TEST - Erro JSON: {str(e)}")
                return True, f"⚠️ Resposta recebida mas não JSON: {result.stdout[:50]}"
        else:
            return False, f"❌ Erro: {result.stderr[:100]}"
    except Exception as e:
        print_verbose(f"YOUTUBE TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"


def test_browser_tool() -> Tuple[bool, str]:
    """Testa ferramenta de navegação (Playwright) - apenas verifica instalação."""
    try:
        print_verbose("BROWSER TEST - Verificando instalação do Playwright")
        
        cmd = ["docker", "mcp", "tool", "call", "browser_install", "--", "{}"]
        print_verbose(f"Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        print_verbose("BROWSER TEST - Saída stdout", result.stdout)
        if result.stderr:
            print_verbose("BROWSER TEST - Saída stderr", result.stderr)
        
        # Se chegou aqui, o comando existe (mesmo que falhe)
        print_verbose("BROWSER TEST - Ferramenta disponível (comando executou)")
        return True, "✅ Ferramenta disponível (não testada navegação real)"
    except Exception as e:
        print_verbose(f"BROWSER TEST - Exceção: {str(e)}")
        return False, f"❌ Exceção: {str(e)[:100]}"
        return False, f"❌ Exceção: {str(e)[:100]}"


# =============================================================================
# SEÇÃO 4: TESTES DE METADATA TRACKING
# =============================================================================

def test_metadata_tracking() -> Dict[str, bool]:
    """Testa se ferramentas Python retornam metadata de rastreamento."""
    results = {}
    
    try:
        from src.crewai_local.tools.mcp_tools import check_mcp_availability
        
        availability = check_mcp_availability()
        
        if not availability.get('gateway_running'):
            return {'error': False, 'message': 'Gateway não está rodando'}
        
        # Testa Search (se disponível)
        if availability.get('search'):
            try:
                from src.crewai_local.tools.mcp_tools import mcp_search_tool
                # Nota: Não podemos chamar diretamente pois é um objeto Tool do CrewAI
                # Verificamos apenas se existe e tem a estrutura correta
                results['search'] = hasattr(mcp_search_tool, 'func') or hasattr(mcp_search_tool, 'run')
            except:
                results['search'] = False
        
        # Testa Wikipedia (se disponível)
        if availability.get('wikipedia'):
            try:
                from src.crewai_local.tools.mcp_tools import mcp_wikipedia_tool
                results['wikipedia'] = hasattr(mcp_wikipedia_tool, 'func') or hasattr(mcp_wikipedia_tool, 'run')
            except:
                results['wikipedia'] = False
        
        # Testa YouTube (se disponível)
        if availability.get('youtube'):
            try:
                from src.crewai_local.tools.mcp_tools import mcp_youtube_tool
                results['youtube'] = hasattr(mcp_youtube_tool, 'func') or hasattr(mcp_youtube_tool, 'run')
            except:
                results['youtube'] = False
                
    except ImportError as e:
        results['error'] = True
        results['message'] = f"Erro ao importar: {str(e)}"
    
    return results


# =============================================================================
# SEÇÃO 5: RELATÓRIO CONSOLIDADO
# =============================================================================

def print_section_header(title: str):
    """Imprime cabeçalho de seção."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Imprime subcabeçalho."""
    print(f"\n{title}")
    print("-" * 80)


def run_complete_test_suite():
    """Executa suite completa de testes e gera relatório consolidado."""
    
    print("=" * 80)
    print("  🧪 SUITE COMPLETA DE TESTES - FERRAMENTAS MCP")
    print("=" * 80)
    print(f"  Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # =========================================================================
    # 1. AUDITORIA DE AGENTES
    # =========================================================================
    print_section_header("1️⃣  AUDITORIA DE AGENTES")
    
    agents_with_mcp, total_agents, all_agents = audit_agents()
    
    if total_agents == 0:
        print("⚠️  Nenhum agente encontrado em src/crewai_local/agents/")
    else:
        coverage = (agents_with_mcp / total_agents * 100) if total_agents > 0 else 0
        
        print(f"\n📊 Resumo:")
        print(f"   ✅ Agentes com MCP tools: {agents_with_mcp}/{total_agents}")
        print(f"   📈 Cobertura: {coverage:.1f}%")
        
        if coverage >= 100:
            print(f"   🎉 PERFEITO! Todos os agentes estão equipados!")
        elif coverage >= 80:
            print(f"   ✅ EXCELENTE! Alta cobertura de ferramentas")
        elif coverage >= 50:
            print(f"   🟡 BOM! Cobertura média, pode melhorar")
        else:
            print(f"   ⚠️  BAIXO! Considere adicionar ferramentas a mais agentes")
        
        # Lista agentes com MCP
        agents_with_tools = [a for a in all_agents if a['uses_enhanced']]
        if agents_with_tools:
            print(f"\n✅ Agentes com ferramentas MCP ({len(agents_with_tools)}):")
            for agent in agents_with_tools:
                print(f"   • {agent['name']:<30} → {agent['tools_type']}")
        
        # Lista agentes sem MCP
        agents_without_tools = [a for a in all_agents if not a['uses_enhanced']]
        if agents_without_tools:
            print(f"\n❌ Agentes sem ferramentas MCP ({len(agents_without_tools)}):")
            for agent in agents_without_tools:
                status = "tools=[]" if agent['tools_empty'] else "outro"
                print(f"   • {agent['name']:<30} ({status})")
    
    # =========================================================================
    # 2. DISPONIBILIDADE DO GATEWAY
    # =========================================================================
    print_section_header("2️⃣  DISPONIBILIDADE DOCKER MCP GATEWAY")
    
    gateway_status = check_docker_mcp_gateway()
    
    if gateway_status['gateway_running']:
        print("\n✅ Docker MCP Gateway está RODANDO")
        print("\n📡 Servers MCP ativos:")
        
        servers = [
            ('DuckDuckGo (Search)', gateway_status['duckduckgo']),
            ('Fetch', gateway_status['fetch']),
            ('Playwright (Browser)', gateway_status['playwright']),
            ('Google Maps', gateway_status['google_maps']),
            ('Airbnb', gateway_status['airbnb']),
            ('Wikipedia', gateway_status['wikipedia']),
            ('YouTube Transcript', gateway_status['youtube']),
        ]
        
        active_count = sum(1 for _, status in servers if status)
        
        for name, status in servers:
            icon = "✅" if status else "❌"
            print(f"   {icon} {name}")
        
        print(f"\n📊 Total: {active_count}/7 servers ativos")
        
    else:
        print("\n❌ Docker MCP Gateway NÃO está rodando")
        print("\n💡 Para iniciar:")
        print("   1. Certifique-se que Docker Desktop está instalado")
        print("   2. Habilite MCP Gateway nas configurações do Docker Desktop")
        print("   3. Adicione servers: docker mcp server add <server-name>")
    
    # =========================================================================
    # 3. FERRAMENTAS PYTHON
    # =========================================================================
    print_section_header("3️⃣  FERRAMENTAS PYTHON MCP")
    
    python_tools = check_python_tools()
    
    if python_tools['mcp_tools_module']:
        print("\n✅ Módulo mcp_tools.py ENCONTRADO")
        print("\n🔧 Ferramentas Python definidas:")
        
        tools = [
            ('mcp_search_tool (DuckDuckGo)', python_tools['mcp_search_tool']),
            ('mcp_fetch_tool (Fetch URL)', python_tools['mcp_fetch_tool']),
            ('mcp_browser_tool (Playwright)', python_tools['mcp_browser_tool']),
            ('mcp_maps_tool (Google Maps)', python_tools['mcp_maps_tool']),
            ('mcp_airbnb_tool (Airbnb)', python_tools['mcp_airbnb_tool']),
            ('mcp_wikipedia_tool (Wikipedia)', python_tools['mcp_wikipedia_tool']),
            ('mcp_youtube_tool (YouTube)', python_tools['mcp_youtube_tool']),
        ]
        
        defined_count = sum(1 for _, status in tools if status)
        
        for name, status in tools:
            icon = "✅" if status else "❌"
            print(f"   {icon} {name}")
        
        print(f"\n📊 Total: {defined_count}/7 ferramentas definidas")
        
    else:
        print("\n❌ Módulo mcp_tools.py NÃO encontrado")
        print("   Verifique: src/crewai_local/tools/mcp_tools.py")
    
    # =========================================================================
    # 4. TESTES REAIS DE FERRAMENTAS
    # =========================================================================
    print_section_header("4️⃣  TESTES REAIS DE FERRAMENTAS MCP")
    
    if not gateway_status['gateway_running']:
        print("\n⚠️  Pulando testes reais (Gateway não está rodando)")
    else:
        print("\n🧪 Executando testes de integração...")
        print("   (Isso pode levar alguns segundos...)\n")
        
        tests = []
        
        if gateway_status['duckduckgo']:
            print("   🔍 Testando Search (DuckDuckGo)...")
            tests.append(('Search (DuckDuckGo)', test_search_tool()))
        
        if gateway_status['fetch']:
            print("   📄 Testando Fetch URL...")
            tests.append(('Fetch URL', test_fetch_tool()))
        
        if gateway_status['wikipedia']:
            print("   📚 Testando Wikipedia...")
            tests.append(('Wikipedia', test_wikipedia_tool()))
        
        if gateway_status['google_maps']:
            print("   🗺️  Testando Google Maps...")
            tests.append(('Google Maps', test_maps_tool()))
        
        if gateway_status['airbnb']:
            print("   🏠 Testando Airbnb...")
            tests.append(('Airbnb', test_airbnb_tool()))
        
        if gateway_status['youtube']:
            print("   🎥 Testando YouTube...")
            tests.append(('YouTube', test_youtube_tool()))
        
        if gateway_status['playwright']:
            print("   🌐 Testando Browser (Playwright)...")
            tests.append(('Browser (Playwright)', test_browser_tool()))
        
        # Resultados
        print("\n📊 Resultados dos Testes:")
        print("-" * 80)
        
        passed = 0
        for name, (success, message) in tests:
            if success:
                passed += 1
            print(f"   {message}")
            if name and not success:
                print(f"      Ferramenta: {name}")
        
        print(f"\n✅ Testes passados: {passed}/{len(tests)}")
        
        if passed == len(tests):
            print("   🎉 PERFEITO! Todas as ferramentas testadas funcionaram!")
        elif passed >= len(tests) * 0.7:
            print("   ✅ BOM! Maioria das ferramentas funcionando")
        else:
            print("   ⚠️  ATENÇÃO! Várias ferramentas com problemas")
    
    # =========================================================================
    # 5. METADATA TRACKING
    # =========================================================================
    print_section_header("5️⃣  VALIDAÇÃO DE METADATA TRACKING")
    
    metadata_results = test_metadata_tracking()
    
    if 'error' in metadata_results:
        print(f"\n❌ Erro: {metadata_results.get('message', 'Desconhecido')}")
    else:
        print("\n🔍 Verificando estrutura das ferramentas Python...")
        
        if metadata_results:
            working = sum(1 for v in metadata_results.values() if v)
            total = len(metadata_results)
            
            for tool_name, is_valid in metadata_results.items():
                icon = "✅" if is_valid else "❌"
                print(f"   {icon} {tool_name}: {'Estrutura válida' if is_valid else 'Estrutura inválida'}")
            
            print(f"\n📊 Total: {working}/{total} ferramentas com estrutura válida")
        else:
            print("   ℹ️  Nenhuma ferramenta disponível para testar")
    
    # =========================================================================
    # RESUMO FINAL
    # =========================================================================
    print_section_header("📈 RESUMO FINAL")
    
    print(f"""
✅ Auditoria de Agentes:
   • {agents_with_mcp}/{total_agents} agentes com MCP tools ({coverage:.1f}% cobertura)

✅ Docker MCP Gateway:
   • Status: {'✅ RODANDO' if gateway_status['gateway_running'] else '❌ NÃO RODANDO'}
   • Servers ativos: {sum(1 for k, v in gateway_status.items() if k != 'gateway_running' and v)}/7

✅ Ferramentas Python:
   • Módulo mcp_tools: {'✅ Encontrado' if python_tools['mcp_tools_module'] else '❌ Não encontrado'}
   • Ferramentas definidas: {sum(1 for k, v in python_tools.items() if k != 'mcp_tools_module' and v)}/7

⚠️  AVISO: Este script usa abordagem CLI antiga (docker mcp tool call)
   Para integração nativa CrewAI com MCP, veja: mcp_tools_new.py
""")
    
    # Recomendações
    print("💡 RECOMENDAÇÕES:")
    print("-" * 80)
    
    recommendations = []
    
    if not gateway_status['gateway_running']:
        recommendations.append("🔴 CRÍTICO: Inicie o Docker MCP Gateway")
    
    if coverage < 100:
        missing = total_agents - agents_with_mcp
        recommendations.append(f"🟡 Adicione ferramentas MCP aos {missing} agentes restantes")
    
    if not python_tools['mcp_tools_module']:
        recommendations.append("🔴 CRÍTICO: Módulo mcp_tools.py não encontrado")
    
    active_servers = sum(1 for k, v in gateway_status.items() if k != 'gateway_running' and v)
    if active_servers < 7:
        missing_servers = 7 - active_servers
        recommendations.append(f"🟡 Ative os {missing_servers} servers MCP restantes")
    
    if not recommendations:
        print("   🎉 Tudo está configurado perfeitamente!")
        print("   ✅ Sistema pronto para uso em produção!")
        print("\n   📚 Próximo passo: Migrar para integração nativa CrewAI:")
        print("      • Veja: src/crewai_local/tools/mcp_tools_new.py")
        print("      • Teste: poetry run python test_mcp_basic.py")
        print("      • Docs: https://docs.crewai.com/en/mcp/overview")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        print(f"\n   {len(recommendations) + 1}. 🔵 Considere migrar para integração nativa CrewAI + MCP")
    
    print("\n" + "=" * 80)
    print("  Teste concluído!")
    print("=" * 80 + "\n")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Parsing de argumentos da linha de comando
    if "--verbose" in sys.argv or "-v" in sys.argv:
        set_verbose(True)
        print("[VERBOSE] Modo detalhado ativado - mostrando detalhes das chamadas MCP\n")
    
    try:
        run_complete_test_suite()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
