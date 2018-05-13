import ply.lex as lex

reserved = {
    'if'    : 'IF',
    'then'  : 'THEN',
    'else'  : 'ELSE',
    'True'  : 'TRUE',
    'False' : 'FALSE',
    'and'   : 'AND',
    'xor'   : 'XOR',
    'ior'   : 'IOR',
    'where' : 'WHERE',
    'None'  : 'NONE'
    #'struct' : 'STRUCT'

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
    'GT',
    'NOT',
    'FLOAT',
    'STRING1',
    'STRING2',
    'LBRACKET1',
    'RBRACKET1',
    'COLON',
    'COMMA',
    'LBRACKET2',
    'RBRACKET2'
)

# Tokens

tokens = list(tokens) + list(reserved.values())

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')    # Check for reserved words
    return t

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
t_NOT = r'!'
t_LBRACKET1 = r'{'
t_RBRACKET1 = r'}'
t_COLON = r':'
t_COMMA = r','
t_LBRACKET2 = r'\['
t_RBRACKET2 = r'\]'

def t_FLOAT(t):
    r'-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t

def t_NATURAL(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        raise Exception("Natural value too large %d", t.value)
    return t

# Characters to ignore
t_ignore = " \t"

def t_STRING1(t):
    r'\'([^\\"]|(\\.))*\''
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str
    return t

def t_STRING2(t):
    r'\"([^\\"]|(\\.))*\"'
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str
    return t

# Comments
def t_comment(t):
    r'--.*'
    t.lexer.lineno += 1

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    raise Exception("Illegal character '%s'" % t.value[0])

# Constroi lexer
lexer = lex.lex()
