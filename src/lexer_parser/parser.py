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

_lambda_childrens = []
_lambda_closure = {}

_functions = {}
_whereDict = {}
_args = {}
_dependence = {}

_exec_tree = {}

_eta = False
_eta_list = []
_eta_temp = 0

_pattern_functions = {}

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

    patternMatching()

    global _functions
    global _args
    global _dependence
    global _exec_tree
    global _whereDict
    global _lambda_closure

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
    #print json.dumps({"_lambda_closure":_lambda_closure}, indent = 1, default = lambda o : o.__dict__)
    #Check if every name is a function name or an argument in the current function
    for func in namesOut['functions']:
        set_of_args = {arg for arg in namesOut['args'][func]}
        set_of_wheres = {where["var"] for where in _whereDict[func]}
        set_of_lambda_vars = {var for var in _lambda_closure[func]} if func in _lambda_closure else set()
        aux = (_names[func] - set_of_args) - set_of_functions - set_of_wheres - set_of_lambda_vars
        if len(aux) > 0:
            str_aux = ", ".join(list(aux))
            clean()
            raise Exception ("Error: {} used inside {} not declared".format(str_aux, func))

    global _eta
    if _eta:
        etaOptimization()
    #print json.dumps(_functions, default = lambda o : {type(o).__name__ : o.__dict__}, indent = 1)
    _exec_tree = ast.execute(_functions['main'])
    execOut['tree'] = dict(_exec_tree)
    clean()

# Clean variables and symbol table
def clean():
    global lambdaCounter
    lambdaCounter = 0
    global _lambda_childrens
    _lambda_childrens = []
    global _lambda_closure
    _lambda_closure = {}

    symboltable.clean()
    if ast._memo:
        ast.memoized = {}
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

    global _pattern_functions
    _pattern_functions = {}

# Do the pattern matching
def patternMatching():
    global _functions
    global _args
    global _pattern_functions

    for func in _functions:
        if len(_functions[func]) == 1:
            _functions[func] = _functions[func][func]
            _args[func] = _args[func][func]
        else:
            _pattern_functions[func] = True
            tree = _functions[func][func]
            argsList = _args[func][func]
            for patternKey in _functions[func]:
                if patternKey != func:
                    argsValues = _args[func][patternKey]
                    eqs = []
                    for (arg, value) in zip(argsList, argsValues):
                        if arg != value:
                            eqs += [ast.Binop(ast.Identifier(arg), "==", value)]
                    cond = eqs[0]
                    for i in range(1,len(eqs)):
                        cond = ast.Binop(cond, "and", eqs[i])
                    tree = ast.Conditional(cond, _functions[func][patternKey], tree)
            _functions[func] = tree
            _args[func] = argsList

# Set optimization flag
def setOptimization(eta_flag, fold_flag, prop_flag, memo_flag):
    global _eta
    _eta = eta_flag
    ast.setOptimization(fold_flag, prop_flag, memo_flag)

# Do the eta optimization
def etaOptimization():
    global _eta_list
    global _functions
    global _eta_temp
    global _whereDict
    global _args
    global _pattern_functions

    toRemove = []
    for func in _eta_list:
        if func in _pattern_functions:
            toRemove.append(func)
    for func in toRemove:
        _eta_list.remove(func)

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
                    if arg != None:
                        funcWhere += [{'var': "{}arg".format(_eta_temp), 'expression': arg}]
                        _eta_temp += 1

                # Build an arg map
                argMap = {}
                p = 0
                for num in range(init, _eta_temp):
                    argMap[_args[node][p]] = "{}arg".format(num)
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
    for fName in _lambda_childrens:
        if fName not in _lambda_closure:
            _lambda_closure[fName] = []

        _lambda_closure[fName] += [w['var'] for w in t[4]]

    global _names
    global _names_aux
    _names[t[1]] = _names_aux

    _names_aux = set()

    global _dependence
    global _dependence_aux
    _dependence[t[1]] =  list(_dependence_aux)

    _dependence_aux = set()
    global _functions
    _functions[t[1]] = {t[1]:t[3]}
    global _args
    _args[t[1]] = {t[1]:[]}
    global _whereDict
    _whereDict[t[1]] = t[4]

    if t[1] != 'main' and type(t[3]).__name__ == "Application" and t[4] == []:
        global _eta_list
        _eta_list += [t[1]]

# Get a unique name of a function definition
def getName(arg):
    primal = True
    tp = type(arg).__name__
    if tp == "Constant":
        primal = False
        tp += "(" + arg.type + ")"
        vl = str(arg.value)
    elif tp == "List":
        primal = False
        vl = ""
        for v in arg.exprs:
            tpAux, vlAux, _ = getName(v)
            tp += tpAux
            vl += vlAux
    elif tp == "Tuple":
        primal = False
        vl = ""
        for v in arg.exprs:
            tpAux, vlAux, _ = getName(v)
            tp += tpAux
            vl += vlAux
    elif tp == "Structure":
        primal = False
        vl = ""
        for v in arg.kvPairs:
            tpAuxKey, vlAuxKey, _ = getName(v[0])
            tpAuxValue, vlAuxValue, _ = getName(v[1])
            tp += tpAuxKey + ":" + tpAuxValue
            vl += vlAuxKey + ":" + vlAuxValue
    else:
        vl = arg
    return tp, vl, primal

def p_function_args(t):
    '''function : NAME argList DEFINITION expression where_expression'''
    _, funcName, args, _, expression, wheres = t

    name = ""
    primal = True
    for arg in args:
        tp, vl, check = getName(arg)
        name += "(" + tp + ")" + vl
        if not check:
            primal = False
    if primal:
        name = funcName

    global _names
    global _names_aux
    _names[funcName] = _names_aux

    _names_aux = set()

    global _dependence
    global _dependence_aux
    _dependence[funcName] = list(_dependence_aux)

    _dependence_aux = set()

    global _functions
    if funcName in _functions:
        _functions[funcName][name] = expression
    else:
        _functions[funcName] = {name:expression}
    global _args
    if funcName in _args:
        _args[funcName][name] = args
    else:
        _args[funcName] = {name:args}
    global _whereDict
    _whereDict[funcName] = wheres

    if funcName != 'main' and type(expression).__name__ == "Application" and wheres == []:
        global _eta_list
        _eta_list += [funcName]

    global _lambda_closure
    for fName in _lambda_childrens:
        if fName not in _lambda_closure:
            _lambda_closure[fName] = []

        _lambda_closure[fName] += [w['var'] for w in wheres] + args



lambdaCounter = 0
def p_lambda_expression(t):
    '''lambda : LAMBDA argList ARROW expression'''
    _,_, args, _, expression = t;
    global lambdaCounter
    funcName = "lambda {}".format(lambdaCounter)
    lambdaCounter += 1


    global _lambda_childrens
    global _lambda_closure
    for fName in _lambda_childrens:
        if fName not in _lambda_closure:
            _lambda_closure[fName] = []

        _lambda_closure[fName] += args

    _lambda_childrens += [funcName]

    wheres = []

    name = ""
    primal = True
    for arg in args:
        tp, vl, check = getName(arg)
        name += "(" + tp + ")" + vl
        if not check:
            primal = False
    if primal:
        name = funcName

    global _names
    global _names_aux
    _names[funcName] = _names_aux

    _names_aux = set()

    global _dependence
    global _dependence_aux
    _dependence[funcName] = list(_dependence_aux)

    _dependence_aux = set()

    global _functions
    if funcName in _functions:
        _functions[funcName][name] = expression
    else:
        _functions[funcName] = {name:expression}
    global _args
    if funcName in _args:
        _args[funcName][name] = args
    else:
        _args[funcName] = {name:args}
    global _whereDict
    _whereDict[funcName] = wheres

    if funcName != 'main' and type(expression).__name__ == "Application" and wheres == []:
        global _eta_list
        _eta_list += [funcName]

    t[0] = ast.Identifier(funcName)

def p_application_lambda(t):
    '''application  : LPAREN lambda RPAREN LPAREN expression RPAREN
                    | LPAREN lambda RPAREN LPAREN lambda RPAREN'''
    t[0] = ast.Application(t[2].name, t[5])

# def p_expression_lambda(t):
#     '''expression : lambda'''
#     t[0] = t[1]

def p_args_list(t):
    '''argList : argList argExpr'''
    t[0] = t[1] + [t[2]]

def p_args(t):
    '''argList : argExpr'''
    t[0] = [t[1]]

def p_arg_expr_name(t):
    '''argExpr : NAME'''
    t[0] = t[1]

def p_arg_expr_constant_expr(t):
    '''argExpr : constantExpr'''
    t[0] = t[1]

def p_constant_expr(t):
    '''constantExpr : constant
        | constList
        | constTuple
        | constStructure'''
    t[0] = t[1]

def p_const_structure_null(t):
    '''constStructure : LBRACKET1 RBRACKET1'''
    t[0] = ast.Structure([])

def p_const_structure_kvList(t):
    '''constStructure : LBRACKET1 constKvList RBRACKET1'''
    t[0] = ast.Structure(t[2])

def p_const_kvList_nested(t):
    '''constKvList : constKvTerm COMMA constKvList'''
    t[0] = [t[1]] + t[3]

def p_const_kvList_kvTerm(t):
    '''constKvList : constKvTerm'''
    t[0] = [t[1]]

def p_const_kvTerm(t):
    '''constKvTerm : constantExpr COLON constantExpr'''
    t[0] = t[1], t[3]

def p_const_list_null(t):
    '''constList :  LBRACKET2 RBRACKET2'''
    t[0] = ast.List([])

def p_const_list_termList(t):
    '''constList : LBRACKET2 constTermList RBRACKET2'''
    t[0] = ast.List(t[2])

def p_const_termList_nested(t):
    '''constTermList : constTerm COMMA constTermList'''
    t[0] = [t[1]] + t[3]

def p_const_termList_term(t):
    '''constTermList : constTerm'''
    t[0] = [t[1]]

def p_const_term_expression(t):
    '''constTerm : constantExpr'''
    t[0] = t[1]

def p_const_tuple_null(t):
    '''constTuple :  LPAREN RPAREN'''
    t[0] = ast.Tuple([])

def p_const_tuple_termTuple(t):
    '''constTuple : LPAREN constTermTuple RPAREN'''
    t[0] = ast.Tuple(t[2])

def p_const_termTuple_nested(t):
    '''constTermTuple : constTerm COMMA constTermTuple'''
    t[0] = [t[1]] + t[3]

def p_const_termTuple_term(t):
    '''constTermTuple : constTerm COMMA constTerm'''
    t[0] = [t[1], t[3]]

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
    '''application : NAME LPAREN expression RPAREN
        | NAME LPAREN lambda RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.Application(t[1], t[3])

def p_application_null(t):
    '''application : NAME LPAREN RPAREN'''
    global _names_aux
    _names_aux |= {t[1]}
    global _dependence_aux
    _dependence_aux |= {t[1]}
    t[0] = ast.Application(t[1], None)

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
    clean()
    raise Exception("Syntax error at %s" % t)

parser = yacc.yacc()
