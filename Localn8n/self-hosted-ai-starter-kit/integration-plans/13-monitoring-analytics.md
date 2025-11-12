# Monitoring & Analytics Stack: Plano de Observabilidade
## Resumo
Montar stack Prometheus + Grafana + Alertmanager + Loki (opcional) para monitorar métricas de ComfyUI, n8n, filas e recursos, fornecendo dashboards e alertas em tempo real.

## Contexto
- Stack Docker permite adicionar novos serviços; blueprint inclui configurações.

## Objetivos
1. Adicionar serviços Prometheus, Grafana, Node Exporter, Alertmanager.
2. Criar exporter customizado `comfyui_metrics_exporter.py`.
3. Definir dashboards padrão (ComfyUI overview, GPU metrics).
4. Configurar alertas (VRAM alta, fila grande, falhas).

## Escopo
- Configurações de scrape, regras de alerta, dashboards JSON.
- Integração com Slack/email via Alertmanager.

## Preparação
- Criar diretório `monitoring/` com arquivos (`prometheus.yml`, `alerts.yml`, dashboards).
- Configurar volumes persistentes.
- Definir variáveis de ambiente (senhas Grafana).

## Etapas
1. **Docker Compose**
   - Adicionar serviços conforme blueprint.
   - Incluir Node Exporter, cadvisor (opcional).
2. **Prometheus**
   - Configurar `prometheus.yml` com targets (ComfyUI exporter, n8n, Node Exporter).
3. **Exporter**
   - Implementar script Python (coleta VRAM, queue, métricas DB).
   - Containerizar (Dockerfile) ou rodar via supervisord.
4. **Dashboards**
   - Criar JSON (ComfyUI Overview, GPU Metrics) e provisionar no Grafana.
   - Criar painel para job queue, custos (do plano nº12).
5. **Alertas**
   - Definir regras (VRAM > 90%, fila > 100, falha > 10%).
   - Configurar Alertmanager com webhook Slack.
6. **Logs (Opcional)**
   - Adicionar Loki + Promtail para logs de containers.
7. **Documentação**
   - Manual de acesso Grafana, troubleshooting.

## Testes
- Validar coleta (ver métricas via `curl localhost:8000/metrics`).
- Simular falha para acionar alerta.
- Checar dashboards atualizando em tempo real.

## Observabilidade
- Cobrir recursos (VRAM, CPU, RAM), performance (tempo p95), business (custo).

## Riscos
- **Sobrecarga**: garantir limites de retenção (30 dias).
- **Segurança**: proteger Grafana com senha forte/TLS.

## Alternativas/Melhorias
- Integrar com Loki para logs estruturados.
- Exportar métricas para DataDog ou Grafana Cloud.
- Automatizar setup via Terraform/Ansible.

## Vantagens
- Visibilidade completa do ecossistema.
- Alertas proativos antes de incidentes.
- Dados históricos para planejamento de capacidade.
