import httpx

def check_pacheco(cep,produto):
    

    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060"
    }
    d_para_link = {
        "Mounjaro 2,5mg/ml": "https://www.drogariaspacheco.com.br/mounjaro-25mg-solucao-injetavel--subcutanea-4-seringa-pree-eli-lilly/p",
        "Mounjaro 5mg/ml": "https://www.drogariaspacheco.com.br/mounjaro-5mg-eli-lilly-4-seringa-preenchida-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 7,5mg/ml": "https://www.drogariaspacheco.com.br/mounjaro-7-5mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 10mg/ml": "https://www.drogariaspacheco.com.br/mounjaro-10mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 12,5mg/ml":"https://www.drogariaspacheco.com.br/mounjaro-15mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 15mg/ml":"https://www.drogariaspacheco.com.br/mounjaro-12-5mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Ritalina 10mg 30 comprimidos":"https://www.drogariaspacheco.com.br/ritalina-10mg-30-comprimidos/p",
        "Ritalina 10mg 60 comprimidos":"https://www.drogariaspacheco.com.br/ritalina-10mg-novartis-biociencias-60-comprimidos/p",
        "Ritalina LA 10mg":"https://www.drogariaspacheco.com.br/ritalina-la-10mg-novatis-30-comprimidos/p",
        "Ritalina LA 20mg":"https://www.drogariaspacheco.com.br/ritalina-la-20mg-novartis-biociencias-30-comprimidos/p",
        "Ritalina LA 30mg":"https://www.drogariaspacheco.com.br/ritalina-la-30mg-novartis-biociencias-30-comprimidos/p",
        "Ritalina LA 40mg":"https://www.drogariaspacheco.com.br/ritalina-la-40mg-novartis-biociencias-30-comprimidos/p",
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
                product_description["url"] = d_para_link[produto]
                return product_description
    
    return None