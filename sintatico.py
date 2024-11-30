from lexico import Token  # Importa a classe Token do módulo lexico

class Node:
    def __init__(self, node_type, children=None, value=None):
        self.node_type = node_type  # Tipo do nó, como "function", "block", etc.
        self.children = children if children is not None else []  # Filhos do nó na árvore
        self.value = value  # Valor associado ao nó, se houver (ex.: nome de uma variável)

    def __str__(self):
        return self._str_recursive(0)

    def _str_recursive(self, level):
        # Cria uma string com a indentação apropriada e o tipo e valor do nó
        ret = "\t" * level + f"{self.node_type}: {self.value if self.value else ''}\n"
        # Itera sobre os filhos do nó
        for child in self.children:
            if isinstance(child, Node):
                # Se o filho for um Node, chama recursivamente _str_recursive
                ret += child._str_recursive(level + 1)
            elif isinstance(child, Token):
                # Se o filho for um Token, exibe o token diretamente
                ret += "\t" * (level + 1) + f"Token({child.type}, {child.lexeme})\n"
            else:
                # Se o filho for um objeto inesperado, exibe uma mensagem de erro
                ret += "\t" * (level + 1) + f"Erro: Objeto inesperado {child}\n"
        return ret




# Classe do Parser (analisador sintático)
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # Lista de tokens a serem analisados
        self.current_index = 0  # Índice atual na lista de tokens
        self.current_token = None  # Token atual sendo analisado
        self.next_token()  # Inicializa o primeiro token

    def next_token(self):
        """Avança para o próximo token na lista."""
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]  # Atualiza o token atual
            self.current_index += 1
        else:
            self.current_token = None  # Não há mais tokens

    def match(self, expected_type):
        """Verifica se o token atual é do tipo esperado e avança para o próximo."""
        if self.current_token and self.current_token.type == expected_type:
            value = self.current_token.lexeme  # Captura o valor (lexeme) do token
            self.next_token()  # Avança para o próximo token
            return Node(expected_type, value=value)  # Retorna um nó com o tipo e valor do token
        else:
            raise SyntaxError(f"Esperado {expected_type}, mas encontrado {self.current_token}")

    def parse_function(self):
        """<function*> -> <type> 'IDENT' '(' ')' <bloco> ;"""
        type_node = self.parse_type()  # Analisa o tipo da função
        ident_node = self.match('IDENTIFIER')  # Analisa o identificador da função
        if self.current_token.lexeme == 'system':
            self.parse_io_stmt()  # Analisa uma instrução de I/O    
        else:
            self.match('OPEN_PAREN')  # Verifica e consome o parêntese de abertura
            self.match('CLOSE_PAREN')  # Verifica e consome o parêntese de fechamento    
        block_node = self.parse_block()  # Analisa o bloco de código da função
        return Node("function", [type_node, ident_node, block_node])  # Retorna o nó da função

    def parse_type(self):
        """<type> -> 'int' | 'float' | 'string'"""
        # Verifica se o token atual é um tipo válido
        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['int', 'float', 'string']:
            return self.match('IDENTIFIER')
        if self.current_token.type == 'STRING':
            return self.match('STRING')
        else:
            raise SyntaxError(f"Tipo esperado: int, float ou string {self.current_token}")

    def parse_block(self):
        """<bloco> -> '{' <stmtList> '}'"""
        self.match('OPEN_BRACE')  # Verifica e consome a chave de abertura
        stmt_list_node = self.parse_stmt_list()  # Analisa a lista de instruções
        self.match('CLOSE_BRACE')  # Verifica e consome a chave de fechamento
        return Node("block", [stmt_list_node])  # Retorna o nó do bloco

    def parse_stmt_list(self):
        """<stmtList> -> <stmt> <stmtList> | &"""
        stmt_list = []  # Lista para armazenar instruções
        while self.current_token and self.current_token.type != 'CLOSE_BRACE':
            stmt = self.parse_stmt()  # Analisa cada instrução
            if stmt is not None:  # Apenas adicione nós válidos
                stmt_list.append(stmt)
        if not stmt_list:
            return Node("empty")  # Produção vazia
        return Node("stmtList", stmt_list)  # Retorna o nó da lista de instruções

    def parse_stmt(self):
        """<stmt> -> <forStmt> | <ioStmt> | <whileStmt> | <atrib> ';' | <ifStmt> | <bloco> | 'break' | 'continue' | <declaration> | ';'"""
        # Lógica para identificar e analisar diferentes tipos de instruções
        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['float', 'int', 'string']:
            return self.parse_declaration()  # Analisa uma declaração de variável
        
        if self.current_token.type == 'VARIABLE':
            var_node = Node("variable", value=self.current_token.lexeme)
            expr_node = self.parse_atrib()  # Analisa a expressão à direita do '='
            if not expr_node:
                raise SyntaxError("Erro ao analisar expressão na atribuição.")
            self.match('SEMICOLON')  # Verifica e consome o ponto e vírgula
            return Node("assign_stmt", [var_node, expr_node])  # Retorna o nó de atribuição
        elif self.current_token.type == 'OPEN_BRACE':
            return self.parse_block()  # Analisa um bloco de código
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'while':
            return self.parse_while_stmt()  # Analisa um loop while
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'if':
            return self.parse_if_stmt()  # Analisa uma instrução if
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'for':
            return self.parse_for_stmt()  # Analisa um loop for
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['break', 'continue']:
            value = self.current_token.lexeme
            self.next_token()
            self.match('SEMICOLON')  # Verifica e consome o ponto e vírgula
            return Node("control", value=value)  # Retorna o nó de controle (break/continue)
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'system':
            io_node = self.parse_io_stmt()  # Analisa uma instrução de I/O
            if not io_node:
                raise SyntaxError("Erro ao analisar instrução de I/O.")
            return io_node
        elif self.current_token.type == 'SEMICOLON':
            self.next_token()  # Consome o ponto e vírgula
            return Node("empty_stmt")  # Retorna um nó de instrução vazia
        else:
            raise SyntaxError(f"Instrução inválida: {self.current_token}")

    def parse_declaration(self):
        """<declaration> -> <type> <identList> ';'"""
        if self.current_token.type in ['IDENTIFIER']:
            type_node = Node("type", value=self.current_token.lexeme)
            self.next_token()  # Consome o tipo
            ident_list_node = self.parse_ident_list()  # Analisa a lista de identificadores
            if self.current_token.type != 'SEMICOLON':
                raise SyntaxError(f"Erro de sintaxe: Esperado ';' mas encontrado {self.current_token}")
            self.next_token()  # Consome ';'
            return Node("declaration", [type_node, ident_list_node])
        else:
            raise SyntaxError(f"Erro de sintaxe: Tipo esperado mas encontrado {self.current_token}")
        
    def parse_ident_list(self):
        """<identList> -> 'IDENT' <restoIdentList>"""
        if self.current_token.type == 'VARIABLE':
            ident_node = Node("identifier", value=self.current_token.lexeme)
            self.next_token()  # Consome o identificador
            resto_node = self.parse_resto_ident_list()  # Analisa o resto da lista de identificadores
            return Node("ident_list", [ident_node, resto_node])
        else:
            raise SyntaxError(f"Erro de sintaxe: IDENT esperado mas encontrado {self.current_token}")
        

    def parse_resto_ident_list(self):
        """<restoIdentList> -> ',' 'IDENT' <restoIdentList> | &"""
        if self.current_token.type == 'COMMA':
            self.next_token()  # Consome ','
            if self.current_token.type == 'VARIABLE':
                ident_node = Node("identifier", value=self.current_token.lexeme)
                self.next_token()  # Consome o identificador
                resto_node = self.parse_resto_ident_list()  # Analisa o resto da lista
                return Node("resto_ident_list", [ident_node, resto_node])
            else:
                raise SyntaxError(f"Erro de sintaxe: IDENT esperado após ',' mas encontrado {self.current_token}")
        else:
            return Node("empty")  # Produção vazia


    # Outros métodos para analisar loops, instruções de controle, expressões, etc.
    def parse_for_stmt(self):
        """<forStmt> -> 'for' '(' <optAtrib> ';' <optExpr> ';' <optAtrib> ')' <stmt>"""
        self.match('IDENTIFIER')  # 'for'
        self.match('OPEN_PAREN')
        self.parse_opt_atrib()  # Analisa a atribuição opcional
        self.match('SEMICOLON')
        self.parse_opt_expr()  # Analisa a expressão opcional
        self.match('SEMICOLON')
        self.parse_opt_atrib()  # Analisa a atribuição opcional
        self.match('CLOSE_PAREN')
        self.parse_stmt()  # Analisa a instrução no corpo do loop

    def parse_opt_atrib(self):
        """<optAtrib> -> <atrib> | &"""
        if self.current_token and self.current_token.type == 'VARIABLE':
            return self.parse_atrib()  # Retorna o nó de atribuição, se houver
        return Node("empty")  # Produção vazia


    def parse_opt_expr(self):
        """<optExpr> -> <expr> | &"""
        if self.current_token and self.current_token.type == 'VARIABLE':
            self.parse_expr()  # Analisa a expressão, se houver

    def parse_io_stmt(self):
        """<ioStmt> -> 'system' '.' 'out' '.' 'print' '(' <outList> ')' ';' | 'system' '.' 'in' '.' 'scan' '(' <outList> ')' ';'"""
        if self.current_token.lexeme == 'system':
            self.match('IDENTIFIER')  # 'system'
            self.match('DOT')
            if self.current_token.lexeme == 'out':
                self.match('IDENTIFIER')  # 'out'
                self.match('DOT')
                self.match('IDENTIFIER')  # 'print'
                self.match('OPEN_PAREN')
                out_list = self.parse_out_list()  # Analisa os argumentos de saída
                self.match('CLOSE_PAREN')
                self.match('SEMICOLON')
                return Node("io_stmt", [Node("output", out_list)])  # Retorna o nó de saída
            elif self.current_token.lexeme == 'in':
                self.match('IDENTIFIER')  # 'in'
                self.match('DOT')
                self.match('IDENTIFIER')  # 'scan'
                self.match('OPEN_PAREN')
                in_list = [None, None] # Inicializa a lista de entrada
                in_list[0] = self.parse_type()  # Analisa os argumentos de entrada
                self.match('COMMA')
                in_list[1] = self.match('VARIABLE')  # Identificador
                self.match('CLOSE_PAREN')
                self.match('SEMICOLON')
                return Node("io_stmt", [Node("input", in_list)])  # Retorna o nó de entrada
        raise SyntaxError(f"Instrução de I/O inválida: {self.current_token}")



    def parse_out_list(self):
        """<outList> -> <out> <restoOutList>"""
        out_list = [self.parse_out()]  # Analisa a primeira saída
        while self.current_token and self.current_token.type == 'COMMA':
            self.match('COMMA')  # Consome a vírgula
            out_list.append(self.parse_out())  # Analisa a próxima saída
        return out_list


    def parse_out(self):
        """<out> -> 'STR' | 'IDENT' | 'NUMdec' | 'NUMfloat' | 'NUMoct' | 'NUMhex'"""
        if self.current_token.type in ['STRING', 'IDENTIFIER', 'VARIABLE', 'SCIENTIFIC_FLOAT', 'FLOAT', 'DECIMAL_INT', 'HEXADECIMAL_INT', 'OCTAL_INT']:
            node = Node("out", value=self.current_token.lexeme)
            self.next_token()  # Consome o token
            return node
        else:
            raise SyntaxError(f"Saída inválida: esperado STRING, IDENTIFIER ou número, mas encontrado {self.current_token}")

    def parse_while_stmt(self):
        """<whileStmt> -> 'while' '(' <expr> ')' <stmt>"""
        self.match('IDENTIFIER')  # 'while'
        self.match('OPEN_PAREN')
        self.parse_expr()  # Analisa a expressão de condição
        self.match('CLOSE_PAREN')
        self.parse_stmt()  # Analisa a instrução no corpo do loop

    def parse_if_stmt(self):
        #print("entrei no if stmt")
        """<ifStmt> -> 'if' '(' <expr> ')' <stmt> <elsePart>"""
        self.match('IDENTIFIER')  # 'if'
        self.match('OPEN_PAREN')
        self.parse_expr()  # Analisa a expressão de condição
        self.match('CLOSE_PAREN')
        self.parse_stmt()  # Analisa a instrução no corpo do if
        if self.current_token and self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'else':
            self.next_token()  # Consome o 'else'
            self.parse_stmt()  # Analisa a instrução no corpo do else

    def parse_atrib(self):
        
        """<atrib> -> 'IDENT' '=' <expr>"""
        if self.current_token.type == 'VARIABLE':
            var_node = Node("variable", value=self.current_token.lexeme)
            self.next_token()  # Consome o identificador
            if self.current_token.type in ['ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN']:
                assign_node = Node("assign_operator", value=self.current_token.lexeme)
                self.next_token()  # Consome o operador de atribuição
                expr_node = self.parse_expr()  # Analisa a expressão à direita do '='
                if expr_node is None:
                    raise SyntaxError("Erro na análise da expressão à direita do operador de atribuição.")
                return Node("assign_stmt", [var_node, assign_node, expr_node])  # Retorna o nó completo
            else:
                raise SyntaxError(f"Operador de atribuição esperado, mas encontrado {self.current_token}")
        else:
            raise SyntaxError(f"Variável esperada, mas encontrada {self.current_token}")




    def parse_expr(self):
        """<expr> -> <or>"""
        #print(f"Parsing expression. Current token: {self.current_token}")
        or_node = self.parse_or()  # Analisa a expressão lógica 'or'
        if or_node is None:
            print("Expression parsing failed.")
            raise SyntaxError("Expressão inválida encontrada.")
        return or_node  # Retorna o nó da expressão


        

    def parse_or(self):
        """<or> -> <and> <restoOr>"""
        #print(f"Parsing OR. Current token: {self.current_token}")
        left_node = self.parse_and()  # Analisa o lado esquerdo
        while self.current_token and self.current_token.type == 'LOGICAL_OR':
            operator_token = self.current_token
            self.next_token()
            right_node = self.parse_and()  # Analisa o lado direito
            left_node = Node("binary_op", [left_node, right_node], operator_token.lexeme)
        return left_node


    def parse_and(self):
        """<and> -> <not> <restoAnd>"""
        #print(f"Parsing AND. Current token: {self.current_token}")
        left_node = self.parse_not()  # Analisa o lado esquerdo
        while self.current_token and self.current_token.type == 'LOGICAL_AND':
            operator_token = self.current_token
            self.next_token()
            right_node = self.parse_not()  # Analisa o lado direito
            left_node = Node("binary_op", [left_node, right_node], operator_token.lexeme)
        return left_node


    def parse_not(self):
        """<not> -> '!' <not> | <rel>"""
        #print(f"Parsing NOT. Current token: {self.current_token}")
        if self.current_token and self.current_token.type == 'LOGICAL_NOT':
            operator_token = self.current_token
            self.next_token()  # Consome o operador '!'
            not_node = self.parse_not()  # Analisa a próxima expressão
            return Node("unary_op", [not_node], operator_token.lexeme)  # Nó unário
        else:
            return self.parse_rel()  # Retorna o nó relacional


    def parse_rel(self):
        """<rel> -> <add> <restoRel>"""
        #print(f"Parsing REL. Current token: {self.current_token}")
        left_node = self.parse_add()  # Analisa o lado esquerdo
        if self.current_token and self.current_token.type in ['EQUAL', 'NOT_EQUAL', 'LESS', 'LESS_EQUAL', 'GREATER', 'GREATER_EQUAL']:
            operator_token = self.current_token
            self.next_token()  # Consome o operador
            right_node = self.parse_add()  # Analisa o lado direito
            return Node("binary_op", [left_node, right_node], operator_token.lexeme)  # Nó binário
        return left_node  # Retorna o lado esquerdo se não houver operadores relacionais


    def parse_add(self):
        """<add> -> <mult> (<ADD | SUB> <mult>)*"""
        #print(f"Parsing ADD. Current token: {self.current_token}")
        left_node = self.parse_mult()  # Analisa o lado esquerdo (multiplicação)
        
        # Enquanto houver operadores de adição ou subtração, continue processando
        while self.current_token and self.current_token.type in ['ADD', 'SUB']:
            operator_token = self.current_token  # Captura o operador
            self.next_token()  # Consome o operador
            right_node = self.parse_mult()  # Analisa o lado direito (multiplicação)
            
            # Cria um nó binário para o operador
            left_node = Node("binary_op", [left_node, right_node], operator_token.lexeme)
            #print(f"Created binary_op node with operator {operator_token.lexeme}")
        
        return left_node  # Retorna o nó completo

    def parse_mult(self):
        """<mult> -> <uno> <restoMult>"""
        #print(f"Parsing MULT. Current token: {self.current_token}")
        left_node = self.parse_uno()  # Analisa o lado esquerdo
        while self.current_token and self.current_token.type in ['MUL', 'DIV', 'MOD']:
            operator_token = self.current_token
            self.next_token()  # Consome o operador
            right_node = self.parse_uno()  # Analisa o lado direito
            left_node = Node("binary_op", [left_node, right_node], operator_token.lexeme)  # Nó binário
        return left_node  # Retorna o nó completo

            
        
    def parse_uno(self):
        """<uno> -> '+' <uno> | '-' <uno> | <factor>"""
        #print(f"Parsing UNO. Current token: {self.current_token}")
        if self.current_token and self.current_token.type in ['ADD', 'SUB']:
            operator_token = self.current_token
            self.next_token()  # Consome o operador
            uno_node = self.parse_uno()  # Analisa o próximo fator
            return Node("unary_op", [uno_node], operator_token.lexeme)  # Nó unário
        else:
            return self.parse_factor()  # Retorna o fator

            
    def parse_factor(self):
        """<factor> -> '(' <expr> ')' | 'IDENT' | 'NUMdec' | 'NUMfloat' | 'NUMoct' | 'NUMhex' | 'STRING'"""
        #print(f"Parsing factor. Current token: {self.current_token}")
        if self.current_token.type == 'OPEN_PAREN':
            self.next_token()
            expr_node = self.parse_expr()  # Analisa a expressão dentro dos parênteses
            if self.current_token.type != 'CLOSE_PAREN':
                raise SyntaxError(f"Erro de sintaxe: Esperado ')' mas encontrado {self.current_token}")
            self.next_token()
            return expr_node
        elif self.current_token.type in ['DECIMAL_INT', 'FLOAT', 'OCTAL_INT', 'HEXADECIMAL_INT', 'STRING', 'SCIENTIFIC_FLOAT']:
            # Se for um literal, crie um nó e avance
            literal_node = Node("literal", value=self.current_token.lexeme)
            self.next_token()  # Consome o literal
            #print(f"Literal node created: {literal_node}")
            return literal_node
        elif self.current_token.type == 'VARIABLE':
            # Se for uma variável, crie um nó e avance
            variable_node = Node("variable", value=self.current_token.lexeme)
            self.next_token()
            return variable_node
        else:
            raise SyntaxError(f"Erro de sintaxe: Token inesperado {self.current_token}")



    



# Código principal para executar o parser
if __name__ == "__main__":
   
    import lexico, sys

    if len(sys.argv) > 1:
        try:
            # Chame lexico.main com o nome do arquivo como argumento
            tokens = lexico.main(sys.argv[1])  # Retorna a lista de tokens

            if not tokens or not isinstance(tokens, list):
                raise ValueError("A lista de tokens está vazia ou em um formato incorreto. Verifique o lexico.py.")

            print("Lista de tokens recebida:")
            for token in tokens:
                print(token)  # Exibe os tokens para depuração

            # Inicializa o parser com a lista de tokens
            parser = Parser(tokens)

            # Gera a árvore sintática
            root_node = parser.parse_function()

            # Imprime a árvore sintática
            print("Árvore sintática gerada:")
            print(root_node)

        except SyntaxError as e:
            print(f"Erro de sintaxe: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    else:
        print("Erro: Nenhum arquivo foi especificado. Por favor, forneça o nome do arquivo.")
        sys.exit(1)