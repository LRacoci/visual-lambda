from tree import *
if __name__ == "__main__":
    from glob import glob
    import json
    for fileAddress in glob('tests/forest*.json'):
        print fileAddress
        
        with open(fileAddress) as jsonInputFile:
            jsonInput = json.load(jsonInputFile)
        
        jsonOutput = change(jsonInput)
        #print "jsonOutput"
        #print json.dumps(jsonOutput, indent = 2)
        
        answerAddress = fileAddress.replace("forest","tree")
        with open(answerAddress) as answerFile:
            jsonAnswer = json.load(answerFile)

        with open(answerAddress.replace(".json","_out.json"), "w") as outputFile:
            json.dump(jsonOutput, outputFile, indent=2)

        if jsonOutput == jsonAnswer:
            print "ok"
        else:
            print "answer =="
            print json.dumps(jsonAnswer, indent = 2)
            print "output =="
            print json.dumps(jsonOutput, indent = 2)
