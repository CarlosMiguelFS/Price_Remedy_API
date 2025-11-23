import httpx

def check_drogaria_sao_paulo(cep, produto):
    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060"
    }

    prod_id = d_para.get(produto.strip())
    if not prod_id: return None

    # Header simples que funcionou no seu teste
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    payload = {
        "items": [{"id": prod_id, "quantity": 1, "seller": "1"}],
        "country": "BRA",
        "postalCode": cep
    }

    try:
        response = httpx.post(
            "https://www.drogariasaopaulo.com.br/api/checkout/pub/orderforms/simulation", 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        response.raise_for_status()
        
        endereco = response.json()

        for values in endereco.get("pickupPoints", []):
            if values.get("address"):
                return {"loja": "Drogaria São Paulo", "endereco": dict(values["address"])} 

    except Exception as e:
        print(f"Erro Drogaria SP: {e}")
        pass

    return None