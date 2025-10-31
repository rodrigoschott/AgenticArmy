"""
Runner para todos os testes individuais de MCP
"""
import subprocess
import sys
from pathlib import Path


def run_test(test_file: str) -> bool:
    """Executa um teste individual"""
    print(f"\n{'='*80}")
    print(f"🧪 Executando: {test_file}")
    print('='*80)
    
    result = subprocess.run(
        ["python", test_file],
        capture_output=False,  # Mostra output diretamente
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    return result.returncode == 0


def main():
    """Executa todos os testes individuais"""
    tests_dir = Path(__file__).parent
    
    tests = [
        "test_search.py",
        "test_wikipedia.py",
        "test_youtube.py",
        "test_maps.py",
        "test_airbnb.py",
        "test_fetch.py"
    ]
    
    results = {}
    
    print("="*80)
    print("🚀 EXECUTANDO TESTES INDIVIDUAIS DE MCP")
    print("="*80)
    
    for test in tests:
        test_path = tests_dir / test
        if test_path.exists():
            success = run_test(str(test_path))
            results[test] = success
        else:
            print(f"⚠️  Teste não encontrado: {test}")
            results[test] = False
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status:12} | {test}")
    
    print("="*80)
    print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    print("="*80)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
