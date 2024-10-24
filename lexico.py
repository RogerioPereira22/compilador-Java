import sys

# Função para ler o conteúdo de um arquivo
def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado.")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo: {str(e)}")

# Função para carregar os tokens do arquivo tokens.txt
def ler_tokens(nome_arquivo_tokens):
    try:
        operators = {}
        reserved_words = {}
        symbols = {}
        
        with open(nome_arquivo_tokens, "r") as file:
            content = file.readlines()
        
        current_section = None
        
        for line in content:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("OPERATORS:"):
                current_section = "operators"
                continue
            elif line.startswith("RESERVED WORDS:"):
                current_section = "reserved_words"
                continue
            elif line.startswith("SYMBOLS:"):
                current_section = "symbols"
                continue
            
            # Dividindo o símbolo/lexema e seu respectivo token
            parts = line.split(" -> ")
            if len(parts) == 2:
                symbol, token = parts
                if current_section == "operators":
                    operators[symbol] = token
                elif current_section == "reserved_words":
                    reserved_words[symbol] = token
                elif current_section == "symbols":
                    symbols[symbol] = token
        
        return operators, reserved_words, symbols
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de tokens '{nome_arquivo_tokens}' não encontrado.")
    except Exception as e:
        raise Exception(f"Erro ao carregar os tokens: {str(e)}")

# Classe para representar um token
class Token:
    def __init__(self, type, lexeme, line, column):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', Line: {self.line}, Column: {self.column})"

# Função do analisador léxico atualizado para lidar com strings e caracteres de escape
def lexer(source_code, operators, reserved_words, symbols):
    tokens = []
    line_number = 1
    column_number = 0

    index = 0
    while index < len(source_code):
        char = source_code[index]

        # Ignora espaços e novas linhas
        if char.isspace():
            if char == '\n':
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
                if source_code[index] == '"' and source_code[index - 1] != '\\':
                    index += 1
                    break
                index += 1

            lexeme = source_code[start_index:index]
            tokens.append(Token("STRING", lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue

        # Identifica números
        if char.isdigit():
            start_index = index
            while index < len(source_code) and (source_code[index].isdigit() or source_code[index] == '.'):
                index += 1
            lexeme = source_code[start_index:index]
            tokens.append(Token("NUMBER", lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue

        # Identifica identificadores ou palavras reservadas
        if char.isalpha() or char == '_':
            start_index = index
            while index < len(source_code) and (source_code[index].isalnum() or source_code[index] == '_'):
                index += 1
            lexeme = source_code[start_index:index]
            token_type = reserved_words.get(lexeme, "IDENTIFIER")
            tokens.append(Token(token_type, lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue

        # Identifica operadores e símbolos
        if char in symbols:
            tokens.append(Token(symbols[char], char, line_number, column_number))
            index += 1
            column_number += 1
            continue

        # Identificação de operadores multi-caracteres
        for op in sorted(operators.keys(), key=len, reverse=True):
            if source_code.startswith(op, index):
                tokens.append(Token(operators[op], op, line_number, column_number))
                index += len(op)
                column_number += len(op)
                break
        else:
            # Tratamento de erro: Token não reconhecido
            error_context = source_code[index:index+10]  # Mostra até os próximos 10 caracteres
            raise ValueError(f"Token não reconhecido na linha {line_number}, coluna {column_number}: '{error_context}'")

    return tokens


# Função principal
def main(nome_arquivo):
    nome_arquivo_tokens = 'tokens.txt'
    
    try:
        arquivo = ler_arquivo(nome_arquivo)
        operators, reserved_words, symbols = ler_tokens(nome_arquivo_tokens)

        # Analisador léxico usando o conteúdo do arquivo e os tokens carregados
        tokens_encontrados = lexer(arquivo, operators, reserved_words, symbols)

        # Criação da lista léxica em formato de tuplas
        lista_lexica = []
        for token in tokens_encontrados:
            lista_lexica.append((token.type, token.lexeme, token.line, token.column))
        
        return lista_lexica
    except Exception as e:
        # Tratamento de erros gerais
        return str(e)

# Execução do script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        lista = main(sys.argv[1])
        print(lista)
