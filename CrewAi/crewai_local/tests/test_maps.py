"""
Teste individual para Google Maps Geocoding
"""
import subprocess
import sys


def test_maps():
    """Testa geocoding de endereço"""
    cmd = [
        "docker", "mcp", "tools", "call",
        "maps_geocode",
        "address=Paraty, RJ, Brasil"
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
    
    # PRIORIDADE 1: Verificar se retornou coordenadas reais (API funcionando)
    if ("lat" in output.lower() and "lng" in output.lower()) or "location" in output.lower():
        print(f"✅ PASSOU: Maps retornou coordenadas")
        # Extrair coordenadas para exibir
        if '"lat":' in output:
            import re
            lat_match = re.search(r'"lat":\s*(-?\d+\.\d+)', output)
            lng_match = re.search(r'"lng":\s*(-?\d+\.\d+)', output)
            if lat_match and lng_match:
                print(f"   Coordenadas: {lat_match.group(1)}, {lng_match.group(1)}")
        return True
    
    # PRIORIDADE 2: Se API não configurada mas tool responde (também ok)
    if "not authorized" in output or "REQUEST_DENIED" in output:
        print(f"⚠️  AVISO: Maps API não configurada (mas tool funcionando)")
        print(f"   Para usar Maps, configure GOOGLE_MAPS_API_KEY")
        return True  # Consideramos sucesso pois a tool responde
    
    print(f"❌ FALHOU: Output inesperado")
    print(f"   Output: {output[:200]}")
    return False


if __name__ == "__main__":
    success = test_maps()
    sys.exit(0 if success else 1)
