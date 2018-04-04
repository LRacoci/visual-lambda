from parser import *

def printTree(tree):
    def printTreeAux(n, tree):
        resp = ""
        if type(tree) is list:
            for sub in tree:
                resp += printTreeAux(n+1,sub)
        elif n >= 0:
            resp = "  "*n + str(tree) + "\n"
        return resp
    return printTreeAux(-1, tree)


from itertools import *
def diff(a,b):
    if type(a) is dict and type(b) is dict:
        return {x: diff(a[x],b[x]) if x in b else a[x] for x in a}
    elif type(a) is list and type(b) is list:
        return [diff(x, y) for x, y in izip(a, b)]
    else:
        return a

if __name__ == "__main__":
    from glob import glob
    import json
    
    for inpFileName in glob('tests/arq*.hs'):
        print inpFileName

        with open(inpFileName) as inpFile:
            problem = inpFile.read()
        
        parser.parse(problem)
        output = namesOut
        outFileName = inpFileName.replace(".hs", "_out.json")
        with open(outFileName, "w") as outFile:
            json.dump(output, outFile, indent = 2)
        
        answer = inpFileName.replace(".hs", ".json")
        with open(answer) as a:
            answer = json.load(a)
        
        ao = diff(answer, output)
        oa = diff(output, answer)
        if ao != {}:
            print "answer - output == "
            print json.dumps(ao, indent = 2)
        
        if oa != {}:
            print "output - answer == "
            print json.dumps(oa, indent = 2)
        
        if oa == {} == ao:
            print "ok"
