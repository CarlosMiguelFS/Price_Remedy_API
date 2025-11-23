def check_drogaria_sao_paulo(cep,produto):
    import httpx
    product_description = {}
    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060"
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

    if endereco.get("logisticsInfo"):
        for product in endereco["logisticsInfo"][0]["slas"]:
            if product.get("pickupStoreInfo", {}).get("address"):
                product_description["endereco"] = product["pickupStoreInfo"]["address"]  
                product_description["value"] = float(endereco["items"][0]["price"]/100)
                product_description["loja"] = "Pacheco"
                return product_description
    return None
