#!/bin/bash
###############################################################################
# ComfyUI Entrypoint Wrapper
# Verifica dependências antes de iniciar o ComfyUI
###############################################################################

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[SETUP]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

###############################################################################
# VERIFICAR E INSTALAR DEPENDÊNCIAS (UMA VEZ)
###############################################################################

DEPS_FLAG="/workspace/.python-deps-installed"
PYTORCH_FLAG="/workspace/.pytorch-nightly-installed"

# Instalar PyTorch Nightly (para RTX 5080 sm_120 support)
if [ ! -f "$PYTORCH_FLAG" ]; then
    log_info "🔥 Instalando PyTorch Nightly com CUDA 13.0 (RTX 5080 sm_120 support)..."
    COMFYUI_PIP="/opt/environments/python/comfyui/bin/pip"
    
    # Desinstalar PyTorch antigo
    $COMFYUI_PIP uninstall -y torch torchvision torchaudio xformers 2>/dev/null || true
    
    # Instalar PyTorch Nightly
    $COMFYUI_PIP install --pre torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/nightly/cu130 \
        --no-cache-dir
    
    # Instalar xformers (sem dependências para não downgrade PyTorch)
    $COMFYUI_PIP install xformers --no-deps --no-cache-dir
    
    touch "$PYTORCH_FLAG"
    echo "PyTorch nightly instalado em: $(date)" >> "$PYTORCH_FLAG"
    log_info "✅ PyTorch Nightly + CUDA 13.0 instalado!"
fi

if [ ! -f "$DEPS_FLAG" ]; then
    log_info "🔧 Primeira inicialização detectada. Instalando dependências..."
    
    PACKAGES=(
        "comfyui-frontend-package"
        "diffusers>=0.35.0"
        "transformers>=4.57.0"
        "accelerate>=1.11.0"
        "safetensors>=0.6.0"
        "huggingface-hub>=0.36.0"
        "av"
        "trimesh"
    )

    # Usar o pip do ambiente virtual do ComfyUI
    COMFYUI_PIP="/opt/environments/python/comfyui/bin/pip"
    
    for package in "${PACKAGES[@]}"; do
        log_info "Instalando $package..."
        $COMFYUI_PIP install --no-cache-dir --quiet "$package" 2>&1 | grep -v "WARNING" || true
    done
    
    # Criar flag
    touch "$DEPS_FLAG"
    echo "Dependências instaladas em: $(date)" >> "$DEPS_FLAG"
    log_info "✅ Dependências instaladas com sucesso!"
else
    log_info "✅ Dependências já instaladas. Pulando instalação..."
    log_info "📅 Instalação original: $(cat $DEPS_FLAG)"
    log_info "⚡ Economia de tempo: ~3-5 minutos!"
fi

###############################################################################
# CORRIGIR PERMISSÕES DO WORKSPACE
###############################################################################

log_info "🔧 Corrigindo permissões do workspace..."
# Criar diretórios necessários se não existirem
mkdir -p /workspace/ComfyUI/temp
mkdir -p /workspace/ComfyUI/user/default
mkdir -p /workspace/ComfyUI/custom_nodes/ComfyUI-Manager/.cache

# Ajustar permissões de todo o diretório ComfyUI
log_warn "Ajustando permissões de /workspace/ComfyUI..."
chmod -R 777 /workspace/ComfyUI 2>/dev/null || true

###############################################################################
# INICIAR COMFYUI COM ENTRYPOINT ORIGINAL
###############################################################################

log_info "🚀 Iniciando ComfyUI..."
exec /opt/ai-dock/bin/init.sh "$@"
