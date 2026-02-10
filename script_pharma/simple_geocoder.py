
import requests
import time
from typing import Optional, Dict
from functools import lru_cache

class SimpleGeocoder:
    """Geocodificador simples usando apenas Nominatim"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MedRadar/1.0 (Pharmacy Locator App - Contact: seu-email@exemplo.com)'
        })
        self.last_request_time = 0
        
    def _normalize_address(self, rua: str, numero: str, bairro: str, 
                          cidade: str, estado: str) -> str:
        """Normaliza o endereço para melhor geocodificação"""
        parts = []
        
        if rua:
            rua_clean = ' '.join(rua.strip().split())
            if numero:
                parts.append(f"{rua_clean}, {numero}")
            else:
                parts.append(rua_clean)
        
        if bairro:
            parts.append(bairro.strip())
            
        if cidade:
            parts.append(cidade.strip())
            
        if estado:
            parts.append(estado.strip())
        
        parts.append("Brasil")  # Sempre adiciona país
            
        return ', '.join(parts)
    
    def _respect_rate_limit(self):
        """
        Nominatim requer 1 segundo entre requisições
        Política de uso: https://operations.osmfoundation.org/policies/nominatim/
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last
            print(f"⏳ Aguardando {sleep_time:.2f}s (rate limit Nominatim)...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @lru_cache(maxsize=1000)
    def geocode(self, rua: str, numero: str, bairro: str,
                cidade: str, estado: str) -> Optional[Dict]:
        """
        Geocodifica um endereço usando Nominatim
        Retorna: {'lat': float, 'lon': float, 'display_name': str} ou None
        """
        # Normaliza o endereço
        full_address = self._normalize_address(rua, numero, bairro, cidade, estado)
        
        # Tenta com endereço completo
        result = self._geocode_nominatim(full_address)
        
        if result:
            print(f"✅ Geocodificado: {full_address[:50]}...")
            return result
        
        # Fallback: tenta sem número
        if numero:
            address_sem_numero = self._normalize_address(rua, "", bairro, cidade, estado)
            result = self._geocode_nominatim(address_sem_numero)
            
            if result:
                print(f"✅ Geocodificado (sem número): {address_sem_numero[:50]}...")
                return result
        
        # Fallback: tenta só cidade/estado
        if cidade and estado:
            address_cidade = f"{cidade}, {estado}, Brasil"
            result = self._geocode_nominatim(address_cidade)
            
            if result:
                print(f"⚠️ Geocodificado apenas cidade: {address_cidade}")
                return result
        
        print(f"❌ Não foi possível geocodificar: {full_address[:50]}...")
        return None
    
    def _geocode_nominatim(self, address: str) -> Optional[Dict]:
        """Faz a requisição real ao Nominatim"""
        try:
            # Respeita rate limit
            self._respect_rate_limit()
            
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'br',
                'addressdetails': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if results:
                result = results[0]
                return {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'display_name': result.get('display_name', ''),
                    'importance': float(result.get('importance', 0)),
                    'type': result.get('type', ''),
                    'class': result.get('class', ''),
                    'source': 'nominatim'
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição Nominatim: {e}")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return None

# Instância global
geocoder = SimpleGeocoder()


# Exemplos de uso:
if __name__ == "__main__":
    print("🧪 Testando geocodificador...")
    
    # Teste 1: Endereço completo
    result1 = geocoder.geocode(
        rua="AVENIDA AUGUSTO EMILIO ESTELITA LINS",
        numero="465",
        bairro="JD CAMBURI",
        cidade="VITÓRIA",
        estado="ES"
    )
    print(f"\nTeste 1: {result1}")
    
    # Teste 2: Endereço sem número
    result2 = geocoder.geocode(
        rua="Avenida José Moreira Martins Rato",
        numero="",
        bairro="de Fátima",
        cidade="Serra",
        estado="ES"
    )
    print(f"\nTeste 2: {result2}")
    
    # Teste 3: Cache (deve ser instantâneo)
    print("\n⏱️ Testando cache...")
    start = time.time()
    result3 = geocoder.geocode(
        rua="AVENIDA AUGUSTO EMILIO ESTELITA LINS",
        numero="465",
        bairro="JD CAMBURI",
        cidade="VITÓRIA",
        estado="ES"
    )
    end = time.time()
    print(f"Tempo com cache: {(end-start)*1000:.2f}ms (deve ser < 1ms)")
    print(f"Teste 3: {result3}")
