"""
Teste individual para ferramenta de busca (DuckDuckGo)
"""
import subprocess
import sys


def test_search():
    """Testa busca por 'Paraty Brasil'"""
    cmd = ["docker", "mcp", "tools", "call", "search", "query=Paraty Brasil"]
    
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
    if "Found" in output and "search results" in output:
        print(f"✅ PASSOU: Encontrou resultados de busca")
        print(f"   Primeiros 150 chars: {output[:150]}...")
        return True
    else:
        print(f"❌ FALHOU: Output inesperado")
        print(f"   Output: {output[:200]}")
        return False


if __name__ == "__main__":
    success = test_search()
    sys.exit(0 if success else 1)
