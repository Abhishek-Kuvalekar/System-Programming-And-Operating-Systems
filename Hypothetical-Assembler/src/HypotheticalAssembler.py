#!/usr/bin/python3
import sys, os

instructions = {"STOP":   0,
                "ADD":    1,
                "SUB":    2,
                "MULT":   3,
                "MOVER":  4,
                "MOVEM":  5,
                "COMP":   6,
                "BC":     7,
                "DIV":    8,
                "READ":   9,
                "PRINT": 10}

macros = {"DB" : 1,
          "DW" : 2,
          "DC" : 1}

errors = {"ORG_ERROR"           : "Invalid operand for ORG.",
         "INVALID_INSTRUCTION"  : "Invalid instruction.",
          "FEW_OPERANDS"        : "Too few operands.",
          "REPEAT_ASSIGNMENT"   : "Repeated assignment.",
          "UNDEFINED_VARIABLE"  : "Undefined variable.",
          "UNUSED_VARIABLE"     : "Unused variable."}

class Instruction():
    def __init__(self, opcode, operand, lineNumber):
        self.opcode = opcode
        self.operand = operand
        self.lineNumber = lineNumber

class Assembler():
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.outputDict = dict()
        self.fileManager = FileManager(self.inputFile, self.outputFile)
        self.startAddress = 1000
        self.hasErrorOccurred = False
        self.symbolTable = dict()
        self.dataSegment = False

    def printErrorMessage(self, message, lineNumber):
        print("E: " + str(lineNumber) + ": " + message)

    def printWarningMessage(self, message, lineNumber):
        print("W: " + str(lineNumber) + ": " + message)

    def completePassOne(self, lineNumber, line):
        try:
            if (line.rstrip('\n').upper() == "STOP"):
                instruction = "STOP"
                operand = None
                self.dataSegment = True
            else:
                (instruction, operand) = line.rstrip('\n').split(' ')
            if (instruction == "ORG"):
                if (operand != None):
                    try:
                        self.startAddress = int(operand)
                    except Exception:
                        self.printErrorMessage(errors['ORG_ERROR'], lineNumber)
                        self.hasErrorOccurred = True
                else:
                    self.printErrorMessage(errors['ORG_ERROR'], lineNumber)
                    self.hasErrorOccurred = True
            else:
                if (instructions.get(instruction.upper(), None) == None):
                    self.printErrorMessage(errors['INVALID_INSTRUCTION'], lineNumber)
                    self.hasErrorOccurred = True
                self.outputDict[self.startAddress] = Instruction(instructions.get(instruction.upper()), operand,
                                                                 lineNumber)
                if (self.symbolTable.get(operand, None) == None):
                    self.symbolTable[operand] = -1
                if (instruction != "STOP"):
                    self.startAddress += 2
                else:
                    self.startAddress += 1
        except Exception:
            self.printErrorMessage(errors['FEW_OPERANDS'], lineNumber)
            self.hasErrorOccurred = True

    def completeSymbolTable(self, lineNumber, line):
        try:
            (macro, variable, value) = line.rstrip('\n').split(" ")
            if(macros.get(macro, None) == None):
                raise Exception
            if(self.symbolTable.get(variable, None) != None):
                if(self.symbolTable[variable] == -1):
                    self.symbolTable[variable] = self.startAddress
                else:
                    self.printErrorMessage(errors['REPEAT_ASSIGNMENT'], lineNumber)
                    self.hasErrorOccurred = True
            else:
                self.printWarningMessage(errors['UNUSED_VARIABLE'], lineNumber)
            self.startAddress += macros[macro]
        except Exception:
            self.printErrorMessage(errors['INVALID_INSTRUCTION'], lineNumber)
            self.hasErrorOccurred = True

    def parseInputFile(self):
        lineNumber = 0
        with self.fileManager.openInputFile() as fp:
            for line in fp:
                lineNumber += 1
                if(self.dataSegment == True):
                    self.completeSymbolTable(lineNumber, line)
                else:
                    self.completePassOne(lineNumber, line)

    def generateOutputFile(self):
        pass



class FileManager():
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile;
        self.outputFile = outputFile
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