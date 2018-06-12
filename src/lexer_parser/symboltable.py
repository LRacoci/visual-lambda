
symbolTable = {}
scopeStack = []
funcTable = {}

# Get the table of current function node
def getTable(node):
    global symbolTable
    global scopeStack
    global funcTable
    funcTable = symbolTable
    for item in scopeStack:
        funcTable = funcTable[item]
    auxNode = "*" + node
    scopeStack.append(auxNode)
    funcTable[auxNode] = {}
    funcTable = funcTable[auxNode]

# Get values from higher levels of the symbol table
def getHighterValues(argName):
    global symbolTable
    global scopeStack
    ret = None
    aux = symbolTable
    for func in scopeStack:
        if argName in aux:
            ret = aux[argName]
        aux = aux[func]

    return ret

# Delete the table of current function node
def deleteTable(node):
    global symbolTable
    global scopeStack
    global funcTable
    scopeStack.pop()
    funcTable = symbolTable
    for item in scopeStack:
        funcTable = funcTable[item]
    del funcTable["*" + node]

# Clean all the tables and variables
def clean():
    global symbolTable
    global scopeStack
    global funcTable
    symbolTable = {}
    scopeStack = []
    funcTable = {}
