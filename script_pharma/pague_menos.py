# import requests
# from crawler_settings import Crawler

# url_pharm = "https://www.paguemenos.com.br/api/catalog_system/pub/products/search?fq=skuId:44726"

# cep ="01010110"
# id = "44726"

# headers = {
#     "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
# }

# resp_frete = requests.get(url_pharm,headers=headers).json()
# for value in resp_frete:   
#     for price in value["items"]:
#         print(price["sellers"][0]["commertialOffer"]["Installments"][0]["Value"])
        

# url_frete = "https://www.paguemenos.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=23424e23-86bb-4397-98b0-238d88d7f528&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2247eca1b9511ec8c41338860ff3532e6cbd7d5a8f3f4a375fab2f8eea2add3d6f%22%2C%22sender%22%3A%22paguemenos.store-theme%407.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"

# frete  = Crawler.requests_pattern_freight(cep,id,url_frete,"PAGUE_MENOS")
# print(frete)
import requests
from crawler_settings import Crawler

def check_pague_menos(cep):

    id_produto = "52148"
    url_frete = "https://www.paguemenos.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=23424e23-86bb-4397-98b0-238d88d7f528&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2247eca1b9511ec8c41338860ff3532e6cbd7d5a8f3f4a375fab2f8eea2add3d6f%22%2C%22sender%22%3A%22paguemenos.store-theme%407.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"

    endereco = Crawler.requests_pattern_freight(cep, id_produto, url_frete,"PAGUE_MENOS")

    if endereco:
        return {"loja": "Pague Menos", "disponibilidade": endereco}

    return None

