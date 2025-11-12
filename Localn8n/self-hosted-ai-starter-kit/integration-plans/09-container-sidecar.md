# Container Sidecar Pattern (Storage & Queue): Plano de Expansão
## Resumo
Adicionar serviços MinIO (S3) e Redis (fila/cache) ao docker-compose, com worker dedicado e integração com n8n/ComfyUI, viabilizando armazenamento escalável e filas eficientes.

## Contexto
- Stack atual possui PostgreSQL, n8n, ComfyUI, Qdrant, Ollama; sem storage S3 nem Redis.

## Objetivos
1. Estender `docker-compose.yml` com serviços MinIO, Redis, Redis Commander.
2. Adaptar workflows e workers para usar MinIO (upload/download).
3. Habilitar caching de prompts no Redis.

## Escopo
- Configuração MinIO com credenciais seguras.
- Queue Worker usando RQ (integração com plano nº6).
- Scripts utilitários para upload/download.

## Preparação
- Atualizar `.env` com `MINIO_PASSWORD`.
- Criar volume `minio_storage`, `redis_storage`.
- Planejar bucket `comfyui-outputs`.

## Etapas
1. **Docker Compose**
   - Inserir blocos conforme blueprint (MinIO, Redis, worker).
   - Garantir dependências e healthchecks.
2. **Inicialização**
   - Script `init_minio.py` para criar buckets e policies.
   - Script `init_redis.py` para configurar TTLs.
3. **Integração Worker**
   - Atualizar worker (plano nº6) para enviar resultados ao MinIO.
   - Incluir caching (hash MD5) para prompts.
4. **n8n**
   - Adicionar credenciais MinIO (S3).
   - Atualizar workflows para salvar e retornar URLs.
5. **Monitoramento**
   - Configurar Grafana plugin `redis-datasource`.
   - Métricas de bucket (usando MinIO Prometheus se disponível).

## Testes
- Upload/Download via SDK Python.
- Enqueue job e validar que resultado vai para MinIO.
- Cache hit/miss no Redis.

## Observabilidade
- Prometheus para MinIO/Redis (scrape endpoints).
- Dashboard com latência de fila e tamanho de bucket.

## Riscos
- **Segurança**: proteger credenciais; considerar reverse proxy com TLS.
- **Consistência**: garantir commit no DB após upload.

## Alternativas/Melhorias
- Usar AWS S3/Cloud para produção.
- Substituir Redis por RabbitMQ (maior confiabilidade).
- Adicionar minio console com SSO.

## Vantagens
- Escalabilidade de armazenamento (ilimitado).
- Fila rápida para workloads intensivos.
- Base para caching e rate limiting.
