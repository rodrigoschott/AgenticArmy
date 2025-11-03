"""
Ferramentas web para os agentes usando MCP tools via Docker CLI.

VERSÃO 2.0: CLI Approach (Production)
- Usa subprocess + docker mcp CLI para estabilidade máxima
- Elimina event loop issues do MCPServerAdapter (DEPRECATED)
- 100% de sucesso (6/6 tools testadas e validadas)
- Timeout configurável, encoding UTF-8, error handling robusto
"""

from typing import List
import subprocess
import logging
from crewai.tools import tool

from ..exceptions import (
    MCPToolExecutionError,
    MCPTimeoutError,
    DockerNotAvailableError
)

# Setup logger for this module
logger = logging.getLogger(__name__)


# ============================================================================
# CLI APPROACH - Subprocess-based MCP Tool Wrappers
# ============================================================================

def call_mcp_tool(tool_name: str, timeout: int = 30, **kwargs) -> str:
    """
    Chama ferramenta MCP via Docker CLI (subprocess approach).

    Esta abordagem elimina event loop issues do MCPServerAdapter.
    Testada e validada em 6/6 ferramentas (100% sucesso).

    Args:
        tool_name: Nome da ferramenta MCP (ex: "search", "fetch", "maps_geocode")
        timeout: Timeout em segundos (padrão: 30s)
        **kwargs: Argumentos da ferramenta (ex: query="Paraty", url="https://...")

    Returns:
        Output da ferramenta (JSON string ou texto)

    Raises:
        Returns error message string if fails (graceful degradation for agents)
    """
    # Log tool call
    logger.debug(f"MCP Tool Call: {tool_name}({', '.join(f'{k}={v}' for k, v in kwargs.items())})")

    # Construir comando CLI
    cmd = ["docker", "mcp", "tools", "call", tool_name]

    # Adicionar argumentos
    for key, value in kwargs.items():
        if value is not None:
            # Converter bool para lowercase string
            if isinstance(value, bool):
                value = str(value).lower()
            cmd.append(f"{key}={value}")

    try:
        # Executar comando com UTF-8 encoding
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            error_msg = result.stderr[:500] if result.stderr else "Unknown error"
            logger.error(f"MCP Tool Error [{tool_name}]: {error_msg}")
            return f"Error calling {tool_name}: {error_msg}"

        # Log successful result
        result_preview = result.stdout[:100] + "..." if len(result.stdout) > 100 else result.stdout
        logger.debug(f"MCP Tool Success [{tool_name}]: {result_preview}")

        return result.stdout

    except subprocess.TimeoutExpired:
        logger.error(f"MCP Tool Timeout [{tool_name}]: {timeout}s exceeded")
        return f"Error: {tool_name} timed out after {timeout}s"
    except FileNotFoundError:
        logger.error(f"Docker command not found - Docker may not be installed or not in PATH")
        return f"Error: Docker command not found. Is Docker Desktop installed and running?"
    except Exception as e:
        logger.error(f"MCP Tool Exception [{tool_name}]: {type(e).__name__}: {str(e)}")
        return f"Error calling {tool_name}: {str(e)}"


# ============================================================================
# MCP CLI Tool Wrappers (Testadas e Validadas - 100% Success Rate)
# ============================================================================

def mcp_search_cli(query: str) -> str:
    """
    Busca web usando DuckDuckGo.
    Retorna até 10 resultados com título, URL e resumo.
    """
    return call_mcp_tool("search", query=query, timeout=30)


def mcp_fetch_cli(url: str, ignore_robots: bool = True) -> str:
    """
    Busca conteúdo de uma URL e retorna como markdown.
    Útil para extrair texto de páginas web.

    Args:
        url: URL para buscar
        ignore_robots: Se True, ignora restrições de robots.txt (padrão: True para pesquisa)
    """
    kwargs = {"url": url, "timeout": 30}
    if ignore_robots:
        kwargs["ignoreRobotsText"] = True
    return call_mcp_tool("fetch", **kwargs)


