# File Watching & Auto-Processing: Plano Operacional
## Resumo
Construir pipelines automáticos que monitoram diretórios compartilhados e disparam geração/análise ao detectar novos arquivos, usando Watchdog (Python) e trigger de arquivo no n8n.

## Contexto
- Volume `./shared` já montado no contêiner n8n e ComfyUI, permitindo troca de arquivos.

## Objetivos
1. Criar serviço Python `watch_and_process.py` rodando fora ou dentro da stack.
2. Configurar workflow n8n com `File Trigger`.
3. Estruturar diretórios (`input`, `processing`, `output`, `archive`).
4. Persistir metadados em PostgreSQL e/ou Qdrant.

## Escopo
- Monitoramento de imagens e prompts `.txt`.
- Processamento: análise com Ollama (descrição) e geração com ComfyUI.
- Movimentação automática de arquivos entre pastas.

## Preparação
- Criar diretórios dentro de `./shared`.
- Ajustar permissões (UID/GID) para containers.
- Adicionar tabela `file_jobs`.

## Etapas
1. **Serviço Python**
   - Implementar handler com Watchdog para `on_created`.
   - Para imagens: chamar `analyze_image` (LLM multimodal se disponível) e registrar resultado.
   - Para textos: invocar `generate_image_from_prompt`.
   - Mover arquivos para `processing` enquanto executa; ao final mover para `output` + copiar original para `archive`.
   - Configurar logging (rotating).
2. **Workflow n8n**
   - File Trigger apontando para `/data/shared/input`.
   - Switch Node com condições por extensão.
   - HTTP Request para ComfyUI (via plano nº1) e nodes para PostgreSQL.
   - Slack/Email Node para notificar conclusão.
3. **Integração com Qdrant**
   - Opcional: se arquivo é texto, indexar prompt + imagem resultante (utilizar pipeline nº5).
4. **Containerização**
   - Opcional: adicionar serviço `watcher` no docker-compose com volume `./shared`.
5. **Documentação**
   - Guia de como depositar arquivos (SFTP, Nextcloud, etc).

## Testes
- Upload de arquivos de imagem e texto (variações).
- Teste de erro: arquivo inválido → mover para `errors`.
- Teste de concorrência (múltiplos uploads).

## Observabilidade
- Dashboard n8n para contagem de arquivos processados.
- Logs do watcher integrados ao stack de observabilidade (plano nº13).

## Riscos
- **Storm** de arquivos → usar fila (integração nº6) para controlar taxa.
- **Duplicidade** → calcular hash e verificar se já processado.

## Alternativas/Melhorias
- Substituir Watchdog por inotifywait em shell minimalista.
- Integrar com MinIO (integração nº9) para evento S3.
- Expor API para consultar status de arquivo.

## Vantagens
- Automatiza ingestão sem UI complexa.
- Escalável para datasets grandes.
- Permite padronizar qualidade e armazenagem.
