from lexer import *
import ply.yacc as yacc

# Regras do parser

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
)

# Dicionario de nomes
names = {
    'functions' : {},
    'args' : {}
}

namesOut = {
    'functions' : {},
    'args' : {}
}

def p_start(t):
    'start : functionList'
    namesOut['functions'] = dict(names['functions'])
    namesOut['args'] = dict(names['args'])
    names['functions'] = {}
    names['args'] = {}

def p_functionList(t):
    '''functionList : functionList function
                    | function '''

def p_function_assign(t):
    'function : NAME DEFINITION statement'
    names['functions'][t[1]] = t[3]
    names['args'][t[1]] = []

def p_function_args(t):
    'function : NAME argList DEFINITION statement'
    names['functions'][t[1]] = t[4]
    names['args'][t[1]] = t[2]

def p_args_list(t):
    'argList : argList NAME'
    t[0] = t[1] + [t[2]]

def p_args(t):
    'argList : NAME'
    t[0] = [t[1]]

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  '''
    t[0] = [[t[2], t[1]], t[3]]


def p_condition_binop(t):
    '''condition :  condition AND condition
                  | condition XOR condition
                  | condition IOR condition
                  | expression EQL expression
                  | expression GTE expression
                  | expression LTE expression
                  | expression DIF expression
                  | expression LT expression
                  | expression GT expression
                  '''
    t[0] = [[t[2], t[1]], t[3]]

def p_statement_ifelse(t):
    'statement : IF condition THEN statement ELSE statement'
    t[0] = [[["cond", t[2]], t[4]], t[6]]   

def p_statement_expression(t):
    'statement : expression'
    t[0] = t[1]

def p_expression_minus(t):
    'expression : expression MINUS expression'
    t[0] = [[t[2], t[3]], t[1]]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = [[t[1], t[2]], 0]


def p_expression_application(t):
    'expression : application '
    t[0] = t[1]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_application_expression(t):
    'application : application LPAREN expression RPAREN'
    t[0] = [t[1], t[3]]

def p_application_group(t):
    'application : LPAREN application RPAREN'
    t[0] = [t[1], t[2]]

def p_condition_group(t):
    'condition : LPAREN condition RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NATURAL'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    t[0] = t[1]

def p_application_name(t):
    'application : NAME'
    t[0] = t[1]

def p_condition_bool(t):
    'condition : BOOL'
    t[0] = t[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()
