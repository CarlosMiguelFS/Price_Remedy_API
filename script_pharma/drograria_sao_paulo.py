def check_drogaria_sao_paulo(cep,produto):
    import httpx
    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060"
    }

    d_para_link = {
        "Mounjaro 2,5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-2-5mg-eli-lilly-4-seringa-preenchidas-0-5ml-solucao-injetavel-subcutaneo---4-canetas/p",
        "Mounjaro 5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-5mg-eli-lilly-4-seringa-preenchida-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 7,5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-7-5mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 10mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-10mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p"
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
    preco = endereco["items"][0]["price"] / 100

    for values in endereco.get("pickupPoints", []):
        if values.get("address"):
            return {
                "loja": "Drogaria São Paulo",
                "endereco": dict(values["address"]),
                "url": d_para_link[produto],
                "melhor_preco": preco
            }

    return None

