from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Certifique-se que os nomes dos arquivos importados estao corretos na sua pasta
from drograsil import check_drogasil
from pacheco import check_pacheco
from indiana import check_indiana
from pague_menos import check_pague_menos
from drograria_sao_paulo import check_drogaria_sao_paulo
from raia import check_drogaraia

app = FastAPI()

origins = [
    "https://3000-i9ej1of031jvjmrchzi0z-c6ad99b1.manus.computer",
    "https://medradar-dnhsdsop.manus.space",
    "https://lovable.dev/projects/7dbf5259-3626-42d5-8b98-22dd3c29409d",
    "https://app-9a8765fc-728b-4155-b95f-496f84e6f469.base44.app",
    "https://med-radar.base44.app",
    "http://localhost:3000",
    "https://radar-meds.lovable.app",
    "https://app.base44.com/apps/69190e47002195fa7c0dd7ec/editor/preview/Home"
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
    check_drogaraia
    # check_drogaria_sao_paulo
]

def formatar_resultado(res):
    endereco = res.get('disponibilidade') or res.get('endereco')
    
    dict_endereco = {
        "rua": "", "numero": "", "bairro": "", "cidade": "", "estado": "", "endereco_formatado": str(endereco)
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

    return {
        "loja": res.get('loja'),
        "url": res.get('url'),
        "melhor_preco": res.get('melhor_preco'),
        "preco_padrao": res.get('preco_padrao'),
        "porcentagem_diferenca": res.get('porcentagem_diferenca'),
        "estoque": res.get('estoque'),
        "endereco_formatado": dict_endereco["endereco_formatado"],
        "rua": dict_endereco["rua"],
        "numero": dict_endereco["numero"],
        "bairro": dict_endereco["bairro"],
        "cidade": dict_endereco["cidade"],
        "estado": dict_endereco["estado"]
    }

@app.get("/buscar/{cep}")
def buscar_remedio_cep(cep:str, produto:str):
    print(f"Buscando {produto} para o CEP:{cep}")
    
    resultados_farma = []

    for checar_farmacia in farmacias_checkers:
        try:
            resultado = checar_farmacia(cep, produto)
            if resultado:
                result_form = formatar_resultado(resultado)
                resultados_farma.append(result_form)
        except Exception as e:
            print(f"Checar o Erro da farmacia {checar_farmacia.__name__}, erro {e}")
    
    if not resultados_farma:
        return {"menssagem": "Produto não encontrado em nenhuma farmacia"}
    print(resultados_farma)
    return {"resultados": resultados_farma}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)