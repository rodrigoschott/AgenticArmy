# 🏨 Sistema Multi-Agente para Pousadas em Paraty

Sistema baseado em CrewAI com **13 agentes especializados** (v2.2) para apoiar decisões de aquisição e gestão de pousadas boutique em Paraty, RJ.

> **Versão:** 2.2 Refinado | **Data:** 31/01/2025 | **Agentes:** 13 | **Workflows:** 4

---

## 🚀 Início Rápido (5 minutos)

```powershell
# 1. Instalar dependências
poetry install

# 2. Executar sistema interativo
poetry run start

# 3. Ou executar exemplos
python exemplos.py
```

---

## ⚡ Requisitos Importantes

### 🔴 Ollama (OBRIGATÓRIO para Produção)

**O sistema REQUER Ollama para funcionar corretamente em produção.**

```bash
# 1. Instalar Ollama
# Download de: https://ollama.com

# 2. Verificar instalação
ollama --version

# 3. Baixar modelo recomendado
ollama pull qwen2.5:14b

# 4. Verificar disponibilidade
curl http://localhost:11434/api/tags
```

**Modelos Recomendados:**
- ⭐ **qwen2.5:14b** - Melhor equilíbrio performance/qualidade (12GB RAM)
- ⭐ **llama3.3:70b** - Máxima qualidade (48GB+ RAM)
- ⚡ **mistral:7b** - Rápido e leve (8GB RAM)

> **⚠️ IMPORTANTE:** O sistema possui modo fallback com respostas estáticas para **desenvolvimento/testes apenas**. Este modo NÃO deve ser usado em produção pois gera respostas genéricas de baixa qualidade.

**Verificação:**
```powershell
# Se você ver esta mensagem ao executar:
# "⚠️ Usando modo demonstração (respostas estáticas)"
#
# → Ollama não está disponível
# → Inicie Ollama: ollama serve
# → Verifique OLLAMA_BASE_URL no .env
```

### 🐳 Docker Desktop (Opcional - para MCP Tools)

MCP tools fornecem 60+ ferramentas aos agentes (busca web, Wikipedia, YouTube, Maps, etc.).

```bash
# Verificar se Docker MCP está disponível
docker mcp tools list

# Se não funcionar:
# 1. Instalar Docker Desktop (https://www.docker.com/products/docker-desktop)
# 2. Habilitar "MCP Toolkit" nas configurações
# 3. Reiniciar Docker Desktop
```

O sistema funciona SEM Docker MCP, mas os agentes terão capacidades limitadas.

---

## 👥 Equipe de Agentes (v2.2 - 13 Agentes)

### 🎯 Estratégia & Negócios (2 agentes)
- **Helena Andrade** - Estrategista de Negócios | `estrategista`
- **Ricardo Tavares** - Analista Financeiro | `estrategista`

### 📊 Mercado & Inteligência (2 agentes)
- **Juliana Campos** - Analista de Mercado Hoteleiro | `mercado`
- **Marcelo Ribeiro** - Especialista Paraty & Experiências | `localizacao`

### ⚖️ Jurídico & Compliance (2 agentes)
- **Dr. Fernando Costa** - Advogado Imobiliário | `estrategista`
- **Dra. Patrícia Lemos** - Compliance & Regulatório | `estrategista`

### 🔧 Técnico & Operacional (3 agentes)
- **Eng. André Martins** - Avaliador Técnico | `tecnico`
- **Arq. Sofia Duarte** - Arquiteta de Hospitalidade | `tecnico`
- **Paula Andrade** - Especialista em Operações | `tecnico`

### 📱 Marketing & Digital (2 agentes)
- **Beatriz Moura** - Estrategista de Marca | `marketing`
- **Thiago Alves** - Digital & Reputação | `marketing`

### ✅ Qualidade & Crítica (2 agentes)
- **Renata Silva** - Auditora de Experiência | `estrategista`
- **Gabriel Motta** - Devil's Advocate | `estrategista`

---

## 🔄 Workflows Disponíveis

### Workflow A: Avaliar Propriedade
**Objetivo:** Decisão go/no-go para aquisição  
**Agentes:** 5 (Marcelo, André, Fernando, Ricardo, Gabriel)  
**Tempo:** 10-20 minutos  
**Outputs:**
- Contexto local e experiências potenciais
- Laudo técnico + CAPEX realista
- Due diligence jurídica completa
- Valuation (3 cenários financeiros)
- Análise de riscos e stress test

