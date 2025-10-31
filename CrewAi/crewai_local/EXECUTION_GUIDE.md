# 🚀 GUIA RÁPIDO: Executar Workflow D (Plano 30 Dias)

**Objetivo:** Executar análise estratégica completa em 2-3 horas de processamento

---

## ✅ PRÉ-REQUISITOS

1. **Ollama instalado** (recomendado) ou usar modo demonstração
2. **Python 3.11+** com Poetry
3. **Projeto já instalado:** `d:\Dev\py\AgenticArmy\CrewAi\crewai_local\`

---

## 📝 PASSO A PASSO

### 1. Verificar Ollama (Opcional mas Recomendado)

Abra um terminal separado e execute:
```bash
ollama serve
```

Se der erro "already serving", está tudo certo. Deixe rodando.

Teste o modelo:
```bash
ollama run gpt-oss
```

Digite algo como "Olá" e veja se responde. Pressione `/bye` para sair.

**Se Ollama não funcionar:** O sistema vai usar modo demonstração (respostas estáticas).

---

### 2. Navegar até o Projeto

```powershell
cd d:\Dev\py\AgenticArmy\CrewAi\crewai_local
```

---

### 3. Executar o Sistema

```powershell
poetry run start
```

Você verá este menu:

```
======================================================================
🏨 SISTEMA DE AVALIAÇÃO DE POUSADAS - PARATY v2.1
======================================================================

Workflows disponíveis:

🗓️  D. Planejamento Inicial (30 Dias) ⭐ RECOMENDADO PARA INICIAR
    └─ Validação estratégica antes de prospectar imóveis

🔍 A. Avaliar Propriedade Específica (Go/No-Go)
    └─ Due diligence completa de um imóvel candidato

🎯 B. Desenvolver Estratégia de Posicionamento
    └─ Definir marca, público-alvo e diferenciação

🚀 C. Preparar para Abertura (Soft Opening)
    └─ SOPs, licenças e lançamento operacional

0. Sair

Escolha um workflow (D/A/B/C/0):
```

---

### 4. Selecionar Workflow D

Digite: **D** (ou **d**) e pressione Enter.

Você verá:
```
🗓️  WORKFLOW D: PLANEJAMENTO INICIAL (30 DIAS)
----------------------------------------------------------------------
Este workflow executa as 5 tarefas críticas do seu plano:
  ✓ Proposta de valor e posicionamento
  ✓ Envelope financeiro
  ✓ Mapa competitivo (15 concorrentes)
  ✓ Calendário de eventos e sazonalidade
  ✓ Síntese e recomendação go/no-go

📊 PERFIL DO PROPRIETÁRIO
----------------------------------------------------------------------
Motivação: estilo_de_vida
Budget: R$2,700,000 - R$3,000,000
Horizonte: longo_prazo
Break-even máximo: 6_meses
Experiência hospitalidade: nenhuma
Conhecimento Paraty: residente

📋 TAREFAS DO PLANO 30 DIAS
----------------------------------------------------------------------
✓ T-1001: Proposta de valor (Helena)
✓ T-1010: Mapa competitivo (Juliana)
✓ T-1011: Calendário eventos (Marcelo)
✓ T-1003: Envelope financeiro (Ricardo)
✓ Síntese final (Helena)

▶️  Iniciar execução? (S/n):
```

---

### 5. Confirmar Execução

Digite: **S** (ou apenas Enter) e pressione Enter.

O sistema começará a processar:
```
🚀 Iniciando análise estratégica...
----------------------------------------------------------------------

[Agente Helena] Analisando proposta de valor...
[Agente Juliana] Mapeando concorrentes...
[Agente Marcelo] Coletando dados de eventos...
...
```

**⏱️ Tempo estimado:** 10-30 minutos (depende do LLM)
- Com Ollama local: 15-30 min
- Modo demonstração: 2-5 min

---

### 6. Aguardar Conclusão

Você verá output contínuo dos agentes pensando e executando tarefas.

**Não interrompa** o processo (a menos que veja erros óbvios).

Ao final, verá:
```
======================================================================
✅ PLANO DE 30 DIAS COMPLETO!
======================================================================

[Resultado consolidado pelos agentes]

💾 Resultado salvo em: plano_30_dias_resultado.md

📌 Próximo passo: Revisar documento e tomar Decision Point 1
   (Aprovar posicionamento e iniciar Fase 3: Pipeline)
