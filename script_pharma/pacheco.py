import httpx

def check_pacheco(cep,produto):
    

    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060"
    }

    product_description = {}
    url_pharm = "https://www.drogariaspacheco.com.br/api/checkout/pub/orderforms/simulation"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }

    payload ={
        "items":[
            {
                "id": d_para[produto.strip()],
                "quantity": 1,
                "seller": "1"
            }
        ],
        "country": "BRA",
        "postalCode": cep
    }

    resp_frete = httpx.post(url_pharm, json= payload ,headers=headers).json()
    
    if resp_frete.get("logisticsInfo"):
        for product in resp_frete["logisticsInfo"][0]["slas"]:
            if product.get("pickupStoreInfo", {}).get("address"):
                product_description["endereco"] = product["pickupStoreInfo"]["address"]  
                product_description["value"] = float(resp_frete["items"][0]["price"]/100)
                product_description["loja"] = "Pacheco"
                return product_description
    
    return None