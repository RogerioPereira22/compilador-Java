class Interpretador:
    def __init__(self, tuplas):
        self.tuplas = tuplas
        self.variaveis = {}
        self.labels = {}
        self.instrucao_atual = 0
        self.preprocessar_labels()

    def preprocessar_labels(self):
        for index, instrucao in enumerate(self.tuplas):
            # Verifica se 'instrucao' é uma lista ou tupla e se começa com 'LABEL'
            if isinstance(instrucao, (list, tuple)) and instrucao[0].upper() == 'LABEL' and len(instrucao) >= 2:
                label_name = instrucao[1]
                self.labels[label_name] = index  # Mapeando o label para sua posição
           

                    

    def executar(self):
        self.preprocessar_labels()
        #print(f"Labels mapeados: {self.labels}")
        contador = 0  # Limitar o número de iterações
        while self.instrucao_atual < len(self.tuplas)and contador < 100:
            contador += 1
            try:
                instrucao = self.tuplas[self.instrucao_atual]
                operador = instrucao[0]
                print(f"Executando instrução: {instrucao}")
                
                # Depuração adicional para ver os valores das variáveis
                print(f"Variáveis antes da execução: {self.variaveis}")
                
                if operador in {"+", "-", "*", "/", "%", "//"}:
                    self.operacao_aritmetica(instrucao)
                elif operador in {"||", "&&", "!", "==", "<>", ">", ">=", "<", "<="}:
                    self.operacao_logica(instrucao)
                elif operador == "=":
                    self.atribuicao(instrucao)
                elif operador == "IF":
                    self.condicional(instrucao)
                elif operador == "JUMP":
                    self.salto(instrucao)
                elif operador == "CALL":
                    self.chamada_sistema(instrucao)
                elif operador == "LABEL":
                    pass  # Labels são tratados no preprocessamento
                else:
                    raise ValueError(f"Operador desconhecido: {operador}")

                # Depuração adicional após a execução de cada instrução
                print(f"Variáveis após a execução: {self.variaveis}")
                
                self.instrucao_atual += 1
            except Exception as e:
                print(f"Erro ao processar a instrução na posição {self.instrucao_atual}: {instrucao} - {e}")
                break



    def obter_valor(self, operando):
        print(f"Obtendo valor para: {operando}")  # Depuração
        if operando is None:
            return None
        if isinstance(operando, bool):  # Verifica se é um booleano
            return operando
        if isinstance(operando, (int, float)):  # Verifica se é um número
            return operando
        if operando.isdigit():  # Verifica se a string é um número
            return int(operando)
        # Se for um nome de variável, retorna seu valor ou None se não existir
        valor = self.variaveis.get(operando, None)
        print(f"Valor de {operando}: {valor}")  # Depuração
        return valor





    def operacao_aritmetica(self, instrucao):
        operador, guardar, op1, op2 = instrucao
        op1_val = self.obter_valor(op1)
        op2_val = self.obter_valor(op2)
        
        if operador == ">":
            # Verifica se op1 é maior que op2 e atribui 1 (True) ou 0 (False)
            self.variaveis[guardar] = 1 if op1_val > op2_val else 0  # Atribui 1 ou 0, não booleano
        elif operador == "+":
            self.variaveis[guardar] = op1_val + op2_val
        elif operador == "-":
            self.variaveis[guardar] = op1_val - op2_val
        elif operador == "*":
            self.variaveis[guardar] = op1_val * op2_val
        elif operador == "/":
            if op2_val == 0:
                print(f"Erro: divisão por zero em {guardar}")
                self.variaveis[guardar] = 0  # Previne erro de divisão por zero
            else:
                self.variaveis[guardar] = op1_val / op2_val
        elif operador == "%":
            if op2_val == 0:
                print(f"Erro: divisão por zero em {guardar}")
                self.variaveis[guardar] = 0  # Previne erro de divisão por zero
            else:
                self.variaveis[guardar] = op1_val % op2_val
        elif operador == "//":
            if op2_val == 0:
                print(f"Erro: divisão inteira por zero em {guardar}")
                self.variaveis[guardar] = 0  # Previne erro de divisão por zero
            else:
                self.variaveis[guardar] = op1_val // op2_val

    def operacao_logica(self, instrucao):
        operador, guardar, op1, op2 = instrucao
        op1_val = self.obter_valor(op1)
        op2_val = self.obter_valor(op2)

        if operador == "||":  # OR
            self.variaveis[guardar] = op1_val or op2_val
        elif operador == "&&":  # AND
            self.variaveis[guardar] = op1_val and op2_val
        elif operador == "!":  # NOT
            self.variaveis[guardar] = not op1_val
        elif operador == "==":  # Igualdade
            self.variaveis[guardar] = op1_val == op2_val
        elif operador == "<>":  # Diferente
            self.variaveis[guardar] = op1_val != op2_val
        elif operador == ">":  # Maior que
            self.variaveis[guardar] = op1_val > op2_val
        elif operador == ">=":  # Maior ou igual
            self.variaveis[guardar] = op1_val >= op2_val
        elif operador == "<":  # Menor que
            self.variaveis[guardar] = op1_val < op2_val
        elif operador == "<=":  # Menor ou igual
            self.variaveis[guardar] = op1_val <= op2_val
        


    def atribuicao(self, instrucao):
        _, guardar, op1, _ = instrucao
        self.variaveis[guardar] = self.obter_valor(op1)
        valor = self.obter_valor(op1)
        print(f"Atribuindo valor {valor} à variável {guardar}")
        self.variaveis[guardar] = valor
        print(self.variaveis)

    def condicional(self, instrucao):
        _, condicao, label1, label2 = instrucao
        condicao_val = self.obter_valor(condicao)
        print(f"Evaluando IF: {condicao} = {condicao_val}")  
        if condicao_val:  # Avalia True ou False
            if label1 in self.labels:
                self.instrucao_atual = self.labels[label1] - 1
            else:
                raise ValueError(f"Label {label1} não encontrado.")
        else:
            if label2 in self.labels:
                self.instrucao_atual = self.labels[label2] - 1
            else:
                raise ValueError(f"Label {label2} não encontrado.")


    def salto(self, instrucao):
        _, label, _, _ = instrucao
        self.instrucao_atual = self.labels[label] - 1

    def chamada_sistema(self, instrucao):
        _, comando, valor, variavel = instrucao
        
        if comando == "CALL":
            if valor == "PRINT":
                # Se valor for uma string literal, imprime o texto diretamente
                if isinstance(valor, str):  
                    # Imprime o texto literal
                    print(valor, end=" ")
                    # Agora, verifica se há uma variável a ser impressa logo após o texto
                    if variavel is not None:
                        valor_a_imprimir = self.obter_valor(variavel)
                        if valor_a_imprimir is not None:
                            print(valor_a_imprimir)  # Imprime o valor da variável após o texto
                        else:
                            print("Erro: variável não encontrada.")
                    else:
                        print()  # Caso não tenha variável, só imprime o texto
                else:
                    valor_a_imprimir = self.obter_valor(valor)
                    if valor_a_imprimir is None:
                        print(f"Erro: variável '{valor}' não encontrada ou valor None", end=" ")
                    else:
                        print(valor_a_imprimir, end=" ")

            elif valor == "SCAN":
                # Exemplo de um outro comando no CALL (como um scanner de entrada)
                print("Operação SCAN não implementada.")
            
            elif valor == "STOP":
                # Implementar um comando STOP, por exemplo
                print("Comando STOP executado.")
            
            else:
                print(f"Comando CALL não reconhecido: {valor}")
        
        # Quando o comando é diretamente PRINT (sem CALL)
        elif comando == "PRINT":
            if valor is not None:
                if isinstance(valor, str):
                    print(valor, end=" ")
                    if variavel is not None:
                        valor_a_imprimir = self.obter_valor(variavel)
                        if valor_a_imprimir is not None:
                            print(valor_a_imprimir)
                        else:
                            print("Erro: variável não encontrada.")
                    else:
                        print()  # Apenas o texto, sem variável
                else:
                    valor_a_imprimir = self.obter_valor(valor)
                    if valor_a_imprimir is None:
                        print(f"Erro: variável '{valor}' não encontrada ou valor None", end=" ")
                    else:
                        print(valor_a_imprimir, end=" ")
            else:
                # Quando valor for None, tenta imprimir a variável
                valor_a_imprimir = self.obter_valor(variavel)
                if valor_a_imprimir is None:
                    print(f"Erro: variável '{variavel}' não encontrada ou valor None")
                else:
                    print(f"{variavel} = {valor_a_imprimir}")



def carregar_codigo_intermediario(caminho):
    with open(caminho, "r") as f:
        conteudo = f.read().strip().splitlines()

    tuplas = []
    for line in conteudo:
        try:
            # Remover parênteses extras ao processar a linha
            tupla = eval(line)
            if isinstance(tupla, tuple) or isinstance(tupla, list):
                if isinstance(tupla[0], tuple):  # Verifica se há aninhamento extra
                    tupla = tupla[0]  # Desaninha a tupla
                tuplas.append(tupla)
        except Exception as e:
            print(f"Erro ao processar a instrução: {line} - {e}")
    return tuplas


if __name__ == "__main__":
    caminho = "testeintermediario.txt"
    tuplas = carregar_codigo_intermediario(caminho)
    interpretador = Interpretador(tuplas)
    interpretador.executar()
