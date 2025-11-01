# Compatibilidade de Modelos com CrewAI

**⚠️ ATUALIZAÇÃO IMPORTANTE (31/10/2025):**  
Consulte `RECOMMENDED_MODELS_RESEARCH.md` para pesquisa completa sobre os melhores modelos de 2025.

---

## 🏆 TOP TIER: ALTAMENTE RECOMENDADOS (2025)

### Qwen 3 (14B) ⭐⭐⭐⭐⭐ **MELHOR MODELO LOCAL 2025**
- **Tamanho:** 14B parâmetros (~9GB quantizado)
- **F1 Score:** 0.971 (praticamente GPT-4!)
- **Context:** 128k tokens
- **Pontos fortes:**
  - 🏆 **Melhor modelo local** para tool calling segundo Docker evaluation
  - 🎯 Acurácia excepcional (96% em schema understanding)
  - 🌍 Multilingual - excelente português
  - 🧠 Reasoning avançado - superior ao Qwen 2.5
  - ✅ Compatível com CrewAI (mesma família Qwen)
- **Latência:** ~120-142s (aceitável para workflows complexos)
- **RAM Necessária:** 16GB+
- **Status:** ✅ Validado pela comunidade CrewAI
- **Comando:** 
  ```bash
  ollama pull qwen3:14b
  # Ou versão quantizada (menor RAM):
  ollama pull qwen3:14b-q4_k_m
  ```

### Qwen 3 (8B) ⭐⭐⭐⭐⭐ **MELHOR CUSTO-BENEFÍCIO**
- **Tamanho:** 8B parâmetros (~5GB quantizado)
- **F1 Score:** 0.933 (empata com Claude 3 Haiku!)
- **Context:** 128k tokens
- **Pontos fortes:**
  - ⚡ **50% mais rápido** que o 14B
  - 💰 **Hardware acessível** (8GB RAM)
  - 🎯 F1 Score excelente (0.933)
  - 🌍 Mesmo suporte multilingual do 14B
  - ✅ Ideal para desenvolvimento iterativo
- **Latência:** ~70-84s
- **RAM Necessária:** 8GB+
- **Status:** ✅ Recomendado para dev/test
- **Comando:** 
  ```bash
  ollama pull qwen3:8b
  # Ou versão quantizada:
  ollama pull qwen3:8b-q4_k_m
  ```

### Qwen 2.5 (14B) ⭐⭐⭐⭐ **JÁ VALIDADO NO PROJETO**
- **Tamanho:** 9.0 GB
- **F1 Score:** 0.812 (sólido)
- **Context:** 128k tokens
- **Pontos fortes:**
  - ✅ **Já testado e validado** no nosso projeto
  - 🎯 Excelente tool calling
  - 📐 Ótimo com estruturas complexas
  - 📋 Segue templates rigorosamente
  - ⚡ Rápido em respostas
- **Status:** ✅ Testado e validado (100% success rate)
- **Comando:** `ollama pull qwen2.5:14b`
- **💡 Nota:** Qwen 3 oferece +16% de acurácia. Migração recomendada quando possível.

---

## 🎖️ TIER A: ALTERNATIVAS SÓLIDAS

### Llama 3.1 (8B Instruct) ⭐⭐⭐⭐
- **Tamanho:** 8B parâmetros
- **F1 Score:** 0.835
- **Context:** 128k tokens
- **Pontos fortes:**
  - 🏢 Suporte Meta oficial
  - 📚 Amplamente testado pela comunidade
  - 🔧 Boa documentação e exemplos
  - ✅ Confiável para tool calling
- **Latência:** ~90s
- **RAM Necessária:** 8GB+
- **Status:** ✅ Fallback confiável
- **Comando:** `ollama pull llama3.1:8b-instruct`

### GLM-4.6 Cloud ⭐⭐⭐⭐
- **Tamanho:** Variável (cloud)
- **Context:** Longo
- **Pontos fortes:**
  - ☁️ Modelo em nuvem (sem uso local de recursos)
  - 🎯 Excelente performance
  - 📊 Boa qualidade de análise
  - 🔧 Suporte a ferramentas
