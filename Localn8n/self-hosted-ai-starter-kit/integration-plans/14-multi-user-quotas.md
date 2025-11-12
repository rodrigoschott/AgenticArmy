# Multi-User Setup & Resource Quotas: Plano de Multi-Tenancy
## Resumo
Implementar autenticação, autorização e quotas para múltiplos usuários compartilharem o ComfyUI com limites individuais, priorização e isolamento de recursos.

## Contexto
- Stack atual não possui auth centralizado; expõe serviços localmente.

## Objetivos
1. Criar serviço FastAPI `auth_service` com JWT.
2. Implementar tabelas `users`, `user_quotas`, `user_usage`, `api_keys`.
3. Integrar com fila de jobs (plano nº6) aplicando prioridades e limites.
4. Configurar reverse proxy (Traefik) com forward auth.

## Escopo
- Registro/login, verificação de token, quotas diárias/mensais, limites de VRAM/resolução.
- Scheduler de prioridade por usuário.
- Logging de uso para billing futuro.

## Preparação
- Criar projeto `auth-service` com Dockerfile.
- Adicionar `JWT_SECRET` ao `.env`.
- Atualizar `docker-compose` com Traefik, auth-service e comfyui-proxy.

## Etapas
1. **Migrations**
   - Criar tabelas conforme blueprint.
   - Índices adequados para lookups (user_id, data).
2. **Auth Service**
   - Implementar endpoints `/register`, `/login`, `/me`, `/verify`.
   - Usar `bcrypt` para hashing, `jwt` para tokens.
3. **Quota Enforcement**
   - Middleware que verifica quotas antes de enfileirar job.
   - Atualizar worker para registrar uso (`total_generation_time`, VRAM estimada).
4. **Priority Scheduler**
   - Implementar classe que busca próximo job ordenado por prioridade.
   - Integrar com `job_queue` (plano nº6).
5. **Reverse Proxy**
   - Traefik container com forward auth para ComfyUI.
   - Configurar DNS/hosts (ex.: `comfyui.local`).
6. **n8n Integration**
   - Workflows que consultam auth-service para registrar requisições.
   - Painel de uso por usuário (Grafana).
7. **Documentação**
   - Guia onboarding usuário, como obter API key.
   - Política de quotas e upgrade.

## Testes
- Criar usuários com quotas distintas e testar limites (diário, VRAM, modelos permitidos).
- Simular concorrência e observar priorização.
- Validar forward auth (ComfyUI inacessível sem token).

## Observabilidade
- Monitorar `user_usage` e alertar quando próximos do limite.
- Relatórios automáticos (n8n).

## Riscos
- **Complexidade**: dividir em fases (auth básico → quotas → billing).
- **Segurança**: proteger tokens, usar HTTPS (Traefik + TLS).

## Alternativas/Melhorias
- Integrar com Keycloak/Authelia para auth corporativo.
- Implementar billing automático (Stripe) baseado em `user_usage`.
- Adicionar RBAC granular (ex.: acesso a modelos específicos).

## Vantagens
- Permite multi-tenancy seguro.
- Facilita monetização ou controle interno.
- Evita abuso de recursos e garante fairness.
