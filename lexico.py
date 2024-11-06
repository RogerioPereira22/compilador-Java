
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

def verificar_notacao_cientifica(numero,line,columm):
    """Verifica se o número está em notação científica válida."""
    if 'e' in numero or 'E' in numero:
        partes = numero.split('e' if 'e' in numero else 'E')
        if len(partes) != 2:
            print(f"Erro: Notação científica incorreta '{numero}' na linha{line} ,coluna{columm}")
            sys.exit(1)
        
        base, expoente = partes[0], partes[1]
        
        if not base.replace('.', '', 1).isdigit() or base.count('.') > 1:
            print(f"Erro: Base inválida na notação científica '{numero}' na linha{line}, coluna{columm}")
            sys.exit(1)

        if expoente[0] in '+-' and expoente[1:].isdigit() or expoente.isdigit():
            return True
        else:
            print(f"Erro: Expoente inválido na notação científica '{numero}'na linha {line} ,coluna {columm}")
            sys.exit(1)
    else:
        return numero.replace('.', '', 1).isdigit()

def verificar_overflow(numero,line, columm):
    """Verifica se o número inteiro está dentro do limite de um int32."""
    try:
        valor = int(float(numero))  # Converte para float, depois para int, em caso de ponto flutuante
        if valor < -2_147_483_648 or valor > 2_147_483_647:
            print(f"Erro: Overflow do número '{numero}' na linha:{line},coluna: {columm}")
            sys.exit(1)
        return True
    except ValueError:
        print(f"Erro: Número inválido '{numero}' na linha: {line},coluna: {columm}")
        sys.exit(1)
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
        match char:
            case '"':
                start_index = index  # Marca o início da string
                
                index += 1  # Avança o índice para ignorar a aspa inicial
                # Continua até encontrar o fechamento da string (aspas duplas não escapadas)
                while index < len(source_code) and (source_code[index] != '"' or source_code[index - 1] == '\\' ):
                    index += 1
                if index < len(source_code):
                    # Extrai o lexema e adiciona um token do tipo STRING
                    lexeme = ""
                    if source_code[index] == '\\' and index + 1 < len(source_code) and (source_code[index + 1] == 'n'):
                        lexeme += '\n'
                        index += 1  # Skip the 'n' character
                    elif source_code[index] == '\\' and index + 1 < len(source_code) and (source_code[index + 1] == 't'):
                        lexeme += '\t'
                        index += 1  # Skip the 'n' character    
                    else:
                        lexeme += source_code[index]
                    lexeme = source_code[start_index:index + 1]
                    tokens.append(Token("STRING", lexeme, line_number, column_number))  # Adiciona o token à lista
                    column_number += len(lexeme)  # Atualiza a coluna
                    index += 1  # Avança após a aspa de fechamento
                else:
                    # Erro se a string não estiver fechada
                    print(f"Erro: String não fechada na linha {line_number}, coluna {column_number}")
                    sys.exit(1)
                continue
            
            case '/':
                 start_index = index  # Marca o início do comentário
                 index += 1  # Avança o índice para ignorar a barra inicial
                
                 if index < len(source_code) and source_code[index] == '/':
                    index += 1  # Avança após o '/'
                    # Continua até encontrar o final da linha
                    while index < len(source_code)-1 and not (source_code[index] == "\n"):
                        index += 1
                    index += 2  # Avança após o fechamento '/n'
                    # Extrai o lexema e adiciona um token do tipo COMMENT
                    lexeme = source_code[start_index:index]
                    #tokens.append(Token("COMMENT", lexeme, line_number, column_number))
                    column_number += len(lexeme)  # Atualiza a coluna
                    
                # Verifica se é um comentário de bloco
                 elif index < len(source_code) and source_code[index] == '*':
                    index += 1  # Avança após o '*'
                    # Continua até encontrar o fechamento do comentário
                    while index < len(source_code) - 1 and not (source_code[index] == '*' and source_code[index + 1] == '/'):
                        index += 1
                    index += 2  # Avança após o fechamento '*/'
                    if index < len(source_code):
                        # Extrai o lexema e adiciona um token do tipo COMMENT
                        lexeme = source_code[start_index:index]
                        #tokens.append(Token("COMMENT", lexeme, line_number, column_number))
                        column_number += len(lexeme)  # Atualiza a coluna
                    else:
                        # Erro se o comentário não estiver fechado
                        print(f"Erro: Comentário não fechado na linha {line_number}, coluna {column_number}")
                        sys.exit(1)
                 continue

        # Identificação de operadores e símbolos
            
        # Identificação de números
       
        # Caso inicie com um dígito ou com o prefixo "0x" indicando um número hexadecimal
        if  char.isdigit() or (char == '0' and index + 1 < len(source_code) and source_code[index + 1].lower() == 'x'):
            start_index = index  # Marca o início do número
            lexeme = ""  # Inicializa a string para acumular o lexema do número

            # Hexadecimal
            if char == '0' and index + 1 < len(source_code) and source_code[index + 1].lower() == 'x':
                lexeme += "0x"
                index += 2  # Avança o índice após "0x"
                
                # Loop para acumular os dígitos e letras válidas em hexadecimal (0-9 e a-f)
                while index < len(source_code) and (source_code[index].isdigit() or source_code[index] in "ABCDEFG.") and not(source_code[index] in "-+={}(),!@#$%¨&*:;/<>|"):
                    if source_code[index] == '.':
                        # Erro: ponto decimal encontrado em hexadecimal
                        print(f"Erro: Ponto decimal não permitido em número hexadecimal '{lexeme + source_code[index]}' na linha {line_number}, coluna {column_number}")
                        sys.exit(1)
                    if source_code[index].isalpha() and source_code[index] not in "ABCDEFG":
                        # Erro: letra inválida fora do intervalo a-f
                        print(f"Erro: Número hexadecimal inválido '{lexeme + source_code[index]}' na linha {line_number}, coluna {column_number}")
                        sys.exit(1)
                    lexeme += source_code[index]  # Adiciona o caractere ao lexema
                    index += 1
                
                # Verificação final para garantir que haja conteúdo válido após "0x"
                if len(lexeme) > 2:
                    tokens.append(Token("HEXADECIMAL_INT", lexeme, line_number, column_number))
                else:
                    print(f"Erro: Número hexadecimal inválido '{lexeme}' na linha {line_number}, coluna {column_number}")
                    sys.exit(1)
                
                column_number += len(lexeme)
                if index < len(source_code) and source_code[index].isalnum():
                    print(f"Erro: Caractere inválido '{source_code[index]}' em número hexadecimal na linha {line_number}, coluna {column_number}")
                    sys.exit(1)
                continue

            # Octal
            elif char == '0' and index + 1 < len(source_code) and source_code[index + 1] in "01234567":
                lexeme += "0"
                index += 1
                
                # Loop para acumular os dígitos válidos em octal (0-7)
                while index < len(source_code) and source_code[index] in "01234567." and not(source_code[index] in "-+={}(),!@#$%¨&*:;/<>|"):
                    if source_code[index] == '.':
                        # Erro: ponto decimal encontrado em octal
                        print(f"Erro: Ponto decimal não permitido em número octal '{lexeme + source_code[index]}' na linha {line_number}, coluna {column_number}")
                        sys.exit(1)
                    lexeme += source_code[index]  # Adiciona o dígito ao lexema
                    index += 1
                
                tokens.append(Token("OCTAL_INT", lexeme, line_number, column_number))
                column_number += len(lexeme)
                # Verificação de caracteres fora do conjunto octal (0-7)
                if index < len(source_code) and source_code[index].isdigit():
                    print(f"Erro: Caractere inválido '{source_code[index]}' em número octal na linha {line_number}, coluna {column_number}")
                    sys.exit(1)
                continue

            # Float e Decimal (com verificação de `..`)
            else:
                has_decimal_point = False  
                is_scientific = False
                # Loop para acumular os dígitos e ponto decimal
                while index < len(source_code)and (source_code[index].isdigit() or source_code[index] in '.eE+-') and not(source_code[index] in "-+={}(),!@#$%¨&*:;/<>|") :
                    """if source_code[index] == '.':
                    if has_decimal_point:
                        print(f"Erro: Número inválido com múltiplos pontos decimais '{lexeme}' na linha {line_number}, coluna {column_number}")
                        sys.exit(1)
                    has_decimal_point = True"""
                    if source_code[index] in 'eE':
                        if is_scientific:
                            print(f"Erro: Notação científica inválida '{lexeme}' na linha {line_number}, coluna {column_number}")
                            sys.exit(1)
                        is_scientific = True
                    lexeme += source_code[index]
                    index += 1
                # Verifica se o número termina com um caractere inválido    
                if lexeme.count('.') > 1:
                     print(f"Erro: Número inválido com múltiplos pontos decimais '{lexeme}' na linha {line_number}, coluna {column_number}")
                     sys.exit(1)    
                # Adiciona '0' após o ponto se necessário, conforme especificação
                if lexeme.endswith('.'):
                    lexeme += '0'
                
                # Validação e classificação do número
                if is_scientific:
                    verificar_notacao_cientifica(lexeme,line_number,column_number)
                    tokens.append(Token("SCIENTIFIC_FLOAT", lexeme, line_number, column_number))
                elif '.' in lexeme:
                    tokens.append(Token("FLOAT", lexeme, line_number, column_number))
                else:
                    verificar_overflow(lexeme,line_number,column_number)
                    tokens.append(Token("DECIMAL_INT", lexeme, line_number, column_number))
                
                column_number += len(lexeme)
                continue

        # Identificação de identificadores e palavras reservadas
        if char.isalpha():
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
            #print("testando!")
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
