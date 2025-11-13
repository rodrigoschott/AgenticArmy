# Model Hot-Swapping & Dynamic Resource Management: Plano Inteligente
## Resumo
Criar sistema para selecionar automaticamente o melhor modelo ComfyUI baseado em urgência, propósito, VRAM e custo, com monitoramento de recursos e ajustes dinâmicos.

## Contexto
- ComfyUI expõe `/system_stats`; diversos modelos Qwen e SDXL disponíveis.

## Objetivos
1. Implementar `ModelRouter` conforme blueprint.
2. Criar arquivo `models_config.json` gerenciado.
3. Integrar com workflow n8n e worker (plano nº6).
4. Registrar métricas em `model_usage_log`, `vram_usage_log`.

## Escopo
- Seleção por urgência/purpose/quality/custo.
- Monitoramento VRAM, fallback de qualidade.
- Auto-scaling de workflow quality.

## Preparação
- Mapear modelos instalados (`./comfyui/models`).
- Estimar tempos médios por modelo (testes manual).
- Criar script `update_models_config.py`.

## Etapas
1. **ModelRouter**
   - Implementar classe conforme blueprint, com logging.
   - Adicionar suporte a `negative_prompt`, CFG, steps custom.
2. **Dynamic Monitoring**
   - Script `vram_monitor.py` (coleta stats + grava no DB).
   - Programar cron job (n8n ou systemd) para executar.
3. **Workflow n8n**
   - Node que chama Python Code (ModelRouter) antes de enviar para ComfyUI.
   - Guardar `selection_reason`, `model_name` no job.
4. **Cost Optimizer**
   - Implementar `CostOptimizer` (plano) para análises batch.
   - Dashboard com custo por qualidade.
5. **Auto-scaling Quality**
   - Função que tenta gerar com qualidade alta → se exceder tempo alvo, degrade.
6. **Documentação**
   - Guia de como adicionar novos modelos (update config + testes).

## Testes
- Simular cenários (urgente vs flexível).
- Testar limites de VRAM (forçar baixa VRAM).
- Avaliar custo estimado vs real.

## Observabilidade
- Tabelas `model_usage_log`, `vram_usage_log`.
- Grafana com métricas (tempo médio por modelo, utilização VRAM).

## Riscos
- **Dados incorretos**: calibrar `avg_time_seconds` com benchmarks reais.
- **Mudança de modelos**: automatizar detecção e atualização.

## Alternativas/Melhorias
- Integrar com MIG GPU ou Kubernetes para autoscaling.
- Suporte a feedback baseado em qualidade do usuário.
- Aglutinar com plano nº12 para quotas por usuário.

## Vantagens
- Evita OOM e otimiza recursos automaticamente.
- Reduz custos em operações massivas.
- Garante SLA adaptando qualidade/velocidade.
