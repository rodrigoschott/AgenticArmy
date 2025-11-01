"""
Ferramentas MCP (Model Context Protocol) para os agentes CrewAI.
Conecta aos servidores MCP do Docker Gateway via integração nativa CrewAI.

ABORDAGEM: Usa MCPServerAdapter do CrewAI para conectar ao Docker MCP Gateway via stdio.
FIX EVENT LOOP: Usa nest_asyncio para permitir nested event loops (resolve "Event loop is closed").
"""

from typing import List, Any
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import os
import nest_asyncio

# Permite nested event loops (necessário para MCP tools em CrewAI)
nest_asyncio.apply()


def get_docker_mcp_tools() -> List[Any]:
    """
    Retorna todas as ferramentas disponíveis do Docker MCP Gateway.
    
    O Docker MCP Gateway agrega múltiplos servers MCP (DuckDuckGo, Wikipedia, 
    YouTube, Maps, Airbnb, Playwright, etc.) e os expõe através de um único ponto.
    
    Returns:
        Lista de ferramentas CrewAI prontas para uso pelos agentes
    """
    # Configuração para conectar ao Docker MCP Gateway via stdio
    server_params = StdioServerParameters(
        command="docker",
        args=["mcp", "gateway", "run"],
        env={**os.environ}  # Herda variáveis de ambiente do sistema
    )
    
    try:
        # MCPServerAdapter conecta ao gateway e descobre automaticamente todas as tools
        with MCPServerAdapter(server_params, connect_timeout=30) as tools:
            print(f"✅ Docker MCP Gateway: {len(tools)} ferramentas disponíveis")
            print(f"📋 Tools: {[tool.name for tool in tools[:10]]}...")  # Mostra primeiras 10
            return list(tools)
    except Exception as e:
        print(f"❌ Erro ao conectar ao Docker MCP Gateway: {e}")
        print("💡 Certifique-se de que o Docker Desktop está rodando e MCP Toolkit está habilitado")
        return []


def get_docker_mcp_tools_filtered(tool_names: List[str]) -> List[Any]:
    """
    Retorna apenas ferramentas específicas do Docker MCP Gateway.
    
    Args:
        tool_names: Lista de nomes das ferramentas desejadas
                   Ex: ["search", "fetch", "search_wikipedia", "maps_geocode"]
    
    Returns:
        Lista de ferramentas CrewAI filtradas
    """
    try:
        # Obter todas as ferramentas
        all_tools = get_docker_mcp_tools()
        
        # Filtrar apenas as ferramentas solicitadas
        filtered_tools = [tool for tool in all_tools if tool.name in tool_names]
        
        print(f"✅ Docker MCP Gateway: {len(filtered_tools)} ferramentas filtradas")
        print(f"📋 Tools: {[tool.name for tool in filtered_tools]}")
        
        return filtered_tools
    except Exception as e:
        print(f"❌ Erro ao filtrar ferramentas: {e}")
        return []


# Funções auxiliares para facilitar a configuração por perfil de agente

def get_search_tools() -> List[Any]:
    """Ferramentas de busca: DuckDuckGo search, Wikipedia, YouTube"""
    return get_docker_mcp_tools_filtered([
        "search",              # DuckDuckGo web search
        "search_wikipedia",    # Wikipedia article search
        "get_video_info"       # YouTube video info
    ])


def get_data_fetch_tools() -> List[Any]:
    """Ferramentas para buscar conteúdo de URLs"""
    return get_docker_mcp_tools_filtered([
        "fetch",               # Fetch URL content
        "fetch_content"        # Alternative fetch with parsing
    ])


def get_location_tools() -> List[Any]:
    """Ferramentas de localização: Maps, Airbnb"""
    return get_docker_mcp_tools_filtered([
        "maps_geocode",        # Address to coordinates
        "maps_reverse_geocode", # Coordinates to address
        "maps_search_places",   # Search for places
        "maps_directions",      # Get directions
        "airbnb_search",       # Search Airbnb listings
        "airbnb_listing_details" # Get listing details
    ])


def get_browser_tools() -> List[Any]:
    """Ferramentas de navegação web: Playwright"""
    return get_docker_mcp_tools_filtered([
        "browser_navigate",    # Navigate to URL
        "browser_snapshot",    # Take accessibility snapshot
        "browser_click",       # Click element
        "browser_type"         # Type text
    ])


def get_wikipedia_tools() -> List[Any]:
    """Ferramentas específicas da Wikipedia"""
    return get_docker_mcp_tools_filtered([
        "search_wikipedia",      # Search articles
        "get_article",           # Get full article
        "get_summary",           # Get article summary
        "get_sections"           # Get article sections
    ])


def get_youtube_tools() -> List[Any]:
    """Ferramentas específicas do YouTube"""
    return get_docker_mcp_tools_filtered([
        "get_video_info",        # Get video metadata
        "get_transcript",        # Get video transcript
        "get_timed_transcript"   # Get transcript with timestamps
    ])


def check_docker_mcp_available() -> tuple[bool, str]:
    """
    Check if Docker MCP Gateway is available.

    Returns:
        Tuple of (is_available: bool, message: str)
    """
    import subprocess

    try:
        # Check if Docker is running
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode != 0:
            return False, "Docker is not running"

        # Check if MCP command is available
        result = subprocess.run(
            ["docker", "mcp", "--help"],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode != 0:
            return False, "Docker MCP Toolkit not available"

        return True, "Docker MCP available"

    except FileNotFoundError:
        return False, "Docker not installed"
    except subprocess.TimeoutExpired:
        return False, "Docker command timeout"
    except Exception as e:
        return False, f"Error checking Docker MCP: {str(e)}"


# Exemplo de uso:
"""
from crewai import Agent
from crewai_local.tools.mcp_tools_new import get_docker_mcp_tools, get_search_tools

# Opção 1: Todas as ferramentas do gateway
agent1 = Agent(
    role="Research Analyst",
    goal="Research information",
    backstory="Expert researcher",
    tools=get_docker_mcp_tools()  # ~61 tools de todos os servers
)

# Opção 2: Apenas ferramentas de busca
agent2 = Agent(
    role="Search Specialist", 
    goal="Find information",
    backstory="Search expert",
    tools=get_search_tools()  # Apenas search, wikipedia, youtube info
)

# Opção 3: Ferramentas customizadas
from crewai_local.tools.mcp_tools_new import get_docker_mcp_tools_filtered

agent3 = Agent(
    role="Location Expert",
    goal="Find locations",
    backstory="Geography specialist",
    tools=get_docker_mcp_tools_filtered(["maps_geocode", "maps_search_places"])
)
"""