- **Status:** ✅ Funcional
- **Comando:** `ollama pull glm-4.6:cloud`

### Llama 3.2 Latest ⭐⭐⭐
- **Tamanho:** 2.0 GB
- **F1 Score:** 0.727
- **Context:** 128k tokens
- **Pontos fortes:**
  - ⚡ Muito rápido
  - 💾 Eficiente em memória
  - ✅ Bom para tasks simples
- **Status:** ✅ Funcional para testes rápidos
- **Comando:** `ollama pull llama3.2:latest`

### Mistral 7B Instruct ⭐⭐⭐⭐
- **Tamanho:** 7B parâmetros
- **F1 Score:** 0.85-0.86 (estimado)
- **Pontos fortes:**
  - ⚡ **Muito eficiente** - menor uso de recursos
  - 🚀 **Rápido** - ótima latência (~80s)
  - 🌍 **Multilingual** - bom suporte europeu
  - 📐 **JSON schema adherence** excelente
- **RAM Necessária:** 7GB+
- **Status:** ✅ Ideal para hardware limitado
- **Comando:** `ollama pull mistral:7b-instruct`

---

## 🔬 MODELOS ESPECIALIZADOS

### Llama 3.1 (70B Instruct) ⭐⭐⭐⭐⭐ **POWERHOUSE**
- **Tamanho:** 70B parâmetros (~40GB)
- **F1 Score:** ~0.94-0.96 (próximo ao GPT-4)
- **Pontos fortes:**
  - 🏆 Acurácia excepcional
  - 🧠 Complex multi-step reasoning
  - 🛡️ Error handling superior
  - 📚 Context understanding avançado
- **Latência:** ~240s (muito lento)
- **RAM Necessária:** 64GB+ recomendado
- **Status:** ⚠️ Apenas para hardware potente
- **Comando:** `ollama pull llama3.1:70b-instruct`

### CodeLlama 13B Instruct ⭐⭐⭐
- **Tamanho:** 13B parâmetros
- **F1 Score:** 0.88
- **Especialização:** Code generation e debugging
- **Pontos fortes:**
  - 💻 Especializado em código
  - 📐 API documentation - entende schemas técnicos
  - 🔧 Code generation superior
- **Status:** ✅ Ideal para workflows DevOps
- **Comando:** `ollama pull codellama:13b-instruct`

### Mixtral 8x7B Instruct ⭐⭐⭐⭐
- **Tamanho:** 8×7B parâmetros (MoE) (~24GB)
- **F1 Score:** 0.88
- **Arquitetura:** Mixture of Experts
- **Pontos fortes:**
  - 🎯 Versatilidade - experts para diferentes domínios
  - 🌍 Multilingual excelente
  - 📐 Complex schemas - roteamento inteligente
- **RAM Necessária:** 24GB+
- **Status:** ✅ Ideal para multi-domínio
- **Comando:** `ollama pull mixtral:8x7b-instruct`

---

## ⚠️ Modelos com Limitações

### GPT-OSS ❌ **NÃO RECOMENDADO PARA CREWAI**
- **Tamanho:** 13 GB
- **Context:** 131k tokens
- **Problema:**
  ```
  ValueError: Invalid response from LLM call - None or empty.
  ```
  
**Por que não funciona com CrewAI?**

O `gpt-oss` usa um **sistema de canais multi-stream** com três canais separados:
- **analysis** - Raciocínio interno (thinking)
- **commentary** - Tool calls
- **final** - Resposta final

**Comportamento:**
- ✅ Prompts simples: Usa apenas canal "final" → **Funciona**
- ❌ Tool calls/contexto complexo: Ativa canal "analysis" primeiro → **Falha**

Quando o modelo ativa o canal "analysis" (comum em workflows com ferramentas), ele retorna:
```
<|start|>assistant<|channel|>analysis<|message|>
[Raciocínio interno]
<|end|>
<|start|>assistant<|channel|>final<|message|>
[Resposta]
<|end|>
```

