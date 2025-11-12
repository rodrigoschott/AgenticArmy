# API REST - ComfyUI → Qualquer Serviço: Plano de Implementação
## Resumo
Implementar uma camada robusta para invocar a API REST nativa do ComfyUI a partir de n8n, scripts Python e webhooks, com polling confiável, download de resultados e persistência no PostgreSQL compartilhado pelo stack Docker atual.

## Contexto Atual
- ComfyUI já exposto no cluster Docker via `http://comfyui:8188` com volumes montados para workflows e saídas.
- n8n opera na mesma rede `skynet`, com PostgreSQL disponível e volume compartilhado `./shared` para troca de arquivos.

## Objetivos
1. Criar workflow n8n reutilizável (HTTP Request + polling + armazenamento).
2. Criar módulo Python (`comfyui_client.py`) com funções `submit_workflow`, `poll_status`, `download_output`.
3. Criar documentação/API blueprint para consumo externo (webhook).
4. Garantir persistência das imagens e metadados no PostgreSQL.

## Escopo e Entregáveis
- Template n8n exportável (JSON) com nós parametrizados.
- Biblioteca Python com testes unitários simulando respostas.
- Scripts SQL para tabela `generated_assets`.
- README operacional com exemplos de requisição.

## Preparação
1. Confirmar credenciais n8n e acesso ao PostgreSQL (`POSTGRES_*` no `.env`).
2. Mapear pasta `./comfyui/output` -> pipeline de download.
3. Definir esquema `generated_assets(id, prompt_id, prompt_text, output_path, metadata JSONB, created_at)`.

## Etapas Detalhadas
1. **n8n**
   - Criar workflow com nós: Webhook Trigger → HTTP Request (POST `/prompt`) → Function (extrai `prompt_id`) → HTTP Request (GET `/history/{id}` com retry/backoff) → IF status completo → HTTP Request (GET `/view`) → Binary → PostgreSQL Insert.
   - Configurar tempo de polling adaptativo (ex.: 5s, 10s, 20s).
   - Parametrizar `client_id` único usando Function Node.
2. **Biblioteca Python**
   - Implementar cliente com `requests.Session`, suporte a `client_id` e timeouts configuráveis.
   - Adicionar função `download_images(prompt_id, destination_dir)` que usa streaming e valida integridade.
   - Criar CLI simples (`python comfyui_client.py prompt.json`).
3. **Persistência**
   - Script SQL para criar tabela e índices em PostgreSQL.
   - Função n8n para inserir/atualizar registro com caminho da imagem (relativo a `./shared` ou URL S3 futuro).
4. **Observabilidade**
   - Logar eventos chave (envio, início download, finalização) no PostgreSQL e opcionalmente no n8n.
   - Ajustar healthcheck n8n para alertar se ComfyUI indisponível.
5. **Documentação**
   - Markdown com exemplos `curl`, formato de payload (workflow JSON), explicação de polling e links para debugging.

## Testes e Validação
- Teste manual com prompts simples.
- Teste de erro (workflow inválido) garantindo tratamento no n8n/Python.
- Teste de concorrência (3 requisições simultâneas) monitorando fila do ComfyUI.

## Observabilidade
- Utilizar logs n8n + métricas do ComfyUI (`/system_stats`) para avaliar tempo médio de execução.
- Configurar alertas n8n (email/Slack) para falha repetida.

## Riscos e Mitigações
- **Timeout longo**: configurar timeout > tempo médio + fallback reprocessar.
- **Workflow inválido**: validar JSON antes do envio.
- **Latência de download**: usar streaming, retry com backoff.

## Alternativas e Melhorias
- Converter polling para WebSocket (integração nº 8) para reduzir latência.
- Adicionar camada FastAPI que abstrai n8n, permitindo multi-tenant.
- Implementar cache (Redis) para prompts repetidos (integração nº 9).

## Vantagens
- Reutilização em diferentes canais (n8n, scripts, webhooks).
- Redução de trabalho manual com orquestração consistente.
- Base sólida para integrações mais complexas (RAG, Agents).
