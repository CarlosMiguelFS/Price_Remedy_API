from crawler_settings import Crawler

def check_indiana(cep):

    id_produto = "194265"
    url = "https://www.farmaciaindiana.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=ed9f8e86-0d83-4019-8c88-cd107db83d18&operationName=shippingSLA&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22c640993a126fbc2846552a076a0ef6f02cd841aa5d346affafbea667f06b37ce%22%2C%22sender%22%3A%22farmaciaindiana.store-theme%403.x%22%2C%22provider%22%3A%22vtex.checkout-graphql%400.x%22%7D%2C%22variables%22%3A%22{base64}%3D%22%7D"

    endereco = Crawler.requests_pattern_freight(cep, id_produto, url, "INDIANA")
    if endereco:
        return {"loja": "Indiana", "disponibilidade": endereco.replace("Retire na loja - ", "")}
    
    return None