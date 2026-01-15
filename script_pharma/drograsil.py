import httpx
from playwright.sync_api import sync_playwright


# =========================
# PLAYWRIGHT → SESSÃO REAL
# =========================
def get_drogasil_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/142.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        page.goto("https://www.drogasil.com.br", timeout=60000)
        page.wait_for_timeout(4000)

        cookies = context.cookies()
        browser.close()

        return {c["name"]: c["value"] for c in cookies}


# =========================
# FUNÇÃO PRINCIPAL
# =========================
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
        "Ritalina 10mg 60 comprimidos": "https://www.drogasil.com.br/ritalina-10-mg-com-60-comprimidos-a3.html",
        "Ritalina LA 10mg/ml": "https://www.drogasil.com.br/ritalina-la-10mg-com-30-capsulas-a3.html",
        "Ritalina LA 30mg/ml": "https://www.drogasil.com.br/ritalina-30mg-acao-prolongada-30-capsulas-gelatinosas-a3.html",
        "Ritalina LA 40mg/ml": "https://www.drogasil.com.br/ritalina-40mg-acao-prolongada-30-capsulas-gelatinosa-a3.html",
        "Ritalina LA 20mg/ml": "https://www.drogasil.com.br/ritalina-la-20mg-acao-prolongada-30-capsulas-gelatinosa-a3.html"
    }

    if chave_produto not in d_para:
        return None

    url_drogasil = "https://www.drogasil.com.br/api/next/product-hub/graphql"

    json_price = {
        "operationName": "PriceBySku",
        "variables": {"sku": d_para[chave_produto]},
        "query": """
        query PriceBySku($sku: String!) {
          priceBySku(sku: $sku) {
            sku
            isInStock
            domains {
              price {
                value
              }
            }
            bestPriceHierarchy {
              value
            }
          }
        }
        """
    }

    json_freight = {
        "operationName": "GET_STOCK",
        "variables": {
            "zipcode": cep.replace("-", ""),
            "products": [{"sku": d_para[chave_produto], "quantity": 1}],
            "logotype": "RD",
            "maxQuantityBranchSearch": "3"
        },
        "query": """
        query GET_STOCK($zipcode: String!, $products: [StockNearbyBtZipCodeTypeInput!]!,
        $logotype: String!, $maxQuantityBranchSearch: String) {
          getNearbyStockByZipCode(
            products: $products
            zipcode: $zipcode
            logotype: $logotype
            maxQuantityBranchSearch: $maxQuantityBranchSearch
          ) {
            branch {
              businessName
              logoType {
                description
              }
              address {
                district
                addressLocal
                addressNumber
                city
                sgState
              }
            }
            stocks {
              quantity
            }
          }
        }
        """
    }

    try:
        cookies = get_drogasil_session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.drogasil.com.br",
            "Referer": "https://www.drogasil.com.br/"
        }

        with httpx.Client(headers=headers, cookies=cookies, timeout=30) as client:
            resp_price = client.post(url_drogasil, json=json_price).json()
            data_price = resp_price.get("data", {}).get("priceBySku")

            if not data_price:
                return None

            standard_price = float(data_price["domains"]["price"]["value"])
            best_price = float(data_price["bestPriceHierarchy"][0]["value"]) \
                if data_price.get("bestPriceHierarchy") else standard_price

            percentage_price = ((standard_price - best_price) / standard_price) * 100

            resp_freight = client.post(url_drogasil, json=json_freight).json()
            data_freight = resp_freight.get("data", {}).get("getNearbyStockByZipCode", [])

            has_drogasil = False
            has_raia = False

            for item_logo in data_freight:
                logo = item_logo["branch"]["logoType"]["description"].upper()
                if logo == "DROGASIL":
                    has_drogasil = True
                elif logo == "RAIA":
                    has_raia = True

            if has_drogasil and has_raia:
                loja_nome = "DROGASIL & RAIA"
            elif has_drogasil:
                loja_nome = "DROGASIL"
            elif has_raia:
                loja_nome = "RAIA"
            else:
                loja_nome = "DESCONHECIDO"

                
            for item in data_freight:
                stocks = item.get("stocks", [])
                if stocks and stocks[0]["quantity"] > 0:
                    return {
                        "melhor_preco": best_price,
                        "preco_padrao": standard_price,
                        "porcentagem_diferenca": percentage_price,
                        "estoque": int(stocks[0]["quantity"]),
                        "disponibilidade": dict(item["branch"]["address"]),
                        "loja": loja_nome,
                        "url": d_para_link.get(chave_produto, "")
                    }

    except Exception as e:
        print(f"Erro Drogasil: {e}")
        return None

    return None

