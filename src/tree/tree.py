def leaves(tree, k=0):
	if type(tree) is list:
		for branch in tree:
			for leaf, j in leaves(branch, k=k+1):
				yield leaf, j
	else:
		yield tree, k

def change(forestDicts):
	forest = forestDicts["functions"]
	dependence = {}
	for root in forest:
		dependence[root] = {}
		for leaf,_ in leaves(forest[root]):
			if leaf in forest:
				dependence[root][leaf] = root
	print dependence
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
	return {root: aux(forest[root]) for root in forest}


if __name__ == "__main__":
	from glob import glob
	import json
	for fileAddress in glob('tests/arq7.json'):
		print fileAddress

		with open(fileAddress) as jsonInputFile:
			jsonInput = json.load(jsonInputFile)
		print "Jason"
		print jsonInput
		print "End"
		jsonOutput = change(jsonInput)
		print jsonOutput

		with open(fileAddress.replace("arq","forest"), "w") as outputFile:
			json.dump(jsonOutput, outputFile, indent=1)
