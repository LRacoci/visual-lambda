
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

# Reset variables
def _reset():
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

# Parser rules
class Node():
    pass

class start(Node):
    def __init__(self,t):
        self.t = t
        'start : functionList'
        _reset()

class functionList(Node):
    def __init__(self,t):
        self.t = t
        '''functionList : functionList function
                        | function '''

class function_assign(Node):
    def __init__(self,t):
        self.t = t
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
        _functions[t[1]] = t[3].t[0]
        _args[t[1]] = []

class function_args(Node):
    def __init__(self,t):
        self.t = t
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
        _functions[t[1]] = t[4].t[0]
        _args[t[1]] = t[2].t[0]

class args_list(Node):
    def __init__(self,t):
        self.t = t
        'argList : argList NAME'
        t[0] = t[1].t[0] + [t[2]]

class args(Node):
    def __init__(self,t):
        self.t = t
        'argList : NAME'
        t[0] = [t[1]]

class expression_binop(Node):
    def __init__(self,t):
        self.t = t
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
        #t[0] = [[t[2].t[0], t[1].t[0]], t[3].t[0]]
        t[0] = {
            "name" : " ",
            "child" : [
                {
                    "name" : " ",
                    "child" : [
                        {"name" : t[2]},
                        t[1].t[0]
                    ]
                },
                t[3].t[0]
            ]
        }

class expression_ifelse(Node):
    def __init__(self,t):
        self.t = t
        'expression : IF expression THEN expression ELSE expression %prec IFELSE'
        #t[0] = [[["cond", t[2].t[0]], t[4].t[0]], t[6].t[0]]
        t[0] = {
            "name" : " ",
            "child" : [
                {
                    "name" : " ",
                    "child" : [
                        {
                            "name" : " ",
                            "child" : [
                                {"name" : "cond"},
                                t[2].t[0]
                            ]
                        },
                        t[4].t[0]
                    ]
                },
                t[6].t[0]
            ]
        }

class expression_uminus(Node):
    def __init__(self,t):
        self.t = t
        'expression : MINUS expression %prec UNARY'
        #t[0] = [[t[1].t[0], t[2].t[0]], 0]
        t[0] = {
            "name" : " ",
            "child" : [
                {
                    "name" : " ",
                    "child" : [
                        t[1],
                        t[2].t[0]
                    ]
                },
                {
                    "name" : 0
                }
            ]
        }

class expression_not(Node):
    def __init__(self,t):
        self.t = t
        'expression : NOT expression %prec UNARY'
        #t[0] = [['xor', t[2].t[0]], 'True']
        t[0] = {
            "name" : " ",
            "child" : [
                {
                    "name" : " ",
                    "child" : [
                        {"name" : "xor"},
                        t[2].t[0]
                    ]
                },
                {
                    "name" : "True"
                }
            ]
        }

class expression_application(Node):
    def __init__(self,t):
        self.t = t
        'expression : application '
        t[0] = t[1].t[0]

class expression_group(Node):
    def __init__(self,t):
        self.t = t
        'expression : LPAREN expression RPAREN'
        t[0] = t[2].t[0]

class application_nested(Node):
    def __init__(self,t):
        self.t = t
        'application : application LPAREN expression RPAREN'
        #t[0] = [t[1].t[0], t[3].t[0]]
        t[0] = {
            "name" : " ",
            "child" : [ t[1].t[0], t[3].t[0] ]
        }

class application_expression(Node):
    def __init__(self,t):
        self.t = t
        'application : NAME LPAREN expression RPAREN'
        global _names_aux 
        _names_aux |= {t[1]} 
        global _dependence_aux
        _dependence_aux |= {t[1]}
        #t[0] = [t[1], t[3].t[0]]
        t[0] = {
            "name" : " ",
            "child" : [ t[1], t[3].t[0] ]
        }

class application_null(Node):
    def __init__(self,t):
        self.t = t
        'application : NAME LPAREN RPAREN'
        global _names_aux 
        _names_aux |= {t[1]} 

        global _dependence_aux
        _dependence_aux |= {t[1]}
        #t[0] = t[1]
        t[0] = {"name" : t[1]}

class expression_number(Node):
    def __init__(self,t):
        self.t = t
        'expression : NATURAL'
        #t[0] = t[1]
        t[0] = {
            "name" : int(t[1])
        }

class expression_name(Node):
    def __init__(self,t):
        self.t = t
        'expression : NAME'
        global _names_aux 
        _names_aux |= {t[1]} 

        #t[0] = t[1].t[0]
        t[0] = {
            "name" : t[1].t[0]
        }

class expression_bool(Node):
    def __init__(self,t):
        self.t = t
        '''expression : TRUE
                    | FALSE'''
        #t[0] = t[1].t[0]
        t[0] = {
            "name" : t[1]
        }

class error(Node):
    def __init__(self,t):
        self.t = t
        _reset()
        raise Exception("Syntax error at %s" % t)

