# Prompt Management System: Plano de Governança
## Resumo
Construir plataforma completa para versionar, organizar, testar e analisar prompts/workflows do ComfyUI, incluindo API, UI, recomendações e A/B testing.

## Contexto
- PostgreSQL disponível; n8n pode consumir APIs; ComfyUI workflows em JSON.

## Objetivos
1. Implementar API FastAPI conforme blueprint.
2. Criar migrations para tabelas `prompt_templates`, `prompt_executions`, `ab_test_campaigns`.
3. Desenvolver UI web simples (HTML/JS) ou React.
4. Integrar com n8n para relatórios e feedback.

## Escopo
- CRUD completo de templates.
- Execução de prompt com substituição de variáveis.
- Sistema de recomendações + A/B testing.

## Preparação
- Definir diretório `prompt_manager`.
- Configurar connection pooling (psycopg2).
- Estruturar autenticação básica (JWT ou API key).

## Etapas
1. **Migrations**
   - Criar scripts SQL conforme blueprint.
   - Configurar Alembic ou similar.
2. **API**
   - Endpoints: create/list/get/execute/feedback/recommend/ab-tests.
   - Validações (campos obrigatórios, rating 1-5).
   - Integração com ComfyUI via HTTP (plano nº1) e job queue (nº6) opcional.
3. **Front-end**
   - Utilizar snippet HTML como base.
   - Implementar fetch e updates dinâmicos.
   - Adicionar login (se necessário) e filtros avançados.
4. **n8n Workflows**
   - Cron job para relatório semanal.
   - Webhook para registrar feedback (ex: portal).
5. **A/B Testing**
   - Endpoint para iniciar campanha e acompanhar resultados.
   - Métricas (taxa de sucesso, tempo médio).
6. **Documentação**
   - Manual de uso, convenções de nome, tags.

## Testes
- Testes unitários/integração da API.
- Testes de execução real (ComfyUI).
- Testes de recomendação com usuário fictício.

## Observabilidade
- Métricas de uso (templates populares, tempo médio).
- Exportar dados para Grafana.

## Riscos
- **Complexidade**: modularizar para MVP → adicionar recursos gradativamente.
- **Sincronização**: se workflow JSON mudar externamente, atualizar template (adicionar checksum).

## Alternativas/Melhorias
- Integrar com Git (commit de JSON).
- Adicionar comentários/anotações colaborativas.
- Suporte a prompts de texto (LLMs) junto com imagem.

## Vantagens
- Centraliza conhecimento e boas práticas.
- Facilita repetição de resultados.
- Permite experimentos controlados (A/B testing).
