import sys
# Função para leitura do conteúdo do arquivo
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
        operators, reserved_words, symbols = {}, {}, {}
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

class Token:
    def __init__(self, type, lexeme, line, column):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', Line: {self.line}, Column: {self.column})"

def lexer(source_code, operators, reserved_words, symbols):
    tokens = []
    line_number = 1
    column_number = 0
    index = 0
    
    while index < len(source_code):
        char = source_code[index]
        if char.isspace():
            if char == '\n':
                line_number += 1
                column_number = 0
            index += 1
            column_number += 1
            continue
        
        # Identificação de strings com tratamento para strings mal formadas
        if char == '"':
            start_index = index
            index += 1
            while index < len(source_code) and (source_code[index] != '"' or source_code[index - 1] == '\\'):
                index += 1
            if index < len(source_code):
                lexeme = source_code[start_index:index + 1]
                tokens.append(Token("STRING", lexeme, line_number, column_number))
                column_number += len(lexeme)
                index += 1
            else:
                print(f"Erro: String não fechada na linha {line_number}, coluna {column_number}")
                break
            continue

        # Identificação de números com validação detalhada
        if char.isdigit():
            start_index = index
            while index < len(source_code) and (source_code[index].isdigit() or source_code[index] in ['.', 'x', 'o']):
                index += 1
            lexeme = source_code[start_index:index]
            try:
                int_value = int(lexeme)
                tokens.append(Token("INT", lexeme, line_number, column_number))
            except ValueError:
                try:
                    float_value = float(lexeme)
                    tokens.append(Token("FLOAT", lexeme, line_number, column_number))
                except ValueError:
                    if lexeme.startswith("0x") and all(c in '0123456789abcdefABCDEF' for c in lexeme[2:]):
                        tokens.append(Token("HEX", lexeme, line_number, column_number))
                    elif lexeme.startswith("0o") and all(c in '01234567' for c in lexeme[2:]):
                        tokens.append(Token("OCT", lexeme, line_number, column_number))
                    else:
                        print(f"Erro: Número inválido '{lexeme}' na linha {line_number}, coluna {column_number}")
            column_number += len(lexeme)
            continue

        # Identificação de identificadores e palavras reservadas
        if char.isalpha() or char == '_':
            start_index = index
            while index < len(source_code) and (source_code[index].isalnum() or source_code[index] == '_'):
                index += 1
            lexeme = source_code[start_index:index]
            token_type = reserved_words.get(lexeme, "VARIABLE")
            tokens.append(Token(token_type, lexeme, line_number, column_number))
            column_number += len(lexeme)
            continue

        # Identificação de operadores e símbolos
        for op in sorted(operators.keys(), key=len, reverse=True):
            if source_code.startswith(op, index):
                tokens.append(Token(operators[op], op, line_number, column_number))
                index += len(op)
                column_number += len(op)
                break
        else:
            if char in symbols:
                tokens.append(Token(symbols[char], char, line_number, column_number))
                index += 1
                column_number += 1
            else:
                print(f"Erro: Token não reconhecido '{char}' na linha {line_number}, coluna {column_number}")
                index += 1
            continue
    
    return tokens

# Função principal que executa o analisador léxico
def main(nome_arquivo):
    nome_arquivo_tokens = 'tokens.txt'
    
    try:
        arquivo = ler_arquivo(nome_arquivo)
        operators, reserved_words, symbols = ler_tokens(nome_arquivo_tokens)
        tokens_encontrados = lexer(arquivo, operators, reserved_words, symbols)
        for token in tokens_encontrados:
            print(token)
    except Exception as e:
        print(e)

# Execução do script
if __name__ == "__main__":
    # Verifica se o nome do arquivo foi passado como argumento
    if len(sys.argv) > 1:
        # Executa o analisador léxico no arquivo fornecido
        lista = main(sys.argv[1])
        # Exibe a lista de tokens encontrados ou o erro
        print(lista)