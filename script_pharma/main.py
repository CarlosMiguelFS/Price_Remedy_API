import sys
from drograsil import check_drogasil
from pacheco import check_pacheco
from santa_lucia import check_santa_lucia
from indiana import check_indiana
from pague_menos import check_pague_menos

def normalizar_resultados(resultado):
    if not resultado:
        return []

    if isinstance(resultado, list):
        return [item for item in resultado if item]

    return [resultado]

def main():

    if len(sys.argv) > 1:
        cep = sys.argv[1]
    else:
        cep = input("Digite o CEP (apenas números): ")

    if len(sys.argv) > 2:
        produto = sys.argv[2]
    else:
        produto = "Mounjaro 2,5mg/ml"

    print(f"Buscando {produto} para o CEP: {cep}...\n")
    
    resultados_encontrados = []

    farmacias_checkers = [
        check_drogasil,
        check_pacheco,
        # check_santa_lucia,
        check_indiana,
        check_pague_menos
    ]

    for checar_farmacia in farmacias_checkers:

        resultado = checar_farmacia(cep, produto)
        resultados_encontrados.extend(normalizar_resultados(resultado))


    if not resultados_encontrados:
        print("Produto não encontrado em nenhuma farmácia para este CEP.")
    else:
        print("\n--- Produto disponível nos seguintes locais: ---")
        for res in resultados_encontrados:
            print("-" * 20)
            print(f"Loja: {res.get('loja')}")
            
            # Pega o objeto de endereço, não importa a chave
            endereco = res.get('disponibilidade') or res.get('endereco')
            if not isinstance(endereco, dict):
                print(f"Endereço: {endereco}")
                continue

            if 'addressLocal' in endereco:
                rua = endereco.get('addressLocal', '')
                num = endereco.get('addressNumber', '')
                bairro = endereco.get('district', '')
                cidade = endereco.get('city', '')
                estado = endereco.get('sgState', '')
            
            else:
                rua = endereco.get('street', '')
                num = endereco.get('number', '')
                bairro = endereco.get('neighborhood', '')
                cidade = endereco.get('city', '')
                estado = endereco.get('state', '')

            print(f"Endereço: {rua}, {num}")
            print(f"Bairro: {bairro}")
            print(f"Cidade: {cidade} - {estado}")

if __name__ == "__main__":
    main()
