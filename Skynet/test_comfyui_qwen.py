#!/usr/bin/env python3
"""
Script de teste para ComfyUI com Qwen-Image
Gera uma imagem usando os modelos Qwen FP8
"""

import json
import requests
import time
import uuid

# Configuração do ComfyUI
COMFYUI_URL = "http://localhost:8188"

def queue_prompt(workflow):
    """Envia workflow para o ComfyUI"""
    p = {"prompt": workflow, "client_id": str(uuid.uuid4())}
    response = requests.post(f"{COMFYUI_URL}/prompt", json=p)
    return response.json()

def get_history(prompt_id):
    """Obtém histórico de execução"""
    response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
    return response.json()

def test_simple_generation():
    """Teste básico de geração de imagem"""
    
    # Workflow simplificado para Qwen-Image
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "qwen_image_fp8_e4m3fn.safetensors"
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "a beautiful landscape with mountains and a lake, photorealistic, 4k",
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "blurry, low quality, distorted",
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "qwen_test",
                "images": ["6", 0]
            }
        }
    }
    
    print("🚀 Enviando workflow para ComfyUI...")
    result = queue_prompt(workflow)
    
    if "prompt_id" in result:
        prompt_id = result["prompt_id"]
        print(f"✅ Workflow enviado! ID: {prompt_id}")
        print("⏳ Gerando imagem... (isso pode demorar alguns minutos na primeira vez)")
        
        # Aguarda conclusão
        while True:
            time.sleep(2)
            history = get_history(prompt_id)
            if prompt_id in history:
                print("✅ Imagem gerada com sucesso!")
                print(f"📁 Imagem salva em: ComfyUI/output/qwen_test_*.png")
                break
    else:
        print(f"❌ Erro: {result}")

if __name__ == "__main__":
    print("🎨 Teste do ComfyUI com Qwen-Image FP8")
    print("=" * 50)
    test_simple_generation()
