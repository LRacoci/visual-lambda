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
    parser = Parser()
    from glob import glob
    
    for problem in glob('tests/arq*.hs'):
        print problem
        answer = problem[:-2] + 'res'
        
        with open(problem) as p:
            problem = p.read()
        
        with open(answer) as a:
            answer = a.read()
        
        #print problem
        #print answer
        result = parser.parse(problem)
        print "Result == ", result
        #result = printTree(result)
        if result != answer:
            print result
        else:
            print "ok"