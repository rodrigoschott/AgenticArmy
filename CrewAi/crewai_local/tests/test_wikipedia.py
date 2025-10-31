"""
Teste individual para Wikipedia
"""
import subprocess
import sys


def test_wikipedia():
    """Testa busca na Wikipedia por 'Paraty'"""
    cmd = ["docker", "mcp", "tools", "call", "get_summary", "title=Paraty"]
    
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
    if "Paraty" in output and len(output) > 100:
        print(f"✅ PASSOU: Wikipedia retornou conteúdo")
        print(f"   Primeiros 150 chars: {output[:150]}...")
        return True
    else:
        print(f"❌ FALHOU: Output muito curto ou sem conteúdo esperado")
        print(f"   Output: {output[:200]}")
        return False


if __name__ == "__main__":
    success = test_wikipedia()
    sys.exit(0 if success else 1)
