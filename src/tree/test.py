from tree import *
if __name__ == "__main__":
    from glob import glob
    import json
    for fileAddress in glob('tests/forest*.json'):
        print fileAddress
        
        with open(fileAddress) as jsonInputFile:
            jsonInput = json.load(jsonInputFile)
        
        jsonOutput = change(jsonInput)
        print "jsonOutput"
        print json.dumps(jsonOutput, indent = 2)
        
        with open(fileAddress.replace("forest","tree"), "w") as outputFile:
            json.dump(jsonOutput, outputFile, indent=2)
