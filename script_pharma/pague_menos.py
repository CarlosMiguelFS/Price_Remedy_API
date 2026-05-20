def check_pague_menos(cep,produto):
    import httpx

    d_para = {
        "Mounjaro 2,5mg/ml": "166502",
        "Mounjaro 5mg/ml": "166503",
        "Mounjaro 7,5mg/ml": "166507",
        "Mounjaro 10mg/ml": "166506",
        "Ritalina 10mg 60 Comprimidos":"28971",
        "Ritalina 10mg com 30 Comprimidos":"44726",
        "Ritalina LA 10mg/ml":"34493",
        "Ritalina LA 20mg/ml":"24172",
        "Ritalina LA 40mg/ml":"24173",
        "Ritalina LA 30mg/ml":"24174",
        # Top 15 mais vendidos (mesmo perfil de farmacia popular - skus via VTEX)
        "Losartana 50mg": "30558",
        "Dipirona 500mg": "35965",
        "Glifage XR 500mg": "27454",
        "Neosoro": "95239",
        "Tadalafila 5mg": "47378",
        "Nimesulida 100mg": "151277",
        "Simeticona 75mg/ml": "67584",
        "Omeprazol 20mg": "1631989",
        "Paracetamol 750mg": "1631488",
        "Hidroclorotiazida 25mg": "49223",
        "Buscopan Composto": "96576",
        "Dorflex": "1633272",
        "Microvlar": "640",
        "Addera D3": "55599",
        "Ciclo 21": "24304",
    }
    d_para_link = {
        "Mounjaro 2,5mg/ml": "https://www.paguemenos.com.br/mounjaro-2-5mg-com-4-seringas/p",
        "Mounjaro 5mg/ml": "https://www.paguemenos.com.br/mounjaro-5mg-com-4-seringas/p",
        "Mounjaro 7,5mg/ml": "https://www.paguemenos.com.br/mounjaro-7-5mg-com-4-seringas/p",
        "Mounjaro 10mg/ml": "https://www.paguemenos.com.br/mounjaro-10mg-com-4-seringas/p",
        "Ritalina 10mg 60 Comprimidos":"https://www.paguemenos.com.br/ritalina-10mg-comprimidos60-p/p",
        "Ritalina 10mg com 30 Comprimidos":"https://www.paguemenos.com.br/ritalina-10mg-com-30-comprimidos-p-a3/p",
        "Ritalina LA 10mg/ml":"https://www.paguemenos.com.br/ritalina-la-10mg-com-30-comprimidos-p/p",
        "Ritalina LA 20mg/ml":"https://www.paguemenos.com.br/ritalina-la-20mg-comprimidos30-p/p",
        "Ritalina LA 40mg/ml":"https://www.paguemenos.com.br/ritalina-la-40mg-comprimidos30-p/p",
        "Ritalina LA 30mg/ml":"https://www.paguemenos.com.br/ritalina-la-30mg-comprimidos30-p/p",
        # Top 15 mais vendidos
        "Losartana 50mg": "https://www.paguemenos.com.br/losartana-potassica-50mg-com-30-comprimidos-genericos-ems/p",
        "Dipirona 500mg": "https://www.paguemenos.com.br/dipirona-sodica-mais-cafeina-com-16-comprimidos-generico-neo-quimica/p",
        "Glifage XR 500mg": "https://www.paguemenos.com.br/glifage-xr-500mg-com-30-comprimidos/p",
        "Neosoro": "https://www.paguemenos.com.br/neosoro-fluid-0-9porcento-spray-50ml/p",
        "Tadalafila 5mg": "https://www.paguemenos.com.br/tadalafila-5mg-com-30-comprimidos-generico-ems/p",
        "Nimesulida 100mg": "https://www.paguemenos.com.br/nimesulida-100mg-12-comprimidos-globo-generico/p",
        "Simeticona 75mg/ml": "https://www.paguemenos.com.br/simeticona-75mg-gotas-10ml/p",
        "Omeprazol 20mg": "https://www.paguemenos.com.br/omeprazol-20mg-56-capsulas-generico-geolab/p",
        "Paracetamol 750mg": "https://www.paguemenos.com.br/paracetamol-750mg-20-comprimidos/p",
        "Hidroclorotiazida 25mg": "https://www.paguemenos.com.br/hidroclorotiazida-25mg-com-30-comprimidos-generico-medquimica/p",
        "Buscopan Composto": "https://www.paguemenos.com.br/buscopan-composto-envelope-com-4-comprimidos/p",
        "Dorflex": "https://www.paguemenos.com.br/kit-dorflex-max-600mg---70mg---100mg-16-comprimidos---dorflex-uno-1g-20-comprimidos/p",
        "Microvlar": "https://www.paguemenos.com.br/microvlar-envelope-com-21-comprimidos/p",
        "Addera D3": "https://www.paguemenos.com.br/addera-d3-600ui-gotas-5ml/p",
        "Ciclo 21": "https://www.paguemenos.com.br/ciclo-21-cartela-com-21-comprimidos/p",
    }
    url_price = f"https://www.paguemenos.com.br/api/catalog_system/pub/products/search?fq=skuId:{d_para[produto]}"

    resp_price = httpx.get(url_price).json()
    standard_price  = resp_price[0]["items"][0]["sellers"][0]["commertialOffer"]["ListPrice"]
    best_price  = resp_price[0]["items"][0]["sellers"][0]["commertialOffer"]["Price"]

    percentage_price = ((standard_price - best_price) / standard_price) * 100

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
    endereco = httpx.post("https://www.paguemenos.com.br/api/checkout/pub/orderForms/simulation", json=payload, headers=headers).json()
    resultados = []

    for values in endereco.get("pickupPoints",[]):
        if values.get("address"):
            resultados.append({"loja": "Pague Menos", "endereco": dict(values["address"]), "url":d_para_link[produto], "melhor_preco" : round(best_price, 2), "preco_padrao":round(standard_price, 2),"porcentagem_diferenca":round(percentage_price, 2) })

    return resultados or None