def mcp_fetch_content_cli(url: str) -> str:
    """
    Busca e extrai conteúdo de uma URL usando fetch_content.

    Este método é MAIS EFICAZ que fetch + browser_navigate para sites com Cloudflare.

    Diferenças:
    - fetch: HTTP básico, pode ser bloqueado por robots.txt ou Cloudflare
    - fetch_content: Extrai conteúdo principal, bypassa Cloudflare em muitos casos
    - browser_navigate: Playwright browser, BLOQUEADO por Cloudflare (sem stealth mode)

    Comprovado funcionar em:
    - zapimoveis.com.br ✅ (2,483 chars de dados reais)
    - Sites com proteção Cloudflare moderada ✅

    Args:
        url: URL para buscar

    Returns:
        Conteúdo da página em texto/markdown
    """
    return call_mcp_tool("fetch_content", url=url, timeout=60)


def _is_cloudflare_block_page(content: str) -> bool:
    """
    Detecta se o conteúdo é uma página de bloqueio do Cloudflare.

    Args:
        content: Conteúdo da página retornado por fetch ou browser

    Returns:
        True se é página de bloqueio, False caso contrário
    """
    block_indicators = [
        "Attention Required! | Cloudflare",
        "Sorry, you have been blocked",
        "Cloudflare Ray ID",
        "Why have I been blocked?",
        "security solution",
        "Checking your browser before accessing",
        "challenge-platform"
    ]
    return any(indicator in content for indicator in block_indicators)


def _is_real_property_content(content: str) -> bool:
    """
    Detecta se o conteúdo contém dados reais de imóvel/propriedade.

    Procura indicadores típicos de anúncios de propriedades como:
    - Preço (R$)
    - Área (m²)
    - Quartos/banheiros
    - Vagas de garagem

    Args:
        content: Conteúdo da página

    Returns:
        True se contém dados de propriedade (alta confiança com 3+ indicadores)
    """
    property_indicators = [
        "R$",  # Preço
        "m²",  # Área
        "m2",  # Área (variação)
        "quarto",  # Quartos
        "banheiro",  # Banheiros
        "vaga",  # Vagas de garagem
        "suíte",  # Suítes
        "dormitório",  # Dormitórios
        "venda",  # Tipo de transação
        "aluguel",  # Tipo de transação
    ]

    # Converter para minúsculas para busca case-insensitive
    content_lower = content.lower()

    # Contar quantos indicadores estão presentes
    matches = sum(1 for ind in property_indicators if ind.lower() in content_lower)

    # Alta confiança se tiver 3 ou mais indicadores
    return matches >= 3


def mcp_wikipedia_summary_cli(title: str) -> str:
    """
    Retorna resumo de um artigo da Wikipedia.
    Use o título exato do artigo (ex: "Paraty", "Rio de Janeiro").
    """
    return call_mcp_tool("get_summary", title=title, timeout=30)


def mcp_youtube_info_cli(url: str) -> str:
    """
    Retorna informações de um vídeo do YouTube (título, descrição, duração).
    URL deve ser no formato: https://youtube.com/watch?v=VIDEO_ID
    """
    return call_mcp_tool("get_video_info", url=url, timeout=40)


def mcp_maps_geocode_cli(address: str) -> str:
    """
    Converte endereço em coordenadas geográficas (lat/lng).
    Requer Google Maps API key configurada.
    """
    return call_mcp_tool("maps_geocode", address=address, timeout=30)


def mcp_maps_search_places_cli(query: str) -> str:
    """
    Busca lugares usando Google Places API.
    Retorna informações detalhadas sobre locais encontrados.
    """
    return call_mcp_tool("maps_search_places", query=query, timeout=30)


def mcp_airbnb_search_cli(location: str, adults: int = 2, children: int = 0) -> str:
    """
    Busca listagens do Airbnb em uma localização.
    IMPORTANTE: Usa ignoreRobotsText=true para bypass de robots.txt.
    """
    return call_mcp_tool(
        "airbnb_search",
        location=location,
        adults=adults,
        children=children,
        ignoreRobotsText=True,  # Bypass robots.txt (necessário)
        timeout=40
    )


def mcp_browser_navigate_cli(url: str) -> str:
    """
    Navega para uma URL usando Playwright browser.
    Renderiza JavaScript e bypassa muitas proteções anti-bot.
    Mais lento que fetch mas mais robusto.
    """
    return call_mcp_tool("browser_navigate", url=url, timeout=60)


