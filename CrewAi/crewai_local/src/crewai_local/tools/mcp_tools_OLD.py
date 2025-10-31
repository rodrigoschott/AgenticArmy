"""
⚠️ DEPRECATED - OLD CLI APPROACH
=================================
This file uses 'docker mcp tool call' CLI commands which are NOT recommended.
Use mcp_tools_new.py with native MCPServerAdapter instead.
Kept for reference only.

For current implementation, see: src/crewai_local/tools/mcp_tools_new.py
=================================

Ferramentas MCP (Model Context Protocol) para os agentes CrewAI.
Conecta aos servidores MCP do Docker para busca web, navegação, mapas, etc.

NOTA: Este módulo usa Tool do CrewAI nativo (já instalado via crewai[tools])
"""

import json
import subprocess
from typing import Any, Optional, Dict, List
from crewai.tools import tool


@tool("Busca Web MCP")
def mcp_search_tool(query: str) -> str:
    """
    Realiza buscas na web usando DuckDuckGo via Docker MCP Gateway.
    Use para encontrar informações atualizadas sobre pousadas, preços,
    eventos em Paraty, tendências de mercado, etc.
    
    IMPORTANTE: Sempre cite as fontes no formato:
    "Segundo pesquisa via DuckDuckGo [data]: [informação]"
    
    Args:
        query: texto da busca (ex: 'pousadas boutique Paraty preços 2025')
    
    Returns:
        Resultados da busca formatados com timestamp para rastreabilidade
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Chama o MCP Gateway do Docker Desktop
        # O Gateway gerencia o servidor duckduckgo automaticamente
        cmd = [
            "docker", "mcp", "tool", "call",
            "duckduckgo_search",
            "--", query
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Adiciona metadados de rastreamento
            header = f"📊 FONTE: Busca Web MCP via DuckDuckGo\n"
            header += f"🔍 Query: '{query}'\n"
            header += f"⏰ Data: {timestamp}\n"
            header += f"{'='*60}\n\n"
            return header + result.stdout
        else:
            return f"Erro na busca MCP: {result.stderr}\nDica: Verifique se o servidor está habilitado com 'docker mcp server list'"
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado. Instale via: https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/"
    except Exception as e:
        return f"Erro ao executar busca MCP: {str(e)}"


@tool("Fetch URL MCP")
def mcp_fetch_tool(url: str) -> str:
    """
    Busca e extrai o conteúdo de uma página web específica via Docker MCP Gateway.
    Use para ler artigos, páginas de pousadas, sites de eventos, etc.
    
    IMPORTANTE: Sempre cite a URL fonte no formato:
    "Segundo [nome do site] (URL): [informação]"
    
    Args:
        url: URL completa (ex: 'https://www.booking.com/hotel/br/pousada-exemplo.html')
    
    Returns:
        Conteúdo da página em texto com metadados de fonte
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Usa o servidor fetch do MCP Gateway
        cmd = [
            "docker", "mcp", "tool", "call",
            "fetch",
            "--", url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Adiciona metadados de rastreamento
            header = f"📄 FONTE: Fetch URL MCP\n"
            header += f"🔗 URL: {url}\n"
            header += f"⏰ Data: {timestamp}\n"
            header += f"{'='*60}\n\n"
            return header + result.stdout
        else:
            return f"Erro ao buscar URL: {result.stderr}\nDica: Habilite o servidor fetch com 'docker mcp server enable fetch'"
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao buscar URL: {str(e)}"


@tool("Navegador Web MCP")
def mcp_browser_tool(action_json: str) -> str:
    """
    Navega em sites de forma interativa via Playwright (abre, clica, preenche formulários).
    Use para pesquisar preços em OTAs, verificar disponibilidade, extrair dados de sites.
    
    Args:
        action_json: JSON com ação e URL, ex: '{"action": "navigate", "url": "https://..."}'
    
    Returns:
        Resultado da navegação
    """
    try:
        # Usa o servidor playwright do MCP Gateway
        action = json.loads(action_json)
        cmd = [
            "docker", "mcp", "tool", "call",
            "playwright_navigate",
            "--", json.dumps(action)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Erro na navegação: {result.stderr}"
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao navegar: {str(e)}"


@tool("Google Maps MCP")
def mcp_maps_tool(query: str) -> str:
    """
    Consulta informações de localização, rotas, lugares próximos via Google Maps.
    Use para verificar localizações de pousadas, distâncias, pontos turísticos.
    
    IMPORTANTE: Sempre cite como "Segundo Google Maps [data]: [informação]"
    
    Args:
        query: query de busca (ex: 'pousadas em Paraty centro histórico')
               ou coordenadas para reverse geocoding
    
    Returns:
        Informações de localização formatadas com metadados
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Usa o servidor google-maps-comprehensive do MCP Gateway
        cmd = [
            "docker", "mcp", "tool", "call",
            "google_maps_search_places",
            "--", json.dumps({"query": query})
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Adiciona metadados de rastreamento
            header = f"🗺️ FONTE: Google Maps MCP\n"
            header += f"🔍 Query: '{query}'\n"
            header += f"⏰ Data: {timestamp}\n"
            header += f"{'='*60}\n\n"
            return header + result.stdout
        else:
            return f"Erro na consulta Maps: {result.stderr}"
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao consultar Maps: {str(e)}"


@tool("Airbnb Search MCP")
def mcp_airbnb_tool(params_json: str) -> str:
    """
    Busca propriedades no Airbnb com filtros de preço, localização, datas.
    Use para análise competitiva de preços, ocupação, reviews.
    
    IMPORTANTE: Sempre cite como "Segundo Airbnb [data] - [localização]: [informação]"
    
    Args:
        params_json: JSON com parâmetros, ex:
                    '{"location": "Paraty", "checkin": "2025-12-20", "adults": 2}'
    
    Returns:
        Listagens do Airbnb formatadas com metadados de fonte
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Usa o servidor openbnb-airbnb do MCP Gateway
        params = json.loads(params_json)
        location = params.get('location', 'desconhecida')
        
        cmd = [
            "docker", "mcp", "tool", "call",
            "airbnb_search",
            "--", json.dumps(params)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Adiciona metadados de rastreamento
            header = f"🏠 FONTE: Airbnb MCP\n"
            header += f"📍 Localização: {location}\n"
            header += f"🔍 Filtros: {params_json}\n"
            header += f"⏰ Data: {timestamp}\n"
            header += f"{'='*60}\n\n"
            return header + result.stdout
        else:
            return f"Erro na busca Airbnb: {result.stderr}"
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao buscar Airbnb: {str(e)}"


@tool("Wikipedia MCP")
def mcp_wikipedia_tool(query: str) -> str:
    """
    Busca e obtém informações da Wikipedia via Docker MCP Gateway.
    Use para encontrar informações confiáveis e enciclopédicas sobre Paraty,
    turismo, história, arquitetura colonial, patrimônio histórico, etc.
    
    IMPORTANTE: Sempre cite as fontes no formato:
    "Segundo Wikipedia consultada em [data]: [informação]"
    
    Args:
        query: termo de busca (ex: 'Paraty história', 'turismo cultural Brasil')
    
    Returns:
        Resumo do artigo da Wikipedia com timestamp para rastreabilidade
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Primeiro, busca artigos relacionados
        search_cmd = [
            "docker", "mcp", "tool", "call",
            "search_wikipedia",
            "--", json.dumps({"query": query, "limit": 3})
        ]
        search_result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=30)
        
        if search_result.returncode != 0:
            return f"Erro na busca Wikipedia: {search_result.stderr}"
        
        # Se encontrou resultados, obtém o resumo do primeiro artigo
        try:
            search_data = json.loads(search_result.stdout)
            if search_data and len(search_data) > 0:
                first_article = search_data[0].get('title', query)
                
                # Obtém resumo do artigo
                summary_cmd = [
                    "docker", "mcp", "tool", "call",
                    "get_summary",
                    "--", json.dumps({"title": first_article})
                ]
                summary_result = subprocess.run(summary_cmd, capture_output=True, text=True, timeout=30)
                
                if summary_result.returncode == 0:
                    # Adiciona metadados de rastreamento
                    header = f"📚 FONTE: Wikipedia MCP\n"
                    header += f"🔍 Query: '{query}'\n"
                    header += f"📖 Artigo: '{first_article}'\n"
                    header += f"⏰ Data: {timestamp}\n"
                    header += f"{'='*60}\n\n"
                    return header + summary_result.stdout
        except json.JSONDecodeError:
            pass
        
        # Se chegou aqui, retorna os resultados da busca
        header = f"📚 FONTE: Wikipedia MCP (Resultados de Busca)\n"
        header += f"🔍 Query: '{query}'\n"
        header += f"⏰ Data: {timestamp}\n"
        header += f"{'='*60}\n\n"
        return header + search_result.stdout
        
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao buscar Wikipedia: {str(e)}"


@tool("YouTube Transcript MCP")
def mcp_youtube_tool(video_url: str) -> str:
    """
    Obtém transcrição de vídeos do YouTube via Docker MCP Gateway.
    Use para analisar conteúdo de vídeos sobre pousadas, reviews de hóspedes,
    vídeos de influenciadores sobre Paraty, estratégias de marketing, etc.
    
    IMPORTANTE: Sempre cite as fontes no formato:
    "Segundo transcrição de vídeo YouTube consultada em [data]: [informação]"
    
    Args:
        video_url: URL completa do vídeo YouTube (ex: 'https://youtube.com/watch?v=...')
    
    Returns:
        Transcrição do vídeo com timestamp para rastreabilidade
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Obtém informações do vídeo primeiro
        info_cmd = [
            "docker", "mcp", "tool", "call",
            "get_video_info",
            "--", json.dumps({"url": video_url})
        ]
        info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        
        video_title = "Vídeo YouTube"
        if info_result.returncode == 0:
            try:
                video_info = json.loads(info_result.stdout)
                video_title = video_info.get('title', video_title)
            except json.JSONDecodeError:
                pass
        
        # Obtém transcrição
        transcript_cmd = [
            "docker", "mcp", "tool", "call",
            "get_transcript",
            "--", json.dumps({"url": video_url, "lang": "pt"})
        ]
        transcript_result = subprocess.run(transcript_cmd, capture_output=True, text=True, timeout=60)
        
        if transcript_result.returncode == 0:
            # Adiciona metadados de rastreamento
            header = f"🎥 FONTE: YouTube Transcript MCP\n"
            header += f"🔗 URL: {video_url}\n"
            header += f"📺 Vídeo: '{video_title}'\n"
            header += f"⏰ Data: {timestamp}\n"
            header += f"{'='*60}\n\n"
            return header + transcript_result.stdout
        else:
            return f"Erro ao obter transcrição: {transcript_result.stderr}"
            
    except FileNotFoundError:
        return "Docker MCP Gateway não encontrado."
    except Exception as e:
        return f"Erro ao processar YouTube: {str(e)}"


# =============================================================================
# FUNÇÕES AUXILIARES PARA OBTER FERRAMENTAS
# =============================================================================

def get_all_mcp_tools() -> List:
    """Retorna lista com todas as ferramentas MCP disponíveis."""
    return [
        mcp_search_tool,
        mcp_fetch_tool,
        mcp_browser_tool,
        mcp_maps_tool,
        mcp_airbnb_tool,
        mcp_wikipedia_tool,
        mcp_youtube_tool,
    ]


def get_search_tools() -> List:
    """Retorna ferramentas de busca (search + fetch + wikipedia)."""
    return [
        mcp_search_tool,
        mcp_fetch_tool,
        mcp_wikipedia_tool,
    ]


def get_market_research_tools() -> List:
    """Retorna ferramentas para pesquisa de mercado."""
    return [
        mcp_search_tool,
        mcp_fetch_tool,
        mcp_browser_tool,
        mcp_airbnb_tool,
        mcp_wikipedia_tool,
        mcp_youtube_tool,
    ]


def get_location_tools() -> List:
    """Retorna ferramentas de localização."""
    return [
        mcp_maps_tool,
    ]


# =============================================================================
# RASTREAMENTO DE FONTES
# =============================================================================

def extract_sources_from_text(text: str) -> List[str]:
    """
    Extrai menções a fontes MCP do texto de resposta do agente.
    
    Args:
        text: Texto de saída do agente
    
    Returns:
        Lista de fontes únicas encontradas com timestamp
    """
    sources = []
    lines = text.split('\n')
    
    for line in lines:
        # Procura por linhas com marcadores de fonte
        if any(marker in line for marker in ['📊 FONTE:', '📄 FONTE:', '🗺️ FONTE:', '🏠 FONTE:', '📚 FONTE:', '🎥 FONTE:']):
            sources.append(line.strip())
        # Procura por linhas com timestamps
        elif '⏰ Data:' in line:
            sources.append(line.strip())
        # Procura por queries e outros metadados
        elif any(marker in line for marker in ['🔍 Query:', '🔗 URL:', '📍 Localização:', '📖 Artigo:', '📺 Vídeo:']):
            sources.append(line.strip())
    
    return sources


def generate_sources_section(sources: List[str]) -> str:
    """
    Gera seção formatada de fontes para adicionar ao final do documento.
    
    Args:
        sources: Lista de fontes extraídas
    
    Returns:
        Seção formatada em Markdown
    """
    if not sources:
        return ""
    
    section = "\n\n---\n\n"
    section += "## 📚 FONTES CONSULTADAS\n\n"
    section += "*Este relatório foi baseado em dados obtidos através das seguintes fontes:*\n\n"
    
    # Agrupa por tipo de fonte
    search_sources = [s for s in sources if 'Busca Web' in s or ('🔍 Query:' in s and 'Wikipedia' not in s)]
    maps_sources = [s for s in sources if 'Google Maps' in s]
    airbnb_sources = [s for s in sources if 'Airbnb' in s]
    fetch_sources = [s for s in sources if 'Fetch URL' in s or ('🔗 URL:' in s and 'YouTube' not in s)]
    wikipedia_sources = [s for s in sources if 'Wikipedia' in s or '📖 Artigo:' in s]
    youtube_sources = [s for s in sources if 'YouTube' in s or '📺 Vídeo:' in s]
    
    if search_sources:
        section += "### 🔍 Buscas Web (DuckDuckGo)\n"
        for source in search_sources[:5]:  # Máximo 5 para não poluir
            section += f"- {source.replace('📊 FONTE:', '').strip()}\n"
        section += "\n"
    
    if wikipedia_sources:
        section += "### 📚 Wikipedia\n"
        for source in wikipedia_sources[:5]:
            section += f"- {source.replace('📚 FONTE:', '').strip()}\n"
        section += "\n"
    
    if youtube_sources:
        section += "### 🎥 YouTube\n"
        for source in youtube_sources[:5]:
            section += f"- {source.replace('🎥 FONTE:', '').strip()}\n"
        section += "\n"
    
    if maps_sources:
        section += "### 🗺️ Google Maps\n"
        for source in maps_sources[:5]:
            section += f"- {source.replace('🗺️ FONTE:', '').strip()}\n"
        section += "\n"
    
    if airbnb_sources:
        section += "### 🏠 Airbnb\n"
        for source in airbnb_sources[:5]:
            section += f"- {source.replace('🏠 FONTE:', '').strip()}\n"
        section += "\n"
    
    if fetch_sources:
        section += "### 📄 Páginas Web\n"
        for source in fetch_sources[:5]:
            section += f"- {source.replace('📄 FONTE:', '').strip()}\n"
        section += "\n"
    
    section += "*Dados coletados em tempo real via Docker MCP Gateway*\n"
    
    return section


# =============================================================================
# VERIFICAÇÃO DE DISPONIBILIDADE
# =============================================================================

def check_mcp_availability() -> Dict[str, bool]:
    """Verifica quais ferramentas MCP estão disponíveis via Docker MCP Gateway."""
    availability = {
        "gateway_running": False,
        "search": False,
        "fetch": False,
        "browser": False,
        "maps": False,
        "airbnb": False,
        "wikipedia": False,
        "youtube": False
    }
    
    # Verifica se Docker MCP Gateway está disponível
    try:
        result = subprocess.run(
            ["docker", "mcp", "server", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        gateway_available = result.returncode == 0
        
        if gateway_available:
            availability["gateway_running"] = True
            output = result.stdout.lower()
            # Verifica servidores específicos na saída
            availability["search"] = "duckduckgo" in output or "search" in output
            availability["fetch"] = "fetch" in output
            availability["browser"] = "browser" in output or "playwright" in output
            availability["maps"] = "maps" in output or "google" in output
            availability["airbnb"] = "airbnb" in output
            availability["wikipedia"] = "wikipedia" in output
            availability["youtube"] = "youtube" in output
                
    except FileNotFoundError:
        # Docker MCP não instalado - todos já False
        pass
    except Exception:
        # Erro genérico - todos já False
        pass
    
    return availability


def get_available_tools() -> List:
    """
    Retorna apenas as ferramentas MCP que estão disponíveis.
    Útil para inicialização dos agentes.
    """
    availability = check_mcp_availability()
    
    # Se nenhuma ferramenta está disponível, retorna lista vazia
    if not any(availability.values()):
        return []
    
    # Se container está rodando, retorna todas as ferramentas
    return get_all_mcp_tools()
