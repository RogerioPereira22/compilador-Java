import sys
import lexico
import sintatico
from interpretador import Interpretador

def main(arquivo):
    # Análise léxica
    tokens = lexico.main(arquivo)
    #print("\n--- Lista de Tokens Gerados ---")
    print(f"🔍 DEBUG: Tokens antes da análise: {tokens}")
    # Análise sintática
    codigo_intermediario = sintatico.main(tokens)
    print("\n🔎 Código Intermediário Gerado:")
    for instrucao in codigo_intermediario:
        print(instrucao)
    # Execução
    interpretador = Interpretador(codigo_intermediario)
    interpretador.rodar()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.java>")
        sys.exit(1)
    main(sys.argv[1])