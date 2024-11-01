import sys  # Importa o módulo sys para utilizar sys.exit() e encerrar a execução em caso de erro

# Função para ler o conteúdo de um arquivo
def ler_arquivo(nome_arquivo):
    try:
        # Tenta abrir o arquivo em modo leitura e retorna seu conteúdo completo
        with open(nome_arquivo, "r") as file:
            return file.read()
    except FileNotFoundError:
        # Exibe uma mensagem de erro e interrompe a execução se o arquivo não for encontrado
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        # Exibe uma mensagem de erro genérica e interrompe a execução para outros erros de leitura
        print(f"Erro ao ler o arquivo: {str(e)}")
        sys.exit(1)

# Função para carregar os tokens do arquivo tokens.txt
def ler_tokens(nome_arquivo_tokens):
    try:
        # Inicializa dicionários para operadores, palavras reservadas e símbolos
        operators, reserved_words, symbols = {}, {}, {}
        # Lê o conteúdo do arquivo de tokens linha por linha
        with open(nome_arquivo_tokens, "r") as file:
            content = file.readlines()
        
        current_section = None  # Variável para rastrear a seção atual no arquivo (operadores, palavras reservadas ou símbolos)
        for line in content:
            line = line.strip()  # Remove espaços em branco ao redor da linha
            if not line:
                continue  # Ignora linhas vazias

            # Define a seção atual dependendo do cabeçalho encontrado
            if line.startswith("OPERATORS:"):
                current_section = "operators"
                continue
            elif line.startswith("RESERVED WORDS:"):
                current_section = "reserved_words"
                continue
            elif line.startswith("SYMBOLS:"):
                current_section = "symbols"
                continue
            
            # Divide a linha em símbolo/lexema e seu token correspondente
            parts = line.split(" -> ")
            if len(parts) == 2:
                symbol, token = parts
                # Adiciona o token ao dicionário apropriado de acordo com a seção atual
                if current_section == "operators":
                    operators[symbol] = token
                elif current_section == "reserved_words":
                    reserved_words[symbol] = token
                elif current_section == "symbols":
                    symbols[symbol] = token
        # Retorna os dicionários preenchidos com operadores, palavras reservadas e símbolos
        return operators, reserved_words, symbols
    except FileNotFoundError:
        # Exibe uma mensagem de erro e interrompe a execução se o arquivo de tokens não for encontrado
        print(f"Erro: Arquivo de tokens '{nome_arquivo_tokens}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        # Exibe uma mensagem de erro genérica e interrompe a execução para outros erros ao carregar tokens
        print(f"Erro ao carregar os tokens: {str(e)}")
        sys.exit(1)

# Classe para representar um token
class Token:
    def __init__(self, type, lexeme, line, column):
        # Inicializa um token com tipo, lexema, linha e coluna
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        # Retorna uma representação em string do token para facilitar a leitura
        return f"Token({self.type}, '{self.lexeme}', Line: {self.line}, Column: {self.column})"

# Função principal do analisador léxico
def lexer(source_code, operators, reserved_words, symbols):
    tokens = []  # Lista para armazenar os tokens encontrados
    line_number = 1  # Contador de linha
    column_number = 0  # Contador de coluna
    index = 0  # Índice para percorrer o código fonte
    
    # Laço principal para iterar sobre cada caractere do código fonte
    while index < len(source_code):
        char = source_code[index]  # Caractere atual

        # Ignora espaços e novas linhas
        if char.isspace():
            if char == '\n':  # Se for nova linha, incrementa o contador de linha e reseta a coluna
                line_number += 1
                column_number = 0
            index += 1  # Avança para o próximo caractere
            column_number += 1  # Avança para a próxima coluna
            continue
        
        # Identificação de strings com tratamento para strings mal formadas
        if char == '"':
            start_index = index  # Marca o início da string
            index += 1  # Avança o índice para ignorar a aspa inicial
            # Continua até encontrar o fechamento da string (aspas duplas não escapadas)
            while index < len(source_code) and (source_code[index] != '"' or source_code[index - 1] == '\\'):
                index += 1
            if index < len(source_code):
                # Extrai o lexema e adiciona um token do tipo STRING
                lexeme = source_code[start_index:index + 1]
                tokens.append(Token("STRING", lexeme, line_number, column_number))  # Adiciona o token à lista
                column_number += len(lexeme)  # Atualiza a coluna
                index += 1  # Avança após a aspa de fechamento
            else:
                # Erro se a string não estiver fechada
                print(f"Erro: String não fechada na linha {line_number}, coluna {column_number}")
                sys.exit(1)
            continue

        # Identificação de números com validação detalhada
        if char.isdigit():
            start_index = index  # Marca o início do número
            has_decimal_point = False  # Flag para controlar o ponto decimal em números flutuantes
            # Continua enquanto os caracteres formarem um número válido
            while index < len(source_code) and (source_code[index].isdigit() or (source_code[index] == '.' and not has_decimal_point)):
                if source_code[index] == '.':
                    has_decimal_point = True  # Define a flag para indicar que já há um ponto decimal
                index += 1
            
            lexeme = source_code[start_index:index]  # Extrai o lexema do número

            # Verifica se há caracteres alfabéticos após o número, indicando erro
            if index < len(source_code) and source_code[index].isalpha():
                print(f"Erro: Número inválido '{lexeme + source_code[index]}' na linha {line_number}, coluna {column_number}")
                sys.exit(1)
                continue
            
            # Tenta classificar o número como FLOAT ou INT
            try:
                if '.' in lexeme:
                    float_value = float(lexeme)
                    tokens.append(Token("FLOAT", lexeme, line_number, column_number))  # Adiciona o token à lista
                else:
                    int_value = int(lexeme)
                    tokens.append(Token("INT", lexeme, line_number, column_number))  # Adiciona o token à lista
            except ValueError:
                # Erro se o número é inválido
                print(f"Erro: Número inválido '{lexeme}' na linha {line_number}, coluna {column_number}")
                sys.exit(1)
                
            column_number += len(lexeme)  # Atualiza a coluna
            continue

        # Identificação de identificadores e palavras reservadas
        if char.isalpha() or char == '_':
            start_index = index  # Marca o início do identificador
            # Continua enquanto os caracteres formarem um identificador válido
            while index < len(source_code) and (source_code[index].isalnum() or source_code[index] == '_'):
                index += 1
            lexeme = source_code[start_index:index]  # Extrai o lexema do identificador
            # Verifica se é uma palavra reservada ou variável
            token_type = reserved_words.get(lexeme, "VARIABLE")
            tokens.append(Token(token_type, lexeme, line_number, column_number))  # Adiciona o token à lista
            column_number += len(lexeme)  # Atualiza a coluna
            continue

        # Identificação de operadores e símbolos
        for op in sorted(operators.keys(), key=len, reverse=True):
            # Tenta encontrar operadores de múltiplos caracteres primeiro
            if source_code.startswith(op, index):
                tokens.append(Token(operators[op], op, line_number, column_number))  # Adiciona o token à lista
                index += len(op)  # Avança o índice
                column_number += len(op)  # Atualiza a coluna
                break
        else:
            # Verifica se o caractere é um símbolo
            if char in symbols:
                tokens.append(Token(symbols[char], char, line_number, column_number))  # Adiciona o token à lista
                index += 1  # Avança o índice
                column_number += 1  # Atualiza a coluna
            else:
                # Erro se o token não é reconhecido
                print(f"Erro: Token não reconhecido '{char}' na linha {line_number}, coluna {column_number}")
                sys.exit(1)
            continue
    
    # Retorna a lista de tokens encontrados
    return tokens

# Função principal que executa o analisador léxico
def main(nome_arquivo):
    nome_arquivo_tokens = 'tokens.txt'  # Nome do arquivo com os tokens
    
    try:
        # Lê o conteúdo do arquivo de código-fonte
        arquivo = ler_arquivo(nome_arquivo)
        # Carrega operadores, palavras reservadas e símbolos do arquivo tokens.txt
        operators, reserved_words, symbols = ler_tokens(nome_arquivo_tokens)
        # Executa o analisador léxico e armazena os tokens encontrados
        tokens_encontrados = lexer(arquivo, operators, reserved_words, symbols)
        # Exibe cada token encontrado
        for token in tokens_encontrados:
            print(token)
    except Exception as e:
        # Exibe erro genérico e interrompe a execução em caso de erro inesperado
        print(f"Erro inesperado: {e}")
        sys.exit(1)

# Executa o script se o arquivo for passado como argumento
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        
        # Exibe uma mensagem se nenhum argumento foi passado
        print("Erro: Nenhum arquivo foi especificado. Por favor, forneça o nome do arquivo.")
        sys.exit(1)
