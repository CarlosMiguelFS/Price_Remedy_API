def check_pague_menos(cep,produto):
    import httpx
    # Removido product_description = {} pois não é mais usado

    d_para = {
        "Mounjaro 2,5mg/ml": "166502",
        "Mounjaro 5mg/ml": "166503",
        "Mounjaro 7,5mg/ml": "166507",
        "Mounjaro 10mg/ml": "166506"
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
    endereco = httpx.post("https://www.paguemenos.com.br/api/checkout/pub/orderForms/simulation", json=payload, headers=headers).json()
    
    # Lógica de retorno corrigida:
    for values in endereco.get("pickupPoints",[]):
        # Retorna o primeiro endereço encontrado
        if values.get("address"):
            return {"loja": "Pague Menos", "endereco": dict(values["address"])} 

    return None