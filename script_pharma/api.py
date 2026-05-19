import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from drograria_sao_paulo import check_drogaria_sao_paulo
from drograsil import check_drogasil
from indiana import check_indiana
from pague_menos import check_pague_menos
from pacheco import check_pacheco
from simple_geocoder import geocoder


app = FastAPI()

origins = [
    "https://med-radar-nine.vercel.app",
    "https://med-location.base44.app",
    "http://localhost:3000",
    "https://radar-medicamentos.base44.app/",
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
    check_drogaria_sao_paulo,
]

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
POSITIONSTACK_API_KEY = os.getenv("POSITIONSTACK_API_KEY")


def normalizar_resultados(resultado):
    if not resultado:
        return []

    if isinstance(resultado, list):
        return [item for item in resultado if item]

    return [resultado]


def extrair_cep(endereco):
    if not isinstance(endereco, dict):
        return ""

    return (
        endereco.get("postalCode")
        or endereco.get("zipcode")
        or endereco.get("zipCode")
        or ""
    )


def normalizar_cep_consultado(cep):
    digits = "".join(ch for ch in str(cep or "") if ch.isdigit())
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits or str(cep or "")


def extrair_coordenadas_nativas(endereco):
    if not isinstance(endereco, dict):
        return None

    geo_coordinates = endereco.get("geoCoordinates")
    if isinstance(geo_coordinates, (list, tuple)) and len(geo_coordinates) >= 2:
        try:
            longitude = float(geo_coordinates[0])
            latitude = float(geo_coordinates[1])
            return {
                "lat": latitude,
                "lon": longitude,
                "source": "native_pickup_point",
                "confidence": 1.0,
                "precision": "native",
            }
        except (TypeError, ValueError):
            pass

    latitude = endereco.get("latitude") or endereco.get("lat")
    longitude = endereco.get("longitude") or endereco.get("lon")
    if latitude is not None and longitude is not None:
        try:
            return {
                "lat": float(latitude),
                "lon": float(longitude),
                "source": "native_branch_address",
                "confidence": 1.0,
                "precision": "native",
            }
        except (TypeError, ValueError):
            return None

    return None


