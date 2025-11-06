# import requests
# from crawler_settings import Crawler

# url = "https://www.farmaciaindiana.com.br/_v/pbm?skuId=194265&pbm=interplayers"
# cep = "29161716"
# # id= "194265"
# id = "20489"
# headers = {
#     "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

# }
# resp = requests.get(url,headers=headers).json()
# for price in resp:
#     print(price["listPrice"])
    
# url = "https://www.farmaciaindiana.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ed9f8e86-0d83-4019-8c88-cd107db83d18&operationName=shippingSLA&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%228bf9eed38f3a3d001bd7284540d600a39d1382e7f311503fd488d2604d88b639%22%2C%22sender%22%3A%22farmaciaindiana.store-theme%403.x%22%2C%22provider%22%3A%22vtex.checkout-graphql%400.x%22%7D%2C%22variables%22%3A%22{base64}%3D%3D%22%7D"

# frete  = Crawler.requests_pattern_freight(cep,id,url,"INDIANA")
# print(frete)
import requests
from crawler_settings import Crawler

def check_indiana(cep):

    id_produto = "194265"
    url = "https://www.farmaciaindiana.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ed9f8e86-0d83-4019-8c88-cd107db83d18&operationName=shippingSLA&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22c640993a126fbc2846552a076a0ef6f02cd841aa5d346affafbea667f06b37ce%22%2C%22sender%22%3A%22farmaciaindiana.store-theme%403.x%22%2C%22provider%22%3A%22vtex.checkout-graphql%400.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"

    endereco = Crawler.requests_pattern_freight(cep, id_produto, url, "INDIANA")
    if endereco:
        return {"loja": "Indiana", "disponibilidade": endereco.replace("Retire na loja - ", "")}
    
    return None