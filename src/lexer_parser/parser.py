from lexer import *
import ply.yacc as yacc

# Regras do parser

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

# Auxiliar variables
_names = {}
_names_aux = set()

_dependence_aux = set()

_functions = {}
_args = {}
_dependence = {}

namesOut = {
    'dependence' : {},
    'functions' : {},
    'args' : {}
}



def reset():
    global _functions
    global _args
    global _dependence
    
    namesOut['functions'] = dict(_functions)
    namesOut['args'] = dict(_args)
    namesOut['dependence'] = dict(_dependence)
    
    _functions = {}
    _args = {}
    _dependence = {}

    # Check if 'main' is defined
    if 'main' not in namesOut['functions']:
        raise Exception("Error: main is not defined")

    # Check if 'main' has no arguments
    if len(namesOut['args']['main']) != 0:
        raise Exception("Error: main is defined with arguments")
    
    set_of_functions = {func for func in namesOut['functions']}

    # Check if every function called is defined or an argument of the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        aux = (set(namesOut['dependence'][func]) - set_of_args) - set_of_functions
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            raise Exception("Error: {} called inside {} is not defined".format(aux, func))
    
    # Check if every name is a function name or an argument in the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        aux = (_names[func] - set_of_args) - set_of_functions
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            raise Exception ("Error: {} used inside {} not declared".format(str_aux, func))

def p_start(t):
    'start : functionList'
    reset()

def p_functionList(t):
    '''functionList : functionList function
                    | function '''

def p_function_assign(t):
    'function : NAME DEFINITION expression'
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

def p_function_args(t):
    'function : NAME argList DEFINITION expression'
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
                  | expression MINUS expression
                  | expression AND expression
                  | expression XOR expression
                  | expression IOR expression
                  | expression EQL expression
                  | expression GTE expression
                  | expression LTE expression
                  | expression DIF expression
                  | expression LT expression
                  | expression GT expression
                  '''
    t[0] = [[t[2], t[1]], t[3]]

def p_expression_ifelse(t):
    'expression : IF expression THEN expression ELSE expression %prec IFELSE'
    t[0] = [[["cond", t[2]], t[4]], t[6]]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UNARY'
    t[0] = [[t[1], t[2]], 0]

def p_expression_not(t):
    'expression : NOT expression %prec UNARY'
    t[0] = [['xor', t[2]], 'True']

def p_expression_application(t):
    'expression : application '
    t[0] = t[1]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_application_nested(t):
    'application : application LPAREN expression RPAREN'
    t[0] = [t[1], t[3]]

def p_application_expression(t):
    'application : NAME LPAREN expression RPAREN'
    global _names_aux 
    _names_aux |= {t[1]} 
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = [t[1], t[3]]

def p_application_null(t):
    'application : NAME LPAREN RPAREN'
    global _names_aux 
    _names_aux |= {t[1]} 

    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = t[1]

def p_expression_number(t):
    'expression : NATURAL'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    global _names_aux 
    _names_aux |= {t[1]} 

    t[0] = t[1]

def p_expression_bool(t):
    '''expression : TRUE
                  | FALSE'''
    t[0] = t[1]

def p_error(t):
    reset()
    raise Exception("Syntax error at %s" % t)

parser = yacc.yacc()
