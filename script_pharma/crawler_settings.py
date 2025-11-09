import requests
import json
import base64
import httpx

class Crawler:
    def request_pattern_price(url):
        import requests
        import json
        from bs4 import BeautifulSoup

        response_prod = requests.get(url).content
        soup = BeautifulSoup(response_prod, "html.parser")
        data_trat = soup.find("script", {"type":"application/ld+json"}).string.replace('<script> type="application/ld+json"',"").replace("</script>", "")
        data = json.loads(data_trat)
    
        return data
    
    def requests_pattern_freight(cep, id_prod, url_trat, pharmacy):
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
        
        payload_decripted = json.dumps({"country":"BRA","postalCode":cep,"items":[{"quantity":"1","id":id_prod,"seller":"1"}]})
        payload_bytes = payload_decripted.encode("utf-8")
        base64_bytes = base64.b64encode(payload_bytes)
        base64_str = base64_bytes.decode("utf-8")

        if "{base64}" not in url_trat:
            raise ValueError("O link precisa ser adicionado a variavel 'Base64' na criptografia")

        url_freight = url_trat.replace("{base64}", base64_str) 
        response_freight = httpx.get(url_freight, headers=headers).json()

        if "SANTA_LUCIA" == pharmacy or "PAGUE_MENOS" == pharmacy:
            slas = response_freight.get("data", {}).get("shipping", {}).get("logisticsInfo", [{}])[0].get("slas", [])
            for frete in slas:
                if frete.get("pickupStoreInfo", {}).get("address"):
                    return frete["pickupStoreInfo"]["address"]
            
        elif "INDIANA" == pharmacy:
            options = response_freight.get("data", {}).get("shippingSLA", {}).get("pickupOptions", [])
            for frete in options:
                if frete.get("id"):
                    return frete["id"]

        return None
        

    def datas(cep, estado, loja, url, sku, produto):
        prod_obj = {
        "cep":cep,
        "estado":estado,
        "loja":loja,
        "link":url,
        "sku":sku,
        "produto":produto,
        }
        return prod_obj