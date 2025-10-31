"""
Teste individual para YouTube Transcript
"""
import subprocess
import sys


def test_youtube():
    """Testa obtenção de info de vídeo do YouTube"""
    cmd = [
        "docker", "mcp", "tools", "call", 
        "get_video_info",
        "url=https://youtube.com/watch?v=dQw4w9WgXcQ"
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        encoding='utf-8',
        errors='replace'
    )
    
    if result.returncode != 0:
        print(f"❌ FALHOU: {result.stderr[:200]}")
        return False
    
    output = result.stdout
    if "title" in output.lower() and len(output) > 50:
        print(f"✅ PASSOU: YouTube retornou informações do vídeo")
        print(f"   Primeiros 150 chars: {output[:150]}...")
        return True
    else:
        print(f"❌ FALHOU: Output não contém informações esperadas")
        print(f"   Output: {output[:200]}")
        return False


if __name__ == "__main__":
    success = test_youtube()
    sys.exit(0 if success else 1)