**Impacto:**
- CrewAI espera resposta direta no formato padrão
- O parser não reconhece tags `<|channel|>analysis`
- Agentes falham com `ValueError: Invalid response from LLM call` em workflows complexos
- Funciona em testes simples mas falha em produção

**Quando usar gpt-oss:**
- ✅ Conversas standalone via `ollama run gpt-oss`
- ✅ Scripts Python simples sem ferramentas
- ❌ **NUNCA** com CrewAI workflows
- ❌ **NUNCA** com agents que usam tools

**Alternativa:**
Se você precisa de um modelo de 13GB+ com tool calling, use:
- `ollama pull deepseek-coder:14b` ou
- `ollama pull mixtral:8x7b`

### DeepSeek-Coder 33B ⚠️ **USO ESPECÍFICO**
- **Tamanho:** 16 GB (quantizado Q3_K_M)
- **Context:** Longo
- **Pontos fortes:**
  - Excelente para código
  - Ótimo para análise técnica
- **Limitações:**
  - Focado em código (não em análise de negócio)
  - Requer muita RAM (16GB modelo + overhead)
- **Status:** ⚠️ Funcional mas não ideal para este projeto
- **Uso recomendado:** Análise técnica de código, não estratégia de negócio

---

## 🔧 Testando Compatibilidade

### Teste Rápido (Terminal):
```bash
# Testar resposta básica
ollama run <modelo> "Hello, respond with 'OK'"

# Se responder "OK" sem prefixos especiais → ✅ Compatível
# Se responder "Thinking... OK" → ❌ Incompatível com CrewAI
```

### Teste Completo (Python):
```python
from crewai import LLM as CrewLLM

llm = CrewLLM(model="ollama/<modelo>", base_url="http://localhost:11434")

try:
    response = llm.call("Say hello")
    print(f"✅ Compatible: {response}")
except Exception as e:
    print(f"❌ Incompatible: {e}")
```

---

## 📊 Tabela de Compatibilidade

| Modelo | Tamanho | Tool Calling | CrewAI | Velocidade | Qualidade |
|--------|---------|--------------|--------|------------|-----------|
| **qwen2.5:14b** | 9 GB | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **glm-4.6:cloud** | ~ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **llama3.2:latest** | 2 GB | ⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| gpt-oss:latest | 13 GB | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| deepseek-coder:33b | 16 GB | ⭐⭐⭐ | ⚠️ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 Recomendação por Caso de Uso

### Workflow Planejamento 30 Dias (Workflow D):
**Melhor opção:** `qwen2.5:14b`
- Precisa de tool calling forte
- Templates complexos
- Análise estratégica

### Workflow Avaliação Propriedade (Workflow A):
**Melhor opção:** `qwen2.5:14b` ou `glm-4.6:cloud`
- Análise financeira detalhada
- Múltiplas ferramentas (maps, search, etc.)

### Workflow Posicionamento (Workflow B):
**Melhor opção:** `llama3.2:latest`
- Menos ferramentas
- Mais criatividade
- Velocidade importante

### Workflow Abertura (Workflow C):
**Melhor opção:** `qwen2.5:14b`
- Muitas ferramentas técnicas
- Precisão crítica

---

## 📋 GUIA DE SELEÇÃO DE MODELOS

### 🎯 Para Desenvolvimento e Testes
1. **qwen3:8b-q4_k_m** ⭐⭐⭐⭐⭐ (MELHOR)
   - F1: 0.933 | Latência: ~70s | RAM: 8GB
   - Migração natural do Qwen 2.5

2. **qwen2.5:14b** ⭐⭐⭐⭐ (JÁ VALIDADO)
   - F1: 0.812 | Continuar para estabilidade
   - Já testado em todos os workflows

3. **llama3.2:latest** ⭐⭐⭐ (RÁPIDO)
   - F1: 0.727 | Use para testes rápidos

### 🚀 Para Produção
1. **qwen3:14b-q4_k_m** ⭐⭐⭐⭐⭐ (MELHOR LOCAL 2025)
   - F1: 0.971 (praticamente GPT-4!)
   - +16% acurácia vs Qwen 2.5
   - Melhor reasoning e multilingual

