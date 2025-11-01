# 🔬 PESQUISA DE MODELOS RECOMENDADOS PARA CREWAI
## Análise Completa de Modelos para Tool Calling e Workflows Agentic

**Data da Pesquisa**: 31 de Outubro de 2025  
**Contexto**: Busca por alternativas após descobrir incompatibilidade do gpt-oss com tool calling no CrewAI

---

## 📊 FONTES DE REFERÊNCIA

### Principais Leaderboards e Estudos
1. **Berkeley Function Calling Leaderboard (BFCL) V4** (Atualizado: Agosto 2025)
   - URL: https://gorilla.cs.berkeley.edu/leaderboard.html
   - Referência acadêmica mais respeitada para avaliação de function calling
   - Metodologia: AST (Abstract Syntax Tree) para avaliação precisa
   - Métricas: Multi-turn interactions, enterprise functions, agentic evaluation

2. **Docker Local LLM Tool Calling Evaluation** (Junho 2025)
   - URL: https://www.docker.com/blog/local-llm-tool-calling-a-practical-evaluation/
   - Testes práticos com 21 modelos e 3,570 casos de teste
   - Hardware: MacBook Pro M4 Max, 128GB RAM
   - Métricas: Tool Invocation, Tool Selection, Parameter Accuracy

3. **Collabnix Ollama Models Guide** (Agosto 2025)
   - URL: https://collabnix.com/best-ollama-models-for-function-calling-tools-complete-guide-2025/
   - Foco em modelos Ollama com suporte nativo a tool calling
   - Comparação de requisitos de hardware e performance

4. **CrewAI Community Forums**
   - URL: https://community.crewai.com/
   - Experiências práticas de desenvolvedores com diferentes modelos
   - Recomendações específicas para Qwen 2.5 e Qwen 3

---

## 🏆 TOP 10 MODELOS PARA TOOL CALLING (2025)

### Ranking Consolidado (por F1 Score em Tool Selection)

| Posição | Modelo | F1 Score | Latência | Tamanho | Disponível no Ollama | Status |
|---------|---------|----------|----------|---------|----------------------|--------|
| 🥇 1 | **GPT-4** | 0.974 | ~5s | - | ❌ | Hosted (OpenAI) |
| 🥈 2 | **Qwen 3 (14B)** | 0.971 | ~142s | 14B | ✅ | **RECOMENDADO** |
| 🥉 3 | **Qwen 3 (14B Q6_K)** | 0.943 | ~120s | 9GB | ✅ | **RECOMENDADO** |
| 4 | **Claude 3 Haiku** | 0.933 | ~3s | - | ❌ | Hosted (Anthropic) |
| 5 | **Qwen 3 (8B)** | 0.933 | ~84s | 8B | ✅ | **RECOMENDADO** |
| 6 | **Qwen 3 (8B Q4_K_M)** | 0.919 | ~70s | 5GB | ✅ | **RECOMENDADO** |
| 7 | **GPT-3.5 Turbo** | 0.899 | ~3s | - | ❌ | Hosted (OpenAI) |
| 8 | **GPT-4o Mini** | 0.852 | ~2s | - | ❌ | Hosted (OpenAI) |
| 9 | **Llama 3.1 (8B)** | 0.835 | ~90s | 8B | ✅ | Alternativa |
| 10 | **Qwen 2.5 (14B Q4_K_M)** | 0.812 | ~130s | 9GB | ✅ | Já testado ✅ |

---

## 🎯 RECOMENDAÇÕES ESPECÍFICAS PARA NOSSO CENÁRIO

### Baseado em:
- ✅ Compatibilidade com CrewAI (testado com qwen2.5:14b)
- ✅ Disponibilidade no Ollama (modelos locais)
- ✅ Suporte a tool calling robusto
- ✅ Performance em workflows complexos
- ✅ Suporte ao idioma português (importante para nossos workflows)

---

## 🌟 TIER S: ALTAMENTE RECOMENDADOS

### 1. **Qwen 3 (14B) - NOVA GERAÇÃO** ⭐⭐⭐⭐⭐
```bash
# Instalação
ollama pull qwen3:14b

# Versão quantizada (menor uso de RAM)
ollama pull qwen3:14b-q4_k_m
```

