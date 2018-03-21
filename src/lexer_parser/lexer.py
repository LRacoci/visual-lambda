import ply.lex as lex

tokens = (
    'PLUS','MINUS','TIMES','DIVIDE','DEFINITION',
    'NATURAL','LPAREN','RPAREN','MAIN',
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