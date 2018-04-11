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
    if a == b:
        return None

    if type(a) is dict and type(b) is dict:
        resp = {}
        for x in a:
            if x in b:
                delta = diff(a[x], b[x])
            else:
                delta = a[x]
            if delta != None:
                resp[x] = delta
        return resp

    if type(a) is list and type(b) is list:
        resp = []
        for x, y in izip(a, b):
            delta = diff(x, y)
            if delta != None:
                resp += [delta]
        return resp

    if a == b:
        return None

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
        #print json.dumps(output)
        outFileName = inpFileName.replace(".hs", "_out.json")
        
        with open(outFileName, "w") as outFile:
            json.dump(output, outFile, indent = 2)
        
        answer = inpFileName.replace(".hs", ".json")
        with open(answer) as a:
            answer = json.load(a)
        
        ao = diff(answer, output)
        oa = diff(output, answer)

        if ao != None:
            print "answer - output == "
            print json.dumps(ao, indent = 2)
        
        if oa != None:
            print "output - answer == "
            print json.dumps(oa, indent = 2)

        if answer == output:
            print "ok"
