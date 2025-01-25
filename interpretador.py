class Interpretador:
    def __init__(self, tuplas):
        self.tuplas = tuplas
        self.variaveis = {}
        self.variaveis_temporarias = {}
        self.labels = {}
        self.instrucao_atual = 0
        self.preprocessar_labels()

    def preprocessar_labels(self):
        # Processa labels e as armazena com suas posições
        for index, instrucao in enumerate(self.tuplas):
            if isinstance(instrucao, (list, tuple)) and len(instrucao) > 0 and isinstance(instrucao[0], str):
                if instrucao[0].upper() == 'LABEL':
                    label_name = instrucao[1]
                    self.labels[label_name] = index

    def executar(self):
        contador = 0  # Limite para evitar loops infinitos
        max_iteracoes = 150  # Ajuste conforme necessário
        while self.instrucao_atual < len(self.tuplas) and contador < max_iteracoes:
            contador += 1
            instrucao = self.tuplas[self.instrucao_atual]
            operador = instrucao[0]

            try:
                operacoes = {
                    "=": self.atribuicao,
                    "CALL": self.chamada_sistema,
                    "+": self.operacao_aritmetica,
                    "-": self.operacao_aritmetica,
                    "*": self.operacao_aritmetica,
                    "/": self.operacao_aritmetica,
                    "%": self.operacao_aritmetica,
                    "//": self.operacao_aritmetica,
                    "||": self.operacao_logica,
                    "&&": self.operacao_logica,
                    "!": self.operacao_logica,
                    "==": self.operacao_logica,
                    "<>": self.operacao_logica,
                    ">": self.operacao_logica,
                    ">=": self.operacao_logica,
                    "<": self.operacao_logica,
                    "<=": self.operacao_logica,
                    "IF": self.condicional,
                    "JUMP": self.salto,
                    "LABEL": lambda x: None,
                }

                if operador in operacoes:
                    operacoes[operador](instrucao)
                else:
                    raise ValueError(f"Operador desconhecido: {operador}")

                self.instrucao_atual += 1
            except Exception as e:
                print(f"Erro na instrução {self.instrucao_atual}: {instrucao} - {e}")
                break

            if contador >= max_iteracoes:
                print("Número máximo de iterações atingido.")
                break

    def obter_valor(self, operando):
        # Diagnóstico: Verificar o valor do operando
        #print(f"Obtendo valor para {operando}")
        if operando is None:
            return None
        if isinstance(operando, (int, float, bool)):
            return operando
        if operando.isdigit():
            return int(operando)
        valor = self.variaveis.get(operando, self.variaveis_temporarias.get(operando))
       # print(f"Valor encontrado: {valor}")
        return valor

    def processar_print(self, valor, variavel):
        # Diagnóstico: Verificar valores antes de imprimir
        #print(f"Preparando para imprimir: valor={valor}, variavel={variavel}")
        if valor is not None:
            # Se o valor for uma string literal, imprima-o diretamente
            if isinstance(valor, str):
                print(valor, end="")
            else:
                print(self.obter_valor(valor) if valor not in self.variaveis else valor, end="")
        elif variavel is not None:
            valor_a_imprimir = self.obter_valor(variavel)
            print(valor_a_imprimir if valor_a_imprimir is not None else f"Erro: '{variavel}' não encontrada.", end="")

    def operacao_aritmetica(self, instrucao):
        operador, guardar, op1, op2 = instrucao
        op1_val, op2_val = self.obter_valor(op1), self.obter_valor(op2)
        operacoes = {
            "+": op1_val + op2_val,
            "-": op1_val - op2_val,
            "*": op1_val * op2_val,
            "/": op1_val / op2_val if op2_val != 0 else 0,
            "%": op1_val % op2_val if op2_val != 0 else 0,
            "//": op1_val // op2_val if op2_val != 0 else 0,
        }
        self.armazenar_resultado(guardar, operacoes.get(operador, 0))

    def operacao_logica(self, instrucao):
        operador, guardar, op1, op2 = instrucao
        op1_val, op2_val = self.obter_valor(op1), self.obter_valor(op2)
        operacoes = {
            "||": op1_val or op2_val,
            "&&": op1_val and op2_val,
            "!": not op1_val,
            "==": op1_val == op2_val,
            "<>": op1_val != op2_val,
            ">": op1_val > op2_val,
            ">=": op1_val >= op2_val,
            "<": op1_val < op2_val,
            "<=": op1_val <= op2_val,
        }
        self.armazenar_resultado(guardar, operacoes.get(operador, False))

    def armazenar_resultado(self, nome, valor):
        if nome.startswith("__temp"):
            self.variaveis_temporarias[nome] = valor
        else:
            self.variaveis[nome] = valor

    def atribuicao(self, instrucao):
        _, guardar, op1, _ = instrucao  # O _ representa o valor que é None
        #print(f"Atribuindo valor {valor} à variável {guardar}")
        self.variaveis[guardar] = self.obter_valor(op1)
        #print(self.variaveis)

    def condicional(self, instrucao):
        _, condicao, label1, label2 = instrucao
        condicao_val = self.obter_valor(condicao)
        proximo_label = label1 if condicao_val else label2
        if proximo_label in self.labels:
            self.instrucao_atual = self.labels[proximo_label] - 1
        else:
            raise ValueError(f"Label {proximo_label} não encontrado.")

    def salto(self, instrucao):
        _, label, *_ = instrucao
        if label in self.labels:
            self.instrucao_atual = self.labels[label] - 1
        else:
            raise ValueError(f"Label {label} não encontrado.")

    def chamada_sistema(self, instrucao):
        _, comando, valor, variavel = instrucao
        if comando == "PRINT":
            self.processar_print(valor, variavel)
            """if isinstance(valor, str):  
                    # Imprime o texto literal
                    print(valor, end=" ")
                    # Agora, verifica se há uma variável a ser impressa logo após o texto
                    if variavel is not None:
                        valor_a_imprimir = self.obter_valor(variavel)
                        if valor_a_imprimir is not None:
                            print(valor_a_imprimir)  # Imprime o valor da variável após o texto
                        else:
                            print("Erro: variável não encontrada.")"""
        elif comando == "SCAN":
            try:
                self.variaveis[variavel] = int(input())
            except ValueError:
                print("Erro: entrada inválida. Insira um número inteiro.")

    
def carregar_codigo_intermediario(caminho):
    with open(caminho, "r") as f:
        conteudo = f.read().strip().splitlines()

    tuplas = []
    for line in conteudo:
        try:
            tupla = eval(line)
            if isinstance(tupla, (tuple, list)):
                if isinstance(tupla[0], tuple):
                    tupla = tupla[0]
                tuplas.append(tupla)
        except Exception as e:
            print(f"Erro ao processar a instrução: {line} - {e}")
    return tuplas

if __name__ == "__main__":
    caminho = "exCodIntermediario.txt"
    tuplas = carregar_codigo_intermediario(caminho)
    interpretador = Interpretador(tuplas)
    interpretador.executar()
