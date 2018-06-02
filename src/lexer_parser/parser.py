from lexer import *
import ply.yacc as yacc
import ast
import symboltable
import json
import copy

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
    ('left', 'LBRACKET2'),
    ('left','COMMA'),
    ('left', 'COLON')
)

# Auxiliar variables
_names = {}
_names_aux = set()

_dependence_aux = set()

_functions = {}
_whereDict = {}
_args = {}
_dependence = {}

_exec_tree = {}

_eta = False
_eta_list = []
_eta_temp = 0

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
            raise Exception(
                "Error: {} called inside {} is not defined"
                .format(
                    ','.join(['"{}"'.format(a) for a in aux]),
                    func
                )
            )

    # Check if every name is a function name or an argument in the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        set_of_wheres = {where["var"] for where in _whereDict[func]}
        aux = (_names[func] - set_of_args) - set_of_functions - set_of_wheres
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            #clean()
            #raise Exception ("Error: {} used inside {} not declared".format(str_aux, func))

    global _eta
    if _eta:
        etaOptimization()

    _exec_tree = ast.execute(_functions['main'])
    execOut['tree'] = dict(_exec_tree)
    clean()

# Clean variables and symbol table
def clean():
    symboltable.clean()

    auxSymbols = {}

    global _names
    _names = {}
    global _names_aux
    _names_aux = set()
    global _dependence_aux
    _dependence_aux = set()
    global _functions
    _functions = {}
    global _whereDict
    _whereDict = {}
    global _args
    _args = {}
    global _dependence
    _dependence = {}

    global _exec_tree
    _exec_tree = {}

    global _eta
    _eta = False
    global _eta_list
    _eta_list = []
    global _eta_temp
    _eta_temp = 0

# Set optimization flag
def setOptimization(eta_flag, fold_flag, prop_flag):
    global _eta
    _eta = eta_flag
    ast.setOptimization(fold_flag, prop_flag)
# Do the eta optimization
def etaOptimization():
    global _eta_list
    global _functions
    global _eta_temp
    global _whereDict
    global _args

    # Search while there is a function to be optimized
    while len(_eta_list) > 0:
        # Search one entry that calls a function that is not an Application
        l = len(_eta_list)
        i = 0
        while i < l:
            node = _functions[_eta_list[i]]
            args = []
            while type(node) is ast.Application:
                args = [node.arg] + args
                node = node.func
            if type(_functions[node]).__name__ != "Application":
                # Build a new where list
                funcWhere = []
                init = _eta_temp
                for arg in args:
                    funcWhere += [{'var': "arg{}".format(_eta_temp), 'expression': arg}]
                    _eta_temp += 1

                # Build an arg map
                argMap = {}
                p = 0
                for num in range(init, _eta_temp):
                    argMap[_args[node][p]] = "arg{}".format(num)
                    p += 1

                # Change variables names in ast
                _functions[_eta_list[i]] = copy.deepcopy(_functions[node])
                ast.etaSearch(argMap, _eta_list[i])

                # Change variables names in where
                where = copy.deepcopy(_whereDict[node])
                for w in where:
                    w['expression'].visit(ast.EtaSearch())
                _whereDict[_eta_list[i]] = funcWhere + where

                break
            i += 1

        # If none is found, then there is a possible infinite loop
        if i == l:
            clean()
            raise Exception("maximum recursion depth exceeded while calling a Python object")
        else:
            del _eta_list[i]

# Parser rules
def p_start(t):
    '''start : functionList'''
    reset()

def p_functionList(t):
    '''functionList : functionList function
        | function '''

def p_function_assign(t):
    '''function : NAME DEFINITION expression where_expression'''
    _,name,_,expression,wheres = t
    print expression
    for where in wheres:
        ast.Application(ast.Lambda(where['var'], expression), where['expression'])

    ast.auxSymbols[name] = [expression]

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

    if t[1] != 'main' and type(t[3]).__name__ == "Application" and t[4] == []:
        global _eta_list
        _eta_list += [t[1]]

def p_function_args(t):
    '''function : NAME argList DEFINITION expression where_expression'''
    _, name, argList, _, expression, wheres = t

    for where in wheres:
        ast.Application(ast.Lambda(where['var'], expression), where['expression'])
    for argName in argList:
        expression = ast.Lambda(argName, expression)

    ast.auxSymbols[name] = [expression]

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

    if t[1] != 'main' and type(t[4]).__name__ == "Application" and t[5] == []:
        global _eta_list
        _eta_list += [t[1]]

def p_args_list(t):
    '''argList : argList pattern'''
    t[0] = t[1] + [t[2]]

def p_args(t):
    '''argList : pattern'''
    t[0] = [t[1]]

def p_pattern_name(t):
    '''pattern : NAME'''
    t[0] = t[1]

# def p_pattern_expression(t):
#     '''pattern : expression'''
#     t[0] = 'expression'

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
    t[0] = ast.Binop(t[1], t[2], t[3])

def p_expression_ifelse(t):
    '''expression : IF expression THEN expression ELSE expression %prec IFELSE'''
    t[0] = ast.Conditional(t[2], t[4], t[6])

def p_expression_uminus(t):
    '''expression : MINUS expression %prec UNARY'''
    t[0] = ast.Binop(ast.Constant(0, "int"), t[1], t[2])

def p_expression_not(t):
    '''expression : NOT expression %prec UNARY'''
    t[0] = ast.Binop(ast.Constant("True", "bool"), "xor", t[2])

def p_expression_application(t):
    '''expression : application'''
    t[0] = t[1]

def p_expression_group(t):
    '''expression : LPAREN expression RPAREN'''
    t[0] = t[2]

def p_application_nested(t):
    '''application : application LPAREN expression RPAREN'''
    t[0] = ast.Application(t[1], t[3])

def p_application_expression(t):
    '''application : NAME LPAREN expression RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.Application(ast.Identifier(t[1]), t[3])

def p_application_null(t):
    '''application : NAME LPAREN RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.Application(ast.Identifier(t[1]), None)

def p_application_lambda(t):
    '''application : lambda LPAREN expression RPAREN'''
    t[0] = ast.Application(t[1], t[3])

def p_expression_lambda(t):
    '''expression : lambda'''
    t[0] = t[1]

def p_lambda_expression(t):
    '''lambda : LPAREN LAMBDA NAME ARROW expression RPAREN'''
    t[0] = ast.Lambda(t[3], t[5])

def p_constant_real_number(t):
    '''constant : FLOAT'''
    t[0] = ast.Constant(t[1], "float")

def p_constant_number(t):
    '''constant : NATURAL'''
    t[0] = ast.Constant(t[1], "int")

def p_constant_string(t):
    '''constant : STRING1
        | STRING2'''
    t[0] = ast.Constant(t[1], "str")

def p_constant_bool(t):
    '''constant : TRUE
        | FALSE'''
    t[0] = ast.Constant(t[1], "bool")

def p_constant_none(t):
    '''constant : NONE'''
    t[0] = ast.Constant(t[1], "none")

def p_expression_constant(t):
    '''expression : constant
        | structure
        | list
        | tuple'''
    t[0] = t[1]

def p_structure_null(t):
    '''structure : LBRACKET1 RBRACKET1'''
    t[0] = ast.Structure([])

def p_structure_kvList(t):
    '''structure : LBRACKET1 kvList RBRACKET1'''
    t[0] = ast.Structure(t[2])

def p_kvList_nested(t):
    '''kvList : kvTerm COMMA kvList'''
    t[0] = [t[1]] + t[3]

def p_kvList_kvTerm(t):
    '''kvList : kvTerm'''
    t[0] = [t[1]]

def p_kvTerm(t):
    '''kvTerm : expression COLON expression'''
    t[0] = t[1], t[3]

def p_expression_structure_call(t):
    '''expression : expression LBRACKET2 expression RBRACKET2'''
    t[0] = ast.StructureCall(t[1], t[3])

def p_list_null(t):
    '''list :  LBRACKET2 RBRACKET2'''
    t[0] = ast.List([])

def p_list_termList(t):
    '''list : LBRACKET2 termList RBRACKET2'''
    t[0] = ast.List(t[2])

def p_termList_nested(t):
    '''termList : term COMMA termList'''
    t[0] = [t[1]] + t[3]

def p_termList_term(t):
    '''termList : term'''
    t[0] = [t[1]]

def p_term_expression(t):
    '''term : expression'''
    t[0] = t[1]

def p_tuple_null(t):
    '''tuple :  LPAREN RPAREN'''
    t[0] = ast.Tuple([])

def p_tuple_termTuple(t):
    '''tuple : LPAREN termTuple RPAREN'''
    t[0] = ast.Tuple(t[2])

def p_termTuple_nested(t):
    '''termTuple : term COMMA termTuple'''
    t[0] = [t[1]] + t[3]

def p_termTuple_term(t):
    '''termTuple : term COMMA term'''
    t[0] = [t[1], t[3]]

def p_expression_name(t):
    '''expression : NAME'''
    global _names_aux
    _names_aux |= {t[1]}
    t[0] = ast.Identifier(t[1])

def p_error(t):
    ''''''
    reset()
    raise Exception("Syntax error at %s" % t)

parser = yacc.yacc()
