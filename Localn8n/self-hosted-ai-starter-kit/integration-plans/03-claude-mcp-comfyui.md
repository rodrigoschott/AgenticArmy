# Claude Code (MCP) ↔ ComfyUI: Plano de Integração
## Resumo
Desenvolver servidor MCP para que Claude Code gere imagens, liste workflows e diagnostique execuções do ComfyUI diretamente no ambiente de desenvolvimento.

## Contexto
- Stack atual roda localmente; desenvolvedores podem executar Python CLI acessando `comfyui` via `http://localhost:8188`.

## Objetivos
1. Implementar servidor MCP em Python conforme esqueleto apresentado.
2. Integrar com VSCode `settings.json` e documentar setup.
3. Criar testes automatizados (pytest) simulando chamadas MCP.
4. Garantir segurança (rate limit básico, validação de prompt).

## Escopo
- Código `server.py` com ferramentas: `generate_image`, `list_workflows`, `get_workflow_status`.
- Helpers para carregar templates e manipular downloads (usando integrações nº1 e nº11).

## Preparação
- Criar virtualenv dedicado com dependências `mcp`, `requests`.
- Mapear diretórios `./comfyui/workflows` e `./shared` para salvar outputs.
- Definir `.env` com `COMFYUI_URL`.

## Etapas
1. **Implementação**
   - Criar módulo `comfyui_mcp` com classe `ComfyUIClient`.
   - Implementar `build_workflow` (carrega JSON, injeta prompt).
   - Implementar `poll_and_download` reutilizando código do plano nº1.
   - Adicionar validação de input (limitar tamanho de prompt).
2. **Registro MCP**
   - Gerar script de instalação (adiciona ao settings do VSCode).
   - Documentar comando `python server.py`.
3. **Dev Experience**
   - Criar prompts de exemplo.
   - Adicionar comando `list_workflows` que varre diretório `./comfyui`.
4. **Testes**
   - Testar CLI offline (mock de requests).
   - Teste end-to-end opcional com ambiente Docker (depende de GPU).
5. **Documentação**
   - `README` com passos de instalação, troubleshooting (ex: HTTP 401 se web auth habilitado).

## Observabilidade
- Logar chamadas (prompt, status) em arquivo e opcionalmente em PostgreSQL.

## Riscos
- **Segurança**: se servidor exposto, validações fracas. Solução: somente local e com prompt sanitization.

## Alternativas/Melhorias
- Adicionar ferramenta `upload_workflow` para manipular JSON via Claude.
- Expor WebSocket streaming (integração nº8).
- Wrap para ChatGPT plugin se necessário.

## Vantagens
- Acelera criação/debug de workflows.
- Permite iteração rápida dentro do IDE.
- Reutiliza infraestrutura local sem expor credenciais.
