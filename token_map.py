# token_map.py

# Constantes para tipos de tokens usando números para melhor desempenho
ADD = 1
SUB = 2
MUL = 3
DIV = 4
MOD = 5
LOGICAL_OR = 6
LOGICAL_AND = 7
LOGICAL_NOT = 8
EQUAL = 9
NOT_EQUAL = 10
GREATER = 11
GREATER_EQUAL = 12
LESS = 13
LESS_EQUAL = 14
ASSIGN = 15
ADD_ASSIGN = 16
SUB_ASSIGN = 17
MUL_ASSIGN = 18
DIV_ASSIGN = 19
MOD_ASSIGN = 20

# Palavras reservadas
INT = 21
FLOAT = 22
STRING = 23
FOR = 24
WHILE = 25
BREAK = 26
CONTINUE = 27
IF = 28
ELSE = 29
RETURN = 30
SYSTEM = 31
OUT = 32
PRINT = 33
IN = 34
SCAN = 35

# Símbolos
SEMICOLON = 36
COMMA = 37
OPEN_BRACE = 38
CLOSE_BRACE = 39
OPEN_PAREN = 40
CLOSE_PAREN = 41
DOT = 42

# Dicionário para operadores
OPERATORS = {
    "+": ADD,
    "-": SUB,
    "*": MUL,
    "/": DIV,
    "%": MOD,
    "||": LOGICAL_OR,
    "&&": LOGICAL_AND,
    "!": LOGICAL_NOT,
    "==": EQUAL,
    "!=": NOT_EQUAL,
    ">": GREATER,
    ">=": GREATER_EQUAL,
    "<": LESS,
    "<=": LESS_EQUAL,
    "=": ASSIGN,
    "+=": ADD_ASSIGN,
    "-=": SUB_ASSIGN,
    "*=": MUL_ASSIGN,
    "/=": DIV_ASSIGN,
    "%=": MOD_ASSIGN,
}

# Dicionário para palavras reservadas
RESERVED_WORDS = {
    "int": INT,
    "float": FLOAT,
    "string": STRING,
    "for": FOR,
    "while": WHILE,
    "break": BREAK,
    "continue": CONTINUE,
    "if": IF,
    "else": ELSE,
    "return": RETURN,
    "system": SYSTEM,
    "out": OUT,
    "print": PRINT,
    "in": IN,
    "scan": SCAN,
}

# Dicionário para símbolos
SYMBOLS = {
    ";": SEMICOLON,
    ",": COMMA,
    "{": OPEN_BRACE,
    "}": CLOSE_BRACE,
    "(": OPEN_PAREN,
    ")": CLOSE_PAREN,
    ".": DOT,
}
