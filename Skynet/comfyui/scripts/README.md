# ComfyUI - Scripts de Configuração Automática

Este diretório contém scripts para automatizar a instalação de dependências e configuração do ComfyUI durante o deployment.

## 📋 Scripts Disponíveis

### `install-dependencies.sh`
Script de inicialização que executa automaticamente quando o container ComfyUI é criado.

**Funcionalidades:**
- ✅ Instala dependências Python necessárias (diffusers, transformers, accelerate, etc.)
- ✅ Cria links simbólicos para modelos Qwen no diretório checkpoints
- ✅ Instala dependências de custom nodes instalados
- ✅ Verifica instalações e lista modelos disponíveis
- ✅ Cria flag de setup concluído para evitar re-execução desnecessária

## 🚀 Como Funciona

### Processo de Inicialização

O `docker-compose.yml` foi configurado com dois containers para ComfyUI:

1. **comfyui-gpu-init** (execução única)
   - Executa o script `install-dependencies.sh`
   - Instala todas as dependências necessárias
   - Configura modelos e custom nodes
   - Termina automaticamente após conclusão

2. **comfyui-gpu** (serviço principal)
   - Aguarda o `comfyui-gpu-init` completar (`depends_on: service_completed_successfully`)
   - Inicia o ComfyUI com todas as dependências já instaladas
   - Acessa a flag de setup para verificar se tudo foi configurado

### Workflow de Deployment

```bash
# 1. Parar containers existentes
docker-compose --profile gpu-nvidia down

# 2. Iniciar com profile gpu-nvidia
docker-compose --profile gpu-nvidia up -d

# 3. O que acontece automaticamente:
#    a) comfyui-gpu-init executa e instala dependências
#    b) comfyui-gpu aguarda init completar
#    c) comfyui-gpu inicia com tudo configurado
#    d) Acesse http://localhost:8188
```

## 📦 Dependências Instaladas Automaticamente

| Pacote | Versão | Propósito |
|--------|--------|-----------|
| `diffusers` | ≥0.35.0 | Framework para modelos de diffusion |
| `transformers` | ≥4.57.0 | Framework para modelos de linguagem |
| `accelerate` | ≥1.11.0 | Otimização de treinamento/inferência |
| `safetensors` | ≥0.6.0 | Formato seguro para tensors |
| `huggingface-hub` | ≥0.36.0 | Cliente para Hugging Face Hub |

## 🔧 Personalização

### Adicionar Novas Dependências

Edite o array `PACKAGES` no arquivo `install-dependencies.sh`:

```bash
PACKAGES=(
    "diffusers>=0.35.0"
    "transformers>=4.57.0"
    "accelerate>=1.11.0"
    "safetensors>=0.6.0"
    "huggingface-hub>=0.36.0"
    "seu-novo-pacote>=1.0.0"  # Adicione aqui
)
```

### Adicionar Custom Nodes Automáticos

Para instalar custom nodes automaticamente durante o setup, adicione no script:

```bash
# Instalar custom node via git
git clone https://github.com/user/custom-node-repo \
    "$CUSTOM_NODES_DIR/custom-node-name"

cd "$CUSTOM_NODES_DIR/custom-node-name"
pip install -r requirements.txt
```

### Desabilitar Instalação Automática

Se quiser desabilitar a instalação automática temporariamente:

```bash
# No docker-compose.yml, remova a dependência:
comfyui-gpu:
  profiles: ["gpu-nvidia"]
  <<: *service-comfyui
  # depends_on:  # <-- Comente estas linhas
  #   comfyui-gpu-init:
  #     condition: service_completed_successfully
```

## 🐛 Troubleshooting

### Ver logs do script de inicialização

```bash
# Logs do container init
docker logs comfyui-gpu-init

# Verificar flag de setup
docker exec comfyui bash -c "ls -la /workspace/.comfyui-setup-done"

# Verificar dependências instaladas
docker exec comfyui bash -c "pip list | grep -E 'diffusers|transformers|accelerate'"
```

### Re-executar Setup Manualmente

```bash
# Remover flag de setup
docker exec comfyui rm /workspace/.comfyui-setup-done

# Executar script manualmente
docker exec comfyui bash /workspace/scripts/install-dependencies.sh
```

### Container init não completa

```bash
# Verificar se script tem permissões de execução
docker exec comfyui-gpu-init ls -la /workspace/scripts/

# Verificar logs de erro
docker logs comfyui-gpu-init --tail 100

# Forçar recriação do container init
docker-compose --profile gpu-nvidia up -d --force-recreate comfyui-gpu-init
```

## 📊 Monitoramento

### Verificar Status do Setup

O script cria uma flag após execução bem-sucedida:

```bash
# Verificar se setup foi executado
docker exec comfyui test -f /workspace/.comfyui-setup-done && echo "✅ Setup completo" || echo "❌ Setup pendente"
```

### Healthcheck do ComfyUI

O container ComfyUI possui healthcheck configurado:

```bash
# Verificar saúde do container
docker inspect comfyui | grep -A 10 "Health"

# Aguardar container ficar healthy
docker-compose --profile gpu-nvidia ps
```

## 🎯 Benefícios

1. **Automação Completa**: Nenhuma intervenção manual necessária após deployment
2. **Repetibilidade**: Setup idêntico em cada deployment
3. **Versionamento**: Scripts versionados junto com docker-compose
4. **Velocidade**: Init container executa uma vez, container principal inicia rápido
5. **Debugging**: Logs separados para setup vs runtime
6. **IaC Compliant**: Totalmente infrastructure-as-code

## 🔐 Segurança

- Scripts montados como **read-only** (`:ro`) no container
- Nenhuma modificação de arquivos de host
- Todas as instalações ocorrem no volume `comfyui_storage`
- Tokens HF/CIVITAI carregados de `.env` (não commitados)

## 📚 Referências

- [ComfyUI Official Docs](https://github.com/comfyanonymous/ComfyUI)
- [AI-Dock ComfyUI Image](https://github.com/ai-dock/comfyui)
- [Docker Compose Init Containers](https://docs.docker.com/compose/startup-order/)
- [Qwen-Image Models](https://huggingface.co/Comfy-Org)
