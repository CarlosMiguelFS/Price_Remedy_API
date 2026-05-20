import httpx

def check_pacheco(cep,produto):
    

    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060",
        "Mounjaro 12,5mg/ml":"888079",
        "Mounjaro 15mg/ml":"888087",
        "Ritalina 10mg 30 comprimidos":"518476",
        "Ritalina 10mg 60 comprimidos":"170356",
        "Ritalina LA 10mg/ml":"276162",
        "Ritalina LA 20mg/ml":"118680",
        "Ritalina LA 30mg/ml":"118699",
        "Ritalina LA 40mg/ml":"118702",
        # Top 15 mais vendidos (markdown)
        "Glifage XR 500mg": "155349",
        "Mecobe 1000mcg": "819000",
        "Glyxambi": "681385",
        "Nimesulida 100mg Cimed": "645958",
        "Tadalafila 5mg EMS": "602426",
        "Fluconazol 150mg Cimed": "525529",
        "Rosuvastatina 20mg EMS": "314625",
        "Prednisolona 20mg EMS": "290602",
        "Ibuprofeno 600mg Prati Donaduzzi": "220850",
        "Neosoro": "116408",
        "Aradois 50mg": "74128",
        "Pantoprazol 40mg Medley": "9300",
        "Aerolin": "50822",
        "Wegovy 1mg": "862029",
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
        "Ritalina LA 10mg/ml":"https://www.drogariaspacheco.com.br/ritalina-la-10mg-novatis-30-comprimidos/p",
        "Ritalina LA 20mg/ml":"https://www.drogariaspacheco.com.br/ritalina-la-20mg-novartis-biociencias-30-comprimidos/p",
        "Ritalina LA 30mg/ml":"https://www.drogariaspacheco.com.br/ritalina-la-30mg-novartis-biociencias-30-comprimidos/p",
        "Ritalina LA 40mg/ml":"https://www.drogariaspacheco.com.br/ritalina-la-40mg-novartis-biociencias-30-comprimidos/p",
        # Top 15 mais vendidos (markdown)
        "Glifage XR 500mg": "https://www.drogariaspacheco.com.br/glifage-xr-500mg-merck-sharp-30-comprimidos/p",
        "Mecobe 1000mcg": "https://www.drogariaspacheco.com.br/mecobe-1000mcg-myralis-30-comprimidos-sublinguais/p",
        "Glyxambi": "https://www.drogariaspacheco.com.br/glyxambi-10mg-30-comprimidos-revestidos-boehringer/p",
        "Nimesulida 100mg Cimed": "https://www.drogariaspacheco.com.br/nimesulida-100mg-generico-cimed-12-comprimidos/p",
        "Tadalafila 5mg EMS": "https://www.drogariaspacheco.com.br/tadalafila-5mg-generico-ems-30-comprimidos-revestidos/p",
        "Fluconazol 150mg Cimed": "https://www.drogariaspacheco.com.br/fluconazol-150mg-generico-cimed-2-comprimidos/p",
        "Rosuvastatina 20mg EMS": "https://www.drogariaspacheco.com.br/rosuvastatina-calcica-20mg-generico-30-comprimidos-revestidos/p",
        "Prednisolona 20mg EMS": "https://www.drogariaspacheco.com.br/prednisolona-20mg-generico-ems-10-comprimidos/p",
        "Ibuprofeno 600mg Prati Donaduzzi": "https://www.drogariaspacheco.com.br/ibuprofeno-600mg-generico-prati-donaduzzi-20-comprimidos/p",
        "Neosoro": "https://www.drogariaspacheco.com.br/neosoro-adulto-solucao-nasal-30ml/p",
        "Aradois 50mg": "https://www.drogariaspacheco.com.br/aradois-50mg-biolab-30-comprimidos/p",
        "Pantoprazol 40mg Medley": "https://www.drogariaspacheco.com.br/pantoprazol-generico-40mg-14-comprimidos/p",
        "Aerolin": "https://www.drogariaspacheco.com.br/aerolin-gsk-gotas-10ml/p",
        "Wegovy 1mg": "https://www.drogariaspacheco.com.br/wegovy-1mg-novo-nordisk-4-doses-injetaveis/p",
    }

    url_pharm = "https://www.drogariaspacheco.com.br/api/checkout/pub/orderforms/simulation"
    
    url_price = f"https://www.drogariaspacheco.com.br/api/catalog_system/pub/products/search?fq=skuId:{d_para[produto]}"

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
    resp_price = httpx.get(url_price, headers=headers).json()
    resultados = []

    if resp_frete.get("logisticsInfo"):
        preco_padrao = float(resp_frete["items"][0]["price"]/100)
        melhor_preco = float(str(resp_price[0]["Valor Desconto Minimo"]).replace("['","").replace("']",""))

        for product in resp_frete["logisticsInfo"][0]["slas"]:
            if product.get("pickupStoreInfo", {}).get("address"):
                resultados.append({
                    "endereco": product["pickupStoreInfo"]["address"],
                    "value": preco_padrao,
                    "melhor_preco": melhor_preco,
                    "loja": "Pacheco",
                    "url": d_para_link[produto]
                })
    
    return resultados or None

