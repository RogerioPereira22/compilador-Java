import sys

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

# Função para carregar os tokens do arquivo tokens.txt
def ler_tokens(nome_arquivo_tokens):
    try:
        # Inicializa dicionários para operadores, palavras reservadas e símbolos
        operators = {}
        reserved_words = {}
        symbols = {}
        
        # Lê o conteúdo do arquivo tokens.txt linha por linha
        with open(nome_arquivo_tokens, "r") as file:
            content = file.readlines()
        
        # Variável para controlar a seção atual (OPERATORS, RESERVED WORDS ou SYMBOLS)
        current_section = None
        
        # Processa cada linha do arquivo
        for line in content:
            line = line.strip()  # Remove espaços em branco ao redor
            if not line:
                continue  # Ignora linhas vazias
            
            # Identifica se a linha indica o início de uma nova seção
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
                # Adiciona o token ao dicionário correspondente
                if current_section == "operators":
                    operators[symbol] = token
                elif current_section == "reserved_words":
                    reserved_words[symbol] = token
                elif current_section == "symbols":
                    symbols[symbol] = token
        
        # Retorna os dicionários preenchidos
        return operators, reserved_words, symbols
    except FileNotFoundError:
        # Caso o arquivo de tokens não seja encontrado, lança um erro específico
        raise FileNotFoundError(f"Arquivo de tokens '{nome_arquivo_tokens}' não encontrado.")
    except Exception as e:
        # Trata qualquer outro erro que possa ocorrer durante a leitura do arquivo de tokens
        raise Exception(f"Erro ao carregar os tokens: {str(e)}")

# Classe para representar um token
class Token:
    def __init__(self, type, lexeme, line, column):
        # Inicializa um token com tipo, lexema, linha e coluna
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        # Representação do token em formato legível
        return f"Token({self.type}, '{self.lexeme}', Line: {self.line}, Column: {self.column})"

# Função principal do analisador léxico
def lexer(source_code, operators, reserved_words, symbols):
    tokens = []  # Lista que armazenará os tokens encontrados
    line_number = 1  # Controle da linha atual
    column_number = 0  # Controle da coluna atual

    index = 0  # Índice para iterar sobre o código fonte
    while index < len(source_code):
        char = source_code[index]  # Caractere atual

        # Ignora espaços e novas linhas
        if char.isspace():
            if char == '\n':
                # Incrementa a linha quando encontra uma nova linha
                line_number += 1
                column_number = 0
            index += 1
            column_number += 1
            continue   
        # Identifica strings (tratando caracteres de escape)
        if char == '"':
            start_index = index
            index += 1
            while index < len(source_code):
                # Verifica se o caractere atual é uma aspa dupla que não foi escapada
                if source_code[index] == '"' and (index == 0 or source_code[index - 1] != '\\'):
                    index += 1
                    break
                index += 1

            # Extrai o lexema da string e cria um token do tipo STRING
            lexeme = source_code[start_index:index]
            tokens.append(Token("STRING", lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue
        
        # Identifica números
        if char.isdigit():
            start_index = index
            while index < len(source_code) and (source_code[index].isdigit() or source_code[index] == '.' or source_code[index]== "x"):
                index += 1
            # Extrai o lexema do número e cria um token do tipo NUMBER
            
            # Extrai o lexema do número e cria um token do tipo NUMBER
            lexeme = source_code[start_index:index]
            print(f"este é lexema: {lexeme}")

            # Verifica se lexeme é int, float, hex ou oct usando lógica
            try:
                # Tenta converter para int
                int_value = int(lexeme)
                tokens.append(Token("INT", lexeme, line_number, column_number))
                column_number += len(lexeme)
            except ValueError:
                try:
                    # Tenta converter para float
                    float_value = float(lexeme)
                    tokens.append(Token("FLOAT", lexeme, line_number, column_number))
                    column_number += len(lexeme)
                except ValueError:
                    if lexeme.startswith("0x"):
                        # Verifica se é hexadecimal
                        try:
                            int(lexeme, 16)
                            tokens.append(Token("HEX", lexeme, line_number, column_number))
                            column_number += len(lexeme)
                        except ValueError:
                            print(f"This number not valid line:{line_number} column:{column_number}")
                            exit()
                    elif lexeme.startswith("0o"):
                        # Verifica se é octal
                        try:
                            int(lexeme, 8)
                            tokens.append(Token("OCT", lexeme, line_number, column_number))
                            column_number += len(lexeme)
                        except ValueError:
                            print(f"This number not valid line:{line_number} column:{column_number}")
                            exit()
                    else:
                        print(f"This number not valid line:{line_number} column:{column_number} {lexeme}")
                        exit()

        # Identifica identificadores ou palavras reservadas
        if char.isalpha() or char == '_':
            start_index = index
            while index < len(source_code) and (source_code[index].isalnum() or source_code[index] == '_'):
                index += 1
            # Verifica se é uma palavra reservada ou um identificador
            lexeme = source_code[start_index:index]
            token_type = reserved_words.get(lexeme, "VARIABLE")
            tokens.append(Token(token_type, lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue

        # Identificação de operadores multi-caracteres primeiro (antes de símbolos de um caractere)
        for op in sorted(operators.keys(), key=len, reverse=True):
            if source_code.startswith(op, index):
                # Cria um token para o operador multi-caracter
                tokens.append(Token(operators[op], op, line_number, column_number))
                index += len(op)
                column_number += len(op)
                break
        else:
            # Identifica operadores e símbolos de um único caractere
            if char in symbols:
                tokens.append(Token(symbols[char], char, line_number, column_number))
                index += 1
                column_number += 1
                continue

            # Tratamento de erro: Token não reconhecido
            error_context = source_code[index:index+10]  # Mostra até os próximos 10 caracteres
            #raise ValueError(f"Token não reconhecido na linha {line_number}, coluna {column_number}: '{error_context}'")

    # Retorna a lista de tokens encontrados
    return tokens

# Função principal que executa o analisador léxico
def main(nome_arquivo):
    nome_arquivo_tokens = 'tokens.txt'
    
    try:
        # Lê o conteúdo do arquivo de código-fonte
        arquivo = ler_arquivo(nome_arquivo)
        # Carrega os operadores, palavras reservadas e símbolos do arquivo tokens.txt
        operators, reserved_words, symbols = ler_tokens(nome_arquivo_tokens)

        # Executa o analisador léxico
        tokens_encontrados = lexer(arquivo, operators, reserved_words, symbols)

        # Cria uma lista de tuplas com as informações dos tokens
        lista_lexica = []
        for token in tokens_encontrados:
            lista_lexica.append((token.type, token.lexeme, token.line, token.column))
        
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