#!/bin/bash
###############################################################################
# ComfyUI Auto-Setup Script
# Instalação automática de dependências e configuração de custom nodes
###############################################################################

set -e

echo "🚀 [ComfyUI Setup] Iniciando configuração automática..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Aguardar ComfyUI estar pronto
log_info "Aguardando ComfyUI inicializar..."
sleep 10

###############################################################################
# 1. VERIFICAR E INSTALAR DEPENDÊNCIAS PYTHON (UMA VEZ)
###############################################################################

# Verificar se dependências já foram instaladas
DEPS_FLAG="/workspace/.python-deps-installed"

if [ -f "$DEPS_FLAG" ]; then
    log_info "Dependências já instaladas anteriormente. Pulando instalação..."
    log_info "Para forçar reinstalação, delete: $DEPS_FLAG"
else
    log_info "Primeira instalação detectada. Instalando dependências Python..."
    
    # Dependências para Qwen-Image-Edit
    PACKAGES=(
        "diffusers>=0.35.0"
        "transformers>=4.57.0"
        "accelerate>=1.11.0"
        "safetensors>=0.6.0"
        "huggingface-hub>=0.36.0"
    )

    for package in "${PACKAGES[@]}"; do
        log_info "Instalando $package..."
        python3 -m pip install --no-cache-dir "$package" || log_warn "Falha ao instalar $package"
    done
    
    # Criar flag de instalação concluída
    touch "$DEPS_FLAG"
    echo "Dependências instaladas em: $(date)" >> "$DEPS_FLAG"
    log_info "Flag de dependências criada: $DEPS_FLAG"
fi

###############################################################################
# 2. CRIAR LINKS SIMBÓLICOS PARA MODELOS
###############################################################################
log_info "Criando links simbólicos para modelos Qwen no diretório checkpoints..."

MODELS_DIR="/workspace/ComfyUI/models"
CHECKPOINTS_DIR="$MODELS_DIR/checkpoints"

# Criar links para modelos de diffusion
if [ -f "$MODELS_DIR/diffusion_models/qwen_image_fp8_e4m3fn.safetensors" ]; then
    ln -sf "$MODELS_DIR/diffusion_models/qwen_image_fp8_e4m3fn.safetensors" "$CHECKPOINTS_DIR/" 2>/dev/null || true
    log_info "Link criado: qwen_image_fp8_e4m3fn.safetensors"
fi

if [ -f "$MODELS_DIR/diffusion_models/qwen-image-edit/qwen_image_edit_2509_fp8_e4m3fn.safetensors" ]; then
    ln -sf "$MODELS_DIR/diffusion_models/qwen-image-edit/qwen_image_edit_2509_fp8_e4m3fn.safetensors" "$CHECKPOINTS_DIR/" 2>/dev/null || true
    log_info "Link criado: qwen_image_edit_2509_fp8_e4m3fn.safetensors"
fi

###############################################################################
# 3. INSTALAR CUSTOM NODES ADICIONAIS
###############################################################################
log_info "Verificando custom nodes instalados..."

CUSTOM_NODES_DIR="/workspace/ComfyUI/custom_nodes"

# Instalar dependências dos custom nodes Qwen se existirem
if [ -d "$CUSTOM_NODES_DIR/Qwen-Image-Edit-2509-ComfyUI-Nodes" ]; then
    log_info "Instalando dependências do Qwen-Image-Edit custom node..."
    cd "$CUSTOM_NODES_DIR/Qwen-Image-Edit-2509-ComfyUI-Nodes"
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt || log_warn "Falha ao instalar requirements.txt"
    fi
    
    if [ -f "pyproject.toml" ]; then
        python3 -m pip install . || log_warn "Falha ao instalar via pyproject.toml"
    fi
fi

###############################################################################
# 4. CONFIGURAÇÕES ADICIONAIS
###############################################################################
log_info "Aplicando configurações adicionais..."

# Criar arquivo de flag para indicar que setup foi executado
touch /workspace/.comfyui-setup-done
log_info "Flag de setup criada: /workspace/.comfyui-setup-done"

###############################################################################
# 5. VERIFICAÇÃO FINAL
###############################################################################
log_info "Verificando instalações..."

python3 -c "import diffusers; print(f'✅ diffusers {diffusers.__version__}')" 2>/dev/null || log_warn "❌ diffusers não encontrado"
python3 -c "import transformers; print(f'✅ transformers {transformers.__version__}')" 2>/dev/null || log_warn "❌ transformers não encontrado"
python3 -c "import accelerate; print(f'✅ accelerate {accelerate.__version__}')" 2>/dev/null || log_warn "❌ accelerate não encontrado"

log_info "Modelos disponíveis em checkpoints:"
ls -lh "$CHECKPOINTS_DIR" | grep -E "qwen|safetensors" || log_warn "Nenhum modelo Qwen encontrado"

echo ""
log_info "✅ Configuração automática concluída!"
echo ""