**Especificações:**
- **F1 Score**: 0.971 (praticamente empatado com GPT-4!)
- **Tamanho**: 14B parâmetros (~9GB quantizado)
- **Latência**: 120-142s (aceitável para workflows complexos)
- **RAM Necessária**: 16GB+ recomendado

**Por que escolher:**
- ✅ **Melhor modelo local** para tool calling segundo Docker evaluation
- ✅ **Evolução do Qwen 2.5** que já testamos e funciona bem
- ✅ **Acurácia excepcional** em schema understanding (96%)
- ✅ **Multilingual** - excelente suporte a português
- ✅ **Comunidade CrewAI** confirma compatibilidade perfeita
- ✅ **Reasoning avançado** - melhor que Qwen 2.5 em raciocínio complexo

**Pontos de atenção:**
- ⚠️ Latência maior que modelos menores (trade-off por qualidade)
- ⚠️ Requer hardware razoável (16GB+ RAM)

**Cenários ideais:**
- Workflows com múltiplas ferramentas
- Tarefas que exigem raciocínio complexo
- Projetos que priorizam acurácia sobre velocidade
- Produção (maior confiabilidade)

---

### 2. **Qwen 3 (8B) - MELHOR EQUILÍBRIO** ⭐⭐⭐⭐⭐
```bash
# Instalação
ollama pull qwen3:8b

# Versão quantizada
ollama pull qwen3:8b-q4_k_m
```

**Especificações:**
- **F1 Score**: 0.933 (empata com Claude 3 Haiku!)
- **Tamanho**: 8B parâmetros (~5GB quantizado)
- **Latência**: 70-84s (quase 50% mais rápido que 14B)
- **RAM Necessária**: 8GB+ recomendado

**Por que escolher:**
- ✅ **Melhor custo-benefício** entre performance e velocidade
- ✅ **F1 Score excelente** (0.933) - perde pouco para o 14B
- ✅ **Latência reduzida** - metade do tempo do 14B
- ✅ **Menor uso de RAM** - roda em hardware mais modesto
- ✅ **Mesma arquitetura** do Qwen 3 14B
- ✅ **Ideal para desenvolvimento** iterativo

**Pontos de atenção:**
- ⚠️ Pode ter dificuldade em cenários extremamente complexos
- ⚠️ Reasoning um pouco inferior ao 14B

**Cenários ideais:**
- Desenvolvimento e testes
- Workflows com complexidade média
- Hardware limitado (8-16GB RAM)
- Aplicações que precisam de respostas mais rápidas

---

### 3. **Qwen 2.5 (14B) - JÁ VALIDADO** ⭐⭐⭐⭐
```bash
# Já instalado
ollama pull qwen2.5:14b
```

**Especificações:**
- **F1 Score**: 0.812
- **Tamanho**: 14B parâmetros (~9GB)
- **Latência**: ~130s
- **RAM Necessária**: 16GB+ recomendado

**Por que escolher:**
- ✅ **Já testado e validado** no nosso projeto ✅
- ✅ **Funciona perfeitamente** com CrewAI (teste confirmou)
- ✅ **Documentação ampla** - conhecemos seu comportamento
- ✅ **Estável** - versão madura e confiável
- ✅ **Multilingual** - bom suporte a português

**Pontos de atenção:**
- ⚠️ Qwen 3 é superior em performance (0.971 vs 0.812)
- ⚠️ Versão anterior - Qwen 3 tem melhorias significativas

**Cenários ideais:**
- Continuar com modelo já validado
- Evitar mudanças disruptivas no projeto
- Manter estabilidade no curto prazo

**💡 Recomendação:** Migrar para Qwen 3 quando possível para ganhar +16% em acurácia

---

## 🎖️ TIER A: ALTERNATIVAS SÓLIDAS

### 4. **Llama 3.1 (8B Instruct)** ⭐⭐⭐⭐
```bash
ollama pull llama3.1:8b-instruct
```

**Especificações:**
- **F1 Score**: 0.835
- **Tamanho**: 8B parâmetros
- **Latência**: ~90s
- **RAM Necessária**: 8GB+

