from crawler_settings import Crawler
import httpx

def check_indiana(cep, produto):

    url = "https://www.farmaciaindiana.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ed9f8e86-0d83-4019-8c88-cd107db83d18&operationName=shippingSLA&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22b02dbc4f2e3fe4b2598cc2330652b0acd378ef80ec79c80e7259e30b06653714%22%2C%22sender%22%3A%22farmaciaindiana.store-theme%403.x%22%2C%22provider%22%3A%22vtex.checkout-graphql%400.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"
    url_price = "https://www.farmaciaindiana.com.br/api/checkout/pub/orderForms/simulation"
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 OPR/125.0.0.0"}
    
    d_para = {
        "Mounjaro 2,5mg/ml": "40221",
        "Mounjaro 5mg/ml": "40222",
        "Mounjaro 10mg/ml": "40223",
        "Ritalina 10mg 60 comprimidos":"20489",
        "Ritalina 10mg 30 comprimidos":"79058",
        "Ritalina LA 10mg/ml":"40927",
        "Ritalina LA 40mg/ml":"17170",
        "Ritalina LA 20mg/ml":"17167",
        "Ritalina LA 30mg/ml":"17168"
    }
    d_para_link = {
        "Mounjaro 2,5mg/ml": "https://www.farmaciaindiana.com.br/mounjaro-tirzepatida-2-5mg-ml-0-5ml-injetavel-4-canetas-aplicadoras/p",
        "Mounjaro 5mg/ml": "https://www.farmaciaindiana.com.br/mounjaro-tirzepatida-5mg-ml-0-5ml-injetavel-4-canetas-aplicadoras/p",
        "Mounjaro 10mg/ml": "https://www.farmaciaindiana.com.br/mounjaro-tirzepatida-10mg-ml-0-5ml-injetavel-4-canetas-aplicadoras/p",
        "Ritalina 10mg 60 comprimidos":"https://www.farmaciaindiana.com.br/ritalina-cloridrato-de-metilfenidato-10mg-60-comprimidos/p",
        "Ritalina 10mg 30 comprimidos":"https://www.farmaciaindiana.com.br/ritalina-cloridrato-de-metilfenidato-10mg-30-comprimidos/p",
        "Ritalina LA 10mg/ml":"https://www.farmaciaindiana.com.br/ritalina-la-cloridrato-de-metilfenidato-10mg-30-capsulas/p",
        "Ritalina LA 40mg/ml":"https://www.farmaciaindiana.com.br/ritalina-la-cloridrato-de-metilfenidato-40mg-30-capsulas/p",
        "Ritalina LA 20mg/ml":"https://www.farmaciaindiana.com.br/ritalina-la-cloridrato-de-metilfenidato-20mg-30-capsulas/p",
        "Ritalina LA 30mg/ml":"https://www.farmaciaindiana.com.br/ritalina-la-cloridrato-de-metilfenidato-30mg-30-capsulas/p"
    }

    chave_produto = produto.strip()
    if chave_produto not in d_para:
        return None

    json_price = {"clientProfileData":{"email":""},"items":[{"id":d_para[chave_produto],"quantity":1,"seller":"1"}]}

    try:
        resp_price = httpx.post(url_price, headers=headers, json=json_price).json()
        
        items = resp_price.get("items", [])
        if not items:
            print(f"Indiana: Nenhum item retornado para {chave_produto}")
            return None
            
        best_price = items[0]["price"]
        
        enderecos = Crawler.requests_pattern_freight(cep, d_para[chave_produto], url, "INDIANA")
        if enderecos:
            if not isinstance(enderecos, list):
                enderecos = [enderecos]

            resultados = []
            for endereco in enderecos:
                disponibilidade = endereco.replace("Retire na loja - ", "") if isinstance(endereco, str) else endereco
                resultados.append({
                    "loja": "Indiana",
                    "disponibilidade": disponibilidade,
                    "url": d_para_link.get(chave_produto, ""),
                    "melhor_preco": best_price/100
                })

            return resultados
            
    except Exception as e:
        print(f"Erro interno Indiana: {e}")
        return None
    
    return None
