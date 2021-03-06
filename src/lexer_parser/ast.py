from abc import ABCMeta, abstractmethod
import parser
import symboltable
import json

NOT_IMPLEMENTED = "You should implement this."

_argMap = {}
_fold = False
_prop = False
_memo = False

specialNames = {
    "map",
    "filter",
    "fold",
    "first",
    "rest",
    "rest",
    "end",
    "first",
    "init",
    "len",
    "last"
}

memoized = {}

def setOptimization(fold_flag, prop_flag, memo_flag):
    global _fold
    _fold = fold_flag
    global _prop
    _prop = prop_flag
    global _memo
    _memo = memo_flag

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

# List definition node
class List(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def visit(self, visitor):
        return visitor.visit_list(self)

# Tuple definition node
class Tuple(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def visit(self, visitor):
        return visitor.visit_tuple(self)

# Structure, list and tuple json call node
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

# Abstract class to implement pattern visitor
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
    def visit_list(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_tuple(self, node):
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
        node.ifthen.visit(EtaSearch())
        node.ifelse.visit(EtaSearch())

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

# Concrete class that goes down the tree changing variables structures
class PropSearch(NodeVisitor):

    def visit_binop(self, node):
        node.left = node.left.visit(PropSearch())
        node.right = node.right.visit(PropSearch())
        return node

    def visit_conditional(self, node):
        node.cond = node.cond.visit(PropSearch())
        node.ifthen = node.ifthen.visit(PropSearch())
        node.ifelse = node.ifelse.visit(PropSearch())
        return node

    def visit_structure(self, node):
        newKvPairs = []
        for exprKey, exprVal in node.kvPairs:
            newKvPairs.append((exprKey.visit(PropSearch()), exprVal.visit(PropSearch())))
        node.kvPairs = newKvPairs
        return node

    def visit_structureCall(self, node):
        node.structure = node.structure.visit(PropSearch())
        node.expression = node.expression.visit(PropSearch())
        return node

    def visit_constant(self, node):
        return node

    def visit_tuple(self, node):
        newExprs = []
        for expr in node.exprs:
            newExprs.append(expr.visit(PropSearch()))
        node.exprs = newExprs
        return node

    def visit_list(self, node):
        newExprs = []
        for expr in node.exprs:
            newExprs.append(expr.visit(PropSearch()))
        node.exprs = newExprs
        return node

    def process(self, entry):
        if entry['type'] in {'int', 'bool', 'float', 'str', 'none'}:
            return Constant(entry['value'], entry['type'])
        elif entry['type'] == 'list':
            nodes = []
            for i in range(len(entry['value'])):
                nodeEntry = entry['exprFromKey'][i]
                exprFromKey = None
                if 'exprFromKey' in nodeEntry:
                    exprFromKey = nodeEntry['exprFromKey']
                node = self.process({
                    'type' : nodeEntry['type'],
                    'value' : nodeEntry['value'],
                    'exprFromKey' : exprFromKey
                })
                nodes.append(node)
            return List(nodes)
        elif entry['type'] == 'tuple':
            nodes = []
            for i in range(len(entry['value'])):
                nodeEntry = entry['exprFromKey'][i]
                exprFromKey = None
                if 'exprFromKey' in nodeEntry:
                    exprFromKey = nodeEntry['exprFromKey']
                node = self.process({
                    'type' : nodeEntry['type'],
                    'value' : nodeEntry['value'],
                    'exprFromKey' : exprFromKey
                })
                nodes.append(node)
            return Tuple(nodes)
        elif entry['type'] == 'structure':
            nodes = []
            for k in entry['value']:
                if entry['exprFromKey'][k]['keyType'] in {'structure', 'list', 'tuple'}:
                    keyNode = entry['exprFromKey'][k]['keyAst'].visit(PropSearch())
                else:
                    keyNode = self.process({
                        'type' : entry['exprFromKey'][k]['keyType'],
                        'value' : k,
                        'exprFromKey' : None
                    })
                exprFromKey = None
                if 'exprFromKey' in entry['exprFromKey'][k]:
                    exprFromKey = entry['exprFromKey'][k]['exprFromKey']
                node = (keyNode, self.process({
                    'type' : entry['exprFromKey'][k]['type'],
                    'value' : entry['exprFromKey'][k]['value'],
                    'exprFromKey' : exprFromKey
                }))
                nodes.append(node)
            return Structure(nodes)

    def visit_identifier(self, node):
        global _argMap
        if node.name in _argMap:
            entry = _argMap[node.name]
            return self.process(entry)
        else:
            return node

    def visit_application(self, node):
        nodeFirst = node
        while type(node) is Application:
            if node.arg != None:
                node.arg = node.arg.visit(PropSearch())
            node = node.func
        return nodeFirst

# Concrete class that has the visit methods implementation
class BuildD3Json(NodeVisitor):

	# Visit a binary operation checking value types
    def visit_binop(self, node):
        left = node.left.visit(BuildD3Json())
        right = node.right.visit(BuildD3Json())

        exprFromKey = None
        newType = None

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
            "value" : value
        }

        if newType:
            ret['type'] = newType
        elif node.op in relOps:
            ret['type'] = "bool"
        elif left['type'] == right['type']:
            ret['type'] = left['type']

        if exprFromKey != None:
            ret['exprFromKey'] = exprFromKey

        global _fold
        if _fold:
            ret['const'] = left['const'] and right['const']
        else:
            ret['const'] = False

        ret["json"] = {
            "name" : "({}) {}".format(ret['type'], ret['value'])
        }

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
        exprFromKey = None
        if cond['value']:
            ifthen = node.ifthen.visit(BuildD3Json())
            retType = ifthen['type']
            ifelse = { "json" : { "name" : "else not executed" } }
            value = ifthen['value']
            answer = ifthen['json']
            if 'exprFromKey' in ifthen:
                exprFromKey = ifthen['exprFromKey']
        else:
            ifthen = { "json" : { "name" : "then not executed" } }
            ifelse = node.ifelse.visit(BuildD3Json())
            retType = ifelse['type']
            value = ifelse['value']
            answer = ifelse['json']
            if 'exprFromKey' in ifelse:
                exprFromKey = ifelse['exprFromKey']
        global _fold
        if _fold:
            const = cond['const']
        else:
            const = False
        ret = {
            "type" : retType if retType else type(value).__name__,
            "value" : value,
            "const" : const,
            "json" : {
                "name" : "({}) {}".format(retType,value),
                "children" : [
                    answer
                ]
            }
        }
        if exprFromKey != None:
            ret['exprFromKey'] = exprFromKey
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
        const = True
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
            exprFromKey[key]['keyType'] = keyExpr['type']
            exprFromKey[key]['keyAst'] = exprKey
            const &= keyExpr['const'] & valExpr['const']

        return {
            "type" : "structure",
            "value" : value,
            "exprFromKey" : exprFromKey,
            "const": const,
            "json" : {
                "name" : "(structure)",
                "children" : children
            }
        }

    # Visit a tuple definition and get the values
    def visit_tuple(self, node):
        exps = [expr.visit(BuildD3Json()) for expr in node.exprs]
        const = True
        for exp in exps:
            const &= exp['const']
        return {
            "type": "tuple",
            "value": tuple([exp['value'] for exp in exps]),
            "exprFromKey": {k : exps[k] for k in range(len(exps))},
            "const": const,
            "json": {
                "name": "(tuple)",
                "children" : [exp['json'] for exp in exps]
            }
        }

    # Visit a list definition and get the values
    def visit_list(self, node):
        exps = [expr.visit(BuildD3Json()) for expr in node.exprs]
        const = True
        for exp in exps:
            const &= exp['const']
        return {
            "type": "list",
            "value": [exp['value'] for exp in exps],
            "exprFromKey": {k : exps[k] for k in range(len(exps))},
            "const": const,
            "json": {
                "name": "(list)",
                "children" : [exp['json'] for exp in exps]
            }
        }

    # Visit a structure json and get its value depending on the key
    def visit_structureCall(self, node):
        structure = node.structure.visit(BuildD3Json())
        expression = node.expression.visit(BuildD3Json())
        const = structure['const'] & expression['const']
        if structure["type"] != "structure" and structure["type"] != "list" and structure["type"] != "tuple":
            raise Exception("{} is not a structure nor a list nor a tuple".format(structure["value"]))
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
        global _fold
        if not _fold:
            const = False
        ret['const'] = const
        ret["json"] = {
            "name" : "({}) {}".format(val['type'], val['value'])
        }
        if not (_fold and ret['const']):
            ret['json']['children'] = [
                structure['json'],
                expression['json']
            ]
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
        if node.name in symboltable.funcTable:
            entry = symboltable.funcTable[node.name]
            ret = dict(entry)
            ret['const'] = False
            if 'json' in entry:
                ret['json'] = {
                    "name" : node.name,
                    "collapse": True,
                    "children" : []
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
                "const" : False,
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
        memoFlag = False
        args = []

        while type(node) is Application:
            if node.arg != None:
                args = [node.arg.visit(BuildD3Json())] + args
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
        k = 0
        while k < len(args):
            entry = dict(args[k])
            argName = parser._args[node][k]
            symboltable.funcTable[argName] = entry
            k += 1

        if node in parser._lambda_closure:
            closure = parser._lambda_closure[node]
            for argName in closure:
                entry = symboltable.getHighterValues(argName)
                if entry:
                    symboltable.funcTable[argName] = entry

        variables = []
        global _prop
        global _argMap
        global _fold
        _argMap = {}
        tam = len(parser._whereDict[node])
        for i in range(tam):
            entry = parser._whereDict[node][i]
            result = entry['expression'].visit(BuildD3Json())
            if result['const'] and _prop:
                _argMap[entry['var']] = result
                for j in range(i+1, tam):
                    parser._whereDict[node][j]['expression'] = parser._whereDict[node][j]['expression'].visit(PropSearch())
            else:
                symboltable.funcTable[entry['var']] = result
                variables += [(entry['var'], result)]

        if _prop:
            parser._functions[node] = parser._functions[node].visit(PropSearch())
        global _memo
        if _memo:
            memoKey = node + ' ' + ' '.join(["({} {})".format(arg['type'],arg['value']) for arg in args])
            global memoized
            if memoKey not in memoized:
                memoized[memoKey] = parser._functions[node].visit(BuildD3Json())
            else:
                memoFlag = True

            exec_tree = memoized[memoKey]
        else:
            exec_tree = parser._functions[node].visit(BuildD3Json())

        symboltable.deleteTable(node)

        if memoFlag:
            exec_tree['json']['collapse'] = True
            if 'children' in exec_tree['json']:
                del exec_tree['json']['children']

            args_tree = {
                "name": "(memoized) {}".format(memoKey),
                "children": [
                    exec_tree['json']
                ]
            }
        else :
            args_string = ""
            for arg in parser._args[node]:
                args_string += " " + arg
            exec_tree['json']['collapse'] = funcName in specialNames
            if funcName in specialNames and 'children' in exec_tree['json']:
                del exec_tree['json']['children']

            args_tree = {
                "name": funcName + args_string + " = ",
                "children": [
                    exec_tree['json']
                ]
            }

        for arg in args:
            args_tree = {
                "name": " ",
                "children": [
                    args_tree,
                    arg['json']
                ]
            }

        for v in variables:
            if not (_fold and v[1]['const']):
                args_tree = {
                        "name": "",
                        "children": [
                            args_tree,
                            {
                                "name" : "where " + v[0] + " = ",
                                "children": [
                                    v[1]['json']
                                ]
                            }
                        ]
                    }
            else:
                args_tree = {
                        "name": "",
                        "children": [
                            args_tree,
                            {
                                "name" : "where " + v[0] + " = ",
                                "children": [{
                                    "name": v[1]['json']['name']
                                }]
                            }
                        ]
                    }

        ret = dict(exec_tree)
        ret['json'] = args_tree
        ret['const'] = False

        return ret

# Execute the main function of the program, with where
def execute(node):

    symboltable.getTable('main')

    variables = []
    global _prop
    global _argMap
    global _fold
    _argMap = {}
    tam = len(parser._whereDict['main'])
    for i in range(tam):
        entry = parser._whereDict['main'][i]
        result = entry['expression'].visit(BuildD3Json())
        if result['const'] and _prop:
            _argMap[entry['var']] = result
            for j in range(i+1, tam):
                parser._whereDict['main'][j]['expression'] = parser._whereDict['main'][j]['expression'].visit(PropSearch())
        else:
            symboltable.funcTable[entry['var']] = result
            variables += [(entry['var'], result)]

    if _prop:
        node = node.visit(PropSearch())

    exec_tree = node.visit(BuildD3Json())
    symboltable.deleteTable('main')

    args_tree = {
        "name": "main = " + str(exec_tree['value']),
        "children": [
            exec_tree['json']
        ]
    }

    if len(variables) > 0:
        global _fold
        for v in variables:
            if not (_fold and v[1]['const']):
                args_tree = {
                        "name": "",
                        "children": [
                            args_tree,
                            {
                                "name" : "where " + v[0] + " = ",
                                "children": [
                                    v[1]['json']
                                ]
                            }
                        ]
                    }
            else:
                args_tree = {
                        "name": "",
                        "children": [
                            args_tree,
                            {
                                "name" : "where " + v[0] + " = ",
                                "children": [{
                                    "name": v[1]['json']['name']
                                }]
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
