# Test Suite Organization

Complete test suite for CrewAI Local - Paraty Project.

## Directory Structure

```
tests/
├── api/                    # API Tests (4 files)
│   ├── conftest.py        # API test fixtures
│   ├── test_endpoints.py  # API endpoint unit tests
│   ├── test_async.py      # Async workflow tests
│   ├── test_job_manager.py # JobManager tests
│   └── test_integration.py # API integration tests
│
├── mcp/                    # MCP Tool Tests (7 files)
│   ├── test_airbnb.py     # Airbnb search tool
│   ├── test_cli_tools.py  # CLI tool wrappers
│   ├── test_fetch.py      # URL content fetching
│   ├── test_maps.py       # Google Maps geocoding & places
│   ├── test_search.py     # DuckDuckGo web search
│   ├── test_wikipedia.py  # Wikipedia article summaries
│   └── test_youtube.py    # YouTube video info
│
├── integration/            # Integration Tests (2 files)
│   ├── test_mcp_suite.py  # ⭐ Main MCP integration suite
│   └── test_single_agent.py # Single agent workflow test
│
├── experimental/           # Experimental/Research Tests (4 files)
│   ├── test_event_loop_fix.py      # Event loop debugging
│   ├── test_event_loop_simple.py   # Simplified event loop test
│   ├── test_gptoss_toolcalls.py    # gpt-oss model compatibility
│   └── test_model_compatibility.py # Ollama model testing
│
├── unit/                   # Unit Tests (future)
│   └── (empty - for future unit tests)
│
├── conftest.py            # Shared test fixtures
├── __init__.py
└── README.md (this file)
```

---

## Quick Start

### Run All Tests

```bash
# Using pytest (recommended)
poetry run pytest tests/

# Or just (pytest auto-discovers tests/)
poetry run pytest

# Run with verbose output
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ --cov=src/crewai_local --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories

```bash
# API tests only
poetry run pytest tests/api/

# MCP tool tests only
poetry run pytest tests/mcp/

# Integration tests only
poetry run pytest tests/integration/

# Experimental tests only
poetry run pytest tests/experimental/

# Specific test file
poetry run pytest tests/api/test_endpoints.py
poetry run pytest tests/integration/test_mcp_suite.py
```

### Run Main MCP Suite

```bash
# Complete test suite (connectivity + agent + audit)
poetry run python tests/integration/test_mcp_suite.py

# Quick connectivity test only
poetry run python tests/integration/test_mcp_suite.py --quick

# Agent test only
poetry run python tests/integration/test_mcp_suite.py --agent

# Audit test only (check all 13 agents)
poetry run python tests/integration/test_mcp_suite.py --audit
```

---

## Test Categories

### 1. MCP Tool Tests (`tests/mcp/`)

**Purpose:** Test individual MCP tools via Docker MCP Gateway

**Coverage:**
- ✅ `test_search.py` - DuckDuckGo web search
- ✅ `test_fetch.py` - URL content fetching
- ✅ `test_wikipedia.py` - Wikipedia article summaries
- ✅ `test_youtube.py` - YouTube video metadata
- ⚠️ `test_maps.py` - Google Maps (requires API key)
- ⚠️ `test_airbnb.py` - Airbnb search (robots.txt issues)
- ✅ `test_cli_tools.py` - CLI wrapper validation

**Requirements:**
- Docker Desktop running
- MCP Toolkit enabled in Docker
- Google Maps API key (for maps test)

**Expected Results:**
- 5/7 tests pass without configuration
- 6/7 tests pass with Google Maps API key
- 7/7 tests pass with robots.txt bypass

---

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test complete workflows with agents and tools

#### `test_mcp_suite.py` ⭐ Main Test Suite

**What it tests:**
1. **Docker MCP Connectivity** - Gateway availability
2. **Agent with LLM** - Real agent task execution
3. **Agent Coverage Audit** - Verify all 13 agents use MCP tools

**Usage:**
```bash
# Full suite
poetry run python tests/integration/test_mcp_suite.py

