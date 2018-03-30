#!/usr/bin/python3
import sys, os

class Assembler():
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.outputDict = dict();
        self.fileManager = FileManager(self.inputFile, self.outputFile)

    def parseInputFile(self):
        inFile = self.fileManager.openInputFile()
        line = self.fileManager.readLine(inFile)
        print(line)
        pass

    def generateOutputFile(self):
        pass

class FileManager():
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile;
        self.outputFile = outputFile
        pass

    def readLine(self, filePointer):
        return filePointer.readline()
        pass

    def writeFile(self):
        pass
    
    def openInputFile(self):
        return open(self.inputFile, "r")

    def openOutputFile(self):
        return open(self.outputFile, "w")

def main(argv=sys.argv):
    print("Hypothetical Assembler.")
    print("Author: Abhishek Kuvalekar")
    if((len(argv) < 2) or (len(argv) > 3)):
        print("Usage:")
        print("HypotheticalAssembler.py inputFile [outputFile]")
        return 1
    else:
        inputFile = argv[1]
        if(len(argv) ==3):
            outputFile = argv[2]
        else:
            outputFile = os.path.splitext(inputFile)[0] + ".output"

    assembler = Assembler(inputFile, outputFile)
    assembler.parseInputFile()
    assembler.generateOutputFile()
    return 0

if __name__ == "__main__":
    sys.exit(main())