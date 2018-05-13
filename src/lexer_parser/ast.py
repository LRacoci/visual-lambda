from abc import ABCMeta, abstractmethod
import parser
import symboltable
import json

NOT_IMPLEMENTED = "You should implement this."

def hashable(v):
    """Determine whether `v` can be hashed."""
    try:
        hash(v)
    except TypeError:
        return False
    return True

# Parser rules
class Node():
    __metaclass__ = ABCMeta
    @abstractmethod
    def visit(self, visitor):
        raise NotImplementedError(NOT_IMPLEMENTED)

class Binop(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def visit(self, visitor):
        return visitor.visit_binop(self)

class Conditional(Node):
    def __init__(self, cond, ifthen, ifelse):
        self.cond = cond
        self.ifthen = ifthen
        self.ifelse = ifelse

    def visit(self, visitor):
        return visitor.visit_conditional(self)

class Structure(Node):
    def __init__(self, kvPairs):
        self.kvPairs = kvPairs

    def visit(self, visitor):
        return visitor.visit_structure(self)

class StructureCall(Node):
    def __init__(self, structure, expression):
        self.structure = structure
        self.expression = expression

    def visit(self, visitor):
        return visitor.visit_structureCall(self)


class Constant(Node):
    def __init__(self, value, type):
        self.value = value
        self.type = type


    def visit(self, visitor):
        return visitor.visit_constant(self)

class Identifier(Node):
    def __init__(self, name):
        self.name = name

    def visit(self, visitor):
        return visitor.visit_identifier(self)

class Application(Node):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def visit(self, visitor):
        return visitor.visit_application(self)

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

class BuildD3Json(NodeVisitor):

    def visit_binop(self, node):
        left = node.left.visit(BuildD3Json())
        right = node.right.visit(BuildD3Json())

        arithmetic_op = {"float", "int", "bool"}
        lr_types_union = {left['type'], right['type']}

        if node.op == '+':
            if lr_types_union.issubset(arithmetic_op) == False and lr_types_union != {"str"}:
                parser.clean()
                raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))

            value = left['value'] + right['value']
        if node.op == '-':
            if lr_types_union.issubset(arithmetic_op) == False:
                parser.clean()
                raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))

            value = left['value'] - right['value']
        if node.op == '*':
            if lr_types_union.issubset(arithmetic_op) == False:
                parser.clean()
                raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))

            value = left['value'] * right['value']
        if node.op == '/':
            if lr_types_union.issubset(arithmetic_op) == False:
                parser.clean()
                raise Exception("Error: invalid operation \'{}\' between \'{}:{}\' and \'{}:{}\'".format(node.op, left['value'], left['type'], right['value'], right['type']))

            if right['value'] == 0:
                parser.clean()
                raise Exception("Error: division by zero between \'{}:{}\' and \'{}:{}\'".format(left['value'], left['type'], right['value'], right['type']))

            value = left['value'] / right['value']

        if node.op == 'and':
            value = left['value'] and right['value']

        if node.op == 'xor':
            value = (left['value'] and not right['value']) or (not left['value'] and right['value'])

        if node.op == 'ior':
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


        return {
            "type" : type(value).__name__,
            "value" : value,
            "json" : {
                "name" : value,
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
                print "New building key is {}".format(key)

            value[key] = valExpr['value']
            exprFromKey[key] = valExpr

        return {
            "type" : "structure",
            "value" : value,
            "exprFromKey" : exprFromKey,
            #"exprFromKey" : exprFromKey,
            "json" : {
                "name" : "(structure)",
                "children" : children
            }
        }

    def visit_structureCall(self, node):
        structure = node.structure.visit(BuildD3Json())
        expression = node.expression.visit(BuildD3Json())
        if structure["type"] != "structure":
            raise Exception("{} is not a structure".format(structure["value"]))

        key = expression['value']
        if not hashable(key):
            key = str(key)
            print "New key calling is {}".format(key)
        print "structure : {}".format(json.dumps(structure, indent = 2))
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

        print value
        return {
            "type" : node.type,
            "value" : value,
            "json" : {
                "name" : "({}) {}".format(node.type, show)
            }
        }

    def visit_identifier(self, node):
        print "Visiting Identifier"
        if node.name in symboltable.funcTable:
            entry = symboltable.funcTable[node.name]
            print json.dumps(entry, indent=2)
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

    def visit_application(self, node):
        args = []
        trees = []
        types = []
        while type(node) is Application:
            if node.arg != None:
                exec_tree = node.arg.visit(BuildD3Json())
                print exec_tree
                arg = exec_tree['value']
                tree = exec_tree['json']
                tp = exec_tree['type']
                args = [arg] + args
                trees = [tree] + trees
                types = [tp] + types
            node = node.func

        print node + ": " + ','.join([str(arg) for arg in args])

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
            value = args[len(symboltable.funcTable)]
            tp = types[len(symboltable.funcTable)]
            symboltable.funcTable[parser._args[node][len(symboltable.funcTable)]] = {
                'value' : value, 'type' : tp
                }

        variables = []
        for entry in parser._whereDict[node]:
            result = entry['expression'].visit(BuildD3Json())
            symboltable.funcTable[entry['var']] = result
            variables += [(entry['var'], result)]

        print node + " symbolTable == " + json.dumps(symboltable.symbolTable, indent=2)
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