def formatar_resultado(res):
    endereco = res.get("disponibilidade") or res.get("endereco")

    dict_endereco = {
        "rua": "",
        "numero": "",
        "bairro": "",
        "cidade": "",
        "estado": "",
        "cep": "",
        "endereco_formatado": str(endereco),
        "latitude": None,
        "longitude": None,
        "geocode_source": None,
        "geocode_confidence": None,
        "coordinate_precision": None,
    }

    if isinstance(endereco, dict):
        if "addressLocal" in endereco:
            dict_endereco["rua"] = endereco.get("addressLocal", "")
            dict_endereco["numero"] = endereco.get("addressNumber", "")
            dict_endereco["bairro"] = endereco.get("district", "")
            dict_endereco["cidade"] = endereco.get("city", "")
            dict_endereco["estado"] = endereco.get("sgState", "")
        else:
            dict_endereco["rua"] = endereco.get("street", "")
            dict_endereco["numero"] = endereco.get("number", "")
            dict_endereco["bairro"] = endereco.get("neighborhood", "")
            dict_endereco["cidade"] = endereco.get("city", "")
            dict_endereco["estado"] = endereco.get("state", "")

        dict_endereco["cep"] = extrair_cep(endereco)
        dict_endereco["endereco_formatado"] = (
            f"{dict_endereco['rua']}, {dict_endereco['numero']}"
        )

    possui_endereco_estruturado = any(
        [
            dict_endereco["rua"],
            dict_endereco["bairro"],
            dict_endereco["cidade"],
            dict_endereco["estado"],
        ]
    )

    coordenadas_nativas = extrair_coordenadas_nativas(endereco)
    if coordenadas_nativas:
        dict_endereco["latitude"] = coordenadas_nativas["lat"]
        dict_endereco["longitude"] = coordenadas_nativas["lon"]
        dict_endereco["geocode_source"] = coordenadas_nativas["source"]
        dict_endereco["geocode_confidence"] = coordenadas_nativas["confidence"]
        dict_endereco["coordinate_precision"] = coordenadas_nativas["precision"]
    elif possui_endereco_estruturado:
        try:
            geo_result = geocoder.geocode_with_fallback(
                rua=dict_endereco["rua"],
                numero=dict_endereco["numero"],
                bairro=dict_endereco["bairro"],
                cidade=dict_endereco["cidade"],
                estado=dict_endereco["estado"],
                cep=dict_endereco["cep"],
                google_api_key=GOOGLE_MAPS_API_KEY,
                positionstack_api_key=POSITIONSTACK_API_KEY,
            )

            if geo_result:
                dict_endereco["latitude"] = geo_result["lat"]
                dict_endereco["longitude"] = geo_result["lon"]
                dict_endereco["geocode_source"] = geo_result.get("source")
                dict_endereco["geocode_confidence"] = geo_result.get(
                    "confidence"
                ) or geo_result.get("importance")
                dict_endereco["coordinate_precision"] = geo_result.get("precision")

                if geo_result.get("display_name"):
                    dict_endereco["endereco_completo"] = geo_result["display_name"]
        except Exception as e:
            print(f"Erro ao geocodificar {dict_endereco['endereco_formatado']}: {e}")

    return {
        "loja": res.get("loja"),
        "url": res.get("url"),
        "melhor_preco": res.get("melhor_preco"),
        "preco_padrao": res.get("preco_padrao"),
        "porcentagem_diferenca": res.get("porcentagem_diferenca"),
        "estoque": res.get("estoque"),
        "endereco_formatado": dict_endereco["endereco_formatado"],
        "endereco_completo": dict_endereco.get("endereco_completo"),
        "rua": dict_endereco["rua"],
        "numero": dict_endereco["numero"],
        "bairro": dict_endereco["bairro"],
        "cidade": dict_endereco["cidade"],
        "estado": dict_endereco["estado"],
        "cep": dict_endereco["cep"],
        "latitude": dict_endereco["latitude"],
        "longitude": dict_endereco["longitude"],
        "geocode_source": dict_endereco["geocode_source"],
        "geocode_confidence": dict_endereco["geocode_confidence"],
        "coordinate_precision": dict_endereco["coordinate_precision"],
    }


@app.get("/")
def root():
    return {
        "message": "API Med Radar - Sistema de busca de medicamentos",
        "endpoints": {
            "/buscar/{cep}": "Buscar medicamento por CEP (query param: produto)",
            "/health": "Status da API",
        },
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "geocoding_services": {
            "nominatim": "ativo",
            "google_maps": "ativo" if GOOGLE_MAPS_API_KEY else "inativo",
            "positionstack": "ativo" if POSITIONSTACK_API_KEY else "inativo",
        },
    }


@app.get("/buscar/{cep}")
def buscar_remedio_cep(cep: str, produto: str):
    print(f"Buscando {produto} para o CEP: {cep}")
    cep_consultado = normalizar_cep_consultado(cep)

    resultados_farma = []

    for checar_farmacia in farmacias_checkers:
        try:
            resultado = checar_farmacia(cep, produto)
            for item in normalizar_resultados(resultado):
                resultados_farma.append(formatar_resultado(item))
        except Exception as e:
            print(f"Erro ao checar farmacia {checar_farmacia.__name__}: {e}")

    if not resultados_farma:
        return {
            "cep_consultado": cep,
            "cep_consultado_formatado": cep_consultado,
            "mensagem": "Produto nao encontrado em nenhuma farmacia",
            "resultados": [],
        }

    resultados_farma.sort(
        key=lambda x: x["melhor_preco"] if x["melhor_preco"] else float("inf")
    )

    print(f"Encontrados {len(resultados_farma)} resultados")
    return {
        "cep_consultado": cep,
        "cep_consultado_formatado": cep_consultado,
        "mensagem": f"Encontrados {len(resultados_farma)} resultado(s)",
        "resultados": resultados_farma,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
