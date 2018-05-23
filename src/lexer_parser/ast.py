from abc import ABCMeta, abstractmethod
import parser
import symboltable
import json

NOT_IMPLEMENTED = "You should implement this."

_argMap = {}

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
            "type" : type(value).__name__,
            "value" : value,
            "json" : {
                "name" : show if show else str(value),
                "children" : [
                    {
                        "name" : " ",
                        "children" : [
                            {"name" : node.op},
                            left['json']
                        ]
                    },
                    right['json']
                ]
            }
        }

        if newType:
            ret['type'] = newType
        elif node.op in relOps:
            ret['type'] = "bool"
        elif left['type'] == right['type']:
            ret['type'] = left['type']

        import json
        if exprFromKey != None:
            ret['exprFromKey'] = exprFromKey

        return ret

    # Visit if-then-else executing just one side depending on the condition
    def visit_conditional(self, node):
        cond = node.cond.visit(BuildD3Json())

        if cond['value']:
            ifthen = node.ifthen.visit(BuildD3Json())
            ifelse = { "json" : { "name" : "else not executed" } }
            value = ifthen['value']
        else:
            ifthen = { "json" : { "name" : "then not executed" } }
            ifelse = node.ifelse.visit(BuildD3Json())
            value = ifelse['value']

        return {
            "type" : type(value).__name__,
            "value" : value,
            "json" : {
                "name" : value,
                "children" : [
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
            }
        }

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
            import json
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
            "json" : {
                "name" : "({}) {}".format(node.type, show)
            }
        }

    # Visit a identifier from the symbol table or function table
    def visit_identifier(self, node):
        if node.name in symboltable.funcTable:
            entry = symboltable.funcTable[node.name]
            ret = dict(entry)
            if 'json' in entry:
                ret['json'] = {
                    "name" : node.name,# + " = " + str(entry['value']),
                    "children" : [
                        entry['json'] if 'json' in entry else {}
                    ]
                }
            else:
                ret["json"] = {
                    "name" : node.name + " = " + str(entry['value'])
                }

            return ret
        elif node.name in parser._functions:
            return {
                "type" : "function",
                "value" : node.name,
                "json" : {
                    "name" : node.name + " = function"
                }
            }
        else:
            parser.clean()
            raise Exception(node.name + " is not defined")

    # Visit a function application, building the function symbol table
    # calculating where and checking erros when making the call
    def visit_application(self, node):
        args = []
        trees = []
        types = []
        exprFromKeyS = []
        while type(node) is Application:
            if node.arg != None:
                exec_tree = node.arg.visit(BuildD3Json())
                arg = exec_tree['value']
                tree = exec_tree['json']
                tp = exec_tree['type']
                exprFromKey = exec_tree['exprFromKey'] if "exprFromKey" in exec_tree else None
                execTrees = [exec_tree]
                args = [arg] + args
                trees = [tree] + trees
                types = [tp] + types
                exprFromKeyS = [exprFromKey] + exprFromKeyS
            node = node.func

        if node in symboltable.funcTable:
            if symboltable.funcTable[node]['type'] == "function":
                funcName = node
                node = symboltable.funcTable[node]['value']
                funcName = "(" + funcName + " = " + node + ")"
            else:
                parser.clean()
                raise Exception(node + " is not a function")
        else:
            funcName = node

        if len(args) > len(parser._args[node]):
            parser.clean()
            raise Exception(node + " is called with more arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))
        if len(args) < len(parser._args[node]):
            parser.clean()
            raise Exception(node + " is called with less arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))

        symboltable.getTable(node)

        while len(symboltable.funcTable) < len(args):
            entry = {}
            entry['value'] = args[len(symboltable.funcTable)]
            entry['type'] = types[len(symboltable.funcTable)]
            if exprFromKeyS[len(symboltable.funcTable)] != None:
                entry['exprFromKey'] = exprFromKeyS[len(symboltable.funcTable)]

            symboltable.funcTable[parser._args[node][len(symboltable.funcTable)]] = entry

        variables = []
        for entry in parser._whereDict[node]:
            result = entry['expression'].visit(BuildD3Json())
            symboltable.funcTable[entry['var']] = result
            variables += [(entry['var'], result)]

        exec_tree = parser._functions[node].visit(BuildD3Json())

        symboltable.deleteTable(node)

        args_string = ""
        for arg in parser._args[node]:
            args_string += " " + arg

        args_tree = {
            "name": funcName + args_string + " = ", #+ str(exec_tree['value']),
            "children": [
                exec_tree['json']
            ]
        }

        for tree in trees:
            args_tree = {
                "name": " ",
                "children": [
                    args_tree,
                    tree
                ]
            }

        for v in variables:
            args_tree = {
                    "name": "",
                    "children": [
                        args_tree,
                        {
                            "name" : "where " + v[0] + " = ",# + str(v[1]['value']),
                            "children": [
                                v[1]['json']
                            ]
                        }
                    ]
                }

        ret = dict(exec_tree)
        ret['json'] = args_tree
        #ret['type'] = type(exec_tree['value']).__name__,
        return ret

# Execute the main function of the program, with where
def execute(node):

    symboltable.getTable('main')

    variables = []
    for entry in parser._whereDict['main']:
        result = entry['expression'].visit(BuildD3Json())
        symboltable.funcTable[entry['var']] = result
        variables += [(entry['var'], result)]

    exec_tree = node.visit(BuildD3Json())
    symboltable.deleteTable('main')

    args_tree = {
        "name": "main = " + str(exec_tree['value']),
        "children": [
            exec_tree['json']
        ]
    }

    if len(variables) > 0:
        for v in variables:
            args_tree = {
                    "name": "",
                    "children": [
                        args_tree,
                        {
                            "name" : "where " + v[0] + " = ",# + str(v[1]['value']),
                            "children": [
                                v[1]['json']
                            ]
                        }
                    ]
                }
        out = {
            "name": "main = " + str(exec_tree['value']),
            "children": [
                args_tree
            ]
        }
    else:
        out = args_tree

    return out

# Do the eta search changing variables names
def etaSearch(m, node):
    global _argMap
    _argMap = m
    parser._functions[node].visit(EtaSearch())