### Workflow B: Estratégia de Posicionamento
**Objetivo:** Desenvolver posicionamento e marca  
**Agentes:** 4 (Juliana, Marcelo, Helena, Beatriz)  
**Tempo:** 8-15 minutos  
**Outputs:**
- Análise competitiva (15 pousadas)
- Segmentação de turistas
- Posicionamento estratégico (2-3 opções)
- Naming e identidade

### Workflow C: Preparação para Abertura
**Objetivo:** Preparar soft opening com conformidade  
**Agentes:** 4 (Paula, Patrícia, Sofia, Renata)  
**Tempo:** 10-18 minutos  
**Outputs:**
- SOPs completos
- Roadmap de licenciamento
- Compliance trabalhista
- Auditoria de experiência

### Workflow D: Plano 30 Dias
**Objetivo:** Análise estratégica completa  
**Agentes:** 13 (todos)  
**Tempo:** 2-3 horas  
**Outputs:** Análise integrada completa do projeto

---

## 💻 Uso

### Modo Interativo

```powershell
poetry run start
```

Menu:
```
🏨 SISTEMA DE AVALIAÇÃO DE POUSADAS - PARATY
======================================================================
1. Avaliar Propriedade Específica (Go/No-Go)
2. Desenvolver Estratégia de Posicionamento
3. Preparar para Abertura (Soft Opening)
4. Plano Completo 30 Dias
0. Sair
```

### Modo Programático

```python
from crewai_local.crew_paraty import (
    run_property_evaluation,
    run_positioning_strategy,
    run_opening_preparation
)

# Avaliar propriedade
result = run_property_evaluation()

# Desenvolver estratégia
result = run_positioning_strategy()

# Preparar abertura
result = run_opening_preparation()
```

---

## ⚙️ Configuração

### Ollama (Recomendado)

```powershell
# Instalar
winget install Ollama.Ollama

# Baixar modelo
ollama pull qwen2.5:14b

# Configurar (opcional)
$env:OLLAMA_BASE_URL = "http://localhost:11434"

# Verificar
curl http://localhost:11434/api/tags
```

**O sistema funciona sem Ollama** em modo demonstração (respostas estáticas).

### Modelos Recomendados
1. **GLM-4.6:cloud** (9GB) - Melhor qualidade
2. **Qwen2.5:14b** - Boa performance
3. **gpt-oss** - Fallback

---

## 🔧 Ferramentas MCP (Model Context Protocol)

Sistema integrado com **Docker MCP Gateway** para acesso a ~60 ferramentas:

### Ferramentas Disponíveis:
- **Busca:** DuckDuckGo, Wikipedia
- **Dados:** Fetch URL, YouTube transcripts
- **Localização:** Google Maps, Airbnb
- **Navegação:** Playwright (browser automation)

### Perfis de Ferramentas:
- `estrategista`: Search + Fetch + Wikipedia
- `mercado`: Search + Fetch + Browser + Airbnb + Wikipedia + YouTube
- `localizacao`: Maps + Search + Fetch
- `marketing`: Search + Fetch + YouTube
- `tecnico`: Search + Fetch + Wikipedia

**Cobertura:** 13/13 agentes (100%) usando ferramentas MCP

### Ver Documentação:
```bash
# Testar integração
poetry run python test_mcp_basic.py

# Teste completo
poetry run python test_mcp_complete.py

# Documentação completa
cat MCP_INTEGRATION.md
```

---

## 📁 Estrutura do Projeto

```
src/crewai_local/
├── agents/                 # 13 agentes especializados
│   ├── estrategia.py       # Helena + Ricardo
│   ├── mercado.py          # Juliana + Marcelo
│   ├── juridico.py         # Fernando + Patrícia
│   ├── tecnico.py          # André + Sofia + Paula
│   ├── marketing.py        # Beatriz + Thiago
│   └── qualidade.py        # Renata + Gabriel
│
├── crews/                  # 4 workflows
│   ├── workflow_avaliacao.py
│   ├── workflow_posicionamento.py
│   ├── workflow_abertura.py
│   └── workflow_completo.py
│
├── tools/                  # Ferramentas
│   ├── mcp_tools_new.py    # Integração MCP nativa (NOVO)
│   ├── mcp_tools.py        # Integração MCP antiga (deprecado)
│   └── web_tools.py        # Distribuição por perfil
│
├── crew_paraty.py          # Integração principal
└── main.py                 # Interface CLI
```

---

## 📊 Outputs

Resultados salvos em arquivos markdown:

- `avaliacao_[propriedade].md` - Workflow A
- `estrategia_posicionamento.md` - Workflow B
- `plano_abertura.md` - Workflow C
- `plano_completo_30_dias.md` - Workflow D

**Integração Obsidian:** Configure `OBSIDIAN_VAULT` em `crew_paraty.py`