**Por que considerar:**
- ✅ **Meta oficial** - suporte corporativo forte
- ✅ **Amplamente testado** pela comunidade
- ✅ **Boa documentação** e exemplos
- ✅ **Confiável** para tool calling

**Limitações:**
- ⚠️ F1 Score inferior aos Qwen (0.835 vs 0.933/0.971)
- ⚠️ Suporte multilingual não é o forte

**Cenários ideais:**
- Integração com ecossistema Meta/Llama
- Casos de uso em inglês prioritariamente
- Fallback se Qwen apresentar problemas

---

### 5. **Mistral 7B Instruct v0.3** ⭐⭐⭐⭐
```bash
ollama pull mistral:7b-instruct
```

**Especificações:**
- **F1 Score**: 0.85-0.86 (estimado)
- **Tamanho**: 7B parâmetros
- **Latência**: ~80s (mais rápido)
- **RAM Necessária**: 7GB+

**Por que considerar:**
- ✅ **Muito eficiente** - menor uso de recursos
- ✅ **Rápido** - ótima latência
- ✅ **Multilingual** - bom suporte europeu
- ✅ **JSON schema adherence** - excelente com estruturas

**Limitações:**
- ⚠️ Menor contexto que Qwen/Llama
- ⚠️ F1 Score um pouco inferior

**Cenários ideais:**
- Hardware muito limitado
- Aplicações que priorizam velocidade
- Tarefas estruturadas (JSON, APIs)

---

### 6. **Llama 3.1 (70B Instruct)** ⭐⭐⭐⭐⭐ (POWERHOUSE)
```bash
ollama pull llama3.1:70b-instruct
```

**Especificações:**
- **F1 Score**: 0.94-0.96 (estimado, próximo ao GPT-4)
- **Tamanho**: 70B parâmetros (~40GB)
- **Latência**: ~240s (muito lento)
- **RAM Necessária**: 64GB+ recomendado

**Por que considerar:**
- ✅ **Acurácia excepcional** - melhor reasoning
- ✅ **Complex multi-step** - excelente em workflows complexos
- ✅ **Error handling** superior
- ✅ **Context understanding** avançado

**Limitações:**
- ❌ **Requisitos de hardware** muito altos (64GB+ RAM)
- ❌ **Latência** proibitiva para uso interativo
- ❌ **Overkill** para maioria dos casos

**Cenários ideais:**
- Hardware de servidor disponível
- Workflows críticos que exigem máxima acurácia
- Produção em grande escala
- Não se importa com latência (batch processing)

---

## 🔬 TIER B: MODELOS ESPECIALIZADOS

### 7. **CodeLlama 13B Instruct** ⭐⭐⭐
```bash
ollama pull codellama:13b-instruct
```

**Especificações:**
- **F1 Score**: 0.88 (Docker test)
- **Tamanho**: 13B parâmetros
- **Especialização**: Code generation e debugging

**Por que considerar:**
- ✅ **Especializado em código** - excelente para DevOps
- ✅ **API documentation** - entende schemas técnicos
- ✅ **Code generation** superior

**Limitações:**
- ⚠️ **Não é generalista** - focado em código
- ⚠️ **Português limitado**

**Cenários ideais:**
- Workflows que geram código
- Integração com APIs técnicas
- DevOps e CI/CD automation

---

### 8. **Mixtral 8x7B Instruct** ⭐⭐⭐⭐
```bash
ollama pull mixtral:8x7b-instruct
```

**Especificações:**
- **F1 Score**: 0.88
- **Tamanho**: 8×7B parâmetros (MoE) (~24GB)
- **Arquitetura**: Mixture of Experts

**Por que considerar:**
- ✅ **Versatilidade** - experts para diferentes domínios
- ✅ **Multilingual** excelente
- ✅ **Complex schemas** - roteamento inteligente

**Limitações:**
- ⚠️ **Alto uso de RAM** (24GB+)
- ⚠️ **Latência moderada** (~120s)

**Cenários ideais:**
- Aplicações multi-domínio
- Workflows internacionais
- Quando precisa de especialização dinâmica

---

