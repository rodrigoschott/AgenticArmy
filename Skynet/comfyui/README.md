# ComfyUI - Configuração e Modelos

Este diretório contém os arquivos de configuração e modelos para o ComfyUI.

## 📁 Estrutura de Diretórios

```
comfyui/
├── models/          # Modelos de IA (checkpoints, VAEs, LoRAs, etc.)
│   ├── checkpoints/ # Modelos principais (SD, SDXL, FLUX, etc.)
│   ├── vae/        # VAE models
│   ├── loras/      # LoRA models
│   ├── controlnet/ # ControlNet models
│   └── upscale_models/ # Upscaler models
├── output/         # Imagens geradas pelo ComfyUI
└── README.md       # Este arquivo
```

## 🎨 Hardware Otimizado

Este setup está otimizado para:
- **GPU**: RTX 5080 (16GB VRAM)
- **RAM**: 128GB
- **Flags**: `--highvram --preview-method auto`

## 📦 Modelos Recomendados para 16GB VRAM

### Modelos Base (escolha 1-2 para começar)

1. **Stable Diffusion XL 1.0** (7GB)
   - Melhor qualidade geral
   - Download: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

2. **FLUX.1-schnell** (12GB)
   - Geração rápida e de alta qualidade
   - Download: https://huggingface.co/black-forest-labs/FLUX.1-schnell
   - Requer HF_TOKEN no .env

3. **Stable Diffusion 3 Medium** (5GB)
   - Balanceado entre qualidade e velocidade
   - Download: https://huggingface.co/stabilityai/stable-diffusion-3-medium
   - Requer HF_TOKEN no .env

### VAE (Opcional mas recomendado)

- **SDXL VAE** (335MB)
  - Download: https://huggingface.co/stabilityai/sdxl-vae

## 🚀 Como Baixar Modelos

### Opção 1: Download Manual

1. Acesse os links acima
2. Baixe os arquivos `.safetensors`
3. Coloque em `./comfyui/models/checkpoints/`

### Opção 2: Via HuggingFace CLI (dentro do container)

```bash
# Entrar no container
docker exec -it comfyui bash

# Instalar HF CLI (se necessário)
pip install huggingface-hub

# Baixar modelo
huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0 \
  --local-dir /workspace/ComfyUI/models/checkpoints/sdxl-1.0 \
  --local-dir-use-symlinks False
```

### Opção 3: ComfyUI Manager (Recomendado)

1. Acesse http://localhost:8188
2. Clique em "Manager" no menu
3. Busque e instale modelos diretamente pela interface

## 🔑 Tokens Necessários

Para modelos "gated" (SD3, FLUX, etc.):

1. **HuggingFace Token**:
   - Acesse: https://huggingface.co/settings/tokens
   - Crie um token com permissão de leitura
   - Adicione no `.env`: `HF_TOKEN=seu_token_aqui`

2. **Civitai Token** (opcional):
   - Acesse: https://civitai.com/user/account
   - Gere um API token
   - Adicione no `.env`: `CIVITAI_TOKEN=seu_token_aqui`

## 📊 Uso de VRAM por Modelo

| Modelo | VRAM Base | VRAM + VAE | Recomendação |
|--------|-----------|------------|--------------|
| SD 1.5 | 3-4GB | 4-5GB | ✅ Perfeito |
| SDXL 1.0 | 6-8GB | 7-9GB | ✅ Perfeito |
| SD3 Medium | 10-12GB | 11-13GB | ✅ Bom |
| FLUX.1 schnell | 12-14GB | 13-15GB | ⚠️ Limite |
| FLUX.1 dev | 14-16GB | 15-17GB | ⚠️ Pode precisar otimização |

## 🔗 Integração com n8n

O ComfyUI está acessível na rede Skynet:
- **URL interna**: `http://comfyui:8188`
- **URL externa**: `http://localhost:8188`

### Exemplo de HTTP Request no n8n:

```json
{
  "method": "POST",
  "url": "http://comfyui:8188/prompt",
  "body": {
    "prompt": {
      "3": {
        "inputs": {
          "seed": 42,
          "steps": 20,
          "cfg": 8,
          "sampler_name": "euler",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
      }
    }
  }
}
```

## 📝 Notas Importantes

1. **Primeiro Boot**: Pode demorar para baixar a imagem Docker (~10GB)
2. **Modelos**: NÃO incluídos por padrão (download manual necessário)
3. **Storage**: Reserve 50-100GB para modelos e outputs
4. **Performance**: Use sempre o profile `gpu-nvidia` para melhor desempenho

## 🛠️ Troubleshooting

### VRAM Insuficiente
Se receber erro de VRAM:
- Use `--medvram` ao invés de `--highvram`
- Reduza batch size
- Use modelos menores (SD 1.5 ao invés de SDXL)

### Container não inicia
```bash
# Verificar logs
docker logs comfyui

# Reiniciar container
docker restart comfyui
```

## 📚 Recursos Adicionais

- [ComfyUI Docs](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Examples](https://comfyanonymous.github.io/ComfyUI_examples/)
- [AI-Dock Docs](https://github.com/ai-dock/comfyui)
