from crawler_settings import Crawler
import httpx

def check_santa_lucia(cep,produto):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    d_para ={
    "Ritalina LA 10mg/ml":"1014105",
    "Ritalina LA 20mg/ml":"998986",
    "Ritalina LA 30mg/ml":"998987",
    "Ritalina LA 40mg/ml":"999053",
    "Ritalina 10mg 60 comprimidos":"1004949",
    "Ritalina 10mg 30 comprimidos":"1022832",
    "Mounjaro 5mg/ml":"1075336",
    # Top 15 mais vendidos (markdown - estimativa)
    "Losartana 50mg": "1033234",
    "Dipirona 500mg": "999948",
    "Glifage XR 500mg": "1001618",
    "Neosoro": "222097",
    "Tadalafila 5mg": "1057267",
    "Nimesulida 100mg": "1059884",
    "Simeticona 75mg/ml": "1040799",
    "Omeprazol 20mg": "1000550",
    "Paracetamol 750mg": "1038709",
    "Hidroclorotiazida 25mg": "1026483",
    "Buscopan Composto": "1073539",
    "Dorflex": "1026748",
    "Microvlar": "1054696",
    "Addera D3": "1057455",
    "Ciclo 21": "1005123",
    }
    d_para_link = {
        "Ritalina LA 10mg/ml":"https://www.santaluciadrogarias.com.br/ritalina-la-10mg-30-caps-----a---pbm/p",
        "Ritalina LA 20mg/ml":"https://www.santaluciadrogarias.com.br/ritalina-la-20mg-30-caps----b---pbm/p",
        "Ritalina LA 30mg/ml":"https://www.santaluciadrogarias.com.br/ritalina-la-30mg-30-caps----b---pbm/p",
        "Ritalina LA 40mg/ml":"https://www.santaluciadrogarias.com.br/ritalina-la-40mg-30-caps---b---pbm/p",
        "Ritalina 10mg 60 comprimidos":"https://www.santaluciadrogarias.com.br/ritalina-10mg-60-cprs----b/p",
        "Ritalina 10mg 30 comprimidos":"https://www.santaluciadrogarias.com.br/ritalina-10mg-30-cprs---b/p",
        "Mounjaro 5mg/ml":"https://www.santaluciadrogarias.com.br/mounjaro-5mg-sol-inj/p",
        # Top 15 mais vendidos (markdown - estimativa)
        "Losartana 50mg": "https://www.santaluciadrogarias.com.br/losart-potassica-50mg-30-cprs---teu-g-/p",
        "Dipirona 500mg": "https://www.santaluciadrogarias.com.br/dipirona-sod-500mg-10ml---med-g-/p",
        "Glifage XR 500mg": "https://www.santaluciadrogarias.com.br/glifage-xr-500mg-30-cprs/p",
        "Neosoro": "https://www.santaluciadrogarias.com.br/neosoro-sol-adulto-30ml-neo/p",
        "Tadalafila 5mg": "https://www.santaluciadrogarias.com.br/tadalafila-5mg-30-cprs---cimed-g-/p",
        "Nimesulida 100mg": "https://www.santaluciadrogarias.com.br/nimesulida-100mg-12-cprs---cimed--g-/p",
        "Simeticona 75mg/ml": "https://www.santaluciadrogarias.com.br/luftal-gts-30ml/p",
        "Omeprazol 20mg": "https://www.santaluciadrogarias.com.br/omeprazol-20mg-28-caps---teu-g-----/p",
        "Paracetamol 750mg": "https://www.santaluciadrogarias.com.br/paracetamol-750mg-20-cprs---teu-g---/p",
        "Hidroclorotiazida 25mg": "https://www.santaluciadrogarias.com.br/hidroclorotiazida-25mg-30cprs---teu-g---p---/p",
        "Buscopan Composto": "https://www.santaluciadrogarias.com.br/buscopan-composto-gotas-20ml/p",
        "Dorflex": "https://www.santaluciadrogarias.com.br/dorflex-36-comprimidos/p",
        "Microvlar": "https://www.santaluciadrogarias.com.br/microvlar-bl-3x21-dgrs/p",
        "Addera D3": "https://www.santaluciadrogarias.com.br/addera-d3-50000ui-8-cprs/p",
        "Ciclo 21": "https://www.santaluciadrogarias.com.br/elani-ciclo-21-cprs--/p",
    }

    url_price = f"https://www.santaluciadrogarias.com.br/api/catalog_system/pub/products/search/?fq=productId:{d_para[produto]}"

    resp_price = httpx.get(url_price,headers=headers).json()
    standard_price  = resp_price[0]["items"][0]["sellers"][0]["commertialOffer"]["ListPrice"]
    best_price  = resp_price[0]["items"][0]["sellers"][0]["commertialOffer"]["Price"]
    percentage_price = ((standard_price - best_price) / standard_price) * 100

    url_frete = "https://www.santaluciadrogarias.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=8e5ecc0f-db08-4d40-8109-0310821be695&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2238e749de50c2b8c9afdc1b72a9fa2718058cc63887449f1a0b48303b947e9d4e%22%2C%22sender%22%3A%22santaluciadrogaria.shipping-simulator%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"
    enderecos = Crawler.requests_pattern_freight(cep, d_para[produto], url_frete, "SANTA_LUCIA")

    if enderecos:
        if not isinstance(enderecos, list):
            enderecos = [enderecos]

        resultados = []
        for endereco in enderecos:
            resultados.append({"loja": "Santa Lucia", "disponibilidade": endereco, "url":d_para_link[produto], "melhor_preco" : round(best_price, 2), "preco_padrao":round(standard_price, 2),"porcentagem_diferenca":round(percentage_price, 2)})

        return resultados
    
    return None
