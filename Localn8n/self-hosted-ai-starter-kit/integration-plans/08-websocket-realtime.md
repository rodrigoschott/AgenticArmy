# WebSocket Real-time Integration: Plano de Telemetria
## Resumo
Habilitar consumo do WebSocket nativo do ComfyUI para feedback em tempo real de progresso, previews e conclusão, integrando com front-end (JS/React), n8n e dashboards.

## Contexto
- ComfyUI expõe endpoint `ws://localhost:8188/ws` por padrão.
- n8n pode usar nodes WebSocket (community) ou função custom.

## Objetivos
1. Criar cliente JS vanilla (`comfyui-client.js`) e componente React.
2. Integrar n8n com WebSocket para atualizar status e salvar em PostgreSQL.
3. Construir dashboard web (HTML) mostrando jobs ativos.

## Escopo
- Gestão de `client_id` (sincronizar com POST).
- Persistência de progresso (em `job_queue` ou nova tabela).
- UI responsiva com preview de imagens intermediárias.

## Preparação
- Garantir CORS/permissões (se usar reverse proxy).
- Criar endpoint HTTP que inicia job e retorna `prompt_id`.
- Ajustar n8n workflow (plano nº1/6) para armazenar `client_id`.

## Etapas
1. **Cliente JS**
   - Implementar classe conforme blueprint (manter).
   - Adicionar reconexão e heartbeat.
   - Expor callbacks `onProgress`, `onComplete`, `onError`.
2. **Componente React**
   - Converter snippet em componente funcional com hooks, integrar com bundler (Vite).
   - Adicionar botão `Cancel` (enviar mensagem para API se suportado).
3. **n8n**
   - Após POST `/prompt`, salvar `prompt_id`.
   - Node WebSocket listening -> Function Node atualiza status no PostgreSQL.
4. **Dashboard**
   - HTML + JS renderizando cards (utilizar snippet).
   - Opcional: integrar com Express/Next.js.
5. **Segurança**
   - Se Web auth do ComfyUI habilitado, incluir token no handshake.

## Testes
- Disparar job e verificar progress bar.
- Simular erro (workflow inválido) e garantir notificação.
- Testar múltiplos clientes conectados simultaneamente.

## Observabilidade
- Registrar métricas de etapas (nó atual, tempo por nó) no `model_usage_log`.

## Riscos
- **Desconexão**: implementar reconexão exponencial.
- **Desalinhamento**: garantir `client_id` consistente entre POST e WS.

## Alternativas/Melhorias
- Empacotar como biblioteca NPM.
- Integrar com frameworks (Next.js, Svelte).
- Adicionar gravação de vídeo/gif a partir de frames (FFmpeg).

## Vantagens
- Melhora UX radical (feedback instantâneo).
- Facilita debug e cancela jobs rapidamente.
- Permite dashboards em tempo real para times.
