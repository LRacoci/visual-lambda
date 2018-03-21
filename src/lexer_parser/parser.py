from lexer import *
import ply.yacc as yacc

# Regras do parser

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
)

# Dicionario de nomes
names = {}

def p_statement_assign(t):
    'statement : MAIN DEFINITION expression'
    names[t[1]] = t[3]

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    t[0] = [[t[2], t[1]], t[3]]

def p_expression_minus(t):
    'expression : expression MINUS expression'
    t[0] = [[t[2], t[3]], t[1]]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = [[t[1], t[2]], 0]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NATURAL'
    t[0] = t[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()
