#!/bin/bash
###############################################################################
# ComfyUI Redeploy Script
# Script para facilitar o redeploy do ComfyUI com setup automático
###############################################################################

set -e

echo "🔄 ComfyUI Redeploy - Configuração Automática de Dependências"
echo "=============================================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml não encontrado! Execute este script no diretório raiz do projeto."
    exit 1
fi

# Perguntar sobre limpeza
echo ""
read -p "Deseja remover volumes (limpar setup anterior)? [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Removendo volumes existentes..."
    docker-compose --profile gpu-nvidia down -v
else
    log_info "Mantendo volumes existentes..."
    docker-compose --profile gpu-nvidia down
fi

echo ""
log_info "Iniciando ComfyUI com setup automático..."
log_info "Processo: init container → instalar dependências → start ComfyUI"
echo ""

# Iniciar com profile gpu-nvidia
docker-compose --profile gpu-nvidia up -d

echo ""
log_info "Containers iniciando..."
echo ""

# Aguardar init container
log_info "Aguardando init container instalar dependências..."
INIT_TIMEOUT=300  # 5 minutos
ELAPSED=0

while [ $ELAPSED -lt $INIT_TIMEOUT ]; do
    INIT_STATUS=$(docker inspect comfyui-gpu-init --format='{{.State.Status}}' 2>/dev/null || echo "")
    
    if [ "$INIT_STATUS" == "exited" ]; then
        EXIT_CODE=$(docker inspect comfyui-gpu-init --format='{{.State.ExitCode}}' 2>/dev/null)
        if [ "$EXIT_CODE" == "0" ]; then
            log_info "✅ Init container completado com sucesso!"
            break
        else
            log_error "❌ Init container falhou com código $EXIT_CODE"
            echo ""
            log_error "Logs do init container:"
            docker logs comfyui-gpu-init --tail 50
            exit 1
        fi
    fi
    
    printf "."
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ $ELAPSED -ge $INIT_TIMEOUT ]; then
    log_error "⏱️ Timeout: Init container não completou em 5 minutos"
    docker logs comfyui-gpu-init --tail 50
    exit 1
fi

echo ""
log_info "Aguardando ComfyUI ficar healthy..."
COMFYUI_TIMEOUT=120  # 2 minutos
ELAPSED=0

while [ $ELAPSED -lt $COMFYUI_TIMEOUT ]; do
    HEALTH=$(docker inspect comfyui --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
    
    if [ "$HEALTH" == "healthy" ]; then
        log_info "✅ ComfyUI está healthy e pronto!"
        break
    fi
    
    printf "."
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

echo ""
echo ""
log_info "================================================"
log_info "🎉 ComfyUI Deployment Completo!"
log_info "================================================"
echo ""
log_info "🌐 Interface Web: http://localhost:8188"
log_info "📦 GPU: RTX 5080 16GB (--highvram mode)"
log_info "🔧 Modelos: Qwen-Image FP8 instalados"
echo ""

# Mostrar status dos containers
log_info "Status dos containers:"
docker-compose --profile gpu-nvidia ps

echo ""
log_info "Logs de instalação (últimas 20 linhas):"
docker logs comfyui-gpu-init --tail 20

echo ""
log_info "Para ver logs do ComfyUI em tempo real:"
echo "  docker logs -f comfyui"
echo ""
log_info "Para verificar dependências instaladas:"
echo "  docker exec comfyui pip list | grep -E 'diffusers|transformers|accelerate'"
echo ""
