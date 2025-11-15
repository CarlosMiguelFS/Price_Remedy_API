from fastapi import FastAPI
import uvicorn

from drograsil import check_drogasil
from pacheco import check_pacheco
from indiana import check_indiana
from pague_menos import check_pague_menos

app= FastAPI()

farmacias_checkers = [
    check_drogasil,
    check_pacheco,
    check_indiana,
    check_pague_menos
]


def formatar_resultado(res):
    """
    Recebe o dicionário bruto da farmácia e retorna
    um dicionário limpo e formatado.
    """

    endereco = res.get('disponibilidade') or res.get('endereco')

    if not isinstance(endereco, dict):
        return {
            "loja": res.get('loja'),
            "endereco_formatado": str(endereco),
            "rua": "",
            "numero": "",
            "bairro": "",
            "cidade": "",
            "estado": ""
        }
    if 'addressLocal' in endereco:
        rua = endereco.get('addressLocal', '')
        num = endereco.get('addressNumber', '')
        bairro = endereco.get('district', '')
        cidade = endereco.get('city', '')
        estado = endereco.get('sgState', '')
    
    else:
        rua = endereco.get('street', '')
        num = endereco.get('number', '')
        bairro = endereco.get('neighborhood', '')
        cidade = endereco.get('city', '')
        estado = endereco.get('state', '')

    return {
        "loja": res.get('loja'),
        "endereco_formatado": f"{rua}, {num}",
        "rua": rua,
        "numero": num,
        "bairro": bairro,
        "cidade": cidade,
        "estado": estado
    }
@app.get("/buscar/{cep}")
def buscar_remedio_cep(cep:str):
    print(f"Buscando Mounjaro para o CEP:{cep}")
    
    resultados_farma = []

    for checar_farmacia in farmacias_checkers:
        try:
            resultado = checar_farmacia(cep)
            if resultado:
                result_form = formatar_resultado(resultado)
                resultados_farma.append(result_form)
        except Exception as e:
            print(f"Checar o Erro da farmacia {checar_farmacia.__name__}, erro {e}")
    
    if not resultados_farma:
        return{"menssagem":"Produto não encontrado em nenhuma farmacia"}
    
    return {"resultados": resultados_farma}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)