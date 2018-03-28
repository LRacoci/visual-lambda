import ply.lex as lex

tokens = (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'DEFINITION',
    'NATURAL',
    'LPAREN',
    'RPAREN',
    'MAIN',
    'AND',
    'XOR',
    'IOR',
    'EQL',
    'GTE',
    'LTE',
    'DIF',
    'LT',
    'GT',
    'IF',
    'ELSE'
)

# Tokens

t_MAIN = r'main'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_DEFINITION = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_AND = r'and'
t_XOR = r'xor'
t_IOR = r'ior'
t_EQL = r'=='
t_GTE = r'>='
t_LTE = r'<='
t_DIF = r'!='
t_LT = r'<'
t_GT = r'>'
t_IF = r'if'
t_ELSE = r'else'


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
