from lexico import Token  # Importa a classe Token do módulo lexico

class Node:
    def __init__(self, node_type, children=None, value=None):
        self.node_type = node_type  # Define o tipo do nó (ex: 'binary_op', 'unary_op', 'literal')
        self.children = children if children else []  # Lista de filhos
        self.value = value  # Valor associado ao nó (ex: operadores, identificadores, números)

    def __str__(self):
        if self.node_type == "binary_op":
            return f"({self.children[0]} {self.value} {self.children[1]})"
        elif self.node_type == "unary_op":
            return f"({self.value} {self.children[0]})"
        return str(self.value)


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
        self.code = []  # Lista para armazenar o código intermediário
        self.temp_counter = 0  # Contador para variáveis temporárias
        self.label_counter = 0  # Contador para labels
        self.variaveis = {}  # 🔴 Adicionado: Dicionário para armazenar variáveis

    def gerar_operacao(self, op, destino, fonte1, fonte2=None):
        """Gera operações básicas: '+', '-', '*', '/', '%', '='"""
        if op not in ('+', '-', '*', '/', '%', '=', '<', '>', '==', '!=', '<=', '>='):
            raise ValueError(f"Operador '{op}' não suportado")
        self.code.append((op, destino, fonte1, fonte2))

    def gerar_label(self, label):
        """Gera uma label no código intermediário."""
        label = f"__label{self.label_counter}"
        print(f"⚠️ DEBUG: Gerando nova label {label}")  # Print de debug
        self.label_counter += 1
        print(self.label_counter)
        self.code.append(("LABEL", label, None, None))    

    def next_token(self):
        """Avança para o próximo token na lista."""
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]  # Atualiza o token atual
            self.current_index += 1
            print(f"➡️ DEBUG: Avançando para próximo token -> {self.current_token}")
        else:
            self.current_token = None  # Não há mais tokens
            print("✅ DEBUG: Final da análise alcançado")

    def match(self, expected_types):
        """Consome o token esperado e avança para o próximo"""
        print(f"🔍 DEBUG: Tentando consumir {expected_types}, token atual: {self.current_token}")

        if isinstance(expected_types, list):  # Para casos como ['ASSIGN', 'ADD_ASSIGN'...]
            if self.current_token and self.current_token.type in expected_types:
                token_atual = self.current_token
                self.next_token()  # Avança para o próximo token
                print(f"✅ DEBUG: Consumido corretamente -> {token_atual}")
                return token_atual
        elif self.current_token and self.current_token.type == expected_types:
            token_atual = self.current_token
            self.next_token()  # Avança para o próximo token
            print(f"✅ DEBUG: Consumido corretamente -> {token_atual}")
            return token_atual

        raise SyntaxError(f"Erro de sintaxe: esperado {expected_types}, encontrado {self.current_token}")

        
    def generate_temp(self):
        temp_var = f"__temp{self.temp_counter}"
        self.temp_counter += 1
        return temp_var

    def generate_label(self):
        label = f"__label{self.label_counter}"
        self.label_counter += 1  # Incrementa ANTES da próxima geração
        return label

    
    def parse_function(self):
        """<function*> -> <type> 'IDENT' '(' ')' <bloco> ;"""
        #print("\n🔍 Entrando em parse_function()")

        # Captura o tipo da função
        type_node = self.parse_type()  
        #print(f"✅ Tipo da função identificado: {type_node.value}")

        # Captura o nome da função
        ident_node = self.match('IDENTIFIER')  
        #print(f"✅ Identificador da função identificado: {ident_node.lexeme}")

        # Verifica e consome os parênteses de abertura e fechamento
        self.match('OPEN_PAREN')
        self.match('CLOSE_PAREN')

        #print("🔍 Chamando parse_block()...")
        block_node = self.parse_block()  # Analisa o bloco da função
        #print("✅ Bloco da função analisado com sucesso.")

        return Node("function", [type_node, ident_node, block_node])  # Retorna o nó da função


    def parse_type(self):
        """<type> -> 'int' | 'float' | 'string'"""
        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['int', 'float', 'string']:
            tipo = self.current_token.lexeme
            self.next_token()
            return Node("type", value=tipo)
        else:
            raise SyntaxError(f"Tipo esperado: int, float ou string, mas encontrado {self.current_token}")

    def parse_block(self):
        """<bloco> -> '{' <stmtList> '}'"""
        #print("\n🔍 Entrando em parse_block()...")

        self.match('OPEN_BRACE')  # Consome '{'
        #print("✅ Encontrado '{', iniciando stmt_list...")

        stmt_list_node = self.parse_stmt_list()  # Analisa lista de instruções
        #print("✅ Lista de instruções analisada com sucesso.")

        self.match('CLOSE_BRACE')  # Consome '}'
        #print("✅ Encontrado '}', bloco de código finalizado.")

        return Node("block", [stmt_list_node])  # Retorna nó do bloco


    def parse_stmt_list(self):
        """<stmt_list> -> <stmt> <stmt_list> | ε"""
        stmt_list = []
        while self.current_token and self.current_token.type not in ('CLOSE_BRACE', 'EOF'):
            #print(f"🔎 DEBUG: Chamando parse_stmt() para {self.current_token}")  # DEBUG
            stmt = self.parse_stmt()
            #print(f"✅ DEBUG: parse_stmt() retornou {stmt}")  # DEBUG
            if stmt:
                stmt_list.append(stmt)
        return stmt_list

   



    def parse_stmt(self):
        """<stmt> -> <forStmt> | <ioStmt> | <whileStmt> | <atrib> ';' | <ifStmt> | <bloco> | 'break' | 'continue' | <declaration> | ';'"""

        #print(f"🔍 Processando statement, token atual: {self.current_token}")

        if self.current_token is None:
            raise SyntaxError("❌ Erro de sintaxe: Token inesperado (EOF encontrado).")

        if self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme in ['int', 'float', 'string']:  # Declaração
            self.parse_declaration()
            return "DECLARATION"  # 🔹 Retorna algo válido

        elif self.current_token.type == 'VARIABLE':  # Atribuição
            #print("Chamando parse atrib")
            atrib_node = self.parse_atrib()
            return atrib_node

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'if':  # Condicional if
            return self.parse_if_stmt()

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'while':
             return self.parse_while_stmt()  # ✅ Agora reconhece 'while'

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'for':  # Laço for
            return self.parse_for_stmt()

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'system':  # Entrada/Saída
            return self.parse_io_stmt()

        elif self.current_token.type == 'OPEN_BRACE':  # Bloco de código '{...}'
            self.match('OPEN_BRACE')
            stmt_list_node = self.parse_stmt_list()
            self.match('CLOSE_BRACE')
            return stmt_list_node

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'break':  # Break
            self.match('IDENTIFIER')
            self.match('SEMICOLON')
            return Node("break")

        elif self.current_token.type == 'IDENTIFIER' and self.current_token.lexeme == 'continue':  # Continue
            self.match('IDENTIFIER')
            self.match('SEMICOLON')
            return Node("continue")

        elif self.current_token.type == 'SEMICOLON':  # Apenas um ';' (vazio)
            self.match('SEMICOLON')
            return Node("empty")

        else:
            raise SyntaxError(f"❌ Erro de sintaxe: Token inesperado '{self.current_token.lexeme}' na linha {self.current_token.line}")




    def parse_declaration(self):
        """<declaration> -> <type> <identList> ';' """
        #print(f"🔍 DEBUG: Entrando em parse_declaration(), token atual: {self.current_token}")

        tipo = self.match('IDENTIFIER').lexeme  # Obtém o tipo da variável
        vars_declaradas = self.parse_ident_list()  # Agora retorna uma lista
        self.match('SEMICOLON')  # Confirma o ponto e vírgula

        if not vars_declaradas:  # Verifica se a lista está vazia
            raise SyntaxError("❌ Erro: Nenhuma variável foi declarada.")

        for var in vars_declaradas:
            if tipo == 'int':
                self.code.append(("=", var, "0", None))
            elif tipo == 'float':
                self.code.append(("=", var, "0.0", None))
            elif tipo == 'string':
                self.code.append(("=", var, '""', None))  # Usar aspas duplas

        #print(f"✅ DEBUG: Declaração processada -> {tipo} {vars_declaradas}")
        return vars_declaradas




    def parse_ident_list(self):
        """<identList> -> 'IDENT' <restoIdentList>"""
        ident_list = []  # Inicializa uma lista vazia para armazenar os identificadores
        
        ident = self.match('VARIABLE').lexeme  # Obtém o primeiro identificador
        ident_list.append(ident)

        while self.current_token.type == 'COMMA':  # Se houver mais variáveis separadas por vírgula
            self.match('COMMA')
            ident = self.match('VARIABLE').lexeme
            ident_list.append(ident)

        #print(f"✅ DEBUG: Lista de identificadores reconhecidos -> {ident_list}")
        return ident_list  # Retorna uma lista de variáveis, não um Node


        

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


    def parse_for_stmt(self):
        label_start = self.generate_label()  # Label para início do loop
        label_body = self.generate_label()   # Label para o corpo do loop
        label_end = self.generate_label()    # Label para sair do loop

        # 1. Inicialização
        self.match('IDENTIFIER')  # 'for'
        self.match('OPEN_PAREN')
        self.parse_opt_atrib()  # Ex: i = 0
        self.match('SEMICOLON')

        # 2. Condição
        self.code.append(("LABEL", label_start, None, None))
        temp_cond = self.generate_temp()
        cond_node = self.parse_expr()  # Processa a condição
        self.gerar_operacao('=', temp_cond, cond_node, None)
        self.match('SEMICOLON')

        # 3. Se condição falsa, pula para o fim
        self.code.append(("IF", temp_cond, label_end, label_body))  # Corrigir labels

        # 4. Incremento (armazenar em uma label separada)
        incremento_label = self.generate_label()
        self.code.append(("LABEL", incremento_label, None, None))
        incremento = self.parse_opt_atrib()  # Ex: i += 1
        self.match('CLOSE_PAREN')

        # 5. Corpo do loop
        self.code.append(("LABEL", label_body, None, None))
        self.parse_stmt()

        # 6. Voltar para o incremento e depois verificar a condição
        self.code.append(("JUMP", incremento_label, None, None))
        self.code.append(("LABEL", label_end, None, None))





    def parse_opt_atrib(self):
        """Processa atribuições opcionais dentro do `for`."""
        print(f"🔍 DEBUG: Entrando em parse_opt_atrib(), token atual: {self.current_token}")

        if self.current_token and self.current_token.type == 'VARIABLE':
            atrib = self.parse_atrib()
            print(f"✅ DEBUG: Atribuição reconhecida -> {atrib}")

            # ⚠️ **REMOVA O CONSUMO DE `;` AQUI!**
            return atrib

        elif self.current_token and self.current_token.type == 'SEMICOLON':
            # ⚠️ **RETORNE `None`, mas não consuma `;` aqui!**
            print("✅ DEBUG: Nenhuma atribuição encontrada, retornando `None`.")
            return None

        else:
            raise SyntaxError(f"Erro de sintaxe: esperado atribuição ou `;`, encontrado {self.current_token}")




    def parse_opt_expr(self):
        """<optExpr> -> <expr> & ;"""
        print(f"🔍 DEBUG: Entrando em parse_opt_expr(), token atual: {self.current_token}")

        # Se houver uma expressão (variável ou número inicial), processamos
        if self.current_token and self.current_token.type in ['VARIABLE', 'DECIMAL_INT', 'FLOAT', 'STRING']:
            expr = self.parse_expr()  # Essa chamada precisa processar toda a expressão, não só um token
            print(f"✅ DEBUG: Expressão reconhecida -> {expr}")

            # Agora, verificamos se o próximo token é um `;`
            if self.current_token and self.current_token.type == 'SEMICOLON':
                print(f"✅ DEBUG: `;` encontrado após expressão -> {self.current_token}")
                self.match('SEMICOLON')
            else:
                raise SyntaxError(f"❌ ERRO: `;` esperado após expressão, encontrado {self.current_token}")

            return expr

        # Se não houver expressão, apenas consumir `;`
        elif self.current_token and self.current_token.type == 'SEMICOLON':
            print("✅ DEBUG: Nenhuma expressão encontrada, apenas `;` consumido.")
            self.match('SEMICOLON')
            return None

        else:
            print(f"❌ ERRO: Expressão inválida encontrada -> {self.current_token}")
            raise SyntaxError(f"Erro de sintaxe: esperado expressão ou `;`, encontrado {self.current_token}")




    def parse_io_stmt(self):
        """<ioStmt> -> 'system' '.' ('in' | 'out') '.' IDENTIFIER '(' <outList> ')' ';'"""
        self.match('IDENTIFIER')  # Consome 'system'
        self.match('DOT')

        io_type = self.current_token.lexeme  # 'in' ou 'out'
        self.match('IDENTIFIER')
        self.match('DOT')

        io_action = self.current_token.lexeme  # 'scan' ou 'print'
        self.match('IDENTIFIER')
        self.match('OPEN_PAREN')

        if io_type == 'in' and io_action == 'scan':
            tipo = self.match('IDENTIFIER').lexeme  # Tipo da variável
            self.match('COMMA')
            var_name = self.match('VARIABLE').lexeme  # Nome da variável
            self.match('CLOSE_PAREN')
            self.match('SEMICOLON')
            self.code.append(("CALL", "SCAN", tipo, var_name))  # ✅ Mantém a estrutura antiga de I/O

        elif io_type == 'out' and io_action == 'print':
            output_list = self.parse_out_list()
            self.match('CLOSE_PAREN')
            self.match('SEMICOLON')

            for item in output_list:
                self.code.append(("CALL", "PRINT", item, None))  # ✅ Mantém a estrutura antiga de I/O

        else:
            raise SyntaxError(f"❌ Erro de sintaxe: I/O inválido '{io_type}.{io_action}'")

    def parse_out_list(self):
        """<outList> -> <out> <restoOutList>"""
        print("🔍 DEBUG: Entrando em parse_out_list()")  # ✅ Confirma a entrada

        output_list = []

        # 📌 CHAMADA OBRIGATÓRIA de parse_out()
        out_value = self.parse_out()
        print(f"✅ DEBUG: parse_out() retornou -> {out_value}")  # 🔍 Confirma retorno
        output_list.append(out_value)

        # 📌 CHAMADA OBRIGATÓRIA de parse_resto_out_list()
        resto_out_values = self.parse_resto_out_list()
        print(f"✅ DEBUG: parse_resto_out_list() retornou -> {resto_out_values}")  # 🔍 Confirma retorno

        output_list.extend(resto_out_values)
        
        return output_list






    def parse_out(self):
        """<out> -> 'STR' | 'IDENT' | 'NUMdec' | 'NUMfloat' | 'NUMoct' | 'NUMhex'"""
        print("🔍 DEBUG: Entrando em parse_out()")  # Confirma entrada

        token_tipo = self.current_token.type

        if token_tipo in ('STRING', 'VARIABLE', 'DECIMAL_INT', 'FLOAT', 'OCTAL_INT', 'HEXADECIMAL_INT'):
            valor = self.match(token_tipo).lexeme
            print(f"✅ DEBUG: parse_out() reconheceu -> {valor}")  # Confirma saída
            return valor.replace("'", '"')
        elif token_tipo == 'STRING':
            return f'"{valor}"'
        else:
            raise SyntaxError(f"❌ Erro de sintaxe: Token inesperado {self.current_token}")

    def parse_resto_out_list(self):
        """<restoOutList> -> ',' <out> <restoOutList> | &"""
        output_list = []
        
        # Enquanto houver vírgula, continua processando a lista de saída
        while self.current_token.type == 'COMMA':
            self.match('COMMA')  # Consome a vírgula
            output_item = self.parse_out()  # Chama parse_out para processar o próximo item
            output_list.append(output_item)  # Adiciona o item processado na lista
        
        return output_list
   
    def parse_while_stmt(self):
        """<whileStmt> -> 'while' '(' <expr> ')' <stmt>"""
        self.match('IDENTIFIER')  # Consome 'while'
        self.match('OPEN_PAREN')
        label_start = self.generate_label()  # Label de INÍCIO do loop
        label_end = self.generate_label()    # Label de SAÍDA do loop

        self.code.append(("LABEL", label_start, None, None))  # ✅ Define início

        # Processa a condição
        condition_node = self.parse_expr()
        temp_cond = self.generate_temp()
        self.gerar_operacao('=', temp_cond, condition_node, None)

        self.match('CLOSE_PAREN')
        
        # ✅ Se a condição for FALSA, pula para o FIM
        self.code.append(("IF", temp_cond, label_end, label_start))  # Alterado

        # Processa o corpo do loop
        self.parse_stmt()

        # ✅ Incremento/adiciona lógica de saída (EXEMPLO: a = a + 1)
        self.gerar_operacao('+', 'a', 'a', '1')  # 🔥 Linha adicionada para modificar a variável

        # ✅ Volta para verificar a condição novamente
        self.code.append(("JUMP", label_start, None, None))

        # ✅ Define a label de SAÍDA
        self.code.append(("LABEL", label_end, None, None))


    def parse_if_stmt(self):
        """<ifStmt> -> 'if' '(' <expr> ')' <stmt> <elsePart> ;"""
        self.match('IDENTIFIER')  # Consome 'if'
        self.match('OPEN_PAREN')

        # Processa a condição
        condition_node = self.parse_expr()
        temp_cond = self.generate_temp()
        self.gerar_operacao('=', temp_cond, condition_node, None)

        self.match('CLOSE_PAREN')

        # ✅ Gera e define labels ANTES do IF
        label_else = self.generate_label()
        label_end = self.generate_label()
        
        self.code.append(("LABEL", label_else, None, None))  # ✅ Adicionado
        self.code.append(("LABEL", label_end, None, None))    # ✅ Adicionado

        # ✅ Ajuste na ordem: IF usa labels já definidas
        self.code.append(("IF", temp_cond, label_else, label_end)) 

        # Processa bloco do IF
        self.parse_stmt()

        # Pula para o fim
        self.code.append(("JUMP", label_end, None, None))

        # Processa else se existir
        if self.current_token and self.current_token.lexeme == 'else':
            self.match('IDENTIFIER')
            self.parse_stmt()

        # Define label do fim
        self.code.append(("LABEL", label_end, None, None))

    def parse_else_part(self, label_else):
        """<elsePart> -> 'else' <stmt> | & ;"""
        
        if self.current_token and self.current_token.lexeme == 'else':
            print(f"✅ DEBUG: 'else' encontrado, processando bloco ELSE...")
            self.match('IDENTIFIER')  # Consome 'else'
            self.code.append(("LABEL", label_else, None, None))  # Define a label do else
            self.parse_stmt()  # Processa o bloco do else
        else:
            # Se não houver 'else', a label_else ainda precisa ser registrada para evitar erros
            self.code.append(("LABEL", label_else, None, None))






    def extract_expression(self, node):
        """Converte um nó da AST para uma string de expressão"""
        if node is None:
            return ""

        if isinstance(node, Node):
            if node.node_type == "binary_op":
                left = self.extract_expression(node.children[0])
                right = self.extract_expression(node.children[1])
                return f"{left} {node.value} {right}"
            elif node.node_type == "unary_op":
                operand = self.extract_expression(node.children[0])
                return f"{node.value} {operand}"
            elif node.node_type in ["variable", "literal", "temp_var"]:
                return str(node.value)
            else:
                return f"<Erro: Tipo de nó desconhecido {node.node_type}>"

        return str(node)  # Caso já seja um valor simples

    def parse_atrib(self):
        """<atrib> -> 'IDENT' '=' <expr> | 'IDENT' ('+=' | '-=' | '*=' | '/=' | '%=') <expr>"""
        print(f"🔍 DEBUG: Entrando em parse_atrib(), token atual: {self.current_token}")

        ident = self.match('VARIABLE').lexeme
        print(f"🔍 DEBUG: Identificador reconhecido -> {ident}")

        operador = self.match(['ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN']).lexeme
        print(f"🔍 DEBUG: Operador de atribuição reconhecido -> {operador}")

        # Processa a expressão à direita do operador
        expr_node = self.parse_expr()

        # Gera código intermediário para operadores compostos (ex: +=, -=)
        if operador != '=':
            temp_var = self.generate_temp()
            self.gerar_operacao(operador[0], temp_var, ident, expr_node)  # operador[0] é '+', '-', etc.
            self.gerar_operacao('=', ident, temp_var, None)
        else:
            self.gerar_operacao(operador, ident, expr_node, None)

        return Node("atrib", [ident, expr_node])


    def parse_term(self):
        """<term> -> <factor> ('*' | '/' | '%') <factor>*"""
        left_node = self.parse_factor()

        while self.current_token and self.current_token.type in ['MUL', 'DIV', 'MOD']:
            operator = self.current_token.lexeme
            self.next_token()
            right_node = self.parse_factor()
            temp_var = self.generate_temp()

            #print(f"✅ DEBUG: Operação detectada: {left_node} {operator} {right_node} -> armazenado em {temp_var}")  # Debug print
            self.code.append((operator, temp_var, left_node.value, right_node.value))
            left_node = Node("binary_op", [left_node, right_node], temp_var)

        return left_node

    def parse_expr(self):
        """<expr> -> <or>"""
        print(f"🔍 DEBUG: Entrando em parse_expr(), token atual: {self.current_token}")
        resultado = self.parse_or()
        print(f"✅ DEBUG: parse_expr() retornou -> {resultado}")
        return resultado
    

    def parse_or(self):
        """<or> -> <and> <restoOr>"""
        print("🔍 DEBUG: Entrando em parse_or()")
        left = self.parse_and()
        return self.parse_resto_or(left)

    def parse_resto_or(self, left):
        """<restoOr> -> '||' <and> <restoOr> | &"""
        while self.current_token.type == 'OR':
            operador = self.match('OR').lexeme
            right = self.parse_and()
            temp_var = self.gerar_temp()
            self.code.append((operador, temp_var, left, right))
            left = temp_var
        return left




    def parse_and(self):
        """<and> -> <not> <restoAnd>"""
        print("🔍 DEBUG: Entrando em parse_and()")
        left = self.parse_not()
        return self.parse_resto_and(left)

    def parse_resto_and(self, left):
        """<restoAnd> -> '&&' <not> <restoAnd> | &"""
        while self.current_token.type == 'AND':
            operador = self.match('AND').lexeme
            right = self.parse_not()
            temp_var = self.gerar_temp()
            self.code.append((operador, temp_var, left, right))
            left = temp_var
        return left




    def parse_not(self):
        """<not> -> '!' <not> | <rel>"""
        print(f"Processando NOT, token atual: {self.current_token}")
        if self.current_token and self.current_token.type == 'LOGICAL_NOT':
            operator_token = self.current_token
            self.next_token()  
            not_node = self.parse_not()  
            return Node("unary_op", [not_node], operator_token.lexeme)  

        return self.parse_rel()  # Passa para o próximo nível


    def parse_rel(self):
        left = self.parse_add()
        if self.current_token.type in ['EQUAL', 'NOT_EQUAL', 'GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']:
            operador = self.match(self.current_token.type).lexeme
            right = self.parse_add()
            
            # ✅ Remova a verificação de tipo estática
            temp_var = self.generate_temp()
            self.code.append((operador, temp_var, left, right))
            return temp_var
        return left

    def parse_resto_rel(self, left):
        """<restoRel> -> ('==' | '!=' | '<' | '<=' | '>' | '>=') <add> | &"""
        operadores_relacionais = {'EQUAL', 'NOT_EQUAL', 'GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'}
        print(f"🔍 DEBUG: Token atual em parse_resto_rel: {self.current_token}")  # DEBUG ADICIONADO
        
        if self.current_token and self.current_token.type in operadores_relacionais:
            operador = self.match(self.current_token.type).lexeme
            print(f"✅ DEBUG: Operador relacional reconhecido -> {operador}")  # DEBUG ADICIONADO
            right = self.parse_add()
            temp_var = self.generate_temp()
            self.code.append((operador, temp_var, left, right))
            return temp_var
        
        print(f"✅ DEBUG: Nenhum operador relacional encontrado. Token atual: {self.current_token}")  # DEBUG ADICIONADO
        return left



    def parse_add(self):
        """<add> -> <mult> <restoAdd>"""
        print(f"🔍 DEBUG: Entrando em parse_add(), token atual: {self.current_token}")
        left = self.parse_mult()
        print(f"✅ DEBUG: parse_add() reconheceu primeiro termo -> {left}")
        return self.parse_resto_add(left)

    def parse_resto_add(self, left):
        """<restoAdd> -> '+' <mult> <restoAdd> | '-' <mult> <restoAdd> | &"""
        print(f"🔍 DEBUG: Entrando em parse_resto_add(), token atual: {self.current_token}")

        while self.current_token and self.current_token.type in ('ADD', 'SUB'):
            print(f"🔎 DEBUG: Esperado operador '+' ou '-', encontrado -> {self.current_token}")

            operador = self.match(self.current_token.type).lexeme  # Consome '+' ou '-'
            print(f"✅ DEBUG: parse_resto_add() reconheceu operador -> {operador}")

            right = self.parse_mult()  # Obtém o próximo termo da multiplicação
            print(f"✅ DEBUG: parse_resto_add() reconheceu segundo termo -> {right}")

            temp_var = self.generate_temp()
            self.code.append((operador, temp_var, left, right))
            left = temp_var

        print(f"✅ DEBUG: parse_resto_add() retornando -> {left}")
        return left





    def parse_mult(self):
        """<mult> -> <uno> <restoMult>"""
        print("🔍 DEBUG: Entrando em parse_mult()")
        left = self.parse_uno()
        return self.parse_resto_mult(left)

    def parse_resto_mult(self, left):
        """<restoMult> -> '*' <uno> <restoMult> | '/' <uno> <restoMult> | '%' <uno> <restoMult> | &"""
        while self.current_token.type in ('DIV', 'MOD', 'MUL'):
            operador = self.match(self.current_token.type).lexeme
            right = self.parse_uno()
            temp_var = self.generate_temp()
            self.code.append((operador, temp_var, left, right))
            left = temp_var
        return left


    

            
        
    def parse_uno(self):
        """<uno> -> '+' <uno> | '-' <uno> | <factor>"""
        print(f"Processando UNO, token atual: {self.current_token}")
        if self.current_token and self.current_token.type in ['ADD', 'SUB']:
            operator_token = self.current_token
            self.next_token()
            uno_node = self.parse_uno()
            return Node("unary_op", [uno_node], operator_token.lexeme)

        return self.parse_factor()  


            
    def parse_factor(self):
        """<fator> -> 'NUMint' | 'NUMfloat' | 'NUMoct' | 'NUMhex' | 'IDENT' | '(' <expr> ')' | 'STR'"""
        print(f"🔍 DEBUG: Entrando em parse_factor(), token atual: {self.current_token}")  

        token_atual = self.current_token  # Obtém o token atual

        if token_atual.type in ('FLOAT', 'SCIENTIFIC_FLOAT'):
            # Converte para float
            valor = float(token_atual.lexeme)
            self.next_token()
            print(f"✅ DEBUG: Número float reconhecido -> {valor}")
            return valor
        elif token_atual.type == 'DECIMAL_INT':
            # Converte para int (base 10)
            valor = int(token_atual.lexeme)
            self.next_token()
            print(f"✅ DEBUG: Número inteiro reconhecido -> {valor}")
            return valor
        elif token_atual.type == 'OCTAL_INT':
            # Converte octal (ex: '0755' → 493)
            valor = int(token_atual.lexeme, 8)
            self.next_token()
            print(f"✅ DEBUG: Octal reconhecido → {valor}")
            return valor
        elif token_atual.type == 'HEXADECIMAL_INT':
            # Converte hexadecimal (ex: '0xFF' → 255)
            valor = int(token_atual.lexeme, 16)
            self.next_token()
            print(f"✅ DEBUG: Hexadecimal reconhecido → {valor}")
            return valor
        elif token_atual.type == 'VARIABLE':
            valor = self.match('VARIABLE').lexeme
            print(f"✅ DEBUG: Variável reconhecida -> {valor}")
            return valor
        elif token_atual.type == 'STRING':
            valor = self.match('STRING').lexeme
            print(f"✅ DEBUG: String reconhecida -> {valor}")
            return valor
        elif token_atual.type == 'OPEN_PAREN':
            self.match('OPEN_PAREN')
            expr_val = self.parse_expr()
            self.match('CLOSE_PAREN')
            return expr_val
        else:
            raise SyntaxError(f"❌ Erro de sintaxe: Token inesperado {token_atual}")





        



