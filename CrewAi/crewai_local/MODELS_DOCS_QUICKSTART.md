# 📚 DOCUMENTAÇÃO DE MODELOS - GUIA RÁPIDO

## 🎯 Qual documento ler?

### 🚀 Quer decisão rápida?
👉 **Leia:** `EXECUTIVE_SUMMARY_MODELS.md`
- Resumo executivo
- Top 3 modelos
- Plano de ação claro
- 5 minutos de leitura

---

### 📊 Quer entender o contexto completo?
👉 **Leia:** `RECOMMENDED_MODELS_RESEARCH.md`
- Pesquisa completa (21 modelos)
- Metodologia detalhada
- Todas as fontes e referências
- 20 minutos de leitura

---

### 🔧 Quer saber como usar?
👉 **Leia:** `MODELS_COMPATIBILITY.md`
- Guia de compatibilidade
- Como instalar modelos
- Configuração recomendada
- Troubleshooting
- 10 minutos de leitura

---

### 🔬 Quer entender o problema do gpt-oss?
👉 **Leia:** `GPTOSS_TECHNICAL_ANALYSIS.md`
- Análise técnica profunda
- Por que não funciona
- Evidências do modelfile
- 15 minutos de leitura

---

## 🗺️ Fluxo de Leitura Recomendado

```
START
  ↓
[EXECUTIVE_SUMMARY_MODELS.md]
  ↓
Precisa de mais detalhes? → SIM → [RECOMMENDED_MODELS_RESEARCH.md]
  ↓                             ↓
  NÃO                        Quer instalar?
  ↓                             ↓
Quer instalar?                [MODELS_COMPATIBILITY.md]
  ↓                             ↓
[MODELS_COMPATIBILITY.md]     END
  ↓
END
```

---

## 📋 Resumo Ultra-Rápido (30 segundos)

### ✅ ATUAL
- **qwen2.5:14b** (F1: 0.812) - Manter por estabilidade

### 🚀 PRÓXIMO
- **qwen3:14b** (F1: 0.971) - Migrar quando possível
- **+16% acurácia**
- Mesma família = migração suave

### ❌ EVITAR
- **gpt-oss** - Incompatível com tool calling

---

## 🔗 Links Rápidos

### Documentação Interna
- [Resumo Executivo](./EXECUTIVE_SUMMARY_MODELS.md)
- [Pesquisa Completa](./RECOMMENDED_MODELS_RESEARCH.md)
- [Guia de Compatibilidade](./MODELS_COMPATIBILITY.md)
- [Análise Técnica gpt-oss](./GPTOSS_TECHNICAL_ANALYSIS.md)
- [Troubleshooting Geral](./TROUBLESHOOTING.md)

### Testes
- [Test: Model Compatibility](./test_model_compatibility.py)
- [Test: GPT-OSS Tool Calls](./test_gptoss_toolcalls.py)

### Código
- [crew_paraty.py](./src/crewai_local/crew_paraty.py) - Seleção de modelo

---

## 📊 Comparação Visual Rápida

| Modelo | F1 | Latência | RAM | Status |
|--------|-----|----------|-----|--------|
| **Qwen 3:14b** | 0.971 ⭐⭐⭐⭐⭐ | ~142s | 16GB | 🎯 MELHOR |
| **Qwen 3:8b** | 0.933 ⭐⭐⭐⭐ | ~70s | 8GB | ⚡ RÁPIDO |
| **Qwen 2.5:14b** | 0.812 ⭐⭐⭐ | ~130s | 16GB | ✅ ATUAL |
| **Llama 3.1:8b** | 0.835 ⭐⭐⭐ | ~90s | 8GB | 🔄 FALLBACK |
| **gpt-oss** | - | - | - | ❌ INCOMPATÍVEL |

---

## 🎯 Perguntas Frequentes

**Q: Qual modelo devo usar agora?**  
A: Qwen 2.5:14b (já validado, estável)

**Q: Qual é o melhor modelo de 2025?**  
A: Qwen 3:14b (F1: 0.971)

**Q: Posso usar gpt-oss?**  
A: ❌ Não para workflows com ferramentas (incompatível)

**Q: Quando devo migrar para Qwen 3?**  
A: Após testes (1-2 meses)

**Q: Qwen 3:8b ou 3:14b?**  
A: 8B para dev (mais rápido), 14B para produção (mais acurado)

---

## 📅 Cronograma

| Período | Ação |
|---------|------|
| **Agora** | Manter Qwen 2.5:14b |
| **1 mês** | Testar Qwen 3:8b e 3:14b |
| **2-3 meses** | Migrar para Qwen 3:14b |

---

**Última atualização:** 31/10/2025  
**Documentos gerados por:** Pesquisa baseada em Docker evaluation, Berkeley BFCL, e CrewAI community
