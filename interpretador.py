import sys

class Interpretador:
    def __init__(self, intruções):
        self.instrucoes = intruções  # Lista de instruções carregadas
        self.variaveis = {}  # Armazena variáveis do programa
        self.temp_vars = {}  # Armazena variáveis temporárias
        self.labels = {}  # Dicionário para armazenar rótulos (LABEL)
        self.current_instrucao = 0  # Índice da instrução atual
        self.preprocess_labels()  # Pré-processa os rótulos antes da execução

    def preprocess_labels(self):
        """Identifica e armazena rótulos (LABEL) para referência futura."""
        for idx, instrucao in enumerate(self.instrucoes):
            if isinstance(instrucao, (list, tuple)) and instrucao and isinstance(instrucao[0], str):
                if instrucao[0].upper() == "LABEL":
                    label_name = instrucao[1]
                    self.labels[label_name] = idx  # Mapeia o nome do rótulo para sua posição

    def rodar(self):
        """Executa as instruções interpretadas até atingir um limite de iterações."""
        max_iteracoes = 2000  # Limite de iterações para evitar loops infinitos
        contarInteracao = 0

        while self.current_instrucao < len(self.instrucoes) and contarInteracao < max_iteracoes:
            contarInteracao += 1
            instrucao = self.instrucoes[self.current_instrucao]
            operator = instrucao[0]  # Identifica a operação da instrução

            try:
                if operator == "=":
                    self.atribuir(instrucao)
                elif operator == "CALL":
                    self.system_call(instrucao)
                elif operator in ["+", "-", "*", "/", "%", "//"]:
                    self.operar_aritimetica(instrucao)
                elif operator in ["||", "&&", "!", "==", "<>", ">", ">=", "<", "<="]:
                    self.logical_operation(instrucao)
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

    def obt_valor(self, operand):
        """Retorna o valor do operando, seja ele uma variável ou um valor direto."""
        if operand is None:
            return None
        if isinstance(operand, (int, float, bool)):
            return operand
        if operand.isdigit():
            return int(operand)
        return self.variaveis.get(operand, self.temp_vars.get(operand))

    def print_valor(self, valor, variavel):
        """Imprime o valor de uma variável ou um valor direto."""
        if valor is not None:
            if isinstance(valor, str):
                print(valor, end="")
            else:
                print(self.obt_valor(valor) if valor not in self.variaveis else valor, end="")
        elif variavel is not None:
            valor_to_print = self.obt_valor(variavel)
            print(valor_to_print if valor_to_print is not None else f"Erro: '{variavel}' não encontrada.", end="")

    def operar_aritimetica(self, instrucao):
        """Executa operações aritméticas básicas."""
        operator, destino, op1, op2 = instrucao
        val1, val2 = self.obt_valor(op1), self.obt_valor(op2)
        result = {
            "+": val1 + val2,
            "-": val1 - val2,
            "*": val1 * val2,
            "/": val1 / val2 if val2 != 0 else 0,
            "%": val1 % val2 if val2 != 0 else 0,
            "//": val1 // val2 if val2 != 0 else 0,
        }.get(operator, 0)
        self.armazen_restado(destino, result)

    def logical_operation(self, instrucao):
        """Executa operações lógicas e comparações."""
        operator, destino, op1, op2 = instrucao
        val1, val2 = self.obt_valor(op1), self.obt_valor(op2)
        result = {
            "||": val1 or val2,
            "&&": val1 and val2,
            "!": not val1,
            "==": val1 == val2,
            "<>": val1 != val2,
            ">": val1 > val2,
            ">=": val1 >= val2,
            "<": val1 < val2,
            "<=": val1 <= val2,
        }.get(operator, False)
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
        self.variaveis[destino] = self.obt_valor(valor)

    def conditional_jump(self, instrucao):
        """Realiza um desvio condicional baseado no valor da condição."""
        _, condition, label1, label2 = instrucao
        condition_valor = self.obt_valor(condition)
        next_label = label1 if condition_valor else label2
        if next_label in self.labels:
            self.current_instrucao = self.labels[next_label] - 1
        else:
            raise ValueError(f"Label {next_label} não encontrado.")

    def jump(self, instrucao):
        """Realiza um salto incondicional para um rótulo."""
        _, label, *_ = instrucao
        if label in self.labels:
            self.current_instrucao = self.labels[label] - 1
        else:
            raise ValueError(f"Label {label} não encontrado.")

    def system_call(self, instrucao):
        """Executa chamadas de sistema como PRINT e SCAN."""
        _, comando, valor, variavel = instrucao
        if comando == "PRINT":
            self.print_valor(valor, variavel)
        elif comando == "SCAN":
            try:
                self.variaveis[variavel] = int(input())
            except ValueError:
                print("Erro: entrada inválida. Insira um número inteiro.")

# Carrega e processa código intermediário

def load_intermediario_cod(path):
    with open(path, "r") as file:
        conteudo = file.read().strip().splitlines()

    intruções = []
    for linha in conteudo:
        try:
            instrucao = eval(linha)
            if isinstance(instrucao, (tuple, list)):
                if isinstance(instrucao[0], tuple):
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
