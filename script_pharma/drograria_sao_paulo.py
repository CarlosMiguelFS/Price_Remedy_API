def check_drogaria_sao_paulo(cep,produto):
    import httpx
    d_para = {
        "Mounjaro Tirzepatida 2,5mg/ml 0,5ml Injetável":"887528", #Mounjaro Tirzepatida 2,5mg/0,5ml 4 Seringas Preenchidas Solução Injetável Subcutânea + 4 Canetas
        "Mounjaro Tirzepatida 5mg/ml 0,5ml Injetável":"887455", #Mounjaro Tirzepatida 5mg/0,5ml 4 Seringas Preenchidas Solução Injetável Subcutânea + 4 Canetas
        "Mounjaro Tirzepatida 7,5mg/ml 0,5ml Injetável":"887951", #Mounjaro Tirzepatida 7,5mg 4 seringas preenchidas de 0,5ml Solução Injetável Subcutâneo + 4 Canetas
        "Mounjaro Tirzepatida 10mg/ml 0,5ml Injetável":"888060" #Mounjaro Tirzepatida 10mg 4 seringas preenchidas de 0,5ml Solução Injetável Subcutâneo + 4 Canetas
    }

    payload = {
        "items":[
            {
                "id":d_para[produto.strip()],
                "quantity":1,
                "seller":"1"
            }
        ],
        "country":"BRA",
        "postalCode":f"{cep}"
    }

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 OPR/123.0.0.0"}
    endereco = httpx.post("https://www.drogariasaopaulo.com.br/api/checkout/pub/orderforms/simulation", json=payload, headers=headers).json()


    for values in endereco.get("pickupPoints",[]):
        if values.get("address"):
            return {"loja": "Pague Menos", "endereco": dict(values["address"])} 

    return None