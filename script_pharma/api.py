from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional

# Certifique-se que os nomes dos arquivos importados estao corretos na sua pasta
from drograsil import check_drogasil
from pacheco import check_pacheco
from indiana import check_indiana
from pague_menos import check_pague_menos
from drograria_sao_paulo import check_drogaria_sao_paulo
from simple_geocoder import geocoder


app = FastAPI()

origins = [
    "https://med-radar-nine.vercel.app",
    "https://med-location.base44.app",
    "http://localhost:3000",  # Para desenvolvimento
    "http://localhost:5173"   # Para desenvolvimento (Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

farmacias_checkers = [
    check_drogasil,
    check_pacheco,
    check_indiana,
    check_pague_menos,
    check_drogaria_sao_paulo
]

# API Keys (opcional - configure via variáveis de ambiente)
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
POSITIONSTACK_API_KEY = os.getenv('POSITIONSTACK_API_KEY')

def normalizar_resultados(resultado):
    if not resultado:
        return []

    if isinstance(resultado, list):
        return [item for item in resultado if item]

    return [resultado]

def formatar_resultado(res):
    endereco = res.get('disponibilidade') or res.get('endereco')
    
    dict_endereco = {
        "rua": "", 
        "numero": "", 
        "bairro": "", 
        "cidade": "", 
        "estado": "", 
        "endereco_formatado": str(endereco),
        "latitude": None,
        "longitude": None,
        "geocode_source": None,
        "geocode_confidence": None
    }

    if isinstance(endereco, dict):
        if 'addressLocal' in endereco:
            dict_endereco["rua"] = endereco.get('addressLocal', '')
            dict_endereco["numero"] = endereco.get('addressNumber', '')
            dict_endereco["bairro"] = endereco.get('district', '')
            dict_endereco["cidade"] = endereco.get('city', '')
            dict_endereco["estado"] = endereco.get('sgState', '')
        else:
            dict_endereco["rua"] = endereco.get('street', '')
            dict_endereco["numero"] = endereco.get('number', '')
            dict_endereco["bairro"] = endereco.get('neighborhood', '')
            dict_endereco["cidade"] = endereco.get('city', '')
            dict_endereco["estado"] = endereco.get('state', '')
        
        dict_endereco["endereco_formatado"] = f"{dict_endereco['rua']}, {dict_endereco['numero']}"
    
    possui_endereco_estruturado = any([
        dict_endereco["rua"],
        dict_endereco["bairro"],
        dict_endereco["cidade"],
        dict_endereco["estado"]
    ])

    if possui_endereco_estruturado:
        try:
            geo_result = geocoder.geocode_with_fallback(
                rua=dict_endereco["rua"],
                numero=dict_endereco["numero"],
                bairro=dict_endereco["bairro"],
                cidade=dict_endereco["cidade"],
                estado=dict_endereco["estado"],
                google_api_key=GOOGLE_MAPS_API_KEY,
                positionstack_api_key=POSITIONSTACK_API_KEY
            )
            
            if geo_result:
                dict_endereco["latitude"] = geo_result['lat']
                dict_endereco["longitude"] = geo_result['lon']
                dict_endereco["geocode_source"] = geo_result.get('source')
                dict_endereco["geocode_confidence"] = geo_result.get('importance') or geo_result.get('confidence')
                
                # Atualiza endereço formatado com o retornado pelo serviço de geocoding
                if geo_result.get('display_name'):
                    dict_endereco["endereco_completo"] = geo_result['display_name']
        except Exception as e:
            print(f"Erro ao geocodificar {dict_endereco['endereco_formatado']}: {e}")

    return {
        "loja": res.get('loja'),
        "url": res.get('url'),
        "melhor_preco": res.get('melhor_preco'),
        "preco_padrao": res.get('preco_padrao'),
        "porcentagem_diferenca": res.get('porcentagem_diferenca'),
        "estoque": res.get('estoque'),
        "endereco_formatado": dict_endereco["endereco_formatado"],
        "endereco_completo": dict_endereco.get("endereco_completo"),
        "rua": dict_endereco["rua"],
        "numero": dict_endereco["numero"],
        "bairro": dict_endereco["bairro"],
        "cidade": dict_endereco["cidade"],
        "estado": dict_endereco["estado"],
        "latitude": dict_endereco["latitude"],
        "longitude": dict_endereco["longitude"],
        "geocode_source": dict_endereco["geocode_source"],
        "geocode_confidence": dict_endereco["geocode_confidence"]
    }

@app.get("/")
def root():
    return {
        "message": "API Med Radar - Sistema de busca de medicamentos",
        "endpoints": {
            "/buscar/{cep}": "Buscar medicamento por CEP (query param: produto)",
            "/health": "Status da API"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "geocoding_services": {
            "nominatim": "ativo",
            "google_maps": "ativo" if GOOGLE_MAPS_API_KEY else "inativo",
            "positionstack": "ativo" if POSITIONSTACK_API_KEY else "inativo"
        }
    }

@app.get("/buscar/{cep}")
def buscar_remedio_cep(cep: str, produto: str):
    print(f"Buscando {produto} para o CEP: {cep}")
    
    resultados_farma = []

    for checar_farmacia in farmacias_checkers:
        try:
            resultado = checar_farmacia(cep, produto)
            for item in normalizar_resultados(resultado):
                result_form = formatar_resultado(item)
                resultados_farma.append(result_form)
        except Exception as e:
            print(f"Erro ao checar farmácia {checar_farmacia.__name__}: {e}")
    
    if not resultados_farma:
        return {
            "mensagem": "Produto não encontrado em nenhuma farmácia",
            "resultados": []
        }
    
    # Ordena por preço (menor primeiro)
    resultados_farma.sort(key=lambda x: x['melhor_preco'] if x['melhor_preco'] else float('inf'))
    
    print(f"Encontrados {len(resultados_farma)} resultados")
    return {
        "mensagem": f"Encontrados {len(resultados_farma)} resultado(s)",
        "resultados": resultados_farma
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