# Quick check
poetry run python tests/integration/test_mcp_suite.py --quick
```

**Expected Output:**
```
✅ TESTE 1: Conectividade MCP - PASS
✅ TESTE 2: Agente com MCP + LLM - PASS
✅ TESTE 3: Auditoria de Agentes - PASS (13/13 agents 100%)
```

#### `test_single_agent.py`

**What it tests:**
- Single agent creation
- Tool assignment
- Task execution
- Output validation

**Requirements:**
- Ollama running
- Model available (qwen2.5:14b recommended)

---

### 3. API Tests (`tests/api/`)

**Purpose:** Test FastAPI REST API endpoints and integrations

**Coverage:**
- ✅ `test_endpoints.py` - Unit tests for API endpoints (health, models, sync workflows)
- ✅ `test_async.py` - Async workflow tests (job submission, status, cancellation, webhooks)
- ✅ `test_job_manager.py` - JobManager class tests (lifecycle, concurrency, cleanup)
- ✅ `test_integration.py` - Full end-to-end API workflow tests

**Requirements:**
- FastAPI and uvicorn installed (via `poetry install`)
- API server NOT running (tests use TestClient)
- Optional: Ollama for integration tests

**Test Categories:**

#### Unit Tests (`test_endpoints.py`)
- Root endpoint and API info
- Health check with Ollama/Docker status
- Models listing and recommendations
- Synchronous workflow endpoints (4 workflows)
- Request validation
- Model override functionality
- CORS headers
- Error handling

#### Async Tests (`test_async.py`)
- Async job submission for all 4 workflows
- Job status polling and updates
- Job cancellation
- Active jobs listing
- Webhook delivery and retry logic
- Concurrent job limits
- Job timeout handling

#### Job Manager Tests (`test_job_manager.py`)
- Job creation and initialization
- Status transitions (QUEUED → RUNNING → COMPLETED/FAILED)
- Elapsed time tracking
- Job retrieval and filtering
- Cancellation logic
- Webhook delivery
- Progress tracking

#### Integration Tests (`test_integration.py`)
- Complete sync workflow execution
- Complete async workflow with webhooks
- Status polling workflows
- Error handling scenarios
- CORS functionality
- Multiple concurrent workflows
- Model override integration
- API documentation accessibility

**Usage:**
```bash
# Run all API tests
poetry run pytest tests/api/

# Run specific test file
poetry run pytest tests/api/test_endpoints.py

# Run with coverage
poetry run pytest tests/api/ --cov=crewai_local.api --cov-report=html

# Run only unit tests
poetry run pytest tests/api/test_endpoints.py

# Run only slow tests (async/integration)
poetry run pytest tests/api/ -m slow

# Run excluding slow tests
poetry run pytest tests/api/ -m "not slow"
```

**Expected Results:**
- **test_endpoints.py:** 25-30 tests, all passing
- **test_async.py:** 20-25 tests, all passing
- **test_job_manager.py:** 15-20 tests, all passing
- **test_integration.py:** 10-15 tests, all passing

**Total:** ~70-90 API tests with >80% coverage

**Important Notes:**
- Tests use FastAPI TestClient (no server needed)
- Mocks are used for Ollama and workflow execution
- Async tests may take longer (marked with `@pytest.mark.slow`)
- Tests are isolated and can run in parallel

---

### 4. Experimental Tests (`tests/experimental/`)

**Purpose:** Development, debugging, and research tests

#### `test_event_loop_fix.py` & `test_event_loop_simple.py`

**What they test:**
- Event loop closure issues (RESOLVED in v2.2)
- nest_asyncio workaround (DEPRECATED)

**Status:** Historical - kept for reference

#### `test_model_compatibility.py`

**What it tests:**
- Ollama model compatibility with CrewAI
- Simple prompt responses
- Model availability

**Usage:**
```bash
poetry run python tests/experimental/test_model_compatibility.py
```

**Models tested:**
- qwen2.5:14b ✅
- llama3.3:70b ✅
- mistral:7b ✅
- gpt-oss ⚠️ (incompatible with tool calls)

#### `test_gptoss_toolcalls.py`

**What it tests:**
- Demonstrates why gpt-oss fails with CrewAI
- Tool calling behavior
- "Thinking mode" response format issues

**Purpose:** Educational - explains gpt-oss limitations

---

## Test Requirements

### Minimal (No external services)

```bash
# Just Python and dependencies
poetry install
poetry run pytest tests/experimental/test_model_compatibility.py
```

### Standard (Docker MCP)

```bash
# Requires Docker Desktop with MCP Toolkit
poetry run pytest tests/mcp/ -k "not maps and not airbnb"
```

### Full (Docker MCP + Ollama + API Keys)

```bash
# Requires all services
export GOOGLE_MAPS_API_KEY=your_key_here
poetry run pytest tests/
```

---

## Expected Test Results

### Baseline (Docker + Ollama running)

| Category | Expected Pass Rate | Notes |
|----------|-------------------|-------|
| MCP Tools | 5/7 (71%) | Airbnb & Maps require config |
| Integration | 2/2 (100%) | All should pass |
| Experimental | N/A | Not run by pytest |

### Optimal (All configured)

| Category | Expected Pass Rate | Notes |
|----------|-------------------|-------|
| MCP Tools | 6/7 (86%) | Airbnb blocked by robots.txt |
| Integration | 2/2 (100%) | All should pass |
| Experimental | N/A | Manual execution |

---

## Known Issues & Workarounds

### Issue: MCP Server Initialization Failures

**Symptoms:**
```
Can't start filesystem: failed to connect: EOF
Can't start desktop-commander: invalid character '>'
```

**Impact:** Low - 9/11 servers working is sufficient

**Workaround:** System functions normally with available servers

---

### Issue: Google Maps API Errors

**Symptoms:**
```
Error calling maps_geocode: This API project is not authorized
```

**Solution:**
1. Get API key from https://console.cloud.google.com
2. Enable Maps JavaScript API, Places API, Geocoding API
3. Add to `.env`:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_key
   ```

