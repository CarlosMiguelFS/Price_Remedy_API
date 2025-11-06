import requests

def check_drogasil(cep):
    
    sku = "1272173"
    url_drogasil = "https://www.drogasil.com.br/api/next/product-hub/graphql"

    product_description = {}

    json_data={
        "operationName":"PriceBySku",
        "variables":{
            "sku":sku
            },
        "query":"query PriceBySku($sku: String!) {\n  priceBySku(sku: $sku) {\n    sku\n    isInStock\n    domains {\n      price {\n        rangeId\n        value\n        discountTypeId\n        inHierarchy\n        __typename\n      }\n      lmpm {\n        simplePercent\n        percent\n        productType {\n          id\n          description\n          productCode\n          __typename\n        }\n        discountValue\n        inHierarchy\n        priceValue\n        percentLimit\n        cuttingAmount\n        markup {\n          id\n          auxDescription\n          description\n          __typename\n        }\n        discountType {\n          id\n          description\n          __typename\n        }\n        groupType {\n          id\n          description\n          __typename\n        }\n        discountTypeId\n        __typename\n      }\n      offer {\n        exclusiveOffers {\n          campaign {\n            actionCode\n            messageCode\n            offerCode\n            offerPoolCode\n            sectionCode\n            actionDescription\n            detailedDescription\n            messageDescription\n            offerDescription\n            __typename\n          }\n          webSectionCode\n          aggregatedCustomCampaignCode\n          lmpmMarkupId\n          discountTypeId\n          promotionalNumber\n          discountPercentage\n          internetDiscountPercentage\n          maximumQuantity\n          minimumQuantity\n          productQuantity\n          discountValue\n          value\n          activeDigital\n          combinedProductCode\n          activationChannel\n          categories {\n            groupCode\n            aggregatedCustomCampaignCode\n            brandCode\n            categoryCode\n            __typename\n          }\n          minimumValue\n          stateAbbreviation\n          inHierarchy\n          __typename\n        }\n        offers {\n          offerId\n          description\n          percent\n          value\n          discountValue\n          rangeId\n          discountTypeId\n          inHierarchy\n          __typename\n        }\n        __typename\n      }\n      card {\n        main {\n          cardId\n          customerGroupId\n          type\n          cardType\n          description\n          percent\n          priceValue\n          discountTypeId\n          inHierarchy\n          __typename\n        }\n        cards {\n          cardId\n          customerGroupId\n          type\n          cardType\n          description\n          percent\n          priceValue\n          discountTypeId\n          inHierarchy\n          __typename\n        }\n        __typename\n      }\n      univers {\n        beneficiaryLegacyId\n        digitalOption\n        cards {\n          cardNumber\n          type\n          __typename\n        }\n        productClassification\n        bestDiscount {\n          typeDiscount\n          percentage\n          value\n          discountValue\n          __typename\n        }\n        discountTypeId\n        inHierarchy\n        __typename\n      }\n      pbm {\n        pbmId\n        group\n        ean\n        doctorData\n        discountTypeId\n        offers {\n          informativeMessage\n          quantity\n          quantityFrom\n          quantityTo\n          operator\n          discountType\n          discountTypeValue\n          discountValue\n          value\n          discount\n          originalValue\n          percent\n          pointing\n          inHierarchy\n          __typename\n        }\n        offerTypes {\n          combo {\n            product {\n              sku\n              name\n              isInStock\n              isGift\n              quantityFrom\n              quantityTo\n              operator\n              discountType\n              discountTypeValue\n              discountPercent\n              discountValue\n              totalPrice\n              __typename\n            }\n            auxiliaryProduct {\n              sku\n              name\n              isInStock\n              isGift\n              quantityFrom\n              quantityTo\n              operator\n              discountType\n              discountTypeValue\n              discountPercent\n              discountValue\n              totalPrice\n              __typename\n            }\n            __typename\n          }\n          lmpm {\n            offers {\n              offerId\n              quantityFrom\n              quantityTo\n              operator\n              discountType\n              discountTypeValue\n              discountPercent\n              discountValue\n              totalPrice\n              point\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      paymentDiscounts {\n        paymentMethodId\n        paymentMethodDescription\n        discountPercent\n        discountPercentCalculated\n        discountValue\n        totalPrice\n        discountTypeId\n        discountType\n        __typename\n      }\n      __typename\n    }\n    bestPriceHierarchy {\n      hierarchy\n      discount {\n        type\n        percent\n        value\n        domain\n        __typename\n      }\n      value\n      description\n      discountTypeId\n      installments {\n        installment\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
    }

    json_freight={
        "operationName":"GET_STOCK",
        "variables":{
            "zipcode":cep.replace("-",""),
            "products":[
                {
                    "sku":sku,
                    "quantity":1
                }
            ],
            "logotype":"RD",
            "maxQuantityBranchSearch":"3"},
        "query":"query GET_STOCK($zipcode: String!, $products: [StockNearbyBtZipCodeTypeInput!]!, $logotype: String!, $maxQuantityBranchSearch: String) {\n  getNearbyStockByZipCode(\n    products: $products\n    zipcode: $zipcode\n    logotype: $logotype\n    maxQuantityBranchSearch: $maxQuantityBranchSearch\n  ) {\n    branch {\n      id\n      businessName\n      flag24hours\n      distanceKMFromSearch\n      address {\n        district\n        addressLocal\n        addressNumber\n        city\n        sgState\n        __typename\n      }\n      branchService {\n        hourOpenNormaly\n        hourEndNormaly\n        __typename\n      }\n      logoType {\n        id\n        description\n        __typename\n      }\n      __typename\n    }\n    stocks {\n      sku\n      quantity\n      __typename\n    }\n    __typename\n  }\n}"
    }

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }

    resp_price = requests.post(url_drogasil, json=json_data, headers=headers).json()
    product_description["price"] = float(resp_price["data"]["priceBySku"]["domains"]["price"]["value"])

    resp_freight = requests.post(url_drogasil, json=json_freight, headers=headers).json()
    
    data_freight = resp_freight.get("data")

    if data_freight and data_freight.get("getNearbyStockByZipCode"):
        for descriptions in data_freight["getNearbyStockByZipCode"]:
            if descriptions.get("stocks") and descriptions["stocks"][0].get("quantity", 0) > 0:
                product_description["estoque"] = int(descriptions["stocks"][0]["quantity"])
                product_description["disponibilidade"] = dict(descriptions["branch"]["address"])
                product_description["loja"] = "Drogasil"
                return product_description
    
    return None