2. **qwen2.5:14b** ⭐⭐⭐⭐ (MANTER POR ENQUANTO)
   - Já validado e estável
   - Migrar para Qwen 3 quando validado

3. **llama3.1:8b-instruct** ⭐⭐⭐⭐ (FALLBACK)
   - F1: 0.835 | Suporte Meta oficial
   - Alternativa confiável

### 💻 Para Hardware Limitado (<8GB RAM)
- **qwen3:8b-q4_k_m** (5GB) - Melhor opção
- **mistral:7b-instruct** (4GB) - Muito rápido
- **llama3.2:latest** (2GB) - Testes básicos

### 🏆 Para Máxima Acurácia (Hardware Potente)
- **qwen3:14b** (16GB+) - F1: 0.971
- **llama3.1:70b-instruct** (64GB+) - F1: ~0.95
  - ⚠️ Latência alta (~240s)

### 🔧 Para Workflows DevOps/Código
- **codellama:13b-instruct** - F1: 0.88
  - Especializado em code generation

### 🌍 Para Aplicações Multi-domínio
- **mixtral:8x7b-instruct** - F1: 0.88
  - Mixture of Experts

---

## 🎯 NOSSA ESTRATÉGIA DE MIGRAÇÃO

### ✅ Curto Prazo (Próximas 2 semanas)
- **Manter Qwen 2.5:14b** para estabilidade
- Já validado, funciona perfeitamente
- F1 Score 0.812 é sólido

### 🧪 Médio Prazo (1 mês)
- **Testar Qwen 3:8b** em ambiente de dev
- **Avaliar Qwen 3:14b** em workflows reais
- Ganho de 12-16% em acurácia esperado

### 🚀 Longo Prazo (2-3 meses)
- **Migrar para Qwen 3:14b** em produção
- Documentar comportamentos diferentes
- Manter Llama 3.1:8b como fallback

---

## ⚙️ CONFIGURAÇÃO RECOMENDADA

### .env
```bash
# Modelo padrão (manter estável por enquanto)
DEFAULT_MODEL=qwen2.5:14b

# Futuro: após testes
# DEFAULT_MODEL=qwen3:14b-q4_k_m

# Ollama endpoint
OLLAMA_BASE_URL=http://localhost:11434
```

### Instalação dos Modelos Recomendados:
```bash
# 1. ATUAL - Manter por estabilidade (9GB)
ollama pull qwen2.5:14b

# 2. PRÓXIMO - Testar para migração (9GB)
ollama pull qwen3:14b-q4_k_m

# 3. ALTERNATIVA - Desenvolvimento rápido (5GB)
ollama pull qwen3:8b-q4_k_m

# 4. FALLBACK - Backup confiável (5GB)
ollama pull llama3.1:8b-instruct

# 5. RÁPIDO - Testes básicos (2GB)
ollama pull llama3.2:latest
```

---

## 🐛 Troubleshooting

### Erro: "Invalid response from LLM call - None or empty"
**Causa:** Modelo usando formato incompatível (ex: gpt-oss)
**Solução:** Use `qwen2.5:14b`, `glm-4.6:cloud` ou `llama3.2:latest`

### Erro: "Model not found"
**Causa:** Modelo não instalado no Ollama
**Solução:** 
```bash
ollama list  # Ver modelos instalados
ollama pull <modelo>  # Instalar modelo
```

### Erro: "Connection refused"
**Causa:** Ollama não está rodando
**Solução:**
```bash
# Windows/Mac: Iniciar Ollama app
# Linux: 
ollama serve
```

---

**Última atualização:** 2025-10-31  
**Versão:** 3.0  
**Pesquisa completa:** Veja `RECOMMENDED_MODELS_RESEARCH.md`

**Principais mudanças nesta versão:**
- ✅ Adicionados modelos Qwen 3 (8B e 14B) - melhores de 2025
- 📊 F1 Scores baseados em Docker evaluation e Berkeley BFCL
- 🎯 Guia de seleção por caso de uso
- 📈 Estratégia de migração definida
- 🔗 Referências a pesquisas atualizadas
