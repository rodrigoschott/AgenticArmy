# 🔧 MCP Integration Guide - Complete Reference

**Model Context Protocol (MCP) Integration for CrewAI Multi-Agent System**

**Version:** 3.0 Native Integration | **Date:** 31 Oct 2025 | **Coverage:** 13/13 agents (100%)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Current Implementation](#current-implementation)
3. [Setup & Installation](#setup--installation)
4. [Available Tools](#available-tools)
5. [Usage Examples](#usage-examples)
6. [Source Tracking System](#source-tracking-system)
7. [Testing & Validation](#testing--validation)
8. [Migration from Old Approach](#migration-from-old-approach)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## 🎯 Overview

### What is MCP?

**Model Context Protocol** enables AI agents to access external tools and data sources through a standardized interface. In our system, agents use **Docker MCP Gateway** to access ~60 tools from 11 different servers.

### Why Use MCP?

✅ **Real Data** - Agents fetch live information instead of hallucinating  
✅ **Source Tracking** - Every piece of data is timestamped and traceable  
✅ **Standardization** - One protocol for all external tools  
✅ **Scalability** - Easy to add new tool servers

### Integration Status

```
✅ CrewAI Version: 1.2.1+ (native MCP support)
✅ MCP Library: 1.20.0
✅ Docker Gateway: Running (11 servers)
✅ Agent Coverage: 13/13 (100%)
✅ Available Tools: ~60 from 11 servers
✅ Source Tracking: Enabled with timestamps
```

---

## 🚀 Current Implementation

### Native Integration (Recommended)

Since CrewAI 1.2.1, MCP integration is **built-in** via `MCPServerAdapter`:

```python
from crewai_tools.tools.mcp_tool import MCPServerAdapter
from mcp import StdioServerParameters

# Connect to Docker MCP Gateway
adapter = MCPServerAdapter(
    server_params=StdioServerParameters(
        command="docker",
        args=["mcp", "gateway", "run"]
    )
)

# Get all available tools (~60 tools)
tools = adapter.list_tools()
```

### Architecture

```
CrewAI Agents
    ↓
mcp_tools_new.py (Native Adapter)
    ↓
Docker MCP Gateway (stdio transport)
    ↓
11 MCP Servers (DuckDuckGo, Maps, Airbnb, etc.)
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Native Integration** | `mcp_tools_new.py` | MCPServerAdapter with stdio transport |
| **Tool Distribution** | `web_tools.py` | Maps tools to agent profiles |
| **Source Tracking** | `mcp_tools.py` | Metadata injection + extraction helpers |
| **Test Suite** | `test_mcp_complete.py` | Comprehensive validation |

---

## ⚙️ Setup & Installation

### Prerequisites

1. **Docker Desktop** with MCP Gateway enabled
2. **Python 3.11+** with Poetry
3. **CrewAI 1.2.1+** with MCP support

### Installation Steps

#### 1. Update Dependencies

```bash
# Update pyproject.toml
poetry add "crewai[tools]@>=1.2.1" mcp "crewai-tools[mcp]@>=1.2.1"

# Install
poetry install
```

#### 2. Configure Docker MCP Gateway

```powershell
# Check if gateway is running
docker mcp server list

# Expected output: 11 servers active
# - mcp-ga-duckduckgo
# - mcp-ga-fetch
# - mcp-ga-wikipedia
# - mcp-ga-youtube
# - mcp-ga-google-maps
# - mcp-ga-airbnb
# - mcp-ga-browser
# - mcp-ga-obsidian
# - mcp-ga-sequential-thinking
# (etc.)
```

#### 3. Verify Installation

```bash
# Run basic test
poetry run python test_mcp_basic.py

# Expected output:
# ✅ Docker MCP Gateway: 3 ferramentas filtradas
# 📋 Tools: ['search', 'search_wikipedia', 'get_video_info']
```

#### 4. Run Complete Test Suite

```bash
# Full validation
poetry run python test_mcp_complete.py

# Expected output:
# 🎉 Tudo está configurado perfeitamente!
# ✅ Sistema pronto para uso em produção!
```

---

## 🔧 Available Tools

### Summary by Category

**Total:** ~60 tools from 11 servers

| Category | Tools | Servers |
|----------|-------|---------|
| Search & Research | 10 | DuckDuckGo, Wikipedia |
| Data Fetching | 3 | Fetch |
| Location & Maps | 7 | Google Maps |
| Accommodation | 2 | Airbnb |
| Video Content | 3 | YouTube |
| Web Automation | 17 | Playwright Browser |
| Note-taking | 12 | Obsidian |
| AI Reasoning | 1 | Sequential Thinking |

### Detailed Tool List

#### 🔍 Search & Research (10 tools)

**DuckDuckGo Search:**
- `search` - Web search with ranking
- `fetch_content` - Extract webpage content

**Wikipedia:**
- `search_wikipedia` - Search articles
- `get_article` - Full article content
- `get_summary` - Article summary
- `get_sections` - Article sections
- `get_related_topics` - Related articles
- `get_coordinates` - Geographic data
- `extract_key_facts` - Key information extraction
- `summarize_article_section` - Section summaries

#### 📄 Data Fetching (3 tools)

**Fetch Server:**
- `fetch` - Download URL content with markdown conversion
- `fetch_content` - Parse and extract main content
- Parameters: `url`, `max_length`, `start_index`, `raw`

#### 🗺️ Location & Maps (7 tools)

**Google Maps:**
- `maps_geocode` - Address → coordinates
- `maps_reverse_geocode` - Coordinates → address
- `maps_search_places` - Find places by query
- `maps_place_details` - Detailed place information
- `maps_directions` - Route between two points
- `maps_distance_matrix` - Multiple origins/destinations
- `maps_elevation` - Elevation data for coordinates

#### 🏠 Accommodation (2 tools)

**Airbnb:**
- `airbnb_search` - Search listings with filters
  - Parameters: `location`, `checkin`, `checkout`, `adults`, `children`, `pets`, `minPrice`, `maxPrice`, `cursor` (pagination)
- `airbnb_listing_details` - Full listing details
  - Parameters: `id`, `checkin`, `checkout`, `adults`, `children`, `pets`

#### 🎥 Video Content (3 tools)

**YouTube:**
- `get_video_info` - Video metadata (title, duration, views)
- `get_transcript` - Full transcript
- `get_timed_transcript` - Transcript with timestamps
- Parameters: `url`, `lang`, `next_cursor` (pagination)

#### 🌐 Web Automation (17 tools)

**Playwright Browser:**
- `browser_navigate` - Go to URL
- `browser_snapshot` - Accessibility snapshot (better than screenshot)
- `browser_click` - Click element
- `browser_type` - Type text
- `browser_fill_form` - Fill multiple fields
- `browser_select_option` - Select from dropdown
- `browser_hover` - Hover over element
- `browser_drag` - Drag and drop
- `browser_press_key` - Keyboard input
- `browser_take_screenshot` - Capture screen (PNG/JPEG)
- `browser_evaluate` - Run JavaScript
- `browser_wait_for` - Wait for text/time
- `browser_file_upload` - Upload files
- `browser_handle_dialog` - Handle alerts/prompts
- `browser_tabs` - Manage tabs
- `browser_network_requests` - Get network activity
- `browser_console_messages` - Get console logs

#### 📝 Note-taking (12 tools)

**Obsidian:**
- `obsidian_list_files_in_vault` - List root files
- `obsidian_list_files_in_dir` - List directory contents
- `obsidian_get_file_contents` - Read file
- `obsidian_batch_get_file_contents` - Read multiple files
- `obsidian_append_content` - Add to file
- `obsidian_patch_content` - Insert at heading/block/frontmatter
- `obsidian_delete_file` - Delete file (requires confirmation)
- `obsidian_simple_search` - Text search
- `obsidian_complex_search` - JsonLogic queries
- `obsidian_get_recent_changes` - Recently modified files
- `obsidian_get_periodic_note` - Daily/weekly/monthly notes
- `obsidian_get_recent_periodic_notes` - Recent periodic notes

#### 🧠 AI Reasoning (1 tool)

**Sequential Thinking:**
- `sequentialthinking` - Chain-of-thought reasoning with revision

---

## 💻 Usage Examples

### Basic Usage - Get All Tools

```python
from src.crewai_local.tools.mcp_tools_new import get_docker_mcp_tools

# Get all ~60 tools
all_tools = get_docker_mcp_tools()
print(f"Total tools: {len(all_tools)}")
```

### Get Specific Tools

```python
from src.crewai_local.tools.mcp_tools_new import get_docker_mcp_tools_filtered

# Get only search tools
search_tools = get_docker_mcp_tools_filtered([
    "search",
    "search_wikipedia",
    "get_video_info"
])
```

### Use Helper Functions

```python
from src.crewai_local.tools.mcp_tools_new import (
    get_search_tools,      # DuckDuckGo, Wikipedia, YouTube
    get_location_tools,    # Maps + Search + Fetch
    get_browser_tools,     # Playwright automation
    get_data_fetch_tools,  # Fetch URL content
    get_airbnb_tools,      # Airbnb search + details
)

# Get pre-configured tool sets
tools = get_search_tools()  # 3 tools
tools = get_location_tools()  # 3 tools
tools = get_browser_tools()  # 17 tools
```

### Agent Integration - Method 1 (Helper Functions)

```python
from crewai import Agent
from src.crewai_local.tools.mcp_tools_new import get_search_tools

agent = Agent(
    role="Market Researcher",
    goal="Research Paraty accommodation market",
    backstory="Expert in hospitality market analysis",
    tools=get_search_tools(),  # 3 MCP tools
    verbose=True
)
```

### Agent Integration - Method 2 (Tool Profiles)

```python
from crewai import Agent
from src.crewai_local.tools.web_tools import get_enhanced_tools_for_agent

# Use predefined profiles
agent = Agent(
    role="Market Analyst",
    goal="Competitive analysis",
    backstory="Expert analyst",
    tools=get_enhanced_tools_for_agent("mercado"),  # 6 tools
    verbose=True
)
```

### Agent Integration - Method 3 (DSL Syntax - Simplest)

```python
from crewai import Agent

agent = Agent(
    role="Researcher",
    goal="Research information",
    backstory="Expert researcher",
    mcps=["docker://gateway"],  # Automatic tool discovery!
    verbose=True
)
# All Docker Gateway tools available automatically
```

### Tool Profiles Available

| Profile | Tools | Count | Agents |
|---------|-------|-------|--------|
| `estrategista` | Search + Fetch + Wikipedia | 3 | 9 agents |
| `mercado` | Search + Fetch + Browser + Airbnb + Wikipedia + YouTube | 6 | 1 agent |
| `localizacao` | Maps + Search + Fetch | 3 | 1 agent |
| `marketing` | Search + Fetch + YouTube | 3 | 2 agents |
| `tecnico` | Search + Fetch + Wikipedia | 3 | 3 agents |

---

## 📚 Source Tracking System

### Why Track Sources?

✅ **Auditability** - Know where each piece of information came from  
✅ **Credibility** - Stakeholders can verify data  
✅ **Hallucination Detection** - Distinguish real data from LLM invention  
✅ **Reproducibility** - Re-run searches with exact parameters

### How It Works

#### 1. Automatic Metadata Injection

Every MCP tool response includes a header:

```
📊 FONTE: Busca Web MCP via DuckDuckGo
🔍 Query: 'pousadas boutique Paraty preços 2025'
⏰ Data: 2025-10-31 14:23
============================================================

[Tool results...]
```

#### 2. Mandatory Citation in Prompts

Tasks instruct agents to cite sources:

```markdown
⚠️ OBRIGATÓRIO - RASTREAMENTO DE FONTES:
- SEMPRE cite as fontes de cada informação
- Formato: "Segundo [Fonte] em [Data]: [Informação]"
- Exemplo: "Segundo DuckDuckGo em 2025-10-31: Casa das Areias R$450/noite"
```

#### 3. Helper Functions for Extraction

```python
from src.crewai_local.tools.mcp_tools import (
    extract_sources_from_text,
    generate_sources_section
)

# Extract all sources from agent output
sources = extract_sources_from_text(agent_output)
# ['📊 FONTE: Busca Web MCP', '⏰ Data: 2025-10-31', ...]

# Generate formatted sources section
section = generate_sources_section(sources)
# Returns markdown section: "## 📚 FONTES CONSULTADAS ..."

# Add to document
final_doc = agent_output + section
```

### Metadata Formats by Tool

**Search (DuckDuckGo):**
```
📊 FONTE: Busca Web MCP via DuckDuckGo
🔍 Query: 'search terms'
⏰ Data: 2025-10-31 14:23
```

**Wikipedia:**
```
📚 FONTE: Wikipedia MCP
🔍 Query: 'article search'
📖 Artigo: 'Article Name'
⏰ Data: 2025-10-31 14:25
```

**YouTube:**
```
🎥 FONTE: YouTube Transcript MCP
🔗 URL: https://youtube.com/watch?v=...
📺 Vídeo: 'Video Title'
⏰ Data: 2025-10-31 14:27
```

**Google Maps:**
```
🗺️ FONTE: Google Maps MCP
🔍 Query: 'location query'
⏰ Data: 2025-10-31 14:30
```

**Airbnb:**
```
🏠 FONTE: Airbnb MCP
📍 Localização: Paraty
🔍 Filtros: {"location": "Paraty", "adults": 2}
⏰ Data: 2025-10-31 14:32
```

### Example: Complete Source Tracking Flow

**Agent Task Execution:**
```
1. Agent receives task: "Research accommodation prices in Paraty"
2. Agent calls mcp_search_tool("pousadas Paraty preços")
3. Tool returns results WITH metadata header
4. Agent writes output citing source:
   "Segundo DuckDuckGo em 2025-10-31: Pousadas custam R$350-800/noite"
5. Helper extracts all citations
6. Generated "FONTES CONSULTADAS" section appended to document
```

**Final Document Includes:**
```markdown
## Análise de Preços

Segundo DuckDuckGo em 2025-10-31: Pousadas boutique em Paraty custam
entre R$350-R$800/noite em alta temporada (média R$520).

Segundo Airbnb em 2025-10-31 - Paraty: 47 propriedades disponíveis
para dezembro 2025, com média de R$515/noite.

---

## 📚 FONTES CONSULTADAS

### 🔍 Buscas Web (DuckDuckGo)
- Busca Web MCP via DuckDuckGo
- Query: 'pousadas boutique Paraty preços alta temporada'
- Data: 2025-10-31 14:35

### 🏠 Airbnb
- Airbnb MCP
- Localização: Paraty
- Filtros: {"location": "Paraty", "checkin": "2025-12-20", "adults": 2}
- Data: 2025-10-31 14:37
```

---

## 🧪 Testing & Validation

### Consolidated Test Suite

**test_mcp_suite.py** - Suite completa com 4 tipos de testes:

```bash
# Test completo (todos os 4 testes)
poetry run python test_mcp_suite.py

# Test apenas conectividade (~3s)
poetry run python test_mcp_suite.py --quick

# Test agente com LLM (~15s)
poetry run python test_mcp_suite.py --agent

# Test auditoria de cobertura (~5s)
poetry run python test_mcp_suite.py --audit
```

### Test Coverage

**TESTE 1: Conectividade** - Valida conexão com Docker MCP Gateway
- Verifica 61 ferramentas disponíveis
- Testa filtragem por categoria (search, maps, etc)

**TESTE 2: Agente com LLM** - Execução real com Ollama
- Cria agente com MCP tools
- Executa tarefa real (pesquisa sobre Paraty)
- Valida retorno do LLM

**TESTE 3: Auditoria de Cobertura** - Verifica todos os agentes
- Analisa 13 agentes do projeto
- Valida distribuição por categoria
- Confirma 100% usando MCP tools

**TESTE 4: Execução Real de Tools** - Opera cada ferramenta MCP
- **search**: Pesquisa web com DuckDuckGo
- **wikipedia**: Consulta artigos da Wikipedia
- **youtube**: Obtém metadados de vídeos
- **maps**: Geocodificação e busca de lugares
- **airbnb**: Busca de listagens
- **fetch**: Download de conteúdo web

### Expected Results

```
✅ TESTE 1: CONECTIVIDADE - 61 tools disponíveis
✅ TESTE 2: AGENTE COM LLM - Task completed com resultado real
✅ TESTE 3: AUDITORIA - 13/13 agentes (100%) com MCP tools
✅ TESTE 4: EXECUÇÃO REAL - 6/6 ferramentas executadas com sucesso

📋 Resultados Detalhados:
   ✅ SEARCH → Paraty é uma cidade histórica...
   ✅ WIKIPEDIA → Paraty é um município brasileiro...
   ✅ YOUTUBE → Rick Astley - Never Gonna Give You Up...
   ✅ MAPS → Coordenadas: lat -23.2189, lng -44.7134
   ✅ AIRBNB → Casa Charming em Paraty (avaliação 4.8)
   ✅ FETCH → Página HTML completa do example.com

🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção
```

### Reference Test (OLD CLI Approach)

**test_mcp_complete_OLD.py** - Mantido apenas como referência da abordagem CLI anterior.
Não é necessário executar - use test_mcp_suite.py para todos os testes.

---

**What It Tests:**
1. ✅ Agent tool coverage (13/13 agents)
2. ✅ Docker Gateway status (11 servers)
3. ✅ Python tool definitions (7 tools)
4. ✅ Real tool execution (search, fetch, etc.)
5. ✅ Metadata tracking structure

**Expected Output:**
```
======================================================================
🎉 RESUMO FINAL
======================================================================
✅ Agentes com MCP tools: 13/13 (100.0%)
✅ Docker MCP Gateway: RODANDO (11/11 servers)
✅ Ferramentas Python: 7/7 definidas
✅ Testes de integração: 7/7 passados
✅ Metadata tracking: Estrutura válida

🎉 Tudo está configurado perfeitamente!
✅ Sistema pronto para uso em produção!
```

### Verbose Mode (Detailed Output)

```bash
# See full tool responses
poetry run python test_mcp_complete.py --verbose
```

**Use Verbose When:**
- 🔍 Debugging specific tool issues
- 📊 Validating tool response formats
- 🐛 Investigating non-JSON responses
- 📈 Understanding what MCP servers return

### Source Tracking Test

```bash
# Validate metadata injection
poetry run python test_source_tracking.py
```

**Expected Output:**
```
✅ Ferramentas com rastreamento: 3/3
🎉 SUCESSO! Todas as ferramentas estão registrando fontes corretamente!
```

### Full Workflow Test

```bash
# Run complete workflow with agents
poetry run start
# Select: D (Planejamento 30 Dias)
```

**What to Verify:**
- Agents calling MCP tools (console shows `🔧 Tool: ...`)
- Citations in output ("Segundo [Source] em [Date]: ...")
- "📚 FONTES CONSULTADAS" section in final document

---

## 🔄 Migration from Old Approach

### Why Migrate?

**Old Approach (CLI commands):**
- ❌ Uses `docker mcp tool call` commands
- ❌ Returns help text instead of executing
- ❌ Not thread-safe for multiple agents
- ❌ Manual JSON parsing required
- ❌ No automatic tool discovery

**New Approach (Native MCPServerAdapter):**
- ✅ Official CrewAI integration
- ✅ Stdio connection to Docker Gateway
- ✅ Automatic tool discovery (~60 tools)
- ✅ Thread-safe and optimized
- ✅ Zero manual configuration

### Migration Steps

#### 1. Update Dependencies

```bash
# Update pyproject.toml
poetry remove crewai  # Remove old version
poetry add "crewai[tools]@>=1.2.1" mcp "crewai-tools[mcp]@>=1.2.1"
```

#### 2. Replace Imports

**Before:**
```python
from src.crewai_local.tools.mcp_tools import (
    mcp_search_tool,
    mcp_fetch_tool,
    mcp_wikipedia_tool
)
```

**After:**
```python
from src.crewai_local.tools.mcp_tools_new import (
    get_search_tools,
    get_location_tools,
    get_docker_mcp_tools_filtered
)
```

#### 3. Update Agents

**Before:**
```python
agent = Agent(
    role="Researcher",
    tools=[mcp_search_tool]  # Single CLI tool
)
```

**After (Option 1 - Helper Functions):**
```python
agent = Agent(
    role="Researcher",
    tools=get_search_tools()  # List of native tools
)
```

**After (Option 2 - DSL Syntax):**
```python
agent = Agent(
    role="Researcher",
    mcps=["docker://gateway"]  # Automatic!
)
```

#### 4. Update web_tools.py

**Before:**
```python
from .mcp_tools import mcp_search_tool

def get_enhanced_tools_for_agent(profile: str):
    if profile == "estrategista":
        return [mcp_search_tool]
```

**After:**
```python
from .mcp_tools_new import get_search_tools

def get_enhanced_tools_for_agent(profile: str):
    if profile == "estrategista":
        return get_search_tools()  # Returns list of tools
```

#### 5. Test Migration

```bash
# Basic test
poetry run python test_mcp_basic.py

# Full test
poetry run python test_mcp_complete.py
```

#### 6. Deprecate Old Files

```bash
# Rename for reference
mv src/crewai_local/tools/mcp_tools.py src/crewai_local/tools/mcp_tools_OLD.py
```

---

## 🐛 Troubleshooting

### Issue: "Container not found"

**Error:** `docker exec: container mcp-server-container not found`

**Solution:**
```bash
# Check container name
docker ps | grep mcp

# Update command in code if needed
# In mcp_tools.py, change container name:
command = ["docker", "exec", "YOUR-ACTUAL-CONTAINER-NAME", ...]
```

### Issue: "Gateway not running"

**Error:** Test shows "❌ Docker MCP Gateway NÃO está rodando"

**Solution:**
```bash
# Start Docker Desktop
# Enable MCP Gateway in settings
# Check servers:
docker mcp server list
```

### Issue: "No tools found"

**Error:** `get_docker_mcp_tools()` returns empty list

**Solution:**
```bash
# Verify gateway connection
docker mcp gateway run

# Check if servers are added
docker mcp server list

# Add missing servers
docker mcp server add duckduckgo
```

### Issue: "OPENAI_API_KEY required"

**Error:** CrewAI 1.2.1+ requires LLM configuration

**Solution (Option 1 - Ollama):**
```python
from crewai import LLM

llm = LLM(
    model="ollama/qwen2.5:14b",
    base_url="http://localhost:11434"
)

agent = Agent(..., llm=llm)
```

**Solution (Option 2 - OpenAI):**
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

agent = Agent(...)  # Uses OpenAI by default
```

### Issue: "Metadata not appearing"

**Error:** Source tracking test fails

**Solution:**
```bash
# Verify datetime import in mcp_tools.py
from datetime import datetime

# Check metadata injection in each tool function
# Should have:
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
metadata = f"📊 FONTE: ...\n⏰ Data: {timestamp}\n..."
```

### Issue: "Tools too slow"

**Problem:** First connection takes ~3 seconds

**Solution:**
```python
# This is normal - tools are lazy-loaded
# Subsequent calls are instant
# If persistently slow:

# 1. Check Docker resources (CPU/RAM)
# 2. Restart Docker Gateway
docker restart mcp-gateway

# 3. Reduce tool count if possible
tools = get_docker_mcp_tools_filtered(["search", "fetch"])  # Only essentials
```

### Issue: "Agent not using tools"

**Problem:** Agent generating responses without calling MCP tools

**Solution:**
```python
# 1. Ensure tools are passed to agent
agent = Agent(
    ...,
    tools=get_search_tools(),  # Must include this!
    verbose=True  # See tool calls
)

# 2. Make task description tool-friendly
task = Task(
    description="""
    IMPORTANTE: Use as ferramentas disponíveis para buscar dados reais.
    Busque em DuckDuckGo, Airbnb, Google Maps conforme necessário.
    """,
    agent=agent
)

# 3. Check LLM model - some models better at tool use
# GLM-4.6, Qwen2.5 > gpt-oss for tool calling
```

---

## 📖 API Reference

### mcp_tools_new.py Functions

#### `get_docker_mcp_tools() -> List[Any]`

Returns all available tools from Docker MCP Gateway (~60 tools).

**Returns:** List of MCP Tool objects

**Example:**
```python
from src.crewai_local.tools.mcp_tools_new import get_docker_mcp_tools

all_tools = get_docker_mcp_tools()
print(f"Available: {len(all_tools)} tools")
```

---

#### `get_docker_mcp_tools_filtered(tool_names: List[str]) -> List[Any]`

Returns specific tools by name.

**Parameters:**
- `tool_names` (List[str]): List of tool names to retrieve

**Returns:** List of matching MCP Tool objects

**Example:**
```python
tools = get_docker_mcp_tools_filtered([
    "search",
    "maps_geocode",
    "airbnb_search"
])
```

---

#### `get_search_tools() -> List[Any]`

Returns search-related tools: DuckDuckGo, Wikipedia, YouTube info.

**Returns:** List of 3 MCP Tool objects

**Use Case:** Research, market analysis, content discovery

---

#### `get_data_fetch_tools() -> List[Any]`

Returns data fetching tools: Fetch URL content.

**Returns:** List of 1 MCP Tool object

**Use Case:** Extract webpage content, parse articles

---

#### `get_wikipedia_tools() -> List[Any]`

Returns Wikipedia-specific tools.

**Returns:** List of Wikipedia MCP Tool objects

**Use Case:** Encyclopedia research, historical context

---

#### `get_youtube_tools() -> List[Any]`

Returns YouTube tools: video info, transcripts.

**Returns:** List of YouTube MCP Tool objects

**Use Case:** Video content analysis, transcript extraction

---

#### `get_location_tools() -> List[Any]`

Returns location tools: Google Maps + Search + Fetch.

**Returns:** List of 3 MCP Tool objects

**Use Case:** Geographic analysis, route planning, POI discovery

---

#### `get_browser_tools() -> List[Any]`

Returns Playwright browser automation tools.

**Returns:** List of ~17 MCP Tool objects

**Use Case:** Web scraping, interactive navigation, form filling

---

#### `get_airbnb_tools() -> List[Any]`

Returns Airbnb search and details tools.

**Returns:** List of 2 MCP Tool objects

**Use Case:** Competitive pricing analysis, accommodation research

---

### mcp_tools.py Functions (Source Tracking)

#### `extract_sources_from_text(text: str) -> List[str]`

Extracts all source citations from agent output.

**Parameters:**
- `text` (str): Agent output or document text

**Returns:** List of source metadata strings

**Example:**
```python
from src.crewai_local.tools.mcp_tools import extract_sources_from_text

sources = extract_sources_from_text(agent_output)
# ['📊 FONTE: Busca Web MCP', '⏰ Data: 2025-10-31', ...]
```

---

#### `generate_sources_section(sources: List[str]) -> str`

Generates formatted "FONTES CONSULTADAS" markdown section.

**Parameters:**
- `sources` (List[str]): List of source metadata (from `extract_sources_from_text`)

**Returns:** Markdown string with formatted sources section

**Example:**
```python
from src.crewai_local.tools.mcp_tools import (
    extract_sources_from_text,
    generate_sources_section
)

sources = extract_sources_from_text(agent_output)
section = generate_sources_section(sources)

final_doc = agent_output + "\n\n" + section
```

---

### web_tools.py Functions

#### `get_enhanced_tools_for_agent(profile: str) -> List[Any]`

Returns MCP tools based on agent profile.

**Parameters:**
- `profile` (str): Agent profile name
  - `"estrategista"` - Search + Fetch + Wikipedia (3 tools)
  - `"mercado"` - Search + Fetch + Browser + Airbnb + Wikipedia + YouTube (6 tools)
  - `"localizacao"` - Maps + Search + Fetch (3 tools)
  - `"marketing"` - Search + Fetch + YouTube (3 tools)
  - `"tecnico"` - Search + Fetch + Wikipedia (3 tools)

**Returns:** List of MCP Tool objects for that profile

**Example:**
```python
from src.crewai_local.tools.web_tools import get_enhanced_tools_for_agent

# Get tools for market analyst
tools = get_enhanced_tools_for_agent("mercado")  # 6 tools

# Use in agent
agent = Agent(
    role="Market Analyst",
    tools=tools,
    ...
)
```

---

## 📝 Best Practices

### 1. Tool Selection

✅ **DO:** Use helper functions for common profiles
```python
tools = get_search_tools()  # Pre-configured set
```

❌ **DON'T:** Manually create tool lists
```python
tools = [tool1, tool2, tool3]  # Error-prone
```

### 2. Source Citations

✅ **DO:** Include citation instructions in tasks
```python
description = """
Analyze market data.

⚠️ OBRIGATÓRIO: Cite sources as "Segundo [Fonte] em [Data]: ..."
"""
```

❌ **DON'T:** Assume agents will cite automatically
```python
description = "Analyze market data."  # No citation guidance
```

### 3. Error Handling

✅ **DO:** Validate tool availability before workflows
```bash
poetry run python test_mcp_basic.py  # Quick check
```

❌ **DON'T:** Run workflows without testing
```bash
poetry run start  # May fail if gateway down
```

### 4. Performance

✅ **DO:** Use filtered tools when possible
```python
tools = get_docker_mcp_tools_filtered(["search", "fetch"])  # Only what you need
```

❌ **DON'T:** Load all tools unnecessarily
```python
tools = get_docker_mcp_tools()  # 60 tools when you need 2
```

### 5. Documentation

✅ **DO:** Generate sources section for reports
```python
section = generate_sources_section(extract_sources_from_text(output))
final_report = output + section
```

❌ **DON'T:** Rely solely on inline citations
```python
# Missing consolidated sources section
final_report = output  # No way to audit all sources
```

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - Project overview and quick start
- **EXECUTION_GUIDE.md** - Detailed workflow execution guide
- **CHANGELOG.md** - Project history and changes

### Code Files

- **src/crewai_local/tools/mcp_tools_new.py** - Native MCP integration (150 lines)
- **src/crewai_local/tools/mcp_tools.py** - Source tracking system (legacy CLI)
- **src/crewai_local/tools/web_tools.py** - Tool distribution by profile
- **test_mcp_basic.py** - Basic connection test
- **test_mcp_complete.py** - Complete test suite
- **test_source_tracking.py** - Metadata validation

### External Links

**CrewAI MCP Documentation:**
- Overview: https://docs.crewai.com/en/mcp/overview
- DSL Integration: https://docs.crewai.com/en/mcp/dsl-integration
- Stdio Transport: https://docs.crewai.com/en/mcp/stdio

**Docker MCP Gateway:**
- Toolkit: https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/
- Gateway: https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/
- Catalog: https://hub.docker.com/mcp

---

## 🎯 Summary

### Quick Reference

```bash
# Test connection
poetry run python test_mcp_basic.py

# Full validation
poetry run python test_mcp_complete.py

# Run workflow
poetry run start
```

### Key Takeaways

1. **Native Integration** - CrewAI 1.2.1+ has built-in MCP support
2. **Docker Gateway** - Connects to ~60 tools from 11 servers
3. **Source Tracking** - Every tool adds timestamped metadata
4. **100% Coverage** - All 13 agents use appropriate MCP tools
5. **Easy Testing** - Comprehensive test suite validates everything

### System Status

```
✅ CrewAI: 1.2.1+ (native MCP)
✅ MCP Library: 1.20.0
✅ Agents: 13/13 with tools (100%)
✅ Tools: ~60 available
✅ Servers: 11 active
✅ Tests: All passing
✅ Production: Ready
```

---

**Version:** 3.0 Native Integration  
**Last Updated:** 31 Oct 2025  
**Maintained By:** CrewAI Multi-Agent Team
