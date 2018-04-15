import json
def nodesPy(tree,onlyLeaves=True, k=0):
    if type(tree) is list:
        for branch in tree:
            for leaf, j in nodesPy(branch,onlyLeaves=onlyLeaves, k=k+1):
                yield leaf, j
    else:
        if onlyLeaves:
            yield tree, k
    if not onlyLeaves:
        yield tree, k

def nodesD3(tree,onlyLeaves=True, k=0):
    if "children" in tree:
        for child in tree["children"]:
            for leaf,j in nodesD3(child,onlyLeaves=onlyLeaves, k=k+1):
                yield leaf, j
    else: 
        if onlyLeaves:
            yield tree, k
    if not onlyLeaves:
        yield tree, k

def cicle(srcName, dependence):
    vision = {v: {} for v in dependence}
    for v in dependence:
        for u in dependence[v]:
            vision[v][u] = vision[v]
    
    return "..." in str(vision[srcName])

MAX_RECURSSION = 1

def change(forest):
    args = forest['args']
    functions = forest['functions']
    dependence = forest['dependence']
    """
    dependence = {
        funcName : {
            leaf: funcName
            for leaf,_ in nodesPy(functions[funcName]) 
            if leaf in functions
        }
        for funcName in functions
    }
    for funcName in functions:
        for leaf,_ in nodesPy(functions[funcName]):
            if leaf in functions:
                dependence[leaf] = funcName
    """
    print "dependencies"
    print json.dumps(dependence, indent = 2)
    
    def aux(tree, k = 0, num_recursions={funcName : 0 for funcName in functions}):
        if type(tree) is list:
            children = []
            for branch in tree:
                children += [aux(branch, k=k+1, num_recursions=num_recursions)]
            return {
                "name": " ",
                "children": children
            }
       
        if str(tree) in functions and num_recursions[str(tree)] < MAX_RECURSSION:
            num_recursions[str(tree)] += 1 if cicle(str(tree), dependence) else 0
            return{
                "name": ' '.join([str(tree)] + args[str(tree)]),
                "children": [aux(functions[str(tree)], k = k+1, num_recursions=num_recursions)]
            }

        return {"name": str(tree)}
    
        
    return {
        "name": "main", 
        "children": [aux(functions["main"])]
    }
