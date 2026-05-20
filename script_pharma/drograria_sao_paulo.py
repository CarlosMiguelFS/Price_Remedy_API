def check_drogaria_sao_paulo(cep,produto):
    import httpx
    d_para = {
        "Mounjaro 2,5mg/ml": "887528",
        "Mounjaro 5mg/ml": "887455",
        "Mounjaro 7,5mg/ml": "887951",
        "Mounjaro 10mg/ml": "888060",
        # Top 15 mais vendidos (markdown)
        "Tadalafila 5mg EMS": "602426",
        "Glifage XR 500mg": "155349",
        "Wegovy 2,4mg": "862045",
        "Wegovy 0,25mg": "862002",
        "Dipirona 1g Cimed": "841188",
        "Mecobe 1000mcg": "818992",
        "Dipirona 500mg Prati Donaduzzi": "701173",
        "Omeprazol 20mg Cimed": "684333",
        "Glyxambi": "681393",
        "Cetoprofeno 150mg Eurofarma": "668419",
        "Nimesulida 100mg Cimed": "645958",
        "Tadalafila 5mg Eurofarma": "530174",
    }

    d_para_link = {
        "Mounjaro 2,5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-2-5mg-eli-lilly-4-seringa-preenchidas-0-5ml-solucao-injetavel-subcutaneo---4-canetas/p",
        "Mounjaro 5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-5mg-eli-lilly-4-seringa-preenchida-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 7,5mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-7-5mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        "Mounjaro 10mg/ml":"https://www.drogariasaopaulo.com.br/mounjaro-10mg-eli-lilly-4-seringa-0-5ml-solucao-injetavel-subcutaneo-4-canetas/p",
        # Top 15 mais vendidos (markdown)
        "Tadalafila 5mg EMS": "https://www.drogariasaopaulo.com.br/tadalafila-5mg-generico-ems-30-comprimidos-revestidos/p",
        "Glifage XR 500mg": "https://www.drogariasaopaulo.com.br/glifage-xr-500mg-merck-sharp-30-comprimidos/p",
        "Wegovy 2,4mg": "https://www.drogariasaopaulo.com.br/wegovy-2-4mg-novo-nordisk-4-doses-injetaveis/p",
        "Wegovy 0,25mg": "https://www.drogariasaopaulo.com.br/wegovy-25mg-novo-nordisk-4-doses-injetaveis/p",
        "Dipirona 1g Cimed": "https://www.drogariasaopaulo.com.br/dipirona-monoidratada-1g-generico-cimed-10-comprimidos/p",
        "Mecobe 1000mcg": "https://www.drogariasaopaulo.com.br/mecobe-1000mcg-myralis-90-comprimidos-sublinguais/p",
        "Dipirona 500mg Prati Donaduzzi": "https://www.drogariasaopaulo.com.br/dipirona-prati--donaduzzi-500mg-generico-30-comprimidos/p",
        "Omeprazol 20mg Cimed": "https://www.drogariasaopaulo.com.br/omeprazol-20mg-generico-cimed-56-capsulas/p",
        "Glyxambi": "https://www.drogariasaopaulo.com.br/glyxambi-25mg-30-comprimidos-revestidos-boehringer/p",
        "Cetoprofeno 150mg Eurofarma": "https://www.drogariasaopaulo.com.br/cetoprofeno-150mg-10-comprimidos-de-liberacao-prolongada-g-eurofarma-labs/p",
        "Nimesulida 100mg Cimed": "https://www.drogariasaopaulo.com.br/nimesulida-100mg-generico-cimed-12-comprimidos/p",
        "Tadalafila 5mg Eurofarma": "https://www.drogariasaopaulo.com.br/tadalafila-5mg-generico-eurofarma-30-comprimidos/p",
    }

    if produto.strip() not in d_para:
        return None

    payload = {
        "items": [
            {
                "id": d_para[produto.strip()],
                "quantity": 1,
                "seller": "1"
            }
        ],
        "country": "BRA",
        "postalCode": f"{cep}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    try:
        endereco = httpx.post(
            "https://www.drogariasaopaulo.com.br/api/checkout/pub/orderforms/simulation",
            json=payload,
            headers=headers,
            timeout=20,
        ).json()
    except Exception as e:
        print(f"Erro Drogaria SP (rede): {e}")
        return None

    try:
        preco = float(endereco["items"][0]["price"]) / 100
    except (KeyError, IndexError, TypeError, ValueError):
        return None

    resultados = []
    for values in endereco.get("pickupPoints", []):
        if values.get("address"):
            resultados.append({
                "loja": "Drogaria São Paulo",
                "endereco": dict(values["address"]),
                "url": d_para_link.get(produto, ""),
                "melhor_preco": round(preco, 2),
                "preco_padrao": round(preco, 2),
            })

    return resultados or None