---

### Issue: Airbnb Robots.txt Blocking

**Symptoms:**
```
Error: This path is disallowed by Airbnb's robots.txt
```

**Workaround:** Use `ignoreRobotsText=true` parameter (already implemented in web_tools.py)

**Note:** Still may fail due to Airbnb's anti-scraping measures

---

### Issue: OAuth Notification Warnings

**Symptoms:**
```
Failed to connect to OAuth notifications
```

**Impact:** None - non-critical warning

**Action:** Ignore - system works without OAuth notifications

---

## Writing New Tests

### MCP Tool Test Template

```python
"""Test for [tool_name] MCP tool."""

def test_[tool_name]_basic():
    """Test basic [tool_name] functionality."""
    from src.crewai_local.tools.web_tools import [tool_function]

    result = [tool_function](param="value")

    assert result is not None
    assert "Error" not in result
    # Add specific assertions

if __name__ == "__main__":
    test_[tool_name]_basic()
```

### Integration Test Template

```python
"""Integration test for [feature]."""

from crewai import Agent, Task, Crew
from src.crewai_local.tools.web_tools import get_enhanced_tools_for_agent
from src.crewai_local.crew_paraty import _initialize_llm

def test_[feature]_integration():
    """Test [feature] end-to-end."""
    llm = _initialize_llm()
    tools = get_enhanced_tools_for_agent("estrategista")

    agent = Agent(
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory",
        tools=tools,
        llm=llm
    )

    task = Task(
        description="Test task",
        expected_output="Test output",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    assert result is not None
    # Add assertions

if __name__ == "__main__":
    test_[feature]_integration()
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Poetry
      run: pip install poetry

    - name: Install dependencies
      run: poetry install

    - name: Run tests
      run: poetry run pytest tests/ -v
```

---

## Troubleshooting

### Tests Hang or Timeout

**Cause:** Ollama not responding or model not loaded

**Solution:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Pull model if needed
ollama pull qwen2.5:14b
```

---

### Import Errors

**Cause:** Tests not finding src modules

**Solution:**
```bash
# Ensure you're in project root
cd D:\Dev\py\AgenticArmy\CrewAi\crewai_local

# Run with poetry
poetry run pytest tests/
```

---

### Docker MCP Not Available

**Cause:** Docker Desktop not running or MCP not enabled

**Solution:**
```bash
# Check Docker
docker ps

# Check MCP
docker mcp tools list

# If fails, enable MCP Toolkit in Docker settings
```

---

## Test Metrics

**Total Tests:** 18 files
**API Tests:** 4 files (~70-90 test cases)
**MCP Tests:** 7 files
**Integration Tests:** 2 files
**Experimental:** 4 files
**Unit Tests:** 0 files (future)

**Coverage Target:** 80%+
**Current Coverage:** TBD (run `pytest --cov`)
**API Coverage:** Expected 80%+ (covers api.py, background_jobs.py, models/)

---

## Contributing

When adding new tests:

1. **Choose correct category:**
   - `mcp/` - Testing individual MCP tools
   - `integration/` - Testing complete workflows
   - `unit/` - Testing individual functions/classes
   - `experimental/` - Research or debugging

2. **Follow naming convention:**
   - `test_<feature>.py` for test files
   - `test_<feature>_<aspect>()` for test functions

3. **Add documentation:**
   - Docstrings for all test functions
   - Comments for complex assertions
   - Update this README if adding new category

4. **Ensure tests are:**
   - Isolated (don't depend on other tests)
   - Repeatable (same input = same output)
   - Fast (< 30 seconds per test)
   - Clear (obvious what failed and why)

---

**Last Updated:** 2025-01-31
**Test Suite Version:** 2.2
**Maintainer:** CrewAI Local Team
