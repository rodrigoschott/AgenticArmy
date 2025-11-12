# ComfyUI Redeploy Script (PowerShell)
# Script para facilitar o redeploy do ComfyUI com setup automático no Windows

$ErrorActionPreference = "Stop"

Write-Host "🔄 ComfyUI Redeploy - Configuração Automática de Dependências" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "[ERROR] docker-compose.yml não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Perguntar sobre limpeza
Write-Host ""
$response = Read-Host "Deseja remover volumes (limpar setup anterior)? [y/N]"

if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "[WARN] Removendo volumes existentes..." -ForegroundColor Yellow
    docker-compose --profile gpu-nvidia down -v
} else {
    Write-Host "[INFO] Mantendo volumes existentes..." -ForegroundColor Green
    docker-compose --profile gpu-nvidia down
}

Write-Host ""
Write-Host "[INFO] Iniciando ComfyUI com setup automático..." -ForegroundColor Green
Write-Host "[INFO] Processo: init container → instalar dependências → start ComfyUI" -ForegroundColor Green
Write-Host ""

# Iniciar com profile gpu-nvidia
docker-compose --profile gpu-nvidia up -d

Write-Host ""
Write-Host "[INFO] Containers iniciando..." -ForegroundColor Green
Write-Host ""

# Aguardar init container
Write-Host "[INFO] Aguardando init container instalar dependências..." -ForegroundColor Green
$initTimeout = 300  # 5 minutos
$elapsed = 0

while ($elapsed -lt $initTimeout) {
    try {
        $initStatus = docker inspect comfyui-gpu-init --format='{{.State.Status}}' 2>$null
        
        if ($initStatus -eq "exited") {
            $exitCode = docker inspect comfyui-gpu-init --format='{{.State.ExitCode}}' 2>$null
            if ($exitCode -eq "0") {
                Write-Host ""
                Write-Host "[INFO] ✅ Init container completado com sucesso!" -ForegroundColor Green
                break
            } else {
                Write-Host ""
                Write-Host "[ERROR] ❌ Init container falhou com código $exitCode" -ForegroundColor Red
                Write-Host ""
                Write-Host "[ERROR] Logs do init container:" -ForegroundColor Red
                docker logs comfyui-gpu-init --tail 50
                exit 1
            }
        }
    } catch {
        # Container ainda não existe
    }
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 5
    $elapsed += 5
}

if ($elapsed -ge $initTimeout) {
    Write-Host ""
    Write-Host "[ERROR] ⏱️ Timeout: Init container não completou em 5 minutos" -ForegroundColor Red
    docker logs comfyui-gpu-init --tail 50
    exit 1
}

Write-Host ""
Write-Host "[INFO] Aguardando ComfyUI ficar healthy..." -ForegroundColor Green
$comfyuiTimeout = 120  # 2 minutos
$elapsed = 0

while ($elapsed -lt $comfyuiTimeout) {
    try {
        $health = docker inspect comfyui --format='{{.State.Health.Status}}' 2>$null
        
        if ($health -eq "healthy") {
            Write-Host ""
            Write-Host "[INFO] ✅ ComfyUI está healthy e pronto!" -ForegroundColor Green
            break
        }
    } catch {
        # Container ainda não está pronto
    }
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 5
    $elapsed += 5
}

Write-Host ""
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎉 ComfyUI Deployment Completo!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] 🌐 Interface Web: http://localhost:8188" -ForegroundColor Green
Write-Host "[INFO] 📦 GPU: RTX 5080 16GB (--highvram mode)" -ForegroundColor Green
Write-Host "[INFO] 🔧 Modelos: Qwen-Image FP8 instalados" -ForegroundColor Green
Write-Host ""

# Mostrar status dos containers
Write-Host "[INFO] Status dos containers:" -ForegroundColor Green
docker-compose --profile gpu-nvidia ps

Write-Host ""
Write-Host "[INFO] Logs de instalação (últimas 20 linhas):" -ForegroundColor Green
docker logs comfyui-gpu-init --tail 20

Write-Host ""
Write-Host "[INFO] Para ver logs do ComfyUI em tempo real:" -ForegroundColor Cyan
Write-Host "  docker logs -f comfyui" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Para verificar dependências instaladas:" -ForegroundColor Cyan
Write-Host "  docker exec comfyui pip list | Select-String 'diffusers|transformers|accelerate'" -ForegroundColor White
Write-Host ""
