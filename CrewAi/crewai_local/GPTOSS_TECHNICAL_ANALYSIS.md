# Análise Técnica: Por que gpt-oss falha com CrewAI

## 📊 Descobertas

### Teste Simples ✅
```bash
$ ollama run gpt-oss "Say hello"
> Hello!
```
**Resultado:** Funciona perfeitamente

### Teste com CrewAI LLM.call() ✅
```python
llm = CrewLLM(model="ollama/gpt-oss")
response = llm.call("Say hello")
# Resultado: "Hello!"
```
**Resultado:** Funciona perfeitamente

### Teste com Workflow CrewAI + Tools ❌
```python
crew = Crew(agents=[agent_with_tools], tasks=[task])
result = crew.kickoff()
# Erro: ValueError: Invalid response from LLM call - None or empty
```
**Resultado:** FALHA TOTAL

---

## 🔬 Análise do Modelfile

Examinando o Modelfile do gpt-oss (`ollama show gpt-oss --modelfile`):

### Sistema de Canais Multi-Stream

O gpt-oss implementa **três canais separados**:

```
# Valid channels: analysis, commentary, final
```

#### Canal 1: `analysis`
- **Propósito:** Raciocínio interno (thinking)
- **Quando ativa:** Contexto complexo, tool calls, raciocínio multi-step
- **Formato:** 
  ```
  <|start|>assistant<|channel|>analysis<|message|>
  [Thinking process]
  <|end|>
  ```

#### Canal 2: `commentary`
- **Propósito:** Tool calls
- **Quando ativa:** Quando agente precisa usar ferramentas
- **Formato:**
  ```
  <|start|>assistant<|channel|>commentary to=functions.tool_name
  {"arguments": "..."}
  <|call|>
  ```

#### Canal 3: `final`
- **Propósito:** Resposta final ao usuário
- **Quando ativa:** Sempre, após analysis (se houver)
- **Formato:**
  ```
  <|start|>assistant<|channel|>final<|message|>
  [Final response]
  <|end|>
  ```

### Reasoning Mode

```
{{- if and .IsThinkSet .Think (ne .ThinkLevel "") }}
Reasoning: {{ .ThinkLevel }}
{{- else if or (not .IsThinkSet) (and .IsThinkSet .Think) }}
Reasoning: medium
{{- end }}
```

Por padrão, o modelo usa `Reasoning: medium`, que **ativa o canal analysis** em contextos complexos.

---

## 🐛 Por que Causa Problemas com CrewAI

### Expectativa do CrewAI
CrewAI espera resposta no formato padrão de chat completion:

```python
{
  "role": "assistant",
  "content": "Resposta direta aqui"
}
```

### O que gpt-oss retorna em workflows

**Cenário 1: Prompt simples (funciona)**
```
<|start|>assistant<|channel|>final<|message|>
Hello!
<|end|>
```
✅ CrewAI consegue parsear o conteúdo

**Cenário 2: Workflow com tool calls (falha)**
```
<|start|>assistant<|channel|>analysis<|message|>
I need to use the calculator tool to solve 15 * 7.
Let me call the tool.
<|end|>
<|start|>assistant<|channel|>commentary to=functions.calculadora_simples
{"operacao": "15 * 7"}
<|call|>
```
❌ CrewAI tenta parsear como resposta padrão → Falha
❌ Parser não reconhece tags `<|channel|>`
❌ Retorna None/vazio → `ValueError`

---

## 🔍 Evidências

### 1. Modelfile confirma multi-canal
```
{{- if gt (len $msg.Thinking) 0 -}}
  <|start|>assistant<|channel|>analysis<|message|>{{ $msg.Thinking }}
{{- end -}}
{{- if gt (len $msg.Content) 0 -}}
  <|start|>assistant<|channel|>final<|message|>{{ $msg.Content }}
{{- end -}}
```

### 2. Template tem lógica condicional para tools
```
{{- if gt (len $msg.ToolCalls) 0 -}}
  {{- range $j, $toolCall := $msg.ToolCalls -}}
    <|start|>assistant<|channel|>commentary to=functions.{{$toolCall.Function.Name}}
```

### 3. Erro real do usuário
```
ValueError: Invalid response from LLM call - None or empty.
```

Este erro acontece em `crewai/utilities/agent_utils.py:261`:
```python
def get_llm_response(...):
    # ...
    if not response or len(response.strip()) == 0:
        raise ValueError("Invalid response from LLM call - None or empty.")
```

---

## 📈 Comportamento por Contexto

| Contexto | Canais Usados | CrewAI Parse | Status |
|----------|---------------|--------------|--------|
| Prompt simples | `final` | ✅ OK | ✅ Funciona |
| Chat básico | `final` | ✅ OK | ✅ Funciona |
| Workflow sem tools | `final` (ou `analysis` + `final`) | ⚠️ Parcial | ⚠️ Pode funcionar |
| **Workflow com tools** | **`analysis` + `commentary` + `final`** | **❌ Falha** | **❌ Quebra** |
| Multi-step reasoning | `analysis` + `final` | ❌ Falha | ❌ Quebra |

---

## 🎯 Conclusão Técnica

### Por que o teste simples passou?
```python
llm.call("Say hello")
```
- Contexto mínimo
- Sem tools disponíveis
- Sem reasoning complexo
- Modelo usa apenas canal `final`
- CrewAI consegue parsear

### Por que o workflow falha?
```python
agent_with_tools → task → crew.kickoff()
```
- Contexto complexo (system prompt + tools + task)
- Tools disponíveis (CrewAI passa lista de ferramentas)
- Modelo detecta reasoning necessário
- Ativa canal `analysis` + `commentary`
- CrewAI não consegue parsear → `None` → `ValueError`

---

## 💡 Solução

### ❌ NÃO use gpt-oss com:
- CrewAI workflows
- Agentes com ferramentas
- Multi-step tasks
- Tool calling scenarios

### ✅ Use gpt-oss para:
- Conversas standalone (`ollama run gpt-oss`)
- Scripts Python simples sem tools
- Casos onde você controla o parsing

### ✅ Alternativas para CrewAI:
1. **qwen2.5:14b** ⭐ - Excelente tool calling, formato padrão
2. **llama3.2:latest** ⭐ - Rápido, eficiente, compatível
3. **glm-4.6:cloud** ⭐ - Cloud, performance excelente

---

## 🧪 Como Validar

### Teste 1: Simples (pode enganar)
```bash
poetry run python test_model_compatibility.py
```
✅ gpt-oss passa (mas não significa compatibilidade real)

### Teste 2: Realista (revela problema)
```bash
poetry run python test_gptoss_toolcalls.py
```
❌ gpt-oss falha (demonstra incompatibilidade real)

---

## 📚 Referências

- **Modelfile completo:** `ollama show gpt-oss --modelfile`
- **CrewAI source:** `crewai/utilities/agent_utils.py`
- **Erro específico:** `ValueError: Invalid response from LLM call - None or empty`
- **Documentação:** `MODELS_COMPATIBILITY.md`

---

**Data:** 2025-10-31  
**Versão:** 1.0  
**Autor:** Análise técnica baseada em debugging real e inspeção do modelfile
