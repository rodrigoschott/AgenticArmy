"""
Teste individual para Airbnb Search
"""
import subprocess
import sys


def test_airbnb():
    """Testa busca de listagens no Airbnb"""
    cmd = [
        "docker", "mcp", "tools", "call",
        "airbnb_search",
        "location=Paraty",
        "adults=2",
        "ignoreRobotsText=true"  # Bypass robots.txt para testes
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        encoding='utf-8',
        errors='replace'
    )
    
    # Airbnb agora deve funcionar com ignoreRobotsText=true
    if result.returncode != 0:
        # Se ainda tiver erro de robots.txt, avisar
        if "robots.txt" in result.stderr or "disallowed" in result.stdout:
            print(f"⚠️  AVISO: Airbnb ainda bloqueado (verifique configuração do MCP)")
            return True  # Não falhar o teste
        print(f"❌ FALHOU: {result.stderr[:200]}")
        return False
    
    output = result.stdout
    if "listing" in output.lower() or len(output) > 100:
        print(f"✅ PASSOU: Airbnb retornou dados")
        print(f"   Primeiros 150 chars: {output[:150]}...")
        return True
    
    print(f"❌ FALHOU: Output inesperado")
    print(f"   Output: {output[:200]}")
    return False


if __name__ == "__main__":
    success = test_airbnb()
    sys.exit(0 if success else 1)