---

## 🧪 Testes

### Suite Consolidada de Testes MCP

```bash
# Teste completo (recomendado)
poetry run python test_mcp_suite.py

# Teste rápido (apenas conectividade - 3s)
poetry run python test_mcp_suite.py --quick

# Teste de agente com LLM (~20s)
poetry run python test_mcp_suite.py --agent

# Auditoria de cobertura (~2s)
poetry run python test_mcp_suite.py --audit
```

**O que é testado:**
- ✅ Conectividade com Docker MCP Gateway (61 tools)
- ✅ Agente real executando tarefa com MCP tools + Ollama
- ✅ Cobertura de ferramentas em 13/13 agentes (100%)

**Resultado esperado:**
```
🎉 TODOS OS TESTES PASSARAM!
✅ Sistema pronto para produção
```

---

## 🐛 Troubleshooting

### Erro: "Import crewai could not be resolved"
```powershell
poetry install --no-cache
```

### Ollama não conecta
```powershell
curl http://localhost:11434/api/tags
# Sistema funciona sem Ollama (modo demo)
```

### Docker MCP Gateway não inicia
```powershell
# Verificar servers
docker mcp server list

# Documentação
# https://docs.docker.com/ai/mcp-catalog-and-toolkit/
```

---

## 📚 Documentação Adicional

- **GUIA_EXECUCAO.md** - Guia detalhado de execução
- **MCP_INTEGRATION.md** - Integração MCP completa
- **CHANGELOG.md** - Histórico de mudanças
- **TEST_MCP_README.md** - Documentação de testes

---

## 🔄 Mudanças v1.0 → v2.0

### Consolidação de Agentes
- **17 funções** → **13 agentes** (eficiência +30%)
- **4 consolidações:**
  1. Marcelo ← Lucas (Experiências)
  2. Patrícia ← Roberto (Trabalhista)
  3. Thiago ← Carla (Concorrência)
  4. Renata ← Eduardo (Processos)

### Nova Integração MCP
- ✅ 13/13 agentes com ferramentas MCP (100%)
- ✅ ~60 ferramentas via Docker Gateway
- ✅ Descoberta automática de tools
- ✅ Rastreamento de fontes com timestamps

### Benefícios
- Menos fragmentação (funções unificadas)
- Workflows eficientes (menos handoffs)
- Zero perda funcional
- Manutenção simplificada
- Integração MCP nativa (CrewAI 1.2.1+)

---

## 🤝 Contribuindo

Projeto de demonstração do sistema multi-agente para avaliação de pousadas.

---

## 📄 Licença

MIT License

---

**Sistema:** Paraty Multi-Agent v2.0  
**Framework:** CrewAI 1.2.1+ com MCP  
**Agentes:** 13 especializados  
**Workflows:** 4 principais  
**Ferramentas:** ~60 via Docker MCP Gateway  
**Última Atualização:** 31/10/2025


- Python 3.11-3.13
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências
- **Obrigatório (produção)**: [Ollama](https://ollama.com/) rodando (modelos recomendados: qwen2.5:14b, llama3.3:70b)
- Opcional: Docker Desktop com MCP Toolkit (para ferramentas avançadas)

## Configuração

1. Instale as dependências:

   ```powershell
   poetry install
   ```

1. Ajuste variáveis de ambiente (`.env`) para apontar para seus serviços Ollama, Qdrant, n8n, etc.
2. (Opcional) Ajuste a URL base do Ollama caso seu serviço não esteja no padrão do docker-compose (`http://localhost:11434`). O repositório já inclui esse valor no arquivo `.env`, então basta garantir que a stack `Skynet` esteja em execução.

   ```powershell
   setx OLLAMA_BASE_URL http://localhost:11434
   ```

   Se o endpoint não responder, o projeto usa respostas estáticas de fallback para permitir execução offline.

3. Crie um arquivo `.env` na raiz, se desejar sobrescrever variáveis adicionais (opcional).

## Execução

Inicie a missão da equipe:

```powershell
poetry run start
```

O comando:

- Carrega os agentes definidos em `crewai_local/crew.py`.
- Executa as três tarefas em sequência.
- Exibe o relatório final no terminal.

## Estrutura

```
src/
  crewai_local/
    crew.py      # definição dos agentes, tarefas e fallback offline
    main.py      # ponto de entrada exposto por poetry run start
```

## Notas

- Para produção, substitua o fallback estático conectando o Ollama (ou outro LLM) com os modelos desejados.
- `DuckDuckGoSearchRun` está disponível para pesquisas, mas o fallback estático retorna respostas pré-determinadas quando os LLMs reais não estão ativos.
