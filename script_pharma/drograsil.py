import httpx
import random

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.52 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.171 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.76 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.35 Safari/537.36",
]

def check_drogasil(cep, produto):
    chave_produto = produto.strip()

    d_para = {
        "Mounjaro 2,5mg/ml": "1272170",
        "Mounjaro 5mg/ml": "1272173",
        "Mounjaro 7,5mg/ml": "1272174",
        "Mounjaro 10mg/ml": "1272177",
        "Ritalina 10mg 30 comprimidos": "1559",
        "Ritalina 10mg 60 comprimidos": "10675",
        "Ritalina LA 10mg/ml": "37153",
        "Ritalina LA 30mg/ml": "97778",
        "Ritalina LA 40mg/ml": "11613",
        "Ritalina LA 20mg/ml": "31770"
    }

    d_para_link = {
        "Mounjaro 2,5mg/ml": "https://www.drogasil.com.br/mounjaro-2-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272170.html",
        "Mounjaro 5mg/ml": "https://www.drogasil.com.br/mounjaro-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272173.html",
        "Mounjaro 7,5mg/ml": "https://www.drogasil.com.br/mounjaro-7-5mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272174.html",
        "Mounjaro 10mg/ml": "https://www.drogasil.com.br/mounjaro-10mg-solucao-injetavel-0-5ml-4-canetas-aplicadoras-1272177.html",
        "Ritalina 10mg 30 comprimidos": "https://www.drogasil.com.br/ritalina-10-mg-com-30-comprimidos-a3.html",
        "Ritalina 10mg 60 comprimidos": "Ritalina Cloridrato de Metilfenidato 10mg 60 comprimidos",
        "Ritalina LA 10mg/ml": "https://www.drogasil.com.br/ritalina-la-10mg-com-30-capsulas-a3.html",
        "Ritalina LA 30mg/ml": "https://www.drogasil.com.br/ritalina-30mg-acao-prolongada-30-capsulas-gelatinosas-a3.html",
        "Ritalina LA 40mg/ml": "https://www.drogasil.com.br/ritalina-40mg-acao-prolongada-30-capsulas-gelatinosa-a3.html",
        "Ritalina LA 20mg/ml": "https://www.drogasil.com.br/ritalina-la-20mg-acao-prolongada-30-capsulas-gelatinosa-a3.html"
    }

    url_drogasil = "https://www.drogasil.com.br/api/next/product-hub/graphql"

    product_description = {}

    if chave_produto not in d_para:
        return None

    json_price = {
        "operationName": "PriceBySku",
        "variables": {"sku": d_para[chave_produto]},
        "query": "query PriceBySku($sku: String!) { priceBySku(sku: $sku) { sku isInStock domains { price { rangeId value discountTypeId inHierarchy __typename } __typename } bestPriceHierarchy { hierarchy discount { type percent value domain __typename } value description discountTypeId installments { installment value __typename } __typename } __typename } }"
    }

    json_freight = {
        "operationName": "GET_STOCK",
        "variables": {
            "zipcode": cep.replace("-", ""),
            "products": [{"sku": d_para[chave_produto], "quantity": 1}],
            "logotype": "RD",
            "maxQuantityBranchSearch": "3"
        },
        "query": "query GET_STOCK($zipcode: String!, $products: [StockNearbyBtZipCodeTypeInput!]!, $logotype: String!, $maxQuantityBranchSearch: String) { getNearbyStockByZipCode(products: $products zipcode: $zipcode logotype: $logotype maxQuantityBranchSearch: $maxQuantityBranchSearch) { branch { id businessName flag24hours distanceKMFromSearch address { district addressLocal addressNumber city sgState __typename } branchService { hourOpenNormaly hourEndNormaly __typename } logoType { id description __typename } __typename } stocks { sku quantity __typename } __typename } }"
    }

    headers = {"User-Agent": random.choice(user_agent_list)}

    try:
        response_price = httpx.post(url_drogasil, json=json_price, headers=headers)
        if response_price.status_code != 200:
            return None

        data_price = response_price.json().get("data", {}).get("priceBySku")
        if not data_price:
            return None

        standard_price = float(data_price["domains"]["price"]["value"])
        best_price = float(data_price["bestPriceHierarchy"][0]["value"]) if data_price.get("bestPriceHierarchy") else standard_price
        percentage_price = ((standard_price - best_price) / standard_price) * 100

        product_description.update({
            "melhor_preco": best_price,
            "preco_padrao": standard_price,
            "porcentagem_diferenca": percentage_price
        })

        response_freight = httpx.post(url_drogasil, json=json_freight, headers=headers)
        if response_freight.status_code != 200:
            return None

        for item in response_freight.json().get("data", {}).get("getNearbyStockByZipCode", []):
            stocks = item.get("stocks", [])
            if stocks:
                product_description.update({
                    "estoque": int(stocks[0].get("quantity", 0)),
                    "disponibilidade": dict(item["branch"]["address"]),
                    "loja": "Drogasil",
                    "url": d_para_link.get(chave_produto, "")
                })
                return product_description

    except Exception:
        return None

    return None
