from lexico import Token
class Node:
    def __init__(self, node_type, children=None, value=None):
        self.node_type = node_type
        self.children = children if children is not None else []
        self.value = value

    def __str__(self, level=0):
        ret = "\t" * level + f"{self.node_type}: {self.value if self.value else ''}\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret
    
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = None
        self.next_token()

    def next_token(self):
        """Avança para o próximo token."""
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
            self.current_index += 1
        else:
            self.current_token = None

    def match(self, expected_type):
        """Verifica se o token atual é do tipo esperado e avança."""
        if self.current_token and self.current_token.type == expected_type:
            value = self.current_token.lexeme
            self.next_token()
            return Node(expected_type, value=value)
        else:
            raise SyntaxError(f"Esperado {expected_type}, mas encontrado {self.current_token}")

    def parse_function(self):
        """<function*> -> <type> 'IDENT' '(' ')' <bloco> ;"""
        type_node = self.parse_type()
        ident_node = self.match('IDENTIFIER')
        self.match('OPEN_PAREN')
        self.match('CLOSE_PAREN')
        block_node = self.parse_block()
        return Node("function", [type_node, ident_node, block_node])

    def parse_type(self):
            """<type> -> 'int' | 'float' | 'string'"""
            if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['int', 'float', 'string']:
                return self.match('IDENTIFIER')
            else:
                raise SyntaxError("Tipo esperado: int, float ou string")
        
    def parse_block(self):
            """<bloco> -> '{' <stmtList> '}'"""
            self.match('OPEN_BRACE')
            stmt_list_node = self.parse_stmt_list()
            self.match('CLOSE_BRACE')
            return Node("block", [stmt_list_node])

    def parse_stmt_list(self):
        """<stmtList> -> <stmt> <stmtList> | &"""
        stmt_list = []
        while self.current_token and self.current_token.type != 'CLOSE_BRACE':
            stmt_list.append(self.parse_stmt())
        return Node("stmtList", stmt_list)

    def parse_stmt(self):
        """<stmt> -> <forStmt> | <ioStmt> | <whileStmt> | <expr> ';' | <ifStmt> | <bloco> | 'break' | 'continue' | <declaration> | ';'"""
        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['int', 'float', 'string']:
            return self.parse_declaration()
        elif self.current_token.type == 'VARIABLE':
            expr_node = self.parse_expr()
            self.match('SEMICOLON')
            return Node("expr_stmt", [expr_node])
        elif self.current_token.type == 'OPEN_BRACE':
            return self.parse_block()
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'while':
            return self.parse_while_stmt()
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'if':
            return self.parse_if_stmt()
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'for':
            return self.parse_for_stmt()
        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['break', 'continue']:
            value = self.current_token.lexeme
            self.next_token()
            self.match('SEMICOLON')
            return Node("control", value=value)
        elif self.current_token.type == 'SEMICOLON':
            self.next_token()
            return Node("empty_stmt")
        else:
            raise SyntaxError(f"Instrução inválida: {self.current_token}")


    def parse_declaration(self):
        """<declaration> -> <type> <identList> ';'"""
        type_node = self.parse_type()
        ident_list_node = self.parse_ident_list()
        self.match('SEMICOLON')
        return Node("declaration", [type_node, ident_list_node])
    
    def parse_ident_list(self):
        """<identList> -> 'IDENT' <restoIdentList>"""
        nodes = [self.match('VARIABLE')]
        while self.current_token and self.current_token.type == 'COMMA':
            self.next_token()
            nodes.append(self.match('VARIABLE'))
        return Node("identList", nodes)
    def parse_for_stmt(self):
        """<forStmt> -> 'for' '(' <optAtrib> ';' <optExpr> ';' <optAtrib> ')' <stmt>"""
        self.match('IDENTIFIER')  # 'for'
        self.match('OPEN_PAREN')
        self.parse_opt_atrib()
        self.match('SEMICOLON')
        self.parse_opt_expr()
        self.match('SEMICOLON')
        self.parse_opt_atrib()
        self.match('CLOSE_PAREN')
        self.parse_stmt()

    def parse_opt_atrib(self):
        """<optAtrib> -> <atrib> | &"""
        if self.current_token and self.current_token.type == 'VARIABLE':
            self.parse_atrib()

    def parse_opt_expr(self):
        """<optExpr> -> <expr> | &"""
        if self.current_token and self.current_token.type == 'VARIABLE':
            self.parse_expr()

    def parse_io_stmt(self):
        """<ioStmt> -> 'system' '.' 'out' '.' 'print' '(' <type> ',' 'IDENT' ')' ';' | 'system' '.' 'in' '.' 'scan' '(' <outList> ')' ';'"""
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
        elif self.current_token.lexeme== 'in':
            self.next_token()
            self.match('DOT')
            self.match('IDENTIFIER')  # 'scan'
            self.match('OPEN_PAREN')
            self.parse_out_list()
            self.match('CLOSE_PAREN')
            self.match('SEMICOLON')

    def parse_out_list(self):
        """<outList> -> <out> <restoOutList>"""
        self.parse_out()
        while self.current_token and self.current_token.type == 'COMMA':
            self.next_token()
            self.parse_out()

    def parse_out(self):
        """<out> -> 'STR' | 'IDENT' | 'NUMdec' | 'NUMfloat' | 'NUMoct' | 'NUMhex'"""
        if self.current_token.type in ['STR', 'VARIABLE', 'NUMdec', 'NUMfloat', 'NUMoct', 'NUMhex']:
            self.next_token()
        else:
            raise SyntaxError("Saída inválida")

    def parse_while_stmt(self):
        """<whileStmt> -> 'while' '(' <expr> ')' <stmt>"""
        self.match('IDENTIFIER')  # 'while'
        self.match('OPEN_PAREN')
        self.parse_expr()
        self.match('CLOSE_PAREN')
        self.parse_stmt()

    def parse_if_stmt(self):
        """<ifStmt> -> 'if' '(' <expr> ')' <stmt> <elsePart>"""
        self.match('IDENTIFIER')  # 'if'
        self.match('OPEN_PAREN')
        self.parse_expr()
        self.match('CLOSE_PAREN')
        self.parse_stmt()
        if self.current_token and self.current_token.type == 'IDENTIFIER' and self.current_token.value == 'else':
            self.next_token()
            self.parse_stmt()

    def parse_atrib(self):
        """<atrib> -> 'IDENT' ':=' <expr> | 'IDENT' '+=' <expr> | 'IDENT' '-=' <expr> | 'IDENT' '*=' <expr> | 'IDENT' '/=' <expr> | 'IDENT' '%=' <expr>"""
        if self.current_token.type == 'VARIABLE':
            self.next_token()
            if self.current_token.type in ['ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN']:
                self.next_token()
                self.parse_expr()
            else:
                raise SyntaxError("Operador de atribuição esperado")

    def parse_expr(self):
        """<expr> -> <or>"""
        self.parse_or()

    def parse_or(self):
        """<or> -> <and> <restoOr>"""
        self.parse_and()
        while self.current_token and self.current_token.type == 'LOGICAL_OR':
            self.next_token()
            self.parse_and()

    def parse_and(self):
        """<and> -> <not> <restoAnd>"""
        self.parse_not()
        while self.current_token and self.current_token.type == 'LOGICAL_AND':
            self.next_token()
            self.parse_not()

    def parse_not(self):
        """<not> -> '!' <not> | <rel>"""
        if self.current_token and self.current_token.type == 'LOGICAL_NOT':
            self.next_token()
            self.parse_not()
        else:
            self.parse_rel()

    def parse_rel(self):
        """<rel> -> <add> <restoRel>"""
        self.parse_add()
        if self.current_token and self.current_token.type in ['EQUAL', 'NOT_EQUAL', 'LESS', 'LESS_EQUAL', 'GREATER', 'GREATER_EQUAL']:
            self.next_token()
            self.parse_add()

    def parse_add(self):
        """<add> -> <mult> <restoAdd>"""
        self.parse_mult()
        while self.current_token and self.current_token.type in ['ADD', 'SUB']:
            self.next_token()
            self.parse_mult()

    def parse_mult(self):
        """<mult> -> <uno> <restoMult>"""
        self.parse_uno()
        while self.current_token and self.current_token.type in ['MUL', 'DIV', 'MOD']:
            self.next_token()
            self.parse_uno()

    def parse_uno(self):
        """<uno> -> '+' <uno> | '-' <uno> | <fator>"""
        if self.current_token and self.current_token.type in ['ADD', 'SUB']:
            self.next_token()
            self.parse_uno()
        else:
            self.parse_fator()

    def parse_fator(self):
        """<fator> -> 'NUMint' | 'NUMfloat' | 'NUMoct' | 'NUMhex' | 'IDENT' | '(' <expr> ')' | 'STR'"""
        if self.current_token.type in ['NUMint', 'NUMfloat', 'NUMoct', 'NUMhex', 'VARIABLE', 'STR']:
            self.next_token()
        elif self.current_token.type == 'OPEN_PAREN':
            self.next_token()
            self.parse_expr()
            self.match('CLOSE_PAREN')
        else:
            raise SyntaxError("Fator esperado")
if __name__ == "__main__":
    import lexico, sys

    if len(sys.argv) > 1:
        try:
            lista = lexico.main(sys.argv[1])
            print("Lista de tokens recebida:", lista)  # Para verificar a saída do lexico

            if not lista or not isinstance(lista, list):
                raise ValueError("A lista de tokens está vazia ou em um formato incorreto. Verifique o lexico.py.")

            parser = Parser(lista)
            parser.parse_function()
            print("Parsing concluído com sucesso!")
            print("Lista de instruções gerada pelo sintático:")
            print(parser)

        except SyntaxError as e:
            print(f"Erro de sintaxe: {e}")
        
