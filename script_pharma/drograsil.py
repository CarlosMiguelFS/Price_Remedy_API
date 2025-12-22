import requests
import httpx

def check_drogasil(cep, produto):
    
    d_para = {
        "Mounjaro 2,5mg/ml": "1272170",
        "Mounjaro 5mg/ml": "1272173",
        "Mounjaro 7,5mg/ml": "1272174",
        "Mounjaro 10mg/ml": "1272177",
        "Ritalina 10mg 30 comprimidos":"1559",
        "Ritalina 10mg 60 comprimidos":"10675",
        "Ritalina LA 10mg":"37153",
        "Ritalina LA 30mg":"97778",
        "Ritalina LA 40mg":"11613",
        "Ritalina LA 20mg":"31770"
    }

    d_para_link ={
        "Mounjaro 2,5mg/ml":"https://www.drogasil.com.br/mounjaro-2-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272170.html",
        "Mounjaro 5mg/ml":"https://www.drogasil.com.br/mounjaro-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272173.html" ,
        "Mounjaro 7,5mg/ml":"https://www.drogasil.com.br/mounjaro-7-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272174.html",
        "Mounjaro 10mg/ml":"https://www.drogasil.com.br/mounjaro-10mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272177.html" ,
        "Ritalina 10mg 30 comprimidos":"https://www.drogasil.com.br/ritalina-10-mg-com-30-comprimidos-a3.html",
        "Ritalina 10mg 60 comprimidos":"Ritalina Cloridrato de Metilfenidato 10mg 60 comprimidos",
        "Ritalina LA 10mg":"https://www.drogasil.com.br/ritalina-la-10mg-com-30-capsulas-a3.html",
        "Ritalina LA 30mg":"https://www.drogasil.com.br/ritalina-30mg-acao-prolongada-30-capsulas-gelatinosas-a3.html",
        "Ritalina LA 40mg":"https://www.drogasil.com.br/ritalina-40mg-acao-prolongada-30-capsulas-gelatinosa-a3.html",
        "Ritalina LA 20mg":"https://www.drogasil.com.br/ritalina-la-20mg-acao-prolongada-30-capsulas-gelatinosa-a3.html"
    }
    
    url_drogasil = "https://www.drogasil.com.br/api/next/product-hub/graphql"

    product_description = {}

    json_freight={
        "operationName":"GET_STOCK",
        "variables":{
            "zipcode":cep.replace("-",""),
            "products":[
                {
                    "sku":d_para[produto.strip()],
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

    resp_freight = httpx.post(url_drogasil, json=json_freight, headers=headers).json()
    
    data_freight = resp_freight.get("data")

    if data_freight and data_freight.get("getNearbyStockByZipCode"):
        for descriptions in data_freight["getNearbyStockByZipCode"]:
            if descriptions.get("stocks") and descriptions["stocks"][0].get("quantity", 0) > 0:
                product_description["estoque"] = int(descriptions["stocks"][0]["quantity"])
                product_description["disponibilidade"] = dict(descriptions["branch"]["address"])
                product_description["loja"] = "Drogasil"
                product_description["url"] = d_para_link[produto]
                return product_description
    
    return None