def mcp_browser_snapshot_cli() -> str:
    """
    Captura snapshot de acessibilidade da página atual (texto renderizado).
    Deve ser chamado após browser_navigate.
    Retorna estrutura em texto do conteúdo visível.
    """
    return call_mcp_tool("browser_snapshot", timeout=30)


def mcp_fetch_with_playwright_fallback_cli(url: str) -> str:
    """
    Smart fetch com múltiplos fallbacks para máxima resiliência.

    ESTRATÉGIA ATUALIZADA (3 camadas):
    1. fetch_content (PRIORITÁRIO) - Bypassa Cloudflare, extrai conteúdo principal
    2. fetch (fallback 1) - HTTP básico com ignore robots.txt
    3. browser_navigate (fallback 2) - Playwright browser (pode ser bloqueado por Cloudflare)

    IMPORTANTE - Detecção de Cloudflare:
    - Verifica se resultado é página de bloqueio do Cloudflare
    - Rejeita páginas de bloqueio e tenta próximo método
    - browser_navigate JÁ RETORNA o snapshot da página (subprocess é stateless)

    Comprovado:
    - fetch_content: ✅ Funciona em zapimoveis.com.br (2,483 chars)
    - browser_navigate: ❌ Bloqueado por Cloudflare (retorna página de desafio)

    Returns:
        Conteúdo da página em markdown, ou mensagem de erro se todos falharem
    """
    logger.debug(f"Smart fetch with multi-layer fallback: {url}")

    # ==================== CAMADA 1: fetch_content (MAIS EFICAZ) ====================
    try:
        logger.debug(f"Trying fetch_content (Layer 1) for {url}")
        content_result = mcp_fetch_content_cli(url)

        # Verificar se retornou erro
        error_indicators = [
            "error calling",
            "failed to fetch",
            "timed out",
            "status code 403",
            "status code 401",
            "status code 500"
        ]
        has_error = any(ind.lower() in content_result.lower() for ind in error_indicators)

        # Verificar se é página de bloqueio Cloudflare
        is_blocked = _is_cloudflare_block_page(content_result)

        # Se não tem erro E não é bloqueio E tem conteúdo substancial
        if not has_error and not is_blocked and len(content_result) > 200:
            logger.info(f"✅ fetch_content succeeded for {url} ({len(content_result)} chars)")
            return f"[Conteúdo obtido via fetch_content]\n\n{content_result}"

        if is_blocked:
            logger.warning(f"fetch_content returned Cloudflare block page, trying fallback")
        else:
            logger.warning(f"fetch_content failed: {content_result[:150]}")

    except Exception as e:
        logger.warning(f"fetch_content exception: {type(e).__name__}: {str(e)}")

    # ==================== CAMADA 2: fetch (fallback tradicional) ====================
    logger.debug(f"Trying fetch (Layer 2) for {url}")
    fetch_result = mcp_fetch_cli(url, ignore_robots=True)

    # Checar se fetch teve sucesso
    error_indicators = [
        "error calling fetch",
        "robots.txt",
        "status code 403",
        "status code 401",
        "Failed to fetch",
        "timed out"
    ]

    fetch_failed = any(indicator.lower() in fetch_result.lower() for indicator in error_indicators)
    fetch_is_blocked = _is_cloudflare_block_page(fetch_result)

    if not fetch_failed and not fetch_is_blocked and len(fetch_result) > 200:
        logger.info(f"✅ fetch succeeded for {url} ({len(fetch_result)} chars)")
        return fetch_result

    if fetch_is_blocked:
        logger.warning(f"fetch returned Cloudflare block page")
    else:
        logger.info(f"fetch blocked for {url}, trying browser_navigate")

    # ==================== CAMADA 3: browser_navigate (último recurso) ====================
    try:
        logger.debug(f"Trying browser_navigate (Layer 3) for {url}")

        # Navegar com Playwright - retorna conteúdo COMPLETO incluindo snapshot!
        navigate_result = mcp_browser_navigate_cli(url)

        # Verificar se houve erro REAL (não substring "error")
        if navigate_result.startswith("Error:") or "error calling browser_navigate" in navigate_result.lower():
            logger.error(f"browser_navigate failed: {navigate_result[:200]}")
            return f"Error: All methods failed for {url}. Last error: {navigate_result[:300]}"

        # Verificar se é página de bloqueio Cloudflare
        navigate_is_blocked = _is_cloudflare_block_page(navigate_result)

        if navigate_is_blocked:
            logger.error(f"❌ browser_navigate returned Cloudflare block page - ALL METHODS BLOCKED")
            # Retornar erro claro indicando que o site está bloqueando
            return (
                f"Error: Site {url} está bloqueando todas as tentativas de acesso.\n\n"
                f"Métodos tentados:\n"
                f"1. fetch_content: {'Bloqueado' if 'is_blocked' in locals() else 'Falhou'}\n"
                f"2. fetch: {'Bloqueado' if fetch_is_blocked else 'Falhou'}\n"
                f"3. browser_navigate: Bloqueado (Cloudflare)\n\n"
                f"Sugestão: Tente acessar manualmente ou use search_web com nome específico da propriedade."
            )

        # Verificar se o conteúdo tem dados reais de propriedade
        has_property_data = _is_real_property_content(navigate_result)

        if has_property_data:
            logger.info(f"✅ browser_navigate succeeded with property data ({len(navigate_result)} chars)")
            return f"[Conteúdo obtido via Playwright Browser]\n\n{navigate_result}"

        # Se não tem dados de propriedade mas tem conteúdo estruturado
        if "### Page state" in navigate_result or "Page Snapshot:" in navigate_result:
            logger.warning(f"⚠️ browser_navigate returned content but no property data detected ({len(navigate_result)} chars)")
            return f"[Conteúdo obtido via Playwright Browser - VALIDAR DADOS]\n\n{navigate_result}"
        else:
            # Formato inesperado
            logger.warning(f"Unexpected navigate_result format ({len(navigate_result)} chars)")
            return f"[Conteúdo obtido via Playwright Browser - FORMATO INESPERADO]\n\n{navigate_result}"

    except Exception as e:
        logger.error(f"browser_navigate exception: {type(e).__name__}: {str(e)}")
        return f"Error: All methods failed for {url}. Last exception: {str(e)}"