# Código principal para executar o parser
"""if __name__ == "__main__":
   
    import lexico, sys

    if len(sys.argv) > 1:
        try:
            # Chame lexico.main com o nome do arquivo como argumento
            tokens1 = lexico.main(sys.argv[1])  # Retorna a lista de tokens

            if not tokens1 or not isinstance(tokens1, list):
                raise ValueError("A lista de tokens está vazia ou em um formato incorreto. Verifique o lexico.py.")

            print("\n--- Lista de Tokens Gerados ---")
            for token in tokens1:
                print(token)  # Exibe os tokens para depuração
            print("--- Fim da Lista de Tokens ---\n")

            # Inicializa o parser com a lista de tokens
            parser = Parser(tokens1)

            # Gera a árvore sintática
            root_node = parser.parse_function()
            for instrucao in parser.code:
                print(instrucao)

            # Imprime a árvore sintática
            #print("Árvore sintática gerada:")
            #print(root_node)

        except SyntaxError as e:
            print(f"Erro de sintaxe: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    else:
        print("Erro: Nenhum arquivo foi especificado. Por favor, forneça o nome do arquivo.")
        sys.exit(1)
    """
def main(tokens):
    try:
        parser = Parser(tokens)
        root_node = parser.parse_function()
        return parser.code
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
        return []    
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            import lexico
            tokens = lexico.main(sys.argv[1])
            codigo = main(tokens)
            for instrucao in codigo:
                print(instrucao)
        except Exception as e:
            print(f"Erro: {e}")
    else:
        print("Erro: Nenhum arquivo foi especificado.")    