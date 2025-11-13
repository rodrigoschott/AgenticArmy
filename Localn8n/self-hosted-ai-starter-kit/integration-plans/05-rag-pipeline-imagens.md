# RAG Pipeline com Imagens: Plano Completo
## Resumo
Implementar sistema RAG multimodal combinando Qdrant, Ollama e ComfyUI para responder perguntas com contexto textual e visual, incluindo armazenamento de conversas e embeddings.

## Contexto
- Qdrant e Ollama já disponíveis via Docker; ComfyUI API pronta.
- PostgreSQL disponível para tabelas `rag_images`, `rag_conversations`.

## Objetivos
1. Implementar API FastAPI `rag_service.py`.
2. Construir workflow n8n para orquestração e resposta rápida.
3. Criar scripts de ingestão de documentos/imagens.
4. Automatizar decisão de gerar nova imagem.

## Escopo
- Endpoints: `/query`, `/ingest-image`, `/ingest-text`.
- Uso de SentenceTransformer para embeddings (instalar via extras).
- Logging detalhado de conversas.

## Preparação
- Criar tabelas SQL conforme blueprint.
- Configurar Qdrant collection `images` com vector size do modelo.
- Validar performance GPU vs CPU.

## Etapas
1. **Serviço Python**
   - Classe `RAGImagePipeline` conforme blueprint.
   - Função `should_generate_image` (heurística: ausência de imagens relevantes ou solicitação explícita).
   - Integração com ComfyUI via cliente (plano nº1).
   - Indexação automática de novas imagens (salvar em PostgreSQL + Qdrant).
2. **Ingestão**
   - Scripts CLI `ingest_images.py` e `ingest_docs.py`.
   - Pipeline para extrair embeddings de imagens existentes (metadata).
3. **Workflow n8n**
   - Webhook recebe query → Qdrant Search Node → Ollama Node (contexto) → IF (gerar nova imagem) → HTTP Request ComfyUI → PostgreSQL Insert → Response.
   - Notificações Slack com preview da imagem.
4. **Front-end opcional**
   - Interface leve (React) para exibir resposta + galeria.
5. **Governança**
   - Políticas de limpeza (cron job para remover registros antigos).
   - Controle de versões do modelo de embedding.

## Testes
- Consultas com/sem necessidade de nova imagem.
- Avaliar latência total; definir SLAs.
- Testar fallback quando Qdrant indisponível.

## Observabilidade
- Métricas: tempo de busca, tempo total, taxa de geração.
- Dashboard Grafana (plano nº13) com contagem de conversas.

## Riscos
- **Custos GPU**: muitas gerações → combinar com cache (integração nº9/12).
- **Consistência**: assegurar transação ao salvar metadados.

## Alternativas/Melhorias
- Utilizar multimodal embedding (Clip) para melhor matching.
- Adicionar função `feedback` para reforço supervisionado.
- Expandir para áudio/vídeo no futuro.

## Vantagens
- Respostas mais contextuais e visuais.
- Reaproveitamento de ativos gera economia.
- Base para chatbots corporativos avançados.
