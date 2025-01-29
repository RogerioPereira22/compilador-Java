import sys

class Interpreter:
    def __init__(self, instructions):
        self.instructions = instructions
        self.variables = {}
        self.temp_vars = {}
        self.labels = {}
        self.current_instruction = 0
        self.preprocess_labels()

    def preprocess_labels(self):
        for idx, instruction in enumerate(self.instructions):
            if isinstance(instruction, (list, tuple)) and instruction and isinstance(instruction[0], str):
                if instruction[0].upper() == "LABEL":
                    label_name = instruction[1]
                    self.labels[label_name] = idx

    def run(self):
        max_iterations = 150
        iteration_count = 0

        while self.current_instruction < len(self.instructions) and iteration_count < max_iterations:
            iteration_count += 1
            instruction = self.instructions[self.current_instruction]
            operator = instruction[0]

            try:
                if operator == "=":
                    self.assign(instruction)
                elif operator == "CALL":
                    self.system_call(instruction)
                elif operator in ["+", "-", "*", "/", "%", "//"]:
                    self.arithmetic_operation(instruction)
                elif operator in ["||", "&&", "!", "==", "<>", ">", ">=", "<", "<="]:
                    self.logical_operation(instruction)
                elif operator == "IF":
                    self.conditional_jump(instruction)
                elif operator == "JUMP":
                    self.jump(instruction)
                elif operator == "LABEL":
                    pass  # Labels são processados no pré-processamento
                else:
                    raise ValueError(f"Operador desconhecido: {operator}")

                self.current_instruction += 1
            except Exception as e:
                print(f"Erro na instrução {self.current_instruction}: {instruction} - {e}")
                break

        if iteration_count >= max_iterations:
            print("Número máximo de iterações atingido.")

    def get_value(self, operand):
        if operand is None:
            return None
        if isinstance(operand, (int, float, bool)):
            return operand
        if operand.isdigit():
            return int(operand)
        return self.variables.get(operand, self.temp_vars.get(operand))

    def print_value(self, value, variable):
        if value is not None:
            if isinstance(value, str):
                print(value, end="")
            else:
                print(self.get_value(value) if value not in self.variables else value, end="")
        elif variable is not None:
            value_to_print = self.get_value(variable)
            print(value_to_print if value_to_print is not None else f"Erro: '{variable}' não encontrada.", end="")

    def arithmetic_operation(self, instruction):
        operator, dest, op1, op2 = instruction
        val1, val2 = self.get_value(op1), self.get_value(op2)
        result = {
            "+": val1 + val2,
            "-": val1 - val2,
            "*": val1 * val2,
            "/": val1 / val2 if val2 != 0 else 0,
            "%": val1 % val2 if val2 != 0 else 0,
            "//": val1 // val2 if val2 != 0 else 0,
        }.get(operator, 0)
        self.store_result(dest, result)

    def logical_operation(self, instruction):
        operator, dest, op1, op2 = instruction
        val1, val2 = self.get_value(op1), self.get_value(op2)
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
        self.store_result(dest, result)

    def store_result(self, dest, value):
        if dest.startswith("__temp"):
            self.temp_vars[dest] = value
        else:
            self.variables[dest] = value

    def assign(self, instruction):
        _, dest, value, _ = instruction
        self.variables[dest] = self.get_value(value)

    def conditional_jump(self, instruction):
        _, condition, label1, label2 = instruction
        condition_value = self.get_value(condition)
        next_label = label1 if condition_value else label2
        if next_label in self.labels:
            self.current_instruction = self.labels[next_label] - 1
        else:
            raise ValueError(f"Label {next_label} não encontrado.")

    def jump(self, instruction):
        _, label, *_ = instruction
        if label in self.labels:
            self.current_instruction = self.labels[label] - 1
        else:
            raise ValueError(f"Label {label} não encontrado.")

    def system_call(self, instruction):
        _, command, value, variable = instruction
        if command == "PRINT":
            self.print_value(value, variable)
        elif command == "SCAN":
            try:
                self.variables[variable] = int(input())
            except ValueError:
                print("Erro: entrada inválida. Insira um número inteiro.")

def load_intermediate_code(path):
    with open(path, "r") as file:
        content = file.read().strip().splitlines()

    instructions = []
    for line in content:
        try:
            instruction = eval(line)
            if isinstance(instruction, (tuple, list)):
                if isinstance(instruction[0], tuple):
                    instruction = instruction[0]
                instructions.append(instruction)
        except Exception as e:
            print(f"Erro ao processar a instrução: {line} - {e}")
    return instructions

def main(path):
    instructions = load_intermediate_code(path)
    interpreter = Interpreter(instructions)
    interpreter.run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Erro: Nenhum arquivo foi especificado. Por favor, forneça o nome do arquivo.")
        sys.exit(1)