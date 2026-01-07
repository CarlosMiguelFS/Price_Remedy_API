import httpx

def check_drogasil(cep, produto):
    
    # 1. Definimos a chave limpa logo no começo
    chave_produto = produto.strip()
    
    d_para = {
        "Mounjaro 2,5mg/ml": "1272170",
        "Mounjaro 5mg/ml": "1272173",
        "Mounjaro 7,5mg/ml": "1272174",
        "Mounjaro 10mg/ml": "1272177",
        "Ritalina 10mg 30 comprimidos":"1559",
        "Ritalina 10mg 60 comprimidos":"10675",
        "Ritalina LA 10mg/ml":"37153",
        "Ritalina LA 30mg/ml":"97778",
        "Ritalina LA 40mg/ml":"11613",
        "Ritalina LA 20mg/ml":"31770"
    }

    d_para_link ={
        "Mounjaro 2,5mg/ml":"https://www.drogasil.com.br/mounjaro-2-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272170.html",
        "Mounjaro 5mg/ml":"https://www.drogasil.com.br/mounjaro-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272173.html" ,
        "Mounjaro 7,5mg/ml":"https://www.drogasil.com.br/mounjaro-7-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272174.html",
        "Mounjaro 10mg/ml":"https://www.drogasil.com.br/mounjaro-10mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272177.html" ,
        "Ritalina 10mg 30 comprimidos":"https://www.drogasil.com.br/ritalina-10-mg-com-30-comprimidos-a3.html",
        "Ritalina 10mg 60 comprimidos":"Ritalina Cloridrato de Metilfenidato 10mg 60 comprimidos",
        "Ritalina LA 10mg/ml":"https://www.drogasil.com.br/ritalina-la-10mg-com-30-capsulas-a3.html",
        "Ritalina LA 30mg/ml":"https://www.drogasil.com.br/ritalina-30mg-acao-prolongada-30-capsulas-gelatinosas-a3.html",
        "Ritalina LA 40mg/ml":"https://www.drogasil.com.br/ritalina-40mg-acao-prolongada-30-capsulas-gelatinosa-a3.html",
        "Ritalina LA 20mg/ml":"https://www.drogasil.com.br/ritalina-la-20mg-acao-prolongada-30-capsulas-gelatinosa-a3.html"
    }
    
    url_drogasil = "https://www.drogasil.com.br/api/next/product-hub/graphql"

    product_description = {}

    # 2. Uso chave_produto aqui
    if chave_produto not in d_para:
        return None

    json_price = {
        "operationName": "PriceBySku",
        "variables": {
            "sku": d_para[chave_produto]
        },
        "query": "query PriceBySku($sku: String!) {\n  priceBySku(sku: $sku) {\n    sku\n    isInStock\n    domains {\n      price {\n        rangeId\n        value\n        discountTypeId\n        inHierarchy\n        __typename\n      }\n      __typename\n    }\n    bestPriceHierarchy {\n      hierarchy\n      discount {\n        type\n        percent\n        value\n        domain\n        __typename\n      }\n      value\n      description\n      discountTypeId\n      installments {\n        installment\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
    }

    # Mantive o seu payload exato (com string "3")
    json_freight={
        "operationName":"GET_STOCK",
        "variables":{
            "zipcode":cep.replace("-",""),
            "products":[
                {
                    "sku":d_para[chave_produto],
                    "quantity":1
                }
            ],
            "logotype":"RD",
            "maxQuantityBranchSearch":"3"},
        "query":"query GET_STOCK($zipcode: String!, $products: [StockNearbyBtZipCodeTypeInput!]!, $logotype: String!, $maxQuantityBranchSearch: String) {\n  getNearbyStockByZipCode(\n    products: $products\n    zipcode: $zipcode\n    logotype: $logotype\n    maxQuantityBranchSearch: $maxQuantityBranchSearch\n  ) {\n    branch {\n      id\n      businessName\n      flag24hours\n      distanceKMFromSearch\n      address {\n        district\n        addressLocal\n        addressNumber\n        city\n        sgState\n        __typename\n      }\n      branchService {\n        hourOpenNormaly\n        hourEndNormaly\n        __typename\n      }\n      logoType {\n        id\n        description\n        __typename\n      }\n      __typename\n    }\n    stocks {\n      sku\n      quantity\n      __typename\n    }\n    __typename\n  }\n}"
    }

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }

    try:
        resp_price = httpx.post(url_drogasil, json=json_price, headers=headers).json()

        # Melhor valor pos desconto
        data_price = resp_price.get("data", {}).get("priceBySku", {})
        if not data_price:
            return None

        standard_price = float(data_price["domains"]["price"]["value"])
        
        if data_price.get("bestPriceHierarchy"):
            best_price = float(data_price["bestPriceHierarchy"][0]["value"])
        else:
            best_price = standard_price

        percentage_price = ((standard_price - best_price) / standard_price) * 100

        product_description["melhor_preco"] = best_price
        product_description["preco_padrao"] = standard_price
        product_description["porcentagem_diferenca"] = percentage_price

        resp_freight = httpx.post(url_drogasil, json=json_freight, headers=headers).json()
        
        data_freight = resp_freight.get("data")

        if data_freight and data_freight.get("getNearbyStockByZipCode"):
            for descriptions in data_freight["getNearbyStockByZipCode"]:
                # Pequena proteção no stocks[0] pra não quebrar se vier lista vazia
                stocks = descriptions.get("stocks", [])
                if stocks and stocks[0].get("quantity", 0) > 0:
                    product_description["estoque"] = int(stocks[0]["quantity"])
                    product_description["disponibilidade"] = dict(descriptions["branch"]["address"])
                    product_description["loja"] = "Drogasil"
                    
                    # 3. AQUI ERA O ERRO: Usei chave_produto (com strip) para pegar o link
                    product_description["url"] = d_para_link.get(chave_produto, "")
                    return product_description
    except Exception as e:
        print(f"Erro Drogasil: {e}")
        return None
    
    return None

print(check_drogasil("29161-716","Mounjaro 5mg/ml"))