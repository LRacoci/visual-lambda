from abc import ABCMeta, abstractmethod
import parser

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

symbolTable = {}

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
        elif node.type == "bool":
            value = True if node.value == "True" else False
        return {
            "value" : value,
            "json" : {
                "name" : str(value)
            }
        }

    def visit_identifier(self, node):
        print "Visiting identifier"
        if node.name in symbolTable:
            value = symbolTable[node.name]
            return {
                "value" : value,
                "json" : {
                    "name" : str(value)
                }
            }
        else:
            raise Exception(node.name + " is not defined")


    def visit_application(self, node):
        args = []
        while type (node) is application:
            if node.arg != None:
                arg = node.arg.accept(NodeDoVisitor())['value']
            else:
                arg = None
            args += [arg]
            node = node.func

        print node + ": " + ','.join([str(arg) for arg in args])
        global symbolTable
        symbolTable = {}
        
        if len(args) > len(parser._args[node]):
            raise Exception(node + " is called with more arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))
        if len(args) < len(parser._args[node]):
            raise Exception(node + " is called with less arguments ({}) than what is defined ({})".format(len(args), len(parser._args[node])))
        
        while len(symbolTable) < len(args):
            symbolTable[parser._args[node][len(symbolTable)]] = args[len(symbolTable)]
        print node + " symbolTable == " + str(symbolTable)
        exec_tree = parser._functions[node].accept(NodeDoVisitor())
        return {
            "value" : exec_tree['value'],
            "json": {
                "name": node + " = " + str(exec_tree['value']),
                "children": [
                    exec_tree['json']
                ]
            }
        }

def execute(node):
    exec_tree = node.accept(NodeDoVisitor())
    return {
        "name": "main = " + str(exec_tree['value']),
        "children": [
            exec_tree['json']
        ]
    }
