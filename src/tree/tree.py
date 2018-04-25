import json

# Function used to debug and search the tree
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

# Function used to debug and search the D3 tree
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

# Check if the function with name srcName is in a recursive cicle
def cicle(srcName, dependence):
    vision = {v: {} for v in dependence}
    for v in dependence:
        for u in dependence[v]:
            vision[v][u] = vision[v]
    
    print "dependence == ", dependence
    print "vision == ", vision
    
    return "..." in str(vision[srcName])

MAX_RECURSSION = 1

# Convert the python forest format to the D3 tree expected by the front end
def change(forest):
    args = forest['args']
    functions = forest['functions']
    dependence = forest['dependence']

    #print "dependencies"
    #print json.dumps(dependence, indent = 2)
    
    # Recursive function that goes down the tree beginning with main
    def aux(name, k = 0, num_recursions={funcName : 0 for funcName in functions}, branch = None):
        if name not in functions:
            return None
        
        if branch == None:
            branch = functions[name]
        
        if type(branch) is list:
            children = []
            for branch in branch:
                children += [aux(name, k=k+1, num_recursions=num_recursions, branch=branch)]
            return {
                "name": " ",
                "children": children
            }
        
        leaf = str(branch)
        if name in dependence and leaf in dependence[name] and num_recursions[leaf] < MAX_RECURSSION * dependence[name][leaf]:
            num_recursions[leaf] += 1 if cicle(leaf, dependence) else 0
            return {
                "name": ' '.join([leaf] + args[leaf]),
                "children": [aux(leaf, k = k+1, num_recursions=num_recursions)]
            }
        
        if leaf in functions:
            return {
                "name": ' '.join([leaf] + args[leaf]),
                "children": [aux(leaf, k = k+1, num_recursions=num_recursions)]
            }

        return {"name": leaf}
    
        
    return {
        "name": "main", 
        "children": [aux("main")]
    }
