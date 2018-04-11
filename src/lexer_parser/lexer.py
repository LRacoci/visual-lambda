import ply.lex as lex

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'True': 'TRUE',
    'False' : 'FALSE',
    'and' : 'AND',
    'xor' : 'XOR',
    'ior' : 'IOR',
}

tokens = (
    'NAME',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'DEFINITION',
    'NATURAL',
    'LPAREN',
    'RPAREN',
    'EQL',
    'GTE',
    'LTE',
    'DIF',
    'LT',
    'GT'
)

tokens = list(tokens) + list(reserved.values())

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')    # Check for reserved words
    return t

# Tokens

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_DEFINITION = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQL = r'=='
t_GTE = r'>='
t_LTE = r'<='
t_DIF = r'!='
t_LT = r'<'
t_GT = r'>'
t_IF = r'if'

def t_NATURAL(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Natural value too large %d", t.value)
        t.value = 0
    return t

# Caracteres para ignorar
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Constroi lexer
lexer = lex.lex()
