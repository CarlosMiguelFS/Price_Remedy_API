from crawler_settings import Crawler

def check_pague_menos(cep):

    id_produto = "52148"
    url_frete = "https://www.paguemenos.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=23424e23-86bb-4397-98b0-238d88d7f528&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2247eca1b9511ec8c41338860ff3532e6cbd7d5a8f3f4a375fab2f8eea2add3d6f%22%2C%22sender%22%3A%22paguemenos.store-theme%407.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"

    endereco = Crawler.requests_pattern_freight(cep, id_produto, url_frete,"PAGUE_MENOS")

    if endereco:
        return {"loja": "Pague Menos", "disponibilidade": endereco}

    return None

