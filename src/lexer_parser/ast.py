from abc import ABCMeta, abstractmethod
import parser
import symboltable
import json

NOT_IMPLEMENTED = "You should implement this."

# Parser rules
class Node():
    __metaclass__ = ABCMeta
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError(NOT_IMPLEMENTED)

class binop(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binop(self)

class ifelse(Node):
    def __init__(self, cond, ifthen, ifelse):
        self.cond = cond
        self.ifthen = ifthen
        self.ifelse = ifelse

    def accept(self, visitor):
        return visitor.visit_ifelse(self)

class constant(Node):
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def accept(self, visitor):
        return visitor.visit_constant(self)

class identifier(Node):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_identifier(self)

class application(Node):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def accept(self, visitor):
        return visitor.visit_application(self)

class NodeVisitor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def visit_binop(self, node):
        raise NotImplementedError(NOT_IMPLEMENTED)

    @abstractmethod
    def visit_ifelse(self, node):
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

class NodeDoVisitor(NodeVisitor):

    def visit_binop(self, node):
        left = node.left.accept(NodeDoVisitor())
        right = node.right.accept(NodeDoVisitor())

        if node.op == '+':
            value = left['value'] + right['value']
        if node.op == '-':
            value = left['value'] - right['value']
        if node.op == '*':
            value = left['value'] * right['value']
        if node.op == '/':
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

    def visit_ifelse(self, node):
        cond = node.cond.accept(NodeDoVisitor())

        if cond['value'] == True:
            ifthen = node.ifthen.accept(NodeDoVisitor())
            ifelse = { "json" : { "name" : "else not executed" } }
            value = ifthen['value']
        else:
            ifthen = { "json" : { "name" : "then not executed" } }
            ifelse = node.ifelse.accept(NodeDoVisitor())
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

    def visit_constant(self, node):
		if node.type == "int":
			value = int(node.value)
		elif node.type == "float":
			value = float(node.value)
		elif node.type == "str":
			value = str(node.value)
		elif node.type == "bool":
			value = True if node.value == "True" else False
		return {
        	"type" : node.type,
        	"value" : value,
        	"json" : {
            	"name" : node.type + " = " + str(value)
        	}
		}

    def visit_identifier(self, node):
        print "Visiting identifier"
        if node.name in symboltable.funcTable:
            entry = symboltable.funcTable[node.name]
            return {
                "type" : entry['type'],
                "value" : entry['value'],
                "json" : {
                    "name" : node.name + " = " + str(entry['value'])
                }
            }
        elif node.name in parser._functions:
            return {
                "type" : "function",
                "value" : node.name,
                "json" : {
                    "name" : node.name + " = function"
                }
            }
        else:
            raise Exception(node.name + " is not defined")


    def visit_application(self, node):

        args = []
        trees = []
        types = []
        while type(node) is application:
            if node.arg != None:
                exec_tree = node.arg.accept(NodeDoVisitor())
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
                raise Exception(node + " is not a function")
        else:
            funcName = node

        if len(args) > len(parser._args[node]):
            raise Exception(node + " is called with more arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))
        if len(args) < len(parser._args[node]):
            raise Exception(node + " is called with less arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))

        symboltable.getTable(node)

        while len(symboltable.funcTable) < len(args):
            value = args[len(symboltable.funcTable)]
            tp = types[len(symboltable.funcTable)]
            symboltable.funcTable[parser._args[node][len(symboltable.funcTable)]] = {'value' : value, 'type' : tp}
        
        variables = []
        for entry in parser._whereDict[node]:
            result = entry['expression'].accept(NodeDoVisitor())
            symboltable.funcTable[entry['var']] = {'value' : result['value'], 'type' : result['type']}
            variables += [(entry['var'], result)]

        print node + " symbolTable == " + json.dumps(symboltable.symbolTable, indent=2)
        exec_tree = parser._functions[node].accept(NodeDoVisitor())

        symboltable.deleteTable(node)

        args_string = ""
        for arg in parser._args[node]:
            args_string += " " + arg

        args_tree = {
            "name": funcName + args_string + " = " + str(exec_tree['value']),
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
                    "name": "where " + v[0] + " = " + str(v[1]['value']),
                    "children": [
                        args_tree,
                        v[1]['json']
                    ]
                }

        return {
            "type" : type(exec_tree['value']).__name__,
            "value": exec_tree['value'],
            "json": args_tree
        }

def execute(node):

    symboltable.getTable('main')

    variables = []
    for entry in parser._whereDict['main']:
        result = entry['expression'].accept(NodeDoVisitor())
        symboltable.funcTable[entry['var']] = {'value' : result['value'], 'type' : result['type']}
        variables += [(entry['var'], result)]
    
    exec_tree = node.accept(NodeDoVisitor())
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
                    "name": "where " + v[0] + " = " + str(v[1]['value']),
                    "children": [
                        args_tree,
                        v[1]['json']
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
