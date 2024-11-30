
# Analisador Léxico e Sintático em Python

Este projeto é um analisador léxico e sintático em Python que processa o código-fonte de uma linguagem simples, identificando tokens e gerando uma árvore sintática baseada na gramática JavaMM.

## Funcionalidades

- **Identificação de Tokens**: Reconhece palavras reservadas, operadores, variáveis, números (inteiros e flutuantes), strings e símbolos.
- **Tratamento de Erros Léxicos**: Identifica e exibe mensagens de erro para strings não fechadas, números com caracteres inválidos e tokens desconhecidos.
- **Exibição dos Tokens**: Cada token identificado é exibido com informações detalhadas sobre sua posição no código-fonte.
- **Geração e Exibição da Árvore Sintática**: Analisador sintático que gera e exibe uma árvore sintática para o código-fonte, com base na gramática `JavaMM.gmr` definida no arquivo `sintatico.py`.

## Estrutura do Projeto

- `analisador.py`: Arquivo principal contendo o código do analisador léxico.
- `sintatico.py`: Código para o analisador sintático, que constrói a árvore sintática.
- `tokens.txt`: Arquivo de configuração que define operadores, palavras reservadas e símbolos que o analisador deve reconhecer.

## Como Funciona

### Analisador Léxico
1. **Ler Arquivo de Código-Fonte**: O analisador abre e lê o conteúdo do arquivo de código-fonte especificado.
2. **Carregar Tokens**: O arquivo `tokens.txt` é lido para identificar operadores, palavras reservadas e símbolos.
3. **Analisar o Código-Fonte**: O código é processado caractere por caractere para identificar tokens válidos. Cada token é armazenado em uma lista e exibido com detalhes.
4. **Tratamento de Erros**: Caso um erro seja encontrado (string não fechada, número inválido, token desconhecido), o analisador exibe uma mensagem e interrompe a execução.

### Analisador Sintático
1. **Geração da Árvore Sintática**: A partir de uma lista de tokens gerados pelo analisador léxico, o analisador sintático constrói uma árvore sintática representando a estrutura do código de acordo com a gramática JavaMM.
2. **Exibição da Árvore(extra)**: A árvore é exibida no terminal com indentação para representar os níveis hierárquicos, incluindo nós como tipos, identificadores, blocos, expressões, etc.

## Estrutura do Arquivo `tokens.txt`

O arquivo `tokens.txt` deve ter o seguinte formato, com seções delimitadas:

```
OPERATORS:
+ -> ADD
- -> SUB
* -> MUL
/ -> DIV
== -> EQUAL
!= -> NOT_EQUAL

RESERVED WORDS:
int -> INT
float -> FLOAT
if -> IF
else -> ELSE
while -> WHILE

SYMBOLS:
( -> OPEN_PAREN
) -> CLOSE_PAREN
{ -> OPEN_BRACE
} -> CLOSE_BRACE
; -> SEMICOLON
, -> COMMA
. -> DOT
```

## Como Executar

1. Certifique-se de ter o Python 3 instalado.
2. Para o analisador léxico, execute o seguinte comando:
   ```bash
   python analisador.py <nome_do_arquivo_de_codigo>
   ```
3. Para gerar a árvore sintática, execute:
   ```bash
   python sintatico.py <nome_do_arquivo_de_codigo>
   ```

## Exemplo de Saída da Árvore Sintática

Para o código de exemplo:

```java
int main() {
    int a = 5;
    if (a > 3) {
        a = a + 1;
    }
}
```

A saída será:

```
function: 
    type: int
    identifier: main
    block: 
        stmtList:
            declaration:
                type: int
                ident_list:
                    identifier: a
            assign_stmt:
                variable: a
                binary_op:
                    literal: 5
            if_stmt:
                binary_op:
                    variable: a
                    operator: >
                    literal: 3
                block:
                    stmtList:
                        assign_stmt:
                            variable: a
                            binary_op:
                                variable: a
                                operator: +
                                literal: 1
```

## Tratamento de Erros

- **Erros Léxicos**:
  - String não fechada: Exibe um erro se uma string não tiver uma aspa de fechamento.
  - Número inválido: Exibe um erro se um número contiver caracteres inválidos.
  - Token não reconhecido: Exibe um erro se o analisador encontra um caractere ou sequência de caracteres desconhecida.
- **Erros Sintáticos**:
  - Estruturas incompletas ou malformadas (ex.: bloco sem chaves, falta de ponto e vírgula).
  - Instruções inválidas ou malformadas.

## Licença

Este projeto está sob a licença MIT.