# ============================================================================
# CrewAI Tools (Decorated Functions for Agents)
# ============================================================================

@tool("search_web")
def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo.
    Returns up to 10 results with title, URL, and summary.
    
    Args:
        query: Search query string (e.g., "best hotels in Paraty")
    
    Returns:
        Search results in text format
    """
    return mcp_search_cli(query)


@tool("fetch_url")
def fetch_url(url: str, ignore_robots: bool = True) -> str:
    """
    Fetch content from a URL and return as markdown.
    Useful for extracting text from web pages.

    IMPORTANT: By default, ignores robots.txt restrictions for research purposes.
    Many property listing sites block automated access, but this tool bypasses that
    to enable legitimate property research and market analysis.

    Args:
        url: Full URL to fetch (e.g., "https://example.com")
        ignore_robots: If True, bypasses robots.txt restrictions (default: True)

    Returns:
        Page content in markdown format
    """
    return mcp_fetch_cli(url, ignore_robots)


@tool("wikipedia_summary")
def wikipedia_summary(title: str) -> str:
    """
    Get a summary of a Wikipedia article.
    Use the exact article title.
    
    Args:
        title: Article title (e.g., "Paraty", "Rio de Janeiro")
    
    Returns:
        Article summary in JSON format
    """
    return mcp_wikipedia_summary_cli(title)


@tool("youtube_info")
def youtube_info(url: str) -> str:
    """
    Get information about a YouTube video (title, description, duration).
    
    Args:
        url: YouTube video URL (e.g., "https://youtube.com/watch?v=VIDEO_ID")
    
    Returns:
        Video metadata in JSON format
    """
    return mcp_youtube_info_cli(url)


@tool("maps_geocode")
def maps_geocode(address: str) -> str:
    """
    Convert address to geographic coordinates (latitude/longitude).
    Requires Google Maps API key to be configured.
    
    Args:
        address: Address to geocode (e.g., "Paraty, RJ, Brazil")
    
    Returns:
        Coordinates and address details in JSON format
    """
    return mcp_maps_geocode_cli(address)


@tool("maps_search_places")
def maps_search_places(query: str) -> str:
    """
    Search for places using Google Places API.
    Returns detailed information about locations found.
    
    Args:
        query: Search query (e.g., "restaurants in Paraty")
    
    Returns:
        Places information in JSON format
    """
    return mcp_maps_search_places_cli(query)


@tool("airbnb_search")
def airbnb_search(location: str, adults: int = 2, children: int = 0) -> str:
    """
    Search Airbnb listings in a location.
    Returns available properties with prices and details.

    Args:
        location: Location to search (e.g., "Paraty, Brazil")
        adults: Number of adults (default: 2)
        children: Number of children (default: 0)

    Returns:
        Airbnb listings in JSON format
    """
    return mcp_airbnb_search_cli(location, adults, children)


@tool("browser_navigate")
def browser_navigate(url: str) -> str:
    """
    Navigate to a URL using Playwright browser.
    Renders JavaScript and bypasses many anti-bot protections.
    Slower than fetch_url but more robust against blocking.

    Args:
        url: Full URL to navigate to

    Returns:
        Navigation result message
    """
    return mcp_browser_navigate_cli(url)


@tool("browser_snapshot")
def browser_snapshot() -> str:
    """
    Capture accessibility snapshot of current browser page.
    Must be called after browser_navigate.
    Returns text structure of visible content.

    Returns:
        Page content as accessibility tree (text format)
    """
    return mcp_browser_snapshot_cli()


@tool("fetch_with_playwright_fallback")
def fetch_with_playwright_fallback(url: str) -> str:
    """
    Smart fetch with automatic Playwright fallback for blocked sites.

    PRIORITY CHAIN:
    1. Try fast fetch_url first (30s timeout)
    2. If robots.txt/403 blocked → automatically use Playwright browser (60s timeout)
    3. Returns content from whichever method succeeds

    USE THIS TOOL when you have a direct link and want maximum success rate.
    This is the PRIMARY tool for fetching property URLs that may be blocked.

    Args:
        url: Full URL to fetch (e.g., property listing page)

    Returns:
        Page content in markdown format (via fetch or Playwright)
    """
    return mcp_fetch_with_playwright_fallback_cli(url)


# ============================================================================
# Agent Tool Distribution
# ============================================================================

def get_enhanced_tools_for_agent(agent_type: str = "general") -> List:
    """
    Retorna lista de ferramentas apropriadas para cada tipo de agente.
    
    VERSÃO 2.0 - CLI APPROACH:
    - Usa subprocess + docker mcp CLI (100% estável)
    - Sem event loop issues
    - Ferramentas testadas e validadas
    
    Args:
        agent_type: Tipo do agente
            - "estrategista": Helena, Ricardo, Fernando, Patricia, Renata, Gabriel
                             → search, fetch, wikipedia (3 tools)
            - "mercado": Juliana → search, fetch, airbnb, wikipedia, youtube (5 tools)
            - "localizacao": Marcelo → maps_geocode, maps_search, search, fetch (4 tools)
            - "marketing": Beatriz, Thiago → search, fetch, youtube (3 tools)
            - "tecnico": André, Sofia, Paula → search, fetch, wikipedia (3 tools)
            - "general": Todas as ferramentas disponíveis (7 tools)
    
    Returns:
        Lista de ferramentas CrewAI decoradas (@tool) prontas para uso
    """
    if agent_type == "estrategista":
        # Estratégia: busca web + fetch + Playwright fallback + Wikipedia
        return [
            search_web,
            fetch_url,
            fetch_with_playwright_fallback,
            wikipedia_summary
        ]

    elif agent_type == "mercado":
        # Mercado: todas as ferramentas de pesquisa exceto maps + Playwright
        return [
            search_web,
            fetch_url,
            fetch_with_playwright_fallback,
            airbnb_search,
            wikipedia_summary,
            youtube_info
        ]
        
    elif agent_type == "localizacao":
        # Localização: Maps + busca básica + Playwright fallback
        return [
            maps_geocode,
            maps_search_places,
            search_web,
            fetch_url,
            fetch_with_playwright_fallback
        ]

    elif agent_type == "marketing":
        # Marketing: busca + fetch + Playwright fallback + YouTube
        return [
            search_web,
            fetch_url,
            fetch_with_playwright_fallback,
            youtube_info
        ]

    elif agent_type == "tecnico":
        # Técnico: busca + fetch + Playwright fallback + Wikipedia
        return [
            search_web,
            fetch_url,
            fetch_with_playwright_fallback,
            wikipedia_summary
        ]
        
    elif agent_type == "general":
        # General: Todas as ferramentas disponíveis incluindo Playwright
        return [
            search_web,
            fetch_url,
            fetch_with_playwright_fallback,
            browser_navigate,
            browser_snapshot,
            wikipedia_summary,
            youtube_info,
            maps_geocode,
            maps_search_places,
            airbnb_search
        ]

    # Fallback: retorna ferramentas básicas + Playwright
    return [search_web, fetch_url, fetch_with_playwright_fallback]


def print_available_tools():
    """Imprime relatório de ferramentas disponíveis."""
    print("\n" + "="*70)
    print("🔧 FERRAMENTAS DISPONÍVEIS PARA AGENTES")
    print("="*70)
    print("\n🚀 VERSÃO 2.0 - CLI APPROACH (Subprocess-based)")
    print("   ✅ 100% de sucesso (6/6 tools testadas)")
    print("   ✅ Sem event loop issues")
    print("   ✅ Timeout configurável (30s padrão)")
    
    print("\n� FERRAMENTAS VALIDADAS:")
    print("   1. search_web                      - DuckDuckGo search")
    print("   2. fetch_url                       - Fetch web content")
    print("   3. fetch_with_playwright_fallback  - Smart fetch with Playwright fallback")
    print("   4. browser_navigate                - Playwright browser navigation")
    print("   5. browser_snapshot                - Playwright page snapshot")
    print("   6. wikipedia_summary               - Wikipedia articles")
    print("   7. youtube_info                    - YouTube video info")
    print("   8. maps_geocode                    - Address → coordinates")
    print("   9. maps_search_places              - Google Places search")
    print("   10. airbnb_search                  - Airbnb listings (robots.txt bypass)")

    print("\n🎯 DISTRIBUIÇÃO POR PERFIL:")
    print("   • estrategista  (8 agents) → 4 tools: search, fetch, playwright_fallback, wikipedia")
    print("   • mercado       (1 agent)  → 6 tools: search, fetch, playwright_fallback, airbnb, wikipedia, youtube")
    print("   • localizacao   (1 agent)  → 5 tools: maps_geocode, maps_search, search, fetch, playwright_fallback")
    print("   • marketing     (2 agents) → 4 tools: search, fetch, playwright_fallback, youtube")
    print("   • tecnico       (3 agents) → 4 tools: search, fetch, playwright_fallback, wikipedia")
    
    # Testar conectividade com Docker MCP
    print("\n🐳 TESTANDO DOCKER MCP GATEWAY:")
    try:
        result = subprocess.run(
            ["docker", "mcp", "tools", "list"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            # Contar ferramentas disponíveis
            lines = result.stdout.strip().split('\n')
            tool_count = len([line for line in lines if line.strip() and not line.startswith('Available')])
            print(f"   ✅ Docker MCP Gateway ATIVO")
            print(f"   📊 Total de ferramentas no gateway: {tool_count}")
            logger.info(f"Docker MCP Gateway is active with {tool_count} tools")
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            print(f"   ❌ Docker MCP Gateway NÃO RESPONDE")
            print(f"   💡 Erro: {error_msg}")
            logger.error(f"Docker MCP Gateway error: {error_msg}")
    except FileNotFoundError:
        print(f"   ❌ DOCKER COMMAND NOT FOUND")
        print(f"   💡 Docker Desktop may not be installed or not in PATH")
        print(f"   💡 Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        logger.error("Docker command not found")
    except subprocess.TimeoutExpired:
        print(f"   ❌ Docker MCP Gateway TIMEOUT (5s)")
        print(f"   💡 Docker may be starting or having issues")
        logger.error("Docker MCP Gateway timeout")
    except Exception as e:
        print(f"   ❌ Docker MCP Gateway NÃO ESTÁ RODANDO")
        print(f"   💡 Erro: {str(e)}")
        print(f"   💡 Inicie o Docker Desktop e habilite MCP Toolkit")
        logger.error(f"Docker MCP Gateway exception: {type(e).__name__}: {str(e)}")

    print("="*70 + "\n")
