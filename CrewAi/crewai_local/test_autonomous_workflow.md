# Testing Autonomous Property Evaluation Workflow

## Overview
The property evaluation workflow now operates in **AUTONOMOUS RESEARCH MODE**, requiring only a property name OR link.

## Setup

1. **Start Docker Infrastructure:**
```powershell
cd D:\Dev\py\AgenticArmy\Localn8n\self-hosted-ai-starter-kit
docker compose --profile cpu up -d
```

2. **Start CrewAI FastAPI Server:**
```powershell
cd D:\Dev\py\AgenticArmy\CrewAi\crewai_local
poetry install
poetry run api
```

Server will be available at: http://localhost:8000
API Docs at: http://localhost:8000/docs

## Test Cases

### Test 1: Property Name Only
```bash
curl -X POST http://localhost:8000/workflows/property-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "property_name": "Pousada do Sandi",
    "location_hint": "Paraty - RJ"
  }'
```

**Expected:**
- Juliana researches "Pousada do Sandi" online
- Finds property details, pricing, room count
- Analyzes competitors for ADR/occupancy benchmarks
- Remaining 5 agents use researched data

### Test 2: Property Link (Airbnb)
```bash
curl -X POST http://localhost:8000/workflows/property-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "property_link": "https://www.airbnb.com.br/rooms/12345678"
  }'
```

**Expected:**
- Juliana fetches property page directly
- Extracts all data from listing
- Remaining agents use extracted data

### Test 3: Async Mode (Recommended for production)
```bash
# Start async job
curl -X POST http://localhost:8000/workflows/property-evaluation/async \
  -H "Content-Type: application/json" \
  -d '{
    "property_name": "Pousada do Sandi",
    "location_hint": "Paraty",
    "webhook_url": "http://n8n:5678/webhook/property-eval-complete"
  }'

# Returns immediately with job_id:
# {"job_id": "property_evaluation-20250201-abc123", ...}

# Check status:
curl http://localhost:8000/workflows/property_evaluation-20250201-abc123/status
```

### Test 4: Invalid Input (Should Fail)
```bash
curl -X POST http://localhost:8000/workflows/property-evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "location_hint": "Paraty"
  }'
```

**Expected:** Validation error - must provide property_name OR property_link

## Verification Checklist

- [ ] API accepts requests with only property_name
- [ ] API accepts requests with only property_link
- [ ] API rejects requests with neither identifier
- [ ] Research task (Juliana) executes first
- [ ] Research task gathers: price, rooms, ADR, occupancy, CAPEX
- [ ] Subsequent tasks reference researched data
- [ ] Final output includes complete evaluation report
- [ ] Async mode works with webhook callback

## Expected Output Structure

```markdown
# AVALIAÇÃO DE PROPRIEDADE - [Nome da Propriedade]

## 1. DADOS PESQUISADOS (Juliana)
- Nome: ...
- Preço: R$ ...
- Quartos: ...
- ADR target: R$ ...
- Ocupação target: ...%
- CAPEX estimado: R$ ...

## 2. CONTEXTO LOCAL (Marcelo)
- Eventos FLIP, calendário...
- 10-15 experiências autênticas...

## 3. AVALIAÇÃO TÉCNICA (André)
- CAPEX detalhado por prioridade...
- Timeline de obras...

## 4. DUE DILIGENCE (Fernando)
- Análise jurídica...
- GO/NO-GO/RESSALVAS

## 5. MODELAGEM FINANCEIRA (Ricardo)
- VPL, TIR, Payback...
- 3 cenários...
- COMPRAR / NÃO COMPRAR / RENEGOCIAR

## 6. STRESS TEST (Gabriel)
- Pre-mortem analysis...
- Risk matrix...
- Conclusão final
```

## N8N Integration Example

**Workflow nodes:**

1. **Webhook Trigger** (receives property_name from user)
2. **HTTP Request** → POST localhost:8000/workflows/property-evaluation
   - Body: `{{ {"property_name": $json.property_name} }}`
3. **Code Node** → Parse markdown result
4. **PostgreSQL** → Save evaluation to database
5. **Send Email** → Notify stakeholders with recommendation

## Troubleshooting

### Issue: "Ollama not connected"
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If not running, start Docker stack
docker compose --profile cpu up -d
```

### Issue: "Docker MCP Gateway unavailable"
```bash
# Check Docker MCP tools
docker mcp tools list

# If not working, ensure Docker Desktop is running
```

### Issue: "Research task returns no data"
- Verify internet connectivity for web search
- Check MCP tools are working: `docker mcp tools call search query="test"`
- Try providing property_link instead of property_name

## Performance Notes

- **Research phase:** 5-7 minutes (Juliana gathering data)
- **Analysis phase:** 10-18 minutes (5 agents analyzing)
- **Total duration:** 15-25 minutes
- **Tokens usage:** ~50k-80k tokens (with research)
- **MCP tool calls:** 10-20 calls (search, fetch, airbnb)

## Success Criteria

✅ Workflow completes without errors
✅ Research task provides all required data
✅ No hardcoded values used (all from research)
✅ Final report includes go/no-go recommendation
✅ Execution time within expected range (15-25 min)
