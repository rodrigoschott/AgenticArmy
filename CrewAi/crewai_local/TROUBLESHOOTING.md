# TROUBLESHOOTING GUIDE

Complete troubleshooting guide for CrewAI Local - Paraty Project.

## Table of Contents

1. [Docker & MCP Issues](#docker--mcp-issues)
2. [Ollama Issues](#ollama-issues)
3. [Python & Dependencies](#python--dependencies)
4. [Google Maps API Issues](#google-maps-api-issues)
5. [Performance Issues](#performance-issues)
6. [Logging & Debugging](#logging--debugging)

---

## Docker & MCP Issues

### Problem: "Docker command not found"

**Symptoms:**
```
❌ DOCKER COMMAND NOT FOUND
💡 Docker Desktop may not be installed or not in PATH
```

**Solutions:**
1. **Install Docker Desktop:**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and restart your computer
   - Verify installation: `docker --version`

2. **Add Docker to PATH (Windows):**
   - Docker Desktop should automatically add itself to PATH
   - If not, manually add: `C:\Program Files\Docker\Docker\resources\bin`

3. **Verify Docker is running:**
   - Check system tray for Docker icon
   - Run: `docker ps`
   - If not running, start Docker Desktop

---

### Problem: "Docker MCP Gateway not responding"

**Symptoms:**
```
❌ Docker MCP Gateway NÃO RESPONDE
💡 Erro: invalid character...
```

**Solutions:**
1. **Enable MCP Toolkit in Docker Desktop:**
   - Open Docker Desktop settings
   - Navigate to "Features in development" or "Experimental features"
   - Enable "MCP Toolkit" or "Model Context Protocol"
   - Restart Docker Desktop

2. **Verify MCP is enabled:**
   ```bash
   docker mcp tools list
   ```

3. **Restart Docker Desktop:**
   - Quit Docker Desktop completely
   - Wait 10 seconds
   - Start Docker Desktop again

4. **Check Docker version:**
   - MCP requires Docker Desktop 4.36+ (November 2024 or later)
   - Update if necessary: Docker Desktop → Check for updates

---

### Problem: "MCP server initialization failed" (filesystem, desktop-commander)

**Symptoms:**
```
Can't start filesystem: failed to connect: calling 'initialize': EOF
Can't start desktop-commander: invalid character '>' looking for beginning of value
```

**Solutions:**

**For Filesystem Server:**
1. Check if npx/Node.js is installed:
   ```bash
   npx --version
   node --version
   ```
2. If not installed, install Node.js from https://nodejs.org
3. Restart Docker Desktop after installing Node.js

**For Desktop Commander:**
1. This server requires Windows-specific permissions
2. May not work on all systems (optional server)
3. Disable if not needed - system works without it

**Note:** 9/11 servers working is sufficient for production use. The failed servers provide optional functionality.

---

### Problem: "OAuth notification stream failed"

**Symptoms:**
```
Failed to connect to OAuth notifications
dial unix \\.\pipe\dockerBackendApiServer: connect: No connection could be made
```

**Solutions:**
1. This is a **non-critical warning** - system works without it
2. Ensure Docker Desktop is fully started (wait 30 seconds after starting)
3. Check Docker Desktop settings → "Expose daemon on tcp://localhost:2375 without TLS"

**Impact:** OAuth-based MCP tools may require manual authentication. Most tools work without this.

---

## Ollama Issues

### Problem: "Ollama is not available"

**Symptoms:**
```
❌ Ollama is not available at http://localhost:11434
```

**Solutions:**
1. **Install Ollama:**
   - Download from https://ollama.com
   - Install and verify: `ollama --version`

2. **Start Ollama service:**
   ```bash
   # Start Ollama in background
   ollama serve
   ```

3. **Verify Ollama is accessible:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Check if models are installed:**
   ```bash
   ollama list
   ```

5. **Pull recommended models:**
   ```bash
   # Good balance of performance and quality
   ollama pull qwen2.5:14b

   # Other options:
   ollama pull llama3.3:70b  # Best quality, needs 48GB+ RAM
   ollama pull mistral:7b    # Fast, needs 8GB RAM
   ollama pull gemma2:27b    # Good quality, needs 20GB RAM
   ```

---

### Problem: "Static/cycling responses from agents"

**Symptoms:**
- Agents always give the same response
- Output says "using static fallback LLM"

**Cause:** Ollama not available, system using fallback mode

**Solutions:**
1. Follow steps in "Ollama is not available" above
2. Ensure `OLLAMA_BASE_URL` in `.env` is correct
3. Restart the application after starting Ollama

**Note:** Static fallback is intentional for offline testing but produces low-quality results. Always use Ollama for production.

---

### Problem: "Invalid response from LLM call - None or empty" (gpt-oss model)

**Symptoms:**
```
ValueError: Invalid response from LLM call - None or empty.
```

**Cause:** Using `gpt-oss` model which has incompatible response format with CrewAI

**Explanation:**
The `gpt-oss` model uses a special "thinking mode" that returns responses in this format:
```
Thinking...
[Internal reasoning]
...done thinking.

[Actual response]
```

CrewAI's agent executor expects direct responses and cannot parse this format, resulting in empty/None responses.

**Solutions:**
1. **Use recommended models instead:**
   ```bash
   # Best option - excellent tool calling
   ollama pull qwen2.5:14b
   
   # Fast alternative
   ollama pull llama3.2:latest
   
   # Cloud option
   ollama pull glm-4.6:cloud
   ```

2. **When starting workflow, select a compatible model:**
   - Choose `qwen2.5:14b` (⭐ recommended)
   - Choose `glm-4.6:cloud` (⭐ recommended)
   - Choose `llama3.2:latest` (⭐ recommended)
   - **AVOID** `gpt-oss:latest` ❌

3. **Check model compatibility:**
   - See `MODELS_COMPATIBILITY.md` for full compatibility matrix
   - Test model: `ollama run <model> "Say hello"`
   - If response includes "Thinking..." → incompatible with CrewAI

**When to use gpt-oss:**
- ✅ Standalone conversations: `ollama run gpt-oss`
- ✅ Simple Python scripts without tools
- ❌ **NEVER** with CrewAI workflows
- ❌ **NEVER** with agents using tools

---

## Python & Dependencies

### Problem: "The currently activated Python version 3.13.7 is not supported"

**Symptoms:**
```
The currently activated Python version 3.13.7 is not supported by the project (>=3.11,<3.14)
```

**Solutions:**
1. **This is now fixed** - pyproject.toml updated to support Python 3.11-3.13
2. Update dependencies:
   ```bash
   poetry lock
   poetry install
   ```

3. **If you prefer specific Python version:**
   ```bash
   poetry env use python3.11
   poetry install
   ```

---

### Problem: "UnicodeDecodeError in subprocess"

**Symptoms:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d
```

**Solutions:**
1. **This is now fixed** - subprocess calls use `encoding='utf-8', errors='replace'`
2. If you still see this, update `web_tools.py` to latest version
3. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:PYTHONIOENCODING="utf-8"

   # Windows CMD
   set PYTHONIOENCODING=utf-8
   ```

---

### Problem: "ModuleNotFoundError" or import errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'crewai_local'
```

**Solutions:**
1. **Reinstall dependencies:**
   ```bash
   poetry install
   ```

2. **Verify you're in the correct directory:**
   ```bash
   cd D:\Dev\py\AgenticArmy\CrewAi\crewai_local
   ```

3. **Clear Poetry cache and reinstall:**
   ```bash
   poetry cache clear pypi --all
   poetry install --no-cache
   ```

4. **Check virtual environment:**
   ```bash
   poetry env info
   poetry shell  # Activate environment
   ```

---

## Google Maps API Issues

### Problem: "This API project is not authorized to use this API"

**Symptoms:**
```
Error calling maps_geocode: This API project is not authorized to use this API
```

**Solutions:**
1. **Get Google Maps API Key:**
   - Go to https://console.cloud.google.com/apis/credentials
   - Create project if needed
   - Create API key

2. **Enable required APIs:**
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Directions API

3. **Configure environment:**
   - Add to `.env`:
     ```
     GOOGLE_MAPS_API_KEY=your_actual_key_here
     ```

4. **Verify key restrictions:**
   - Check API key restrictions in Google Cloud Console
   - For development, use "None" restriction
   - For production, restrict to specific IPs/domains

---

### Problem: "Location tools not working"

**Symptoms:**
- maps_geocode fails
- maps_search_places fails
- Marcelo Ribeiro agent (localizacao) cannot find locations

**Solutions:**
1. Check if Google Maps API key is configured (see above)
2. Verify API key has sufficient quota:
   - Go to Google Cloud Console → APIs & Services → Quotas
   - Check if you've exceeded free tier limits
3. If not critical, disable location tools:
   - Location tools are optional
   - System works without them

---

## Performance Issues

### Problem: "MCP tools are slow (3-4 seconds per call)"

**Symptoms:**
- Long wait times between agent actions
- "Reading configuration..." appears multiple times
- Workflows take 10+ minutes

**Current Status:** **PARTIALLY FIXED**
- CLI approach eliminates connection overhead
- Each tool call is independent (no connection reuse needed)
- Typical response time: 1-3 seconds per tool

**Further optimizations:**
1. **Use specific tool sets per agent:**
   - Don't give all tools to all agents
   - Use `get_enhanced_tools_for_agent(agent_type)` appropriately

2. **Reduce agent count:**
   - Combine similar tasks
   - Use fewer, more capable agents

3. **Ollama optimization:**
   - Use smaller models for faster responses
   - Use GPU if available
   - Increase Ollama context window

---

### Problem: "High memory usage"

**Symptoms:**
- System slows down during execution
- Out of memory errors
- Docker Desktop using lots of RAM

**Solutions:**
1. **Optimize Ollama model selection:**
   - Use 7B models (8GB RAM needed)
   - Avoid 70B models unless you have 48GB+ RAM
   - Recommended: qwen2.5:14b (12GB RAM)

2. **Adjust Docker resource limits:**
   - Docker Desktop → Settings → Resources
   - Reduce memory allocation if needed
   - Minimum: 4GB for Docker

3. **Close other applications:**
   - CrewAI agents can be memory-intensive
   - Close browsers, IDEs during execution

---

## Logging & Debugging

### Problem: "Cannot find log files"

**Solutions:**
1. **Default log location:**
   ```
   D:\Dev\py\AgenticArmy\CrewAi\crewai_local\logs\crewai.log
   ```

2. **Log rotation files:**
   - `crewai.log` - current log
   - `crewai.log.1` to `crewai.log.5` - rotated backups
   - Maximum 10MB per file

3. **Configure logging:**
   - Set `LOG_LEVEL` in `.env`:
     ```
     LOG_LEVEL=DEBUG  # For detailed logs
     LOG_LEVEL=INFO   # For normal operation
     ```

---

### Problem: "Need to debug MCP tool calls"

**Solutions:**
1. **Enable DEBUG logging:**
   ```bash
   # In .env
   LOG_LEVEL=DEBUG
   ```

2. **View tool calls in real-time:**
   ```bash
   # PowerShell
   Get-Content logs\crewai.log -Wait -Tail 50

   # Linux/Mac
   tail -f logs/crewai.log
   ```

3. **Test MCP tools manually:**
   ```bash
   # Test search tool
   docker mcp tools call search query="Paraty hotels"

   # Test fetch tool
   docker mcp tools call fetch url="https://example.com"

   # List all available tools
   docker mcp tools list
   ```

4. **Use print_available_tools():**
   ```python
   from crewai_local.tools.web_tools import print_available_tools
   print_available_tools()
   ```

---

### Problem: "Agent is stuck or not progressing"

**Solutions:**
1. **Check logs for errors:**
   - Look in `logs/crewai.log`
   - Search for "ERROR" or "CRITICAL"

2. **Verify Ollama is responding:**
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "qwen2.5:14b",
     "prompt": "Hello",
     "stream": false
   }'
   ```

3. **Check agent task definition:**
   - Review task descriptions in `tasks/*.py`
   - Ensure expected output is clear
   - Check if agent has appropriate tools

4. **Increase timeout:**
   - MCP tools have 30s default timeout
   - For slow operations, increase in `web_tools.py`

---

## Environment Variables Reference

Required environment variables and their purposes:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama API endpoint |
| `GOOGLE_MAPS_API_KEY` | No | None | Google Maps API access |
| `DEFAULT_MODEL` | No | None | Default Ollama model (will prompt if not set) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `LOG_MAX_SIZE_MB` | No | `10` | Max log file size before rotation |
| `LOG_BACKUP_COUNT` | No | `5` | Number of rotated log files to keep |
| `SKIP_DOCKER_CHECK` | No | `false` | Skip Docker validation (testing only) |
| `SKIP_STARTUP_VALIDATION` | No | `false` | Skip all validation (testing only) |

---

## Getting Help

If this guide doesn't solve your problem:

1. **Check logs:** `logs/crewai.log` with `LOG_LEVEL=DEBUG`
2. **Review documentation:**
   - `README.md` - Project overview
   - `MCP_GUIDE.md` - MCP tools documentation
   - `EXECUTION_GUIDE.md` - Workflow execution guide
3. **Create an issue:** Include:
   - Error message (full stack trace)
   - Log excerpt (last 50 lines)
   - Environment info (Python version, OS, Docker version)
   - Steps to reproduce

---

## Quick Diagnostics Checklist

Run through this checklist to identify issues:

```bash
# 1. Check Python version
python --version  # Should be 3.11-3.13

# 2. Check Docker
docker --version
docker ps

# 3. Check Docker MCP
docker mcp tools list

# 4. Check Ollama
curl http://localhost:11434/api/tags
ollama list

# 5. Check environment
cat .env  # or `type .env` on Windows

# 6. Check logs
cat logs/crewai.log  # or `type logs\crewai.log` on Windows

# 7. Test MCP tool
docker mcp tools call search query="test"

# 8. Run startup validation
poetry run start  # Check for validation errors
```

---

**Last Updated:** 2025-01-31
**Version:** 2.1
