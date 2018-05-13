
symbolTable = {}
scopeStack = []
funcTable = {}

def getTable(node):
    global symbolTable
    global scopeStack
    global funcTable
    funcTable = symbolTable
    for item in scopeStack:
        funcTable = funcTable[item]
    scopeStack.append(node)
    funcTable[node] = {}
    funcTable = funcTable[node]

def deleteTable(node):
    global symbolTable
    global scopeStack
    global funcTable
    scopeStack.pop()
    funcTable = symbolTable
    for item in scopeStack:
        funcTable = funcTable[item]
    del funcTable[node]

def clean():
    global symbolTable
    global scopeStack
    global funcTable
    symbolTable = {}
    scopeStack = []
    funcTable = {}
