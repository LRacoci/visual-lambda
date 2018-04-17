from parser import *
import sys
import os

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
        try:
            parser.parse(problem)
        except Exception as err:

            output = err.args[0]

            outFileName = inpFileName.replace(".hs", "_out.err")
            with open(outFileName, "w") as outFile:
                outFile.write(output)
            
            answer = inpFileName.replace(".hs", ".err")
            with open(answer) as a:
                answer = a.read()
            
            if answer == output:
                print "ok"
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        else:
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
