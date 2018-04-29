from lexer import *
import ply.yacc as yacc
import ast

# Parser precende

precedence = (
    ('left','IFELSE'),
    ('left', 'IOR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQL', 'DIF'),
    ('left', 'GT', 'GTE', 'LT', 'LTE'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UNARY'),
)
# Parser rules
def p_start(t):
    '''start : functionList'''
    t[0] = ast.start(t)

def p_functionList(t):
    '''functionList : functionList function
        | function '''
    t[0] = ast.functionList(t)

def p_function_assign(t):
    '''function : NAME DEFINITION expression'''
    t[0] = ast.function_assign(t)

def p_function_args(t):
    '''function : NAME argList DEFINITION expression'''
    t[0] = ast.function_args(t)

def p_args_list(t):
    '''argList : argList NAME'''
    t[0] = ast.args_list(t)

def p_args(t):
    '''argList : NAME'''
    t[0] = ast.args(t)

def p_expression_binop(t):
    '''expression : expression PLUS expression
        | expression TIMES expression
        | expression DIVIDE expression
        | expression MINUS expression
        | expression AND expression
        | expression XOR expression
        | expression IOR expression
        | expression EQL expression
        | expression GTE expression
        | expression LTE expression
        | expression DIF expression
        | expression LT expression
        | expression GT expression'''
    t[0] = ast.expression_binop(t)

def p_expression_ifelse(t):
    '''expression : IF expression THEN expression ELSE expression %prec IFELSE'''
    t[0] = ast.expression_ifelse(t)

def p_expression_uminus(t):
    '''expression : MINUS expression %prec UNARY'''
    t[0] = ast.expression_uminus(t)

def p_expression_not(t):
    '''expression : NOT expression %prec UNARY'''
    t[0] = ast.expression_not(t)

def p_expression_application(t):
    '''expression : application '''
    t[0] = ast.expression_application(t)

def p_expression_group(t):
    '''expression : LPAREN expression RPAREN'''
    t[0] = ast.expression_group(t)

def p_application_nested(t):
    '''application : application LPAREN expression RPAREN'''
    t[0] = ast.application_nested(t)

def p_application_expression(t):
    '''application : NAME LPAREN expression RPAREN'''
    t[0] = ast.application_expression(t)

def p_application_null(t):
    '''application : NAME LPAREN RPAREN'''
    t[0] = ast.application_null(t)

def p_expression_number(t):
    '''expression : NATURAL'''
    t[0] = ast.expression_number(t)

def p_expression_name(t):
    '''expression : NAME'''
    t[0] = ast.expression_name(t)

def p_expression_bool(t):
    '''expression : TRUE
        | FALSE'''
    t[0] = ast.expression_bool(t)

def p_error(t):
    ''''''
    t[0] = ast.error(t)

parser = yacc.yacc()
