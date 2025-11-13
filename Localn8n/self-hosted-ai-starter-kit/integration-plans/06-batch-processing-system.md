# Batch Processing System: Plano de Fila de Jobs
## Resumo
Criar sistema de fila robusto para processar grandes volumes de prompts, com priorização, retries e monitoramento, suportando tanto PostgreSQL quanto Redis.

## Contexto
- PostgreSQL e n8n prontos; Redis ainda não configurado (será adicionado via plano nº9).

## Objetivos
1. Implementar fila via PostgreSQL (MVP) com worker Python.
2. Opcional: habilitar modo Redis + RQ para maior throughput.
3. Construir API FastAPI para submissão de jobs.
4. Criar workflow n8n de dashboard e alertas.

## Escopo
- Tabelas `job_queue`, `job_logs`.
- Serviço `comfyui-worker` containerizado.

## Preparação
- Rodar migrations SQL.
- Criar diretório `./comfyui-worker` com Dockerfile (Python + dependencies).
- Definir variáveis `DATABASE_URL`, `COMFYUI_URL`.

## Etapas
1. **Fila PostgreSQL**
   - Implementar worker com `FOR UPDATE SKIP LOCKED`.
   - Suporte a retries, registro de erro.
   - Download de imagens (plano nº1) e upload para storage (MinIO futuro).
2. **API FastAPI**
   - Endpoints `/jobs` (POST), `/jobs/{id}` (GET).
   - Validação de parâmetros (prioridade, workflow).
   - Autenticação básica (token) por segurança mínima.
3. **Worker Container**
   - Dockerfile (Python 3.11-slim) com entrypoint `python worker.py`.
   - Healthcheck que verifica conexão DB + ComfyUI.
4. **n8n Dashboard**
   - Workflow scheduler que monitora `pending`, envia alertas e limpa registros antigos.
   - Dashboard com dataset para Grafana (plano nº13).
5. **Escalonamento**
   - Instruções para subir múltiplos workers (compartilhando fila).
6. **Documentação**
   - Guia de operação (start/stop workers, ver status).

## Testes
- Enfileirar 10 jobs e validar ordem por prioridade.
- Simular erro (ComfyUI off) e verificar retries.
- Teste de concorrência com 2 workers.

## Observabilidade
- Logs por job (tempo de início/fim).
- Métricas exportadas para Prometheus (plano nº13).

## Riscos
- **Deadlock**: Mitigar com `SKIP LOCKED`.
- **Jobs gigantes**: Limitar tamanho do prompt e anexos.

## Alternativas/Melhorias
- Migrar para Redis + RQ ou Celery com RabbitMQ.
- Adicionar UI para submissão manual (integração nº11).
- Implementar quotas por usuário (integração nº14).

## Vantagens
- Controle de carga na GPU.
- Histórico completo e auditável.
- Facilidade de scaling horizontal.
