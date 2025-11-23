from crawler_settings import Crawler

def check_santa_lucia(cep):
    
    # id_produto = "1022832"
    #Ritalina
    

    url_frete = "https://www.santaluciadrogarias.com.br/_v/segment/graphql/v1?workspace=master&maxAge=medium&appsEtag=remove&domain=store&locale=pt-BR&__bindingId=8e5ecc0f-db08-4d40-8109-0310821be695&operationName=getShippingEstimates&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2238e749de50c2b8c9afdc1b72a9fa2718058cc63887449f1a0b48303b947e9d4e%22%2C%22sender%22%3A%22santaluciadrogaria.shipping-simulator%400.x%22%2C%22provider%22%3A%22vtex.store-graphql%402.x%22%7D%2C%22variables%22%3A%22{base64}%22%7D"      
    
    endereco = Crawler.requests_pattern_freight(cep, id_produto, url_frete, "SANTA_LUCIA")
    
    if endereco:
        return {"loja": "Santa Lucia", "disponibilidade": endereco}
    
    return None