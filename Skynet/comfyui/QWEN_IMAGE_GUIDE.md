# 🎨 Qwen-Image no ComfyUI - Guia de Uso

## ❌ Problema Identificado

O workflow que você tentou usar está **ERRADO** para modelos Qwen-Image!

```
❌ CheckpointLoaderSimple → NÃO funciona com Qwen-Image
❌ Custom node "Qwen-Image-Edit-2509-ComfyUI-Nodes" → QUEBRADO (classe inexistente)
```

## ✅ Solução Correta

Os modelos Qwen-Image usam **nodes especiais**, não os nodes padrão do Stable Diffusion.

### 📁 Verificação dos Modelos

Seus modelos estão nos lugares corretos:

| Modelo | Localização | Tamanho | Status |
|--------|-------------|---------|--------|
| Diffusion Model | `ComfyUI/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors` | 20GB | ✅ OK |
| Text Encoder | `ComfyUI/models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors` | 8.8GB | ✅ OK |
| VAE | `ComfyUI/models/vae/qwen_image_vae.safetensors` | 243MB | ✅ OK |
| Edit Model | `ComfyUI/models/diffusion_models/qwen-image-edit/qwen_image_edit_2509_fp8_e4m3fn.safetensors` | 20GB | ✅ OK |

**⚠️ IMPORTANTE:** NÃO use `models/checkpoints/` com Qwen! Use `diffusion_models/` diretamente.

---

## 🚀 Como Usar (3 Passos)

### 1️⃣ Acesse o ComfyUI

```
http://localhost:8188
```

### 2️⃣ Carregue o Workflow Exemplo

**Opção A - Arrastar imagem:**
1. Baixe a imagem: [qwen_image_basic_example.png](https://comfyanonymous.github.io/ComfyUI_examples/qwen_image/qwen_image_basic_example.png)
2. Arraste para o canvas do ComfyUI
3. O workflow será carregado automaticamente!

**Opção B - Do arquivo local:**
```powershell
# A imagem já está em:
./comfyui/output/qwen_image_basic_example.png

# Arraste esta imagem para o ComfyUI
```

### 3️⃣ Execute o Workflow

Clique em **"Queue Prompt"** no canto superior direito!

---

## 📊 Nodes Corretos para Qwen-Image

### **Para Gerar Imagens (Qwen-Image):**

```
DiffusionModelLoader        → Carrega qwen_image_fp8_e4m3fn.safetensors
CLIPTextEncode (Qwen)       → Prompt de texto
VAELoader                   → Carrega qwen_image_vae.safetensors
EmptyLatentImage            → Latent vazio
KSampler                    → Gera imagem
VAEDecode                   → Decodifica latent
SaveImage                   → Salva resultado
```

### **Para Editar Imagens (Qwen-Image-Edit):**

```
DiffusionModelLoader        → Carrega qwen_image_edit_2509_fp8_e4m3fn.safetensors
CLIPTextEncode (Qwen)       → Prompt de edição
LoadImage                   → Imagem original para editar
ImageResize                 → Redimensiona para 512x512
VAEEncode                   → Codifica imagem
KSampler                    → Processa edição
VAEDecode                   → Decodifica
SaveImage                   → Salva resultado
```

---

## 🔧 Configurações Recomendadas

### KSampler Settings:
- **Sampler:** `dpmpp_2m` ou `euler`
- **Scheduler:** `sgm_uniform` (recomendado para Qwen) ou `karras`
- **Steps:** 25-30 (menos steps = mais rápido, mais steps = melhor qualidade)
- **CFG:** 5.0-7.0 (Qwen é sensível, não use valores altos)
- **Denoise:** 1.0 (geração nova) ou 0.6-0.8 (edição de imagem)

### Resolução:
- **Treinado em:** 512x512, 768x768, 1024x1024
- **Recomendado inicial:** 512x512 (mais rápido)
- **Para qualidade:** 1024x1024 (mais lento, mais VRAM)

### GPU (RTX 5080 16GB):
- ✅ `--highvram` ativado (usa toda VRAM disponível)
- ✅ 512x512: ~2-3GB VRAM, ~30s geração
- ✅ 1024x1024: ~8-10GB VRAM, ~90s geração

---

## 📝 Exemplo de Prompt

### Bom Prompt:
```
a photo of a cyberpunk city at night, neon lights, rain, 
detailed architecture, cinematic lighting, high resolution, 
photorealistic, 8k
```

### Negative Prompt:
```
blurry, low quality, watermark, text, cartoon, illustration, 
bad anatomy, distorted
```

---

## 🐛 Troubleshooting

### ❌ Erro: "Could not detect model type"
**Causa:** Você está usando `CheckpointLoaderSimple`  
**Solução:** Use `DiffusionModelLoader` (node específico do Qwen)

### ❌ Erro: "No module named 'diffusers'"
**Causa:** Custom node quebrado tentando importar classe inexistente  
**Solução:** Remova o custom node (já fizemos isso!)

### ❌ Erro: "Out of memory"
**Causa:** Resolução muito alta ou CFG muito alto  
**Solução:** 
- Reduza resolução para 512x512
- Reduza CFG para 5.0
- Reduza steps para 20

### ❌ Imagem com qualidade ruim
**Causa:** Configurações inadequadas  
**Solução:**
- Aumente steps para 30-40
- Use scheduler `sgm_uniform`
- CFG entre 5.5-6.5
- Melhore o prompt

---

## 📚 Workflows Disponíveis

### 1. Basic Generation (geração do zero)
**Arquivo:** `qwen_image_basic_example.png` (já baixado em `/comfyui/output/`)  
**Usa:** `qwen_image_fp8_e4m3fn.safetensors`  
**Descrição:** Gera imagem apenas com texto

### 2. Image Editing v2509 (edição guiada)
**Download:** https://comfyanonymous.github.io/ComfyUI_examples/qwen_image/qwen_image_edit_2509_basic_example.png  
**Usa:** `qwen_image_edit_2509_fp8_e4m3fn.safetensors`  
**Descrição:** Edita imagem existente com até 3 inputs

### 3. Image Editing v1 (versão antiga)
**Download:** https://comfyanonymous.github.io/ComfyUI_examples/qwen_image/qwen_image_edit_basic_example.png  
**Usa:** `qwen_image_edit_fp8_e4m3fn.safetensors` (modelo antigo - você não tem)  
**Descrição:** Primeira versão do editor

---

## 🎯 Próximos Passos

1. ✅ Acesse http://localhost:8188
2. ✅ Arraste `./comfyui/output/qwen_image_basic_example.png` no canvas
3. ✅ Modifique o prompt positivo
4. ✅ Clique "Queue Prompt"
5. ✅ Aguarde 30-60 segundos
6. ✅ Veja sua imagem gerada!

---

## 📖 Documentação Oficial

- **ComfyUI Examples:** https://comfyanonymous.github.io/ComfyUI_examples/qwen_image/
- **HuggingFace Model:** https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI
- **Qwen-Image GitHub:** https://github.com/QwenLM/Qwen-Image

---

## 💡 Dicas Extras

### Performance:
- Feche outros programas para liberar RAM/VRAM
- Use FP8 (já está usando) em vez de BF16 para economizar VRAM
- Resolução 512x512 é 4x mais rápida que 1024x1024

### Qualidade:
- Prompts detalhados = melhores resultados
- Negative prompts são essenciais para evitar artefatos
- Scheduler `sgm_uniform` é otimizado para Qwen-Image

### Experimentação:
- Teste diferentes samplers: `euler`, `dpmpp_2m`, `dpmpp_sde`
- Varie CFG: 4.0 (mais criativo) até 8.0 (mais fiel ao prompt)
- Steps: 20 (rápido) até 50 (máxima qualidade)

---

**🎨 Agora você pode gerar imagens com o Qwen-Image corretamente!** 🚀
