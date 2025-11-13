# Multi-Model Pipeline: Plano de Execução Sequencial
## Resumo
Construir pipelines sofisticados que combinam múltiplos modelos ComfyUI (hero, lifestyle, variações) com textos do Ollama e persistência em PostgreSQL para uso em e-commerce, branding e marketing.

## Contexto
- Modelo Qwen-Image instalado (FP8) segundo README; outputs salvos em `./comfyui/output`.

## Objetivos
1. Montar pipeline `Product Showcase` (hero + lifestyle + copy).
2. Criar biblioteca de templates JSON para workflows multi-modelo.
3. Automatizar armazenamento em `product_galleries`.
4. Criar orquestração n8n/async Python.

## Escopo
- Funções de geração paralela (asyncio).
- Gestão de assets (nomes de arquivos, URLs).
- Integração com MinIO (opcional via plano nº9).

## Preparação
- Criar diretório `workflow_templates` com JSONs (hero, lifestyle, thumbnail).
- Definir tabela `product_galleries`.
- Validar VRAM disponível para execuções paralelas (plano nº12).

## Etapas
1. **Templates**
   - Criar JSON base com CLIPText nodes, variáveis (utilizar placeholders substituídos em runtime).
2. **Aplicação Python**
   - Classe `ProductShowcaseGenerator` (conforme blueprint) usando `asyncio.gather`.
   - Função para gerar prompts com Ollama (model `llama3.2`).
   - Função para compor HTML/JSON final.
3. **Workflow n8n**
   - Webhook recebe `product_info`.
   - HTTP Request para Ollama (specs) → HTTP Request ComfyUI (hero).
   - Loop Node 4x para variações (com `Wait`/`Merge`).
   - PostgreSQL Insert + envio de pack por email.
4. **Gestão de Assets**
   - Nomear arquivos `product_{id}_hero.png`, etc.
   - Upload para MinIO (plano nº9) e salvar URL pública.
5. **Documentação**
   - Guia de prompts (estilo, iluminação).
   - Parâmetros ajustáveis (CFG, steps).

## Testes
- Rodar pipeline com produto fictício.
- Medir tempo total vs latência individual.
- Testar fallback se uma variação falhar (re-execução).

## Observabilidade
- Registrar tempos no `model_usage_log` (plano nº12) ou PostgreSQL.

## Riscos
- **Consumo de VRAM**: executar sequencialmente ou usar `--normalvram`.
- **Consistência visual**: reusar seeds e prompt prefixo.

## Alternativas/Melhorias
- Adicionar `Style Transfer` pipeline (do blueprint).
- Integrar com front-end React para pré-visualização.
- Permitir edições manuais via `Prompt Management` (plano nº11).

## Vantagens
- Produção massiva de conteúdo consistente.
- Reduz tempo de design e copywriting.
- Escalável para catálogos completos.
