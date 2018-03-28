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

if __name__ == "__main__":
    from glob import glob
    import json
    
    for inpFileName in glob('tests/arq*.hs'):
        print inpFileName

        with open(inpFileName) as inpFile:
            problem = inpFile.read()
        
        parser.parse(problem)
        output = namesOut
        print output
        '''outFileName = inpFileName.replace(".hs", "_out.json")
        with open(outFileName, "w") as outFile:
            json.dump(output, outFile, indent = 2)
        
        output = json.dumps(output, indent=2)
        
        
        answer = inpFileName.replace(".hs", ".json")
        with open(answer) as a:
            answer = a.read()
        
        if answer == output:
            print "ok"
        else:
            from itertools import *
            for a,o in izip_longest(answer.split("\n"), output.split("\n")):
                if a != o:
                    print "answer: ", a 
                    print "output: ", o'''
