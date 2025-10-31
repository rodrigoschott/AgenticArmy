"""
Teste individual para Fetch (Web Content)
"""
import subprocess
import sys


def test_fetch():
    """Testa fetch de conteúdo web"""
    cmd = [
        "docker", "mcp", "tools", "call",
        "fetch",
        "url=https://example.com"
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
    if len(output) > 100:
        print(f"✅ PASSOU: Fetch retornou conteúdo ({len(output)} chars)")
        print(f"   Primeiros 150 chars: {output[:150]}...")
        return True
    else:
        print(f"❌ FALHOU: Output muito curto")
        print(f"   Output: {output[:200]}")
        return False


if __name__ == "__main__":
    success = test_fetch()
    sys.exit(0 if success else 1)
