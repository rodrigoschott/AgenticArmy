# n8n como Orquestrador Central: Plano de Implementação
## Resumo
Transformar n8n em hub central que coordena fluxos entre Ollama, ComfyUI, Qdrant e PostgreSQL, entregando pipelines para conteúdo, análise documental e automação social.

## Contexto Atual
- n8n já roda com workflows demo e acesso a banco/volumes; nodes de AI disponíveis com Ollama local e Qdrant na rede.

## Objetivos
1. Construir três workflows baseados nos casos A/B/C.
2. Configurar credenciais centralizadas no n8n (Ollama, PostgreSQL, APIs sociais).
3. Implementar bibliotecas auxiliares (por exemplo, Node Functions) para reuso de prompts.
4. Padronizar logs, notificações e storage de resultados.

## Escopo
- Workflow `AI Content Generator` (webhook → Ollama → ComfyUI → Postgres).
- Workflow `Document Intelligence` (upload → OCR/extraction → Qdrant).
- Workflow `Social Media Automation` (scheduler → copy → imagem → postagem API).

## Preparação
- Registrar credenciais API (LinkedIn/Twitter) em `n8n`.
- Criar tabelas: `content_posts`, `documents`, `social_logs`.
- Configurar pastas `./shared/input` e `output` para uploads (link com integração nº4).

## Etapas
1. **Modelagem de Dados**
   - Scripts SQL com constraints, JSONB para metadata.
2. **Workflow A**
   - Webhook Node recebe tópico.
   - Ollama Node (modelo `llama3.2`) gera outline → Function Node refina prompt.
   - ComfyUI via HTTP Request (plano nº1) gera imagem.
   - PostgreSQL Insert (texto + URL).
   - Response Node com JSON completo.
3. **Workflow B**
   - Utilize `HTTP Request` + `Binary` nodes para upload PDF.
   - Function Node extrai texto (usar Python code com `pdfminer` via `code` node se permitido) ou chamar serviço externo.
   - Ollama summarization.
   - Qdrant nodes para embeddings (ver doc do plugin).
   - ComfyUI gera thumbnail.
4. **Workflow C**
   - Cron node configura frequência.
   - Template prompts em tabela `prompt_templates` (integração nº11) ou arquivo.
   - HTTP Request para APIs sociais via credenciais OAuth.
   - Logging final no PostgreSQL.
5. **Governança**
   - Nomear workflows, configurar tags, habilitar `Error Workflow` padrão para retentativas.
   - Documentar triggers e endpoints (OpenAPI).

## Testes
- Testes end-to-end com dados fictícios.
- Verificar retentativas n8n ao simular falha (desligar ComfyUI temporariamente).
- Monitorar latências e throughput via estatísticas n8n.

## Observabilidade
- Habilitar webhook logs, exportar métricas para Prometheus (integração nº13).
- Criar painel de status no n8n (ex: workflow com `Execute Workflow`).

## Riscos
- **Dependencies**: se Ollama não responder, workflows bloqueiam → adicionar `Timeout` + fallback.
- **APIs sociais**: limites de rate → adicionar throttling e caching.

## Alternativas/Melhorias
- Criar template CLI (n8n CLI) para importar/exportar workflows.
- Substituir steps intensivos por microserviços FastAPI para escalabilidade.
- Adicionar suporte multi-idioma via nodes de tradução.

## Vantagens
- Centralização facilita manutenção.
- Reuso de credenciais e monitoramento nativo.
- Escalável para novos fluxos (RAG, Agents).
