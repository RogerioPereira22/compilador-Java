import sys

def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as arquivo:
        return arquivo.readlines()

def ler_tokens(nome_arquivo_tokens):
    with open(nome_arquivo_tokens, 'r') as arquivo_tokens:
        return arquivo_tokens.readlines()


def main(nome_arquivo):
    nome_arquivo_tokens = 'tokens.txt'

    arquivo = ler_arquivo(nome_arquivo)
    lista_tokens = ler_tokens(nome_arquivo_tokens)

    #tokens_encontrados = parser(arquivo, lista_tokens)

    #lista_lexica = []
    #for token_linha, lexima, linha, coluna in tokens_encontrados:
       # lista_lexica.append((token_linha, lexima, linha, coluna))
   # return lista_lexica

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lista = main(sys.argv[1])
        print(lista)