## ❌ MODELOS NÃO RECOMENDADOS PARA CREWAI

### 🚫 **gpt-oss:latest** - INCOMPATÍVEL
```bash
# NÃO USAR para workflows com tool calling
ollama pull gpt-oss:latest
```

**Por que evitar:**
- ❌ **Multi-channel format** incompatível com CrewAI
- ❌ **Falha em workflows** com ferramentas (validado)
- ❌ **Resposta None/empty** em contextos complexos
- ⚠️ Funciona apenas em conversas simples

**Status:** ✅ Já documentado e warning implementado em `crew_paraty.py`

---

### 🚫 **xLAM-2-8B-fc-r** - INSTÁVEL
**Por que evitar:**
- ❌ **Eager invocation** - chama tools desnecessariamente
- ❌ **Wrong tool selection** frequente
- ❌ **Invalid arguments** - parâmetros malformados

---

### 🚫 **watt-tool-8B** - BAIXA PERFORMANCE
**Por que evitar:**
- ❌ **F1 Score**: 0.484 (muito baixo)
- ❌ **Ignora tool responses** frequentemente
- ❌ **Conversas incompletas**

---

## 📋 COMPATIBILIDADE COM OLLAMA

### ✅ Modelos Disponíveis no Ollama (Verificados)

| Modelo | Comando | Status | F1 Score |
|--------|---------|--------|----------|
| Qwen 3 (14B) | `ollama pull qwen3:14b` | ✅ Disponível | 0.971 |
| Qwen 3 (8B) | `ollama pull qwen3:8b` | ✅ Disponível | 0.933 |
| Qwen 2.5 (14B) | `ollama pull qwen2.5:14b` | ✅ Instalado | 0.812 |
| Llama 3.1 (8B) | `ollama pull llama3.1:8b-instruct` | ✅ Disponível | 0.835 |
| Llama 3.1 (70B) | `ollama pull llama3.1:70b-instruct` | ✅ Disponível | ~0.95 |
| Llama 3.2 | `ollama pull llama3.2` | ✅ Instalado | 0.727 |
| Mistral 7B | `ollama pull mistral:7b-instruct` | ✅ Disponível | 0.85-0.86 |
| CodeLlama 13B | `ollama pull codellama:13b-instruct` | ✅ Disponível | 0.88 |
| Mixtral 8x7B | `ollama pull mixtral:8x7b-instruct` | ✅ Disponível | 0.88 |
| DeepSeek Coder | `ollama pull deepseek-coder:33b` | ✅ Instalado | Não testado |
| GLM-4.6 | `ollama pull glm-4.6` | ✅ Instalado | Não testado |

---

## 🎯 DECISÃO FINAL: NOSSO PLANO DE AÇÃO

### 🚀 RECOMENDAÇÃO IMEDIATA

**Curto Prazo (Próximas 2 semanas):**
1. **Continuar com Qwen 2.5:14b** para estabilidade ✅
   - Já validado, funciona perfeitamente
   - Evita riscos de mudanças disruptivas
   - F1 Score 0.812 é sólido

**Médio Prazo (1 mês):**
2. **Migrar para Qwen 3:8b ou Qwen 3:14b** 🎯
   - Ganho de 12-16% em acurácia (0.933 ou 0.971)
   - Mesma família Qwen = migração suave
   - Testar em ambiente de dev primeiro

**Testes Paralelos:**
3. **Avaliar Llama 3.1:8b-instruct** como fallback
   - Diferente família = comportamento diferente
   - Pode ser útil em cenários específicos
   - F1 Score 0.835 é competitivo

---

### 📊 MATRIZ DE DECISÃO

| Critério | Qwen 2.5:14b | Qwen 3:8b | Qwen 3:14b | Llama 3.1:8b |
|----------|--------------|-----------|------------|--------------|
| **F1 Score** | 0.812 ⭐⭐⭐ | 0.933 ⭐⭐⭐⭐ | 0.971 ⭐⭐⭐⭐⭐ | 0.835 ⭐⭐⭐ |
| **Latência** | ~130s ⭐⭐⭐ | ~70s ⭐⭐⭐⭐⭐ | ~142s ⭐⭐⭐ | ~90s ⭐⭐⭐⭐ |
| **RAM** | 16GB ⭐⭐⭐ | 8GB ⭐⭐⭐⭐⭐ | 16GB ⭐⭐⭐ | 8GB ⭐⭐⭐⭐⭐ |
| **Português** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Validado** | ✅ | ⏳ | ⏳ | ⏳ |
| **Recomendação** | **Manter** | **Testar** | **Migrar** | **Backup** |

---

## 🔧 PLANO DE MIGRAÇÃO

### Fase 1: Preparação (1 dia)
```bash
# Instalar novos modelos
ollama pull qwen3:8b-q4_k_m
ollama pull qwen3:14b-q4_k_m
ollama pull llama3.1:8b-instruct

# Verificar instalação
ollama list
```

### Fase 2: Testes (2-3 dias)
```bash
# Rodar testes de compatibilidade
poetry run python test_model_compatibility.py

# Rodar teste avançado com tool calls
poetry run python test_gptoss_toolcalls.py

# Testar workflows reais
poetry run start
# Selecionar Qwen 3:8b e rodar Workflow A, B, C, D
```

### Fase 3: Comparação (1 dia)
- Comparar outputs de qualidade
- Medir latência real nos workflows
- Avaliar uso de memória
- Documentar diferenças comportamentais

### Fase 4: Decisão (1 dia)
- Escolher modelo final (provavelmente Qwen 3:14b ou 3:8b)
- Atualizar `crew_paraty.py` com novo default
- Atualizar documentação
- Commit das mudanças

---

## 📚 REFERÊNCIAS TÉCNICAS

### Berkeley Function Calling Leaderboard (BFCL)
- **Paper**: "The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation"
- **Autores**: Patil et al., 2025
- **Conferência**: Forty-second International Conference on Machine Learning
- **Citação**:
```bibtex
@inproceedings{patil2025bfcl,
  title={The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models},
  author={Patil, Shishir G. and Mao, Huanzhi and Cheng-Jie Ji, Charlie and Yan, Fanjia and Suresh, Vishnu and Stoica, Ion and E. Gonzalez, Joseph},
  booktitle={Forty-second International Conference on Machine Learning},
  year={2025},
}
```

### Docker Evaluation Study
- **Título**: "Local LLM Tool Calling: Which LLM Should You Use?"
- **Data**: Junho 2025
- **Metodologia**: 21 modelos, 3,570 testes, hardware M4 Max
- **Métricas**: Tool Invocation, Tool Selection, Parameter Accuracy

### CrewAI Community Insights
- **Fonte**: https://community.crewai.com/
- **Destaque**: Qwen 2.5 e Qwen 3 são mais recomendados pela comunidade
- **Confirmação**: Function calling funciona bem com Qwen family

---

## 💡 CONCLUSÃO

Com base na pesquisa extensiva de múltiplas fontes confiáveis:

### 🎯 VENCEDOR ABSOLUTO: **Qwen 3 (14B)**
- **F1 Score**: 0.971 (praticamente GPT-4 local!)
- **Melhor modelo local** para tool calling em 2025
- **Evolução natural** do nosso Qwen 2.5:14b
- **Migração de baixo risco** (mesma família)

### 🥈 VICE-CAMPEÃO: **Qwen 3 (8B)**
- **Melhor custo-benefício** (0.933 F1, metade da latência)
- **Ideal para desenvolvimento** iterativo
- **Hardware acessível** (8GB RAM)

### 🏆 NOSSA ESTRATÉGIA:
1. ✅ **Agora**: Manter Qwen 2.5:14b (estabilidade)
2. 🧪 **Próxima semana**: Testar Qwen 3:8b (desenvolvimento)
3. 🚀 **Próximo mês**: Migrar para Qwen 3:14b (produção)

### ⚠️ EVITAR:
- ❌ gpt-oss (incompatível - já documentado)
- ❌ xLAM-2-8B (instável)
- ❌ watt-tool-8B (baixa performance)

---

**Documento gerado em**: 31/10/2025  
**Próxima revisão**: Dezembro 2025 (novos modelos podem surgir)  
**Responsável**: Equipe CrewAI Local
