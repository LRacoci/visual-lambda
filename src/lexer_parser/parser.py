from lexer import *
import ply.yacc as yacc
import ast
from collections import deque
import json

# Parser precende

precedence = (
    ('left', 'IFELSE'),
    ('left', 'IOR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQL', 'DIF'),
    ('left', 'GT', 'GTE', 'LT', 'LTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UNARY'),
    ('left', 'LBRACKET2')
)

# Auxiliar variables
_names = {}
_names_aux = set()

_dependence_aux = set()

_functions = {}
_whereDict = {}
_args = {}
_dependence = {}

_functions_queue = deque(['main'])

_exec_tree = {}

namesOut = {
    'dependence' : {},
    'functions' : {},
    'args' : {}
}

execOut = {
    'tree' : {}
}

# Reset variables
def reset():
    global _functions
    global _args
    global _dependence
    global _exec_tree
    global _whereDict

    namesOut['functions'] = dict(_functions)
    namesOut['args'] = dict(_args)
    namesOut['dependence'] = dict(_dependence)

    # Check if 'main' is defined
    if 'main' not in namesOut['functions']:
        clean()
        raise Exception("Error: main is not defined")

    # Check if 'main' has no arguments
    if len(namesOut['args']['main']) != 0:
        clean()
        raise Exception("Error: main is defined with arguments")

    set_of_functions = {func for func in namesOut['functions']}

    # Check if every function called is defined or an argument of the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        aux = (set(namesOut['dependence'][func]) - set_of_args) - set_of_functions
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            clean()
            raise Exception("Error: {} called inside {} is not defined".format(aux, func))

    # Check if every name is a function name or an argument in the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        set_of_wheres = {where["var"] for where in _whereDict[func]}
        print set_of_wheres
        aux = (_names[func] - set_of_args) - set_of_functions - set_of_wheres
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            clean()
            raise Exception ("Error: {} used inside {} not declared".format(str_aux, func))

    _exec_tree = ast.execute(_functions['main'])
    execOut['tree'] = dict(_exec_tree)
    clean()

def clean():
    _functions = {}
    _whereDict = {}
    print _whereDict
    _args = {}
    _dependence = {}
    _exec_tree = {}
    _whereDict = {}

# Parser rules
def p_start(t):
    '''start : functionList'''
    reset()

def p_functionList(t):
    '''functionList : functionList function
        | function '''

def p_function_assign(t):
    '''function : NAME DEFINITION expression where_expression'''
    global _names
    global _names_aux
    _names[t[1]] = _names_aux

    _names_aux = set()

    global _dependence
    global _dependence_aux
    _dependence[t[1]] =  list(_dependence_aux)

    _dependence_aux = set()
    global _functions
    _functions[t[1]] = t[3]
    _args[t[1]] = []
    global _whereDict
    _whereDict[t[1]] = t[4]

def p_function_args(t):
    '''function : NAME argList DEFINITION expression where_expression'''
    global _names
    global _names_aux
    _names[t[1]] = _names_aux

    _names_aux = set()

    global _dependence
    global _dependence_aux
    _dependence[t[1]] = list(_dependence_aux)

    _dependence_aux = set()

    global _functions
    _functions[t[1]] = t[4]
    _args[t[1]] = t[2]
    global _whereDict
    _whereDict[t[1]] = t[5]

def p_args_list(t):
    '''argList : argList NAME'''
    t[0] = t[1] + [t[2]]

def p_args(t):
    '''argList : NAME'''
    t[0] = [t[1]]

def p_where_expression(t):
    '''where_expression : WHERE NAME DEFINITION expression where_expression
                        | '''
    if len(t) > 1:
        t[0] = [{"var": t[2], "expression": t[4]}] + t[5]
    else:
        t[0] = []

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
    t[0] = ast.binop(t[1], t[2], t[3])

def p_expression_ifelse(t):
    '''expression : IF expression THEN expression ELSE expression %prec IFELSE'''
    t[0] = ast.conditional(t[2], t[4], t[6])

def p_expression_uminus(t):
    '''expression : MINUS expression %prec UNARY'''
    t[0] = ast.binop(ast.constant(0, "int"), t[1], t[2])

def p_expression_not(t):
    '''expression : NOT expression %prec UNARY'''
    t[0] = ast.binop(ast.constant("True", "bool"), "xor", t[2])

def p_expression_application(t):
    '''expression : application'''
    t[0] = t[1]

def p_expression_group(t):
    '''expression : LPAREN expression RPAREN'''
    t[0] = t[2]

def p_application_nested(t):
    '''application : application LPAREN expression RPAREN'''
    t[0] = ast.application(t[1], t[3])

def p_application_expression(t):
    '''application : NAME LPAREN expression RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.application(t[1], t[3])

def p_application_null(t):
    '''application : NAME LPAREN RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.application(t[1], None)

def p_constant_real_number(t):
    '''constant : FLOAT'''
    t[0] = ast.constant(t[1], "float")

def p_constant_number(t):
    '''constant : NATURAL'''
    t[0] = ast.constant(t[1], "int")

def p_constant_string(t):
    '''constant : STRING1
        | STRING2'''
    t[0] = ast.constant(t[1], "str")

def p_constant_bool(t):
    '''constant : TRUE
        | FALSE'''
    t[0] = ast.constant(t[1], "bool")

def p_expression_constant(t):
    '''expression : constant
        | structure'''
    t[0] = t[1]

def p_structure_null(t):
    '''structure : LBRACKET1 RBRACKET1'''
    t[0] = ast.structure([])

def p_structure_kvList(t):
    '''structure : LBRACKET1 kvList RBRACKET1'''
    t[0] = ast.structure(t[2])

def p_kvList_nested(t):
    '''kvList : kvTerm COMMA kvList'''
    t[0] = [t[1]] + t[3]

def p_kvList_kvTerm(t):
    '''kvList : kvTerm'''
    t[0] = [t[1]]

def p_kvTerm(t):
    '''kvTerm : constant COLON expression'''
    t[0] = t[1], t[3]

def p_expression_structure_call(t):
    '''expression : expression LBRACKET2 expression RBRACKET2'''
    t[0] = ast.structureCall(t[1], t[3])

def p_expression_name(t):
    '''expression : NAME'''
    global _names_aux
    _names_aux |= {t[1]}
    t[0] = ast.identifier(t[1])

def p_error(t):
    ''''''
    reset()
    raise Exception("Syntax error at %s" % t)

parser = yacc.yacc()
