import sys
import ast

class Interpretador:
    def __init__(self, instrucoes):
        self.instrucoes = instrucoes  # Lista de instruções carregadas
        self.variaveis = {}  # Armazena variáveis e seus valores
        self.temp_vars = {}  # Armazena variáveis temporárias (usadas para cálculos)
        self.labels = {}  # Dicionário para armazenar rótulos (LABEL)
        self.current_instrucao = 0  # Índice da instrução atual
        self.preprocess_labels()  # Pré-processa os rótulos antes da execução

    def preprocess_labels(self):
        for idx, instrucao in enumerate(self.instrucoes):
            if isinstance(instrucao, (list, tuple)) and instrucao[0] == "LABEL":
                label_name = instrucao[1]
                self.labels[label_name] = idx
                print(f"✅ DEBUG: Label '{label_name}' registrada na posição {idx}")
                      
    def armazenar_variaveis(self):
        """ Armazena todas as variáveis declaradas antes da execução """
        for instrucao in self.instrucoes:
            if isinstance(instrucao, tuple) and instrucao[0] == "=":
                var = instrucao[1]
                if var not in self.variaveis:
                    self.variaveis[var] = None  # Inicializa variável sem valor
                    
    def rodar(self):
        """Executa as instruções interpretadas até atingir um limite de iterações."""
        self.armazenar_variaveis()
        max_iteracoes = 200 # Limite de iterações para evitar loops infinitos
        contarInteracao = 0
        print("🔍 Labels registradas:", self.labels)  # Antes de executar
        while self.current_instrucao < len(self.instrucoes) and contarInteracao < max_iteracoes:
            contarInteracao += 1
            instrucao = self.instrucoes[self.current_instrucao]
            operator = instrucao[0]  # Identifica a operação da instrução

            try:
                print(f"🔍 DEBUG: Processando instrução: {instrucao}")
                if not isinstance(instrucao, (tuple, list)) or len(instrucao) < 4:
                    raise ValueError(f"❌ ERRO: Instrução mal formada! Recebido: {instrucao}")
                if operator == "=":
                    self.atribuir(instrucao)
                elif operator == "CALL":
                    self.system_call(instrucao)
                elif operator in ["+", "-", "*", "/", "%", "//"]:
                    self.operar_aritimetica(instrucao)
                elif operator in ["||", "&&", "!", "==", "<>", ">", ">=", "<", "<=","!="]:
                    self.operarLogica(instrucao)
                elif operator == "IF":
                    self.conditional_jump(instrucao)
                elif operator == "JUMP":
                    self.jump(instrucao)
                elif operator == "LABEL":
                    pass  # Labels já foram processados no pré-processamento
                else:
                    raise ValueError(f"Operador desconhecido: {operator}")

                self.current_instrucao += 1  # Avança para a próxima instrução
            except Exception as e:
                print(f"Erro na instrução {self.current_instrucao}: {instrucao} - {e}")
                break

        if contarInteracao >= max_iteracoes:
            print("Número máximo de iterações atingido.")

    """def obt_valor(self, operand):
        #Retorna o valor do operando, garantindo que seja numérico quando necessário.
        
        if operand is None:
            return 0  # 🔴 Evita erros ao operar com valores nulos

        if isinstance(operand, (int, float, bool)):
            return operand  # Já é número, retorna direto

        if isinstance(operand, str):
            # 🔴 Se for uma string que representa um número, converte para int ou float
            try:
                if operand.replace('.', '', 1).isdigit():
                    return float(operand) if '.' in operand else int(operand)
                elif operand.lower().startswith("0x"):  # Hexadecimal
                    return int(operand, 16)
                elif operand.lower().startswith("0") and operand != "0":  # Octal
                    return int(operand, 8)
            except ValueError:
                pass

            # 🔴 Busca a variável no interpretador
            valor_variavel = self.variaveis.get(operand, self.temp_vars.get(operand, operand))

            # 🔴 Se a variável armazenada for string numérica, converte
            if isinstance(valor_variavel, str) and valor_variavel.replace('.', '', 1).isdigit():
                return float(valor_variavel) if '.' in valor_variavel else int(valor_variavel)

            return valor_variavel

        return operand"""
    def obt_valor(self, operand):
        if operand is None:
            return 0
        
        # Verifica se é uma variável
        if isinstance(operand, str) and (operand in self.variaveis or operand in self.temp_vars):
            valor = self.variaveis.get(operand, self.temp_vars.get(operand))
            # Converte strings numéricas para int/float
            if isinstance(valor, str):
                if valor.startswith('"') and valor.endswith('"'):  # É uma string literal
                    return valor.strip('"')
                try:
                    return float(valor) if '.' in valor else int(valor)
                except:
                    return valor
            return valor
        
        # Se for uma string literal (ex: "hello")
        if isinstance(operand, str) and operand.startswith('"') and operand.endswith('"'):
            return operand.strip('"')
        
        return operand

    def print_valor(self, valor1, valor2):
        """Imprime corretamente valores e interpreta caracteres especiais como \t e \n."""
        
        def formatar_saida(valor):
            if isinstance(valor, str):
                return valor.strip('"').encode().decode('unicode_escape')
            return valor

        saida1 = formatar_saida(self.obt_valor(valor1)) if valor1 is not None else ""
        saida2 = formatar_saida(self.obt_valor(valor2)) if valor2 is not None else ""

        print(f"{saida1} {saida2}".strip())  # 🔴 Evita espaço extra no final

    def operar_aritimetica(self, instrucao):
        """Executa operações aritméticas básicas com tratamento de tipos e erros."""
        operator, destino, op1, op2 = instrucao
        try:
            # Conversão segura para números
            def converter(valor):
                if isinstance(valor, (int, float)):
                    return valor
                try:
                    return float(valor) if '.' in valor else int(valor)
                except:
                    return self.obt_valor(valor)  # Caso seja referência a outra variável

            val1 = converter(op1)
            val2 = converter(op2) if op2 is not None else None

            # Operações aritméticas
            result = {
                "+": val1 + val2,
                "-": val1 - val2,
                "*": val1 * val2,
                "/": val1 / val2 if val2 != 0 else float('inf'),
                "%": val1 % val2 if val2 != 0 else 0,
                "//": val1 // val2 if val2 != 0 else 0,
            }.get(operator, 0)

        except ZeroDivisionError:
            print(f"Erro: Divisão por zero em {instrucao}")
            result = float('inf')
        except Exception as e:
            print(f"Erro na operação {operator}: {str(e)}")
            result = 0

        self.armazen_restado(destino, result)

    def operarLogica(self, instrucao):
        operator, destino, op1, op2 = instrucao
        try:
            val1 = self.obt_valor(op1)
            val2 = self.obt_valor(op2) if op2 is not None else None

            # Verificar se os tipos são comparáveis
            if (isinstance(val1, (int, float)) and isinstance(val2, str)) or \
            (isinstance(val2, (int, float)) and isinstance(val1, str)):
                raise TypeError("Comparação entre número e string não permitida")

            # Permite comparação entre booleanos e inteiros (True=1, False=0)
            if isinstance(val1, bool) and isinstance(val2, (int, float)):
                val1 = int(val1)
            elif isinstance(val2, bool) and isinstance(val1, (int, float)):
                val2 = int(val2)
                
            # Remover a verificação redundante
            # if isinstance(val1, str) or isinstance(val2, str):
            #    raise TypeError("Comparação entre string e número não permitida")   

            # Type checking
            if type(val1) != type(val2):
                raise TypeError(f"Comparação inválida: {val1} ({type(val1)}) e {val2} ({type(val2)})")

            # Logical operators
            result = {
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
                ">": lambda a, b: a > b,
                ">=": lambda a, b: a >= b,
                "<": lambda a, b: a < b,
                "<=": lambda a, b: a <= b,
            }[operator](val1, val2)

        except KeyError:
            print(f"Operador lógico inválido: {operator}")
            result = False
        except Exception as e:
            print(f"Erro na operação lógica: {str(e)}")
            result = False

        self.armazen_restado(destino, result)

    def armazen_restado(self, destino, valor):
        """Armazena o resultado de uma operação em uma variável."""
        if destino.startswith("__temp"):
            self.temp_vars[destino] = valor
        else:
            self.variaveis[destino] = valor

    def atribuir(self, instrucao):
        """Atribui um valor a uma variável."""
        _, destino, valor, _ = instrucao
        valor_resolvido = self.obt_valor(valor)
        
        # 🔴 Debug para verificar se a variável está sendo armazenada corretamente
        #print(f"📌 Atribuindo: {destino} = {valor} (resolvido: {valor_resolvido})")

        if valor_resolvido is not None:
            self.variaveis[destino] = valor_resolvido
        else:
            #print(f"⚠️ Erro: Tentativa de atribuir 'None' a {destino}, definindo como 0.")
            self.variaveis[destino] = 0  # 🔴 Agora inicializa a variável corretamente




    def conditional_jump(self, instrucao):
        """Realiza um desvio condicional baseado no valor da condição."""
        _, condition, label1, label2 = instrucao
        print(f"🔍 DEBUG: Valor de {condition} = {self.obt_valor(condition)}")

        condition_valor = self.obt_valor(condition)

        # ✅ Depuração: Exibir informações do IF antes da execução
        print(f"🔍 DEBUG: Executando IF: condition={condition}, label1={label1}, label2={label2}")

        # ⚠️ Se qualquer label for None, gera um erro crítico
        if label1 is None or label2 is None:
            raise ValueError(f"❌ ERRO CRÍTICO: IF gerado com label inválida! Condição={condition}, Label1={label1}, Label2={label2}")

        next_label = label1 if condition_valor else label2

        # ✅ Verifica se a label realmente foi registrada antes de acessar
        if next_label not in self.labels:
            raise ValueError(f"❌ ERRO CRÍTICO: Label {next_label} não encontrada no interpretador! Labels registradas: {self.labels}")

        # Salta para a instrução da label
        self.current_instrucao = self.labels[next_label]



    def jump(self, instrucao):
        """Realiza um salto incondicional para um rótulo."""
        _, label, *_ = instrucao
        if label in self.labels:
            self.current_instrucao = self.labels[label] - 1 #subtraindo 1 para que a próxima instrução seja a instrução do label
        else:
            raise ValueError(f"Label {label} não encontrado.")

    def system_call(self, instrucao):
        _, comando, arg1, arg2 = instrucao

        if comando == "PRINT":
            self.print_valor(arg1, arg2)

        elif comando == "SCAN":
            tipo = arg1
            variavel = arg2

            # 🔴 Se a variável não existe no dicionário, inicializá-la antes da leitura
            if variavel not in self.variaveis:
                #print(f"⚠️ Variável '{variavel}' não declarada antes do SCAN. Inicializando como 0.")
                self.variaveis[variavel] = 0

            valor_lido = input(f"Digite um valor para {variavel} ({tipo}): ")
            if tipo == "int":
                self.variaveis[variavel] = int(valor_lido)
            elif tipo == "float":
                self.variaveis[variavel] = float(valor_lido)
            else:
                self.variaveis[variavel] = valor_lido

            #print(f"📌 Variável '{variavel}' recebeu o valor: {self.variaveis[variavel]}")


# Carrega e processa código intermediário

def load_intermediario_cod(path):
    with open(path, "r") as file:
        conteudo = file.read().strip().splitlines() #lendo o arquivo e separando por linhas

    intruções = []
    for linha in conteudo:
        try:
            instrucao = ast.literal_eval(linha) 
            #u sando ast.literal_eval para converter a string em uma lista e para não ter problemas com segurança
            if isinstance(instrucao, (tuple, list)):
                if isinstance(instrucao[0], tuple):#se a primeira posição for uma tupla, a instrução será uma lista de instruções
                    instrucao = instrucao[0]
                intruções.append(instrucao)
        except Exception as e:
            print(f"Erro ao processar a instrução: {linha} - {e}")
    return intruções

# Função principal

def main(path):
    instruções = load_intermediario_cod(path)
    Inter = Interpretador(instruções)
    Inter.rodar()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Erro: Nenhum arquivo foi especificado. Por favor, forneça o nome do arquivo.")
        sys.exit(1)
