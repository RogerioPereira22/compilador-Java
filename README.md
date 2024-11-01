# Analisador Léxico em Python

Este projeto é um analisador léxico em Python que processa o código-fonte de uma linguagem simples, identificando tokens, palavras reservadas, operadores e símbolos. O analisador léxico lê um arquivo de código-fonte e um arquivo de definição de tokens, exibindo cada token reconhecido com informações sobre o tipo, lexema, linha e coluna.

## Funcionalidades

- **Identificação de Tokens**: Reconhece palavras reservadas, operadores, variáveis, números (inteiros e flutuantes), strings e símbolos.
- **Tratamento de Erros**: Identifica e exibe mensagens de erro para strings não fechadas, números com caracteres inválidos e tokens desconhecidos.
- **Exibição dos Tokens**: Cada token identificado é exibido com informações detalhadas sobre sua posição no código-fonte.

## Estrutura do Projeto

- `analisador.py`: Arquivo principal contendo o código do analisador léxico.
- `tokens.txt`: Arquivo de configuração que define operadores, palavras reservadas e símbolos que o analisador deve reconhecer.
  
## Como Funciona

1. **Ler Arquivo de Código-Fonte**: O analisador abre e lê o conteúdo do arquivo de código-fonte especificado.
2. **Carregar Tokens**: O arquivo `tokens.txt` é lido para identificar operadores, palavras reservadas e símbolos.
3. **Analisar o Código-Fonte**: O código é processado caractere por caractere para identificar tokens válidos. Cada token é armazenado em uma lista e exibido com detalhes.
4. **Tratamento de Erros**: Caso um erro seja encontrado (string não fechada, número inválido, token desconhecido), o analisador exibe uma mensagem e interrompe a execução.

## Estrutura do Arquivo `tokens.txt`

O arquivo `tokens.txt` deve ter o seguinte formato, com seções delimitadas:

OPERATORS:

-> ADD
-> SUB
-> MUL / -> DIV == -> EQUAL != -> NOT_EQUAL
RESERVED WORDS: int -> INT float -> FLOAT if -> IF else -> ELSE while -> WHILE

SYMBOLS: ( -> OPEN_PAREN ) -> CLOSE_PAREN { -> OPEN_BRACE } -> CLOSE_BRACE ; -> SEMICOLON , -> COMMA . -> DOT


Cada seção (`OPERATORS`, `RESERVED WORDS`, `SYMBOLS`) é separada e cada linha dentro de uma seção define um símbolo ou palavra-chave e seu token correspondente.

## Como Executar

1. Certifique-se de ter o Python 3 instalado.
2. No terminal, execute o seguinte comando:

   ```bash
   python analisador.py <nome_do_arquivo_de_codigo>

Exemplo de execução:

python analisador.py codigo_exemplo.txt


Exemplos de Saída

Para o código a seguir:

int main() {
    int a, b;
    float f;
    f = 3.14;
}

A saída será:

Token(IDENTIFIER, 'int', Line: 1, Column: 0)
Token(IDENTIFIER, 'main', Line: 1, Column: 4)
Token(OPEN_PAREN, '(', Line: 1, Column: 8)
Token(CLOSE_PAREN, ')', Line: 1, Column: 9)
Token(OPEN_BRACE, '{', Line: 1, Column: 10)
Token(IDENTIFIER, 'int', Line: 2, Column: 5)
Token(VARIABLE, 'a', Line: 2, Column: 9)
Token(COMMA, ',', Line: 2, Column: 11)
Token(VARIABLE, 'b', Line: 2, Column: 12)
Token(SEMICOLON, ';', Line: 2, Column: 13)
Token(IDENTIFIER, 'float', Line: 3, Column: 5)
Token(VARIABLE, 'f', Line: 3, Column: 11)
Token(SEMICOLON, ';', Line: 3, Column: 12)
Token(VARIABLE, 'f', Line: 4, Column: 5)
Token(ASSIGN, '=', Line: 4, Column: 7)
Token(FLOAT, '3.14', Line: 4, Column: 9)
Token(SEMICOLON, ';', Line: 4, Column: 13)
Token(CLOSE_BRACE, '}', Line: 5, Column: 0)


Tratamento de Erros
O analisador léxico interrompe a execução quando encontra um erro e exibe uma mensagem descritiva. Exemplos de erros incluem:

String não fechada: Exibe um erro se uma string não tiver uma aspa de fechamento.
Número inválido: Exibe um erro se um número contiver caracteres inválidos.
Token não reconhecido: Exibe um erro se o analisador encontra um caractere ou sequência de caracteres desconhecida.

Licença
Este projeto está sob a licença MIT.