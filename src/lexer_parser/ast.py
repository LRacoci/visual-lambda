from abc import ABCMeta, abstractmethod
import parser
import symboltable
import json

debug = False
auxSymbols = {}

NOT_IMPLEMENTED = "You should implement this."

_argMap = {}
_fold = False
_prop = False
def setOptimization(fold_flag, prop_flag):
    global _fold
    _fold = fold_flag
    global _prop
    _prop = prop_flag

def hashable(v):
    """Determine whether `v` can be hashed."""
    try:
        hash(v)
    except TypeError:
        return False
    return True

# AST nodes
class Node():
    __metaclass__ = ABCMeta
    @abstractmethod
    def visit(self, visitor):
        raise NotImplementedError(NOT_IMPLEMENTED)

# Binary operation node
class Binop(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def visit(self, visitor):
        return visitor.visit_binop(self)

# If-then-else conditional node
class Conditional(Node):
    def __init__(self, cond, ifthen, ifelse):
        self.cond = cond
        self.ifthen = ifthen
        self.ifelse = ifelse

    def visit(self, visitor):
        return visitor.visit_conditional(self)

# Structure json node
class Structure(Node):
    def __init__(self, kvPairs):
        self.kvPairs = kvPairs

    def visit(self, visitor):
        return visitor.visit_structure(self)

class List(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def visit(self, visitor):
        return visitor.visit_list(self)

class Tuple(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def visit(self, visitor):
        return visitor.visit_tuple(self)

# Structure json call node
class StructureCall(Node):
    def __init__(self, structure, expression):
        self.structure = structure
        self.expression = expression

    def visit(self, visitor):
        return visitor.visit_structureCall(self)

# Constant node
class Constant(Node):
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def visit(self, visitor):
        return visitor.visit_constant(self)

# Identifier node
class Identifier(Node):
    def __init__(self, name):
        self.name = name

    def visit(self, visitor):
        return visitor.visit_identifier(self)

class Lambda(Node):
    def __init__(self, arg, expr):
        self.arg = arg
        self.expr = expr

    def visit(self, visitor):
        return visitor.visit_lambda(self)

# Function application node
class Application(Node):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def visit(self, visitor):
        return visitor.visit_application(self)

# Abstract class to implemente pattern visitor
class NodeVisitor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def visit_binop(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_conditional(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_structure(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_structureCall(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_constant(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_identifier(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_lambda(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_application(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

# Concrete class that goes down the tree changing variables names
class EtaSearch(NodeVisitor):

    def visit_binop(self, node):
        node.left.visit(EtaSearch())
        node.right.visit(EtaSearch())

    def visit_conditional(self, node):
        node.cond.visit(EtaSearch())
        node.ifthen(EtaSearch())
        node.ifelse(EtaSearch())

    def visit_structure(self, node):
        for exprKey, exprVal in node.kvPairs:
            exprVal.visit(EtaSearch())
            exprKey.visit(EtaSearch())

    def visit_structureCall(self, node):
        node.structure.visit(EtaSearch())
        node.expression.visit(EtaSearch())

    def visit_constant(self, node):
        pass

    def visit_lambda(self, node):
        # ???
        pass

    def visit_tuple(self, node):
        for expr in node.exprs:
            expr.visit(EtaSearch())

    def visit_list(self, node):
        for expr in node.exprs:
            expr.visit(EtaSearch())

    def visit_identifier(self, node):
        global _argMap
        if node.name in _argMap:
            node.name = _argMap[node.name]

    def visit_application(self, node):
        while type(node) is Application:
            if node.arg != None:
                node.arg.visit(EtaSearch())
            node = node.func

# Concrete class that has the visit methods implementation
class BuildD3Json(NodeVisitor):

    # Visit a binary operation checking value types
    def visit_binop(self, node):
        left = node.left.visit(BuildD3Json())
        right = node.right.visit(BuildD3Json())

        exprFromKey = None
        newType = None
        show = None

        arithmetic_op = {"float", "int", "bool", "long"}
        lr_types_union = {left['type'], right['type']}

        if "unbind" in lr_types_union:
            value = None
            newType = "unbind"
            show = "Unbind None"

        else:
            if node.op == '+':
                if lr_types_union == {"list"}:
                    exprFromKey = {}
                    for key in left['exprFromKey']:
                        exprFromKey[key] = left['exprFromKey'][key]
                    for key in right['exprFromKey']:
                        exprFromKey[len(left['value']) + key] = right['exprFromKey'][key]

                elif not lr_types_union < arithmetic_op and lr_types_union != {"str"}:
                    parser.clean()
                    raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))
                value = left['value'] + right['value']

            if node.op == '-':
                if not lr_types_union < arithmetic_op:
                    parser.clean()
                    raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))
                value = left['value'] - right['value']

            if node.op == '*':
                if not lr_types_union < arithmetic_op:
                    parser.clean()
                    raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))
                value = left['value'] * right['value']

            if node.op == '/':
                if not lr_types_union < arithmetic_op:
                    parser.clean()
                    raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))
                if right['value'] == 0:
                    parser.clean()
                    raise Exception("Error: division by zero between \'{}:{}\' and \'{}:{}\'".format(left['value'], left['type'], right['value'], right['type']))
                value = left['value'] / right['value']

            if node.op == 'and':
                if lr_types_union == {"structure"}:
                    value = {}
                    for key in left['value']:
                        if key in right['value']:
                            value[key] = right['value'][key]

                    exprFromKey = {}
                    for key in left['exprFromKey']:
                        if key in right['exprFromKey']:
                            exprFromKey[key] = right['exprFromKey'][key]

                else:
                    value = left['value'] and right['value']

            if node.op == 'xor':
                if lr_types_union == {"structure"}:
                    value = {}
                    for key in left['value']:
                        if key not in right['value']:
                            value[key] = left['value'][key]

                    for key in right['value']:
                        if key not in left['value']:
                            value[key] = right['value'][key]

                    exprFromKey = {}
                    for key in left['exprFromKey']:
                        if key not in right['exprFromKey']:
                            exprFromKey[key] = left['exprFromKey'][key]

                    for key in right['exprFromKey']:
                        if key not in left['exprFromKey']:
                            exprFromKey[key] = right['exprFromKey'][key]

                else:
                    value = (left['value'] and not right['value']) or (not left['value'] and right['value'])

            if node.op == 'ior':
                if lr_types_union == {"structure"}:
                    value = {}
                    for key in left['value']:
                        value[key] = left['value'][key]
                    for key in right['value']:
                        value[key] = right['value'][key]

                    exprFromKey = {}
                    for key in left['exprFromKey']:
                        exprFromKey[key] = left['exprFromKey'][key]
                    for key in right['exprFromKey']:
                        exprFromKey[key] = right['exprFromKey'][key]

                else:
                    value = left['value'] or right['value']

            if node.op == '==':
                value = left['value'] == right['value']

            if node.op == '!=':
                value = left['value'] != right['value']

            if node.op == '>=':
                value = left['value'] >= right['value']

            if node.op == '<=':
                value = left['value'] <= right['value']

            if node.op == '>':
                value = left['value'] > right['value']

            if node.op == '<':
                value = left['value'] < right['value']


        relOps = {"==", "!=", ">=", "<=", ">", "<"}

        ret = {
            "value" : value,
        }

        if newType:
            ret['type'] = newType
        elif node.op in relOps:
            ret['type'] = "bool"
        elif left['type'] == right['type']:
            ret['type'] = left['type']
        else:
            ret['type'] = type(value).__name__

        if exprFromKey != None:
            ret['exprFromKey'] = exprFromKey

        global _fold


        ret["json"] = {}
        if show:
            ret["json"]["name"] = show
        else:
            ret["json"]["name"] = "({}) {}".format(ret['type'], ret['value'])

        if _fold:
            ret['const'] = left['const'] and right['const']

        if not (_fold and ret['const']):
            ret["json"]["children"] = [
                {
                    "name" : " ",
                    "children" : [
                        {"name" : node.op},
                        left['json']
                    ]
                },
                right['json']
            ]

        return ret

    # Visit if-then-else executing just one side depending on the condition
    def visit_conditional(self, node):
        retType = None
        cond = node.cond.visit(BuildD3Json())

        const = None

        if cond['type'] == 'unbind':
            value = None
            ifelse = node.ifelse.visit(BuildD3Json())
            ifthen = node.ifthen.visit(BuildD3Json())
            retType = 'unbind'
            const  = False
        elif cond['value']:
            ifthen = node.ifthen.visit(BuildD3Json())
            retType = ifthen['type']
            ifelse = { "json" : { "name" : "else not executed" } }
            value = ifthen['value']
            if _fold:
                const =  ifthen['const']
        else:
            ifthen = { "json" : { "name" : "then not executed" } }
            ifelse = node.ifelse.visit(BuildD3Json())
            retType = ifelse['type']
            value = ifelse['value']
            if _fold:
                const = ifelse['const']


        ret = {
            "type" : retType if retType else type(value).__name__,
            "value" : value,
            "json" : {
                "name" : "({}) {}".format(retType,value),

            }
        }

        if _fold:
            ret['const'] = const

        if not (_fold and const):
            ret['json']['children']  = [
                {
                    "name" : " ",
                    "children" : [
                        {
                            "name" : " ",
                            "children" : [
                                {"name" : "cond"},
                                cond['json']
                            ]
                        },
                        ifthen['json']
                    ]
                },
                ifelse['json']
            ]
        return ret

    # Visit a structure json and build its value
    def visit_structure(self, node):
        exprFromKey = {}
        children = []
        value = {}
        for exprKey, exprVal in node.kvPairs:
            valExpr = exprVal.visit(BuildD3Json())
            keyExpr = exprKey.visit(BuildD3Json())
            keyJson = dict(keyExpr['json'])
            keyJson['name'] = "key : ({}) {}".format(keyExpr['type'], keyExpr['value'])
            valJson = dict(valExpr['json'])
            valJson['name'] = "value : ({}) {}".format(valExpr['type'], valExpr['value'])
            child = {
                "name" : "({}) {} : ({}) {}".format(keyExpr['type'], keyExpr['value'], valExpr['type'], valExpr['value']),
                "children" : [
                    keyJson,
                    valJson
                ]
            }
            children += [child]
            key = keyExpr['value']
            if not hashable(key):
                key = str(key)

            value[key] = valExpr['value']
            exprFromKey[key] = valExpr

        return {
            "type" : "structure",
            "value" : value,
            "exprFromKey" : exprFromKey,
            "json" : {
                "name" : "(structure)",
                "children" : children
            }
        }

    def visit_tuple(self, node):
        exps = [expr.visit(BuildD3Json()) for expr in node.exprs]
        return {
            "type": "tuple",
            "value": tuple([exp['value'] for exp in exps]),
            "exprFromKey": {k : exps[k] for k in range(len(exps))},
            "json": {
                "name": "(tuple)",
                "children" : [exp['json'] for exp in exps]
            }
        }

    def visit_list(self, node):
        exps = [expr.visit(BuildD3Json()) for expr in node.exprs]
        return {
            "type": "list",
            "value": [exp['value'] for exp in exps],
            "exprFromKey": {k : exps[k] for k in range(len(exps))},
            "json": {
                "name": "(list)",
                "children" : [exp['json'] for exp in exps]
            }
        }

    # Visit a structure json and get its value depending on the key
    def visit_structureCall(self, node):
        structure = node.structure.visit(BuildD3Json())
        expression = node.expression.visit(BuildD3Json())

        if structure["type"] != "structure"  and structure["type"] != "list":
            raise Exception("{} is not a structure nor a list".format(structure["value"]))
        key = expression['value']
        if not hashable(key):
            key = str(key)

        if "exprFromKey" not in structure:
            raise Exception("No exprFromKey")

        if key in structure["exprFromKey"]:
            val = structure["exprFromKey"][key]
        else:
            val = {
                'type' : "ERROR",
                'value' : None
            }
        ret = dict(val)
        ret["json"] = {
            "name" : "({}) {}".format(val['type'], val['value']),
            "children" : [
                structure['json'],
                expression['json']
            ]
        }
        return ret

    # Visit a constant depending on its type
    def visit_constant(self, node):
        if node.type == "int":
            value = int(node.value)
            show = str(value)
        elif node.type == "float":
            value = float(node.value)
            show = str(value)
        elif node.type == "str":
            value = str(node.value)
            show = '"{}"'.format(str(value))
        elif node.type == "bool":
            value = True if node.value == "True" else False
            show = str(value)
        elif node.type == "none" and node.value == "None":
            value = None
            show = "None"

        return {
            "type" : node.type,
            "value" : value,
            "const" : True,
            "json" : {
                "name" : "({}) {}".format(node.type, show)
            }
        }

    # Visit a identifier from the symbol table or function table
    def visit_identifier(self, node):
        global auxSymbols
        if node.name in auxSymbols and len(auxSymbols[node.name]) > 0:
            arg = auxSymbols[node.name][-1]
            d3Arg = arg.visit(BuildD3Json())

            if 'json' in d3Arg:
                d3Arg['json'] = {
                    "name" : node.name,
                    "children" : [
                        {"name":  d3Arg['json']['name']}
                    ]
                }
            else :
                d3Arg['json'] = {
                    "name" : node.name
                }
            return d3Arg
        else:
            return {
                "const" : False,
                "value" : None,
                "type" : "unbind",
                "json" : {
                    "name" : "(unbind) " +  node.name
                }
            }

    # Visit a lambda expression, returns an applicable function as 'value'
    def visit_lambda(self, node):
        closure = {}
        global auxSymbols
        for var in auxSymbols:
            if len(auxSymbols[var]) > 0 :
                closure[var] = auxSymbols[var][-1]

        def bind(arg):

            global auxSymbols
            if node.arg not in auxSymbols:
                auxSymbols[node.arg] = []

            auxSymbols[node.arg] += [arg]

            func = node.expr.visit(BuildD3Json())

            auxSymbols[node.arg].pop()

            func['json'] = {
                    "name": "(lambda)",
                    "children" : [
                        func['json'],
                        {"name" : node.arg}
                    ]
                }

            return func

        ret = node.expr.visit(BuildD3Json())

        ret['bind'] = bind
        ret['type'] = "function"
        ret['closure'] = closure

        return ret

    # Visit a function application, building the function symbol table
    # calculating where and checking erros when making the call
    def visit_application(self, node):
        func = node.func.visit(BuildD3Json())
        arg = node.arg.visit(BuildD3Json())
        if "unbind" in {func["type"], arg["type"]}:
            return {
                "value" : None,
                "type" : "unbind",
                "const" : False,
                "json" : {
                    "name" : "",
                    "children" : [
                        func['json'],
                        arg['json']
                    ]
                }
            }

        print "bind function : ", func['bind']
        ret = func['bind'](node.arg)
        ret['json'] = {
            "name" : "({}) {}".format(ret['type'], ret['value']),
            "children" : [
                ret['json'],
                arg['json']
            ]
        }
        return ret

# Execute the main function of the program, with where
def execute(node):
    global auxSymbols

    print json.dumps(
        auxSymbols,
        default = lambda o : {type(o).__name__ : vars(o)},
        indent = 1
    )

    if "main" in auxSymbols and len(auxSymbols["main"]) == 1:
        main = auxSymbols["main"][0]
        ret = main.visit(BuildD3Json())

        return {
            "name" : "main",
            "children" : [
                ret['json']
            ]
        }

# Do the eta search changing variables names
def etaSearch(m, node):
    global _argMap
    _argMap = m
    parser._functions[node].visit(EtaSearch())