```

---

## 📄 ANALISAR RESULTADOS

### Arquivo gerado: `plano_30_dias_resultado.md`

Abra o arquivo e você encontrará:

1. **Executive Summary**
   - Recomendação go/no-go
   - 3 principais achados
   - 3 principais riscos

2. **Posicionamento Validado**
   - Promessa central
   - 1-2 personas PRIMÁRIAS (ajustadas)
   - Diferenciais competitivos

3. **Análise de Mercado**
   - Top 5-15 concorrentes
   - Gaps de oportunidade
   - ADR validado

4. **Sazonalidade e Pricing**
   - Calendário anual
   - Estratégia de tarifas

5. **Viabilidade Financeira**
   - Budget alocado
   - Cenários (conservador/base/otimista)
   - ⚠️ Viabilidade break-even 6 meses

6. **Riscos e Mitigações**
   - Top 5 riscos
   - Planos de ação

7. **Próximos Passos**
   - Semana 5-8: Prospecção ativa
   - Visitas anônimas
   - Pipeline de imóveis

8. **Decisão Requerida**
   - Aprovar posicionamento?
   - Aprovar budget?
   - Iniciar prospecção?

---

## 🔄 COPIAR PARA OBSIDIAN

### Método Manual

1. Abra `plano_30_dias_resultado.md` em editor de texto
2. Copie todo o conteúdo
3. No Obsidian, crie novo arquivo: `Analises/Plano_30_Dias_Resultado_2025-10-30.md`
4. Cole o conteúdo
5. Revise e adicione suas observações

### Atualizar Status de Tarefas

Em `01-Controle-Projeto-Waterfall.md`, marque como concluídas:

```markdown
- [x] T-1001 Proposta de valor e posicionamento ✅
- [x] T-1003 Envelope financeiro + contas PJ ✅
- [x] T-1010 Mapa competitivo (15 concorrentes) ✅
- [x] T-1011 Calendário de eventos e sazonalidade ✅
```

### Registrar Decisão

Em `Registro de Decisões.md`, adicione:

```markdown
## D-2025-10-30-002: Resultado do Plano de 30 Dias

- **ID:** D-2025-10-30-002
- **Data:** 2025-10-30
- **Assunto:** Análise dos Resultados do Workflow D
- **Área:** Governança

### Resultado dos Agentes

[Cole resumo do Executive Summary aqui]

### Decisão

- **Posicionamento:** Aprovado / Ajustar / Rejeitar
- **Budget:** Confirmado / Ajustar / Insuficiente
- **Próximo passo:** Iniciar prospecção / Aguardar / Abortar projeto

### Justificativa

[Suas observações sobre as recomendações dos agentes]

### Próximas Ações

- [ ] Contatar 5-10 corretores locais
- [ ] Buscar 10-15 imóveis (sites + networking)
- [ ] Agendar 2-3 visitas anônimas
```

---

## ⚠️ TROUBLESHOOTING

### Erro: "Ollama não disponível"

**Mensagem:**
```
⚠️  Ollama não disponível. Usando modo demonstração (respostas estáticas).
```

**Solução 1:** Iniciar Ollama
```bash
ollama serve
```

**Solução 2:** Aceitar modo demonstração (respostas genéricas mas suficientes para testar)

---

### Erro: "Poetry command not found"

**Solução:**
```powershell
# Reinstalar Poetry
pip install poetry

# Ou executar direto com Python
python -m crewai_local.main
```

---

### Erro: "Import crewai could not be resolved"

**Solução:**
```powershell
# Instalar dependências
poetry install

# Ou com pip
pip install -r requirements.txt
```

---

### Workflow muito lento (>1 hora)

**Causa:** Ollama local pode ser lento dependendo do hardware.

**Soluções:**
1. Usar modelo menor: `ollama run llama3:8b` em vez de `gpt-oss`
2. Aceitar modo demonstração (mais rápido)
3. Executar em horário com PC ocioso

---

## 📊 EXPECTATIVA DE OUTPUT

### Tamanho do Resultado

- **Arquivo:** 5-15 KB (texto)
- **Linhas:** 200-500 linhas
- **Seções:** 8-10 seções estruturadas

### Qualidade Esperada

**Com Ollama (gpt-oss):**
- ✅ Análises detalhadas
- ✅ Recomendações específicas
- ✅ Dados numéricos (ADR, ocupação, budget)
- ✅ Trade-offs identificados

**Modo demonstração:**
- ⚠️ Análises genéricas
- ⚠️ Recomendações superficiais
- ⚠️ Dados numéricos fictícios
- ✅ Estrutura correta (útil para teste)

---

## 🎯 PRÓXIMOS PASSOS APÓS EXECUÇÃO

### Decision Point 1: Revisar e Decidir

1. **Ler documento completo** (30-60 min)
2. **Validar recomendações** com sua intuição e conhecimento local
3. **Ajustar se necessário:**
   - Posicionamento parece correto?
   - Budget está adequado?
   - Break-even em 6 meses é viável?
   - Personas fazem sentido?

### Se Aprovado → Iniciar Fase 3 (Pipeline)

4. **Prospecção ativa:**
   - Contatar corretores
   - Buscar imóveis online
   - Networking local

5. **Preparar pipeline:**
   - Usar template `03-Anexos-Modelos.md`
   - Preencher 10-15 imóveis
   - Aplicar scorecard

6. **Visitas anônimas:**
   - Reservar 2-3 pousadas como hóspede
   - Usar checklist de avaliação
   - Documentar experiência

### Se Ajuste Necessário → Re-executar Workflow D

7. **Atualizar perfil proprietário:**
   - Editar `src/crewai_local/owner_profile.py`
   - Ajustar expectativas (ADR, budget, etc.)
   - Re-executar workflow

---

## 📞 SUPORTE

**Documentação completa:**
- `ANALISE_INTEGRACAO_OBSIDIAN_CREWAI.md` (este projeto)
- `README_PARATY.md` (overview dos agentes)
- Obsidian: `00-Inicial.md` (plano mestre)

**Logs úteis:**
- Saída do terminal durante execução
- Arquivo `plano_30_dias_resultado.md`

**Próxima evolução:**
- Adicionar Agente de Pipeline (Fase 3)
- Automatizar sincronização Obsidian ↔ CrewAI
- Criar dashboards visuais de progresso

---

**Boa sorte! 🚀**

Execute o comando e deixe os agentes trabalharem para você.
