from lexico import Token  # Importa a classe Token do módulo lexico

# Classe que representa um nó na árvore de sintaxe
class Node:
    def __init__(self, node_type, children=None, value=None):
        self.node_type = node_type  # Tipo do nó, como "function", "block", etc.
        self.children = children if children is not None else []  # Filhos do nó na árvore
        self.value = value  # Valor associado ao nó, se houver (ex.: nome de uma variável)

    def __str__(self, level=0):
        # Método para imprimir a árvore de forma hierárquica
        ret = "\t" * level + f"{self.node_type}: {self.value if self.value else ''}\n"
        for child in self.children:
            ret += child.__str__(level + 1)  # Imprime os filhos com um nível de indentação maior
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
            stmt_list.append(self.parse_stmt())  # Analisa cada instrução e adiciona à lista
        return Node("stmtList", stmt_list)  # Retorna o nó da lista de instruções

    def parse_stmt(self):
        """<stmt> -> <forStmt> | <ioStmt> | <whileStmt> | <atrib> ';' | <ifStmt> | <bloco> | 'break' | 'continue' | <declaration> | ';'"""
        # Lógica para identificar e analisar diferentes tipos de instruções
        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['float', 'int', 'string']:
            return self.parse_declaration()  # Analisa uma declaração de variável
        
        if self.current_token.type == 'VARIABLE':
            var_node = Node("variable", value=self.current_token.lexeme)
            self.next_token()
            print(self.current_token.type)
            if self.current_token.type == 'ASSIGN':
                self.next_token()  # Consome o token de atribuição
                expr_node = self.parse_atrib()  # Analisa a expressão à direita do '='
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
            self.parse_io_stmt()  # Analisa uma instrução de I/O
        elif self.current_token.type == 'SEMICOLON':
            self.next_token()  # Consome o ponto e vírgula
            return Node("empty_stmt")  # Retorna um nó de instrução vazia
        else:
            raise SyntaxError(f"Instrução inválida: {self.current_token}")


    def parse_declaration(self):
        """<declaration> -> <type> <identList> ';'"""
        type_node = self.parse_type()  # Analisa o tipo
        ident_list_node = self.parse_ident_list()  # Analisa a lista de identificadores
        self.match('SEMICOLON')  # Verifica e consome o ponto e vírgula
        return Node("declaration", [type_node, ident_list_node])  # Retorna o nó da declaração

    def parse_ident_list(self):
        """<identList> -> 'IDENT' <restoIdentList>"""
        nodes = [self.match('VARIABLE')]  # Começa com um identificador
        while self.current_token and self.current_token.type == 'COMMA':
            self.next_token()  # Consome a vírgula
            nodes.append(self.match('VARIABLE'))  # Adiciona o próximo identificador
        return Node("identList", nodes)  # Retorna o nó da lista de identificadores

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
            self.parse_atrib()  # Analisa a atribuição, se houver

    def parse_opt_expr(self):
        """<optExpr> -> <expr> | &"""
        if self.current_token and self.current_token.type == 'VARIABLE':
            self.parse_expr()  # Analisa a expressão, se houver

    def parse_io_stmt(self):
        """<ioStmt> -> 'system' '.' 'out' '.' 'print' '(' <type> ',' 'IDENT' ')' ';' | 'system' '.' 'in' '.' 'scan' '(' <outList> ')' ';'"""
        if self.current_token.lexeme == 'system':
            self.match('IDENTIFIER')  # 'system'
            self.match('DOT')
        if self.current_token.lexeme == 'out':
            self.next_token()
            self.match('DOT')
            self.match('IDENTIFIER')  # 'print'
            self.match('OPEN_PAREN')
            self.parse_type()
            self.match('COMMA')
            self.match('VARIABLE')
            self.match('CLOSE_PAREN')
            self.match('SEMICOLON')
        elif self.current_token.lexeme == 'in':
            self.next_token()
            self.match('DOT')
            self.match('IDENTIFIER')  # 'scan'
            self.match('OPEN_PAREN')
            self.parse_out_list()
            self.match('CLOSE_PAREN')
            self.match('SEMICOLON')

    def parse_out_list(self):
        """<outList> -> <out> <restoOutList>"""
        self.parse_out()  # Analisa a primeira saída
        while self.current_token and self.current_token.type == 'COMMA':
            self.next_token()  # Consome a vírgula
            self.parse_out()  # Analisa a próxima saída

    def parse_out(self):
        """<out> -> 'STR' | 'IDENT' | 'NUMdec' | 'NUMfloat' | 'NUMoct' | 'NUMhex'"""
        if self.current_token.type in ['STR', 'VARIABLE', 'NUMdec', 'NUMfloat', 'NUMoct', 'NUMhex']:
            self.next_token()  # Consome o token
        else:
            raise SyntaxError("Saída inválida")

    def parse_while_stmt(self):
        """<whileStmt> -> 'while' '(' <expr> ')' <stmt>"""
        self.match('IDENTIFIER')  # 'while'
        self.match('OPEN_PAREN')
        self.parse_expr()  # Analisa a expressão de condição
        self.match('CLOSE_PAREN')
        self.parse_stmt()  # Analisa a instrução no corpo do loop

    def parse_if_stmt(self):
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
        """<atrib> -> 'IDENT' ':=' <expr> | 'IDENT' '+=' <expr> | 'IDENT' '-=' <expr> | 'IDENT' '*=' <expr> | 'IDENT' '/=' <expr> | 'IDENT' '%=' <expr>"""
        if self.current_token.type == 'VARIABLE':
            self.next_token()  # Consome o identificador
            if self.current_token.type in ['ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN']:
                self.next_token()  # Consome o operador de atribuição
                self.parse_expr()  # Analisa a expressão
            else:
                raise SyntaxError("Operador de atribuição esperado")

    def parse_expr(self):
        """<expr> -> <or>"""
        self.parse_or()  # Analisa a expressão lógica 'or'

    def parse_or(self):
        """<or> -> <and> <restoOr>"""
        self.parse_and()  # Analisa a expressão lógica 'and'
        while self.current_token and self.current_token.type == 'LOGICAL_OR':
            self.next_token()  # Consome o operador 'or'
            self.parse_and()  # Analisa a próxima expressão 'and'

    def parse_and(self):
        """<and> -> <not> <restoAnd>"""
        self.parse_not()  # Analisa a expressão lógica 'not'
        while self.current_token and self.current_token.type == 'LOGICAL_AND':
            self.next_token()  # Consome o operador 'and'
            self.parse_not()  # Analisa a próxima expressão 'not'

    def parse_not(self):
        """<not> -> '!' <not> | <rel>"""
        if self.current_token and self.current_token.type == 'LOGICAL_NOT':
            self.next_token()  # Consome o operador '!'
            self.parse_not()  # Analisa a próxima expressão 'not'
        else:
            self.parse_rel()  # Analisa a expressão relacional

    def parse_rel(self):
        """<rel> -> <add> <restoRel>"""
        self.parse_add()  # Analisa a expressão de adição
        if self.current_token and self.current_token.type in ['EQUAL', 'NOT_EQUAL', 'LESS', 'LESS_EQUAL', 'GREATER', 'GREATER_EQUAL']:
            self.next_token()  # Consome o operador relacional
            self.parse_add()  # Analisa a próxima expressão de adição

    def parse_add(self):
        """<add> -> <mult> <restoAdd>"""
        self.parse_mult()  # Analisa a expressão de multiplicação
        while self.current_token and self.current_token.type in ['ADD', 'SUB']:
            self.next_token()  # Consome o operador '+' ou '-'
            self.parse_mult()  # Analisa a próxima expressão de multiplicação

    def parse_mult(self):
        """<mult> -> <uno> <restoMult>"""
        self.parse_uno()  # Analisa a expressão unária
        while self.current_token and self.current_token.type in ['MUL', 'DIV', 'MOD']:
            self.next_token()  # Consome o operador '*', '/' ou '%'
            self.parse_uno()  # Analisa a próxima expressão unária

    def parse_uno(self):
        """<uno> -> '+' <uno> | '-' <uno> | <fator>"""
        if self.current_token and self.current_token.type in ['ADD', 'SUB']:
            self.next_token()  # Consome o operador '+' ou '-'
            self.parse_uno()  # Analisa a próxima expressão unária
        else:
            self.parse_fator()  # Analisa o fator

    def parse_fator(self):
        """<fator> -> 'INT' | 'FLOAT' | 'OCT' | 'HEX' | 'IDENT' | '(' <expr> ')' | 'STR'"""
        if self.current_token.type in ['INT', 'FLOAT', 'OCTAL_INT', 'HEXADECIMAL_INT', 'VARIABLE', 'STR', 'SCIENTIFIC_FLOAT','DECIMAL_INT']:
            self.next_token()  # Consome o token
        elif self.current_token.type == 'OPEN_PAREN':
            self.next_token()  # Consome o parêntese de abertura
            self.parse_expr()  # Analisa a expressão dentro dos parênteses
            self.match('CLOSE_PAREN')  # Verifica e consome o parêntese de fechamento
        else:
            raise SyntaxError(f"Fator esperado: {self.current_token}, {self.current_token.type}, {self.current_token.lexeme}")

# Código principal para executar o parser
if __name__ == "__main__":
    import lexico, sys

    if len(sys.argv) > 1:
        try:
            lista = lexico.main(sys.argv[1])  # Obtém a lista de tokens do módulo lexico
            print("Lista de tokens recebida:", lista)  # Para verificar a saída do lexico

            if not lista or not isinstance(lista, list):
                raise ValueError("A lista de tokens está vazia ou em um formato incorreto. Verifique o lexico.py.")

            parser = Parser(lista)  # Inicializa o parser com a lista de tokens
            parser.parse_function()  # Inicia o parsing da função
            print("Parsing concluído com sucesso!")
            print("Lista de instruções gerada pelo sintático:")
            print(parser)

        except SyntaxError as e:
            print(f"Erro de sintaxe: {e}")
