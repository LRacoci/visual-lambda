import json
def leaves(tree, k=0):
	if type(tree) is list:
		for branch in tree:
			for leaf, j in leaves(branch, k=k+1):
				yield leaf, j
	else:
		yield tree, k


def change(forest):
    args = forest['args']
    forest = forest['functions']
    dependence = {}
    for root in forest:
        for leaf,_ in leaves(forest[root]):
            if leaf in forest:
                dependence[leaf] = root
    
    print "dependencies"
    print json.dumps(dependence, indent = 2)
    
    def aux(tree, k = 0):
        if type(tree) is list:
            children = []
            for branch in tree:
                children += [aux(branch, k=k+1)]
            return {
                "name": " ",
                "children": children
            }
        else:
            return {"name": str(tree)}
    resp = {}

    for root in forest:
        resp["name"] =  ' '.join([root] + args[root])
        resp["children"] = [aux(forest[root])]
    
    return resp
    
    
