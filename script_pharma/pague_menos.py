import httpx

def check_pague_menos(cep, produto):
    d_para = {
        "Mounjaro 2,5mg/ml": "166502",
        "Mounjaro 5mg/ml": "166503",
        "Mounjaro 7,5mg/ml": "166507",
        "Mounjaro 10mg/ml": "166506"
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
            "https://www.paguemenos.com.br/api/checkout/pub/orderForms/simulation", 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        # Se der erro 403/500, vai pular pro except agora
        response.raise_for_status()
        
        endereco = response.json()
    
        for values in endereco.get("pickupPoints", []):
            if values.get("address"):
                return {"loja": "Pague Menos", "endereco": dict(values["address"])} 

    except Exception as e:
        # Isso vai aparecer no log do uvicorn se der erro, ajudando a debugar
        print(f"Erro Pague Menos: {e}")
        pass

    return None