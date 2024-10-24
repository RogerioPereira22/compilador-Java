import sys
# Importação da biblioteca token_map
from token_map import OPERATORS, RESERVED_WORDS, SYMBOLS

# Função para ler o conteúdo de um arquivo
def ler_arquivo(nome_arquivo):
    try:
        # Tenta abrir o arquivo no modo leitura e lê o conteúdo completo
        with open(nome_arquivo, "r") as file:
            return file.read()
    except FileNotFoundError:
        # Caso o arquivo não seja encontrado, lança um erro específico
        raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado.")
    except Exception as e:
        # Trata qualquer outro erro que possa ocorrer durante a leitura do arquivo
        raise Exception(f"Erro ao ler o arquivo: {str(e)}")

# Classe para representar um token
class Token:
    def __init__(self, tipo, lexema, linha, coluna):
        # Inicializa um token com tipo (numérico), lexema, linha e coluna
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        # Representação do token em formato legível
        return f"Token({self.tipo}, '{self.lexema}', Linha: {self.linha}, Coluna: {self.coluna})"

# Função principal do analisador léxico
def lexer(codigo_fonte):
    tokens = []  # Lista que armazenará os tokens encontrados
    linha_atual = 1  # Controle da linha atual
    coluna_atual = 0  # Controle da coluna atual

    indice = 0  # Índice para iterar sobre o código fonte
    while indice < len(codigo_fonte):
        char = codigo_fonte[indice]  # Caractere atual

        # Ignora espaços e novas linhas
        if char.isspace():
            if char == '\n':
                # Incrementa a linha quando encontra uma nova linha
                linha_atual += 1
                coluna_atual = 0
            indice += 1
            coluna_atual += 1
            continue

        # Identifica strings (tratando caracteres de escape)
        if char == '"':
            inicio_indice = indice
            indice += 1
            while indice < len(codigo_fonte):
                # Verifica se o caractere atual é uma aspa dupla que não foi escapada
                if codigo_fonte[indice] == '"' and (indice == 0 or codigo_fonte[indice - 1] != '\\'):
                    indice += 1
                    break
                indice += 1

            # Extrai o lexema da string e cria um token do tipo STRING
            lexema = codigo_fonte[inicio_indice:indice]
            tokens.append(Token(RESERVED_WORDS['string'], lexema, linha_atual, coluna_atual))
            coluna_atual += len(lexema)
            continue

        # Identifica números
        if char.isdigit():
            inicio_indice = indice
            while indice < len(codigo_fonte) and (codigo_fonte[indice].isdigit() or codigo_fonte[indice] == '.'):
                indice += 1
            # Extrai o lexema do número e cria um token do tipo NUMBER
            lexema = codigo_fonte[inicio_indice:indice]
            tokens.append(Token("NUMBER", lexema, linha_atual, coluna_atual))
            coluna_atual += len(lexema)
            continue

        # Identifica identificadores ou palavras reservadas
        if char.isalpha() or char == '_':
            inicio_indice = indice
            while indice < len(codigo_fonte) and (codigo_fonte[indice].isalnum() or codigo_fonte[indice] == '_'):
                indice += 1
            # Verifica se é uma palavra reservada ou um identificador
            lexema = codigo_fonte[inicio_indice:indice]
            tipo_token = RESERVED_WORDS.get(lexema, "IDENTIFICADOR")
            tokens.append(Token(tipo_token, lexema, linha_atual, coluna_atual))
            coluna_atual += len(lexema)
            continue

        # Identificação de operadores multi-caracteres primeiro (antes de símbolos de um caractere)
        for op in sorted(OPERATORS.keys(), key=len, reverse=True):
            if codigo_fonte.startswith(op, indice):
                # Cria um token para o operador multi-caracter
                tokens.append(Token(OPERATORS[op], op, linha_atual, coluna_atual))
                indice += len(op)
                coluna_atual += len(op)
                break
        else:
            # Identifica operadores e símbolos de um único caractere
            if char in SYMBOLS:
                tokens.append(Token(SYMBOLS[char], char, linha_atual, coluna_atual))
                indice += 1
                coluna_atual += 1
                continue

            # Tratamento de erro: Token não reconhecido
            contexto_erro = codigo_fonte[indice:indice+10]  # Mostra até os próximos 10 caracteres
            raise ValueError(f"Token não reconhecido na linha {linha_atual}, coluna {coluna_atual}: '{contexto_erro}'")

    # Retorna a lista de tokens encontrados
    return tokens

# Função principal que executa o analisador léxico
def main(nome_arquivo):
    try:
        # Lê o conteúdo do arquivo de código-fonte
        arquivo = ler_arquivo(nome_arquivo)

        # Executa o analisador léxico
        tokens_encontrados = lexer(arquivo)

        # Cria uma lista de tuplas com as informações dos tokens
        lista_lexica = []
        for token in tokens_encontrados:
            lista_lexica.append((token.tipo, token.lexema, token.linha, token.coluna))
        
        # Retorna a lista léxica final
        return lista_lexica
    except Exception as e:
        # Tratamento de erros gerais
        return str(e)

# Execução do script
if __name__ == "__main__":
    # Verifica se o nome do arquivo foi passado como argumento
    if len(sys.argv) > 1:
        # Executa o analisador léxico no arquivo fornecido
        lista = main(sys.argv[1])
        # Exibe a lista de tokens encontrados ou o erro
        print(lista)
