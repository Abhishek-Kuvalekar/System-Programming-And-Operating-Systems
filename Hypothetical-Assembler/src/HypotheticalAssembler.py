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
          "UNUSED_VARIABLE"     : "Unused variable.",
          "DUPLICATE_LABEL"     : "Duplicate label.",
          "EXTRA_OPERANDS"      : "Extra operands.",
          "INVALID_LABEL"       : "Invalid label."}


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
            iList = line.rstrip('\n').split(' ')
            if(len(iList) == 1):
                instruction = iList[0]
                operand = None
            elif(len(iList) == 2):
                if(iList[0].endswith(':') == True):
                    label = iList[0].rstrip(":")
                    if (self.symbolTable.get(label, None) == None):
                        self.symbolTable[label] = self.startAddress
                    else:
                        if(self.symbolTable[label] == -1):
                            self.symbolTable[label] = self.startAddress
                        else:
                            self.printErrorMessage(errors['DUPLICATE_LABEL'], lineNumber)
                            self.hasErrorOccurred = True
                    if(iList[1].upper() == "STOP"):
                        instruction = iList[1].upper()
                        operand = None
                    else:
                        self.printErrorMessage(errors['FEW_OPERANDS'], lineNumber)
                        self.hasErrorOccurred = True
                else:
                    (instruction, operand) = (iList[0], iList[1])
            elif(len(iList) == 3):
                (label, instruction, operand) = (iList[0], iList[1], iList[2])
                if(label != None):
                    if(label.endswith(':') == True):
                        label = label.rstrip(":")
                        if(self.symbolTable.get(label, None) == None):
                            self.symbolTable[label] = self.startAddress
                        else:
                            if(self.symbolTable[label] == -1):
                                self.symbolTable[label] = self.startAddress
                            else
                                self.printErrorMessage(errors['DUPLICATE_LABEL'], lineNumber)
                                self.hasErrorOccurred = True
                    else:
                        self.printErrorMessage(errors['INVALID_LABEL'], lineNumber)
                        self.hasErrorOccurred = True
                else:
                    self.printErrorMessage(errors['INVALID_INSTRUCTION'], lineNumber)
                    self.hasErrorOccurred = True

            if (instruction == "STOP"):
                if(operand == None):
                    self.dataSegment = True
                else:
                    self.printErrorMessage(errors['EXTRA_OPERANDS'], lineNumber)
                    self.hasErrorOccurred = True
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
                if(operand != None):
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
        file = self.fileManager.openOutputFile()
        addressList = list(self.outputDict.keys())
        addressList.sort()
        for address in addressList:
            line = str(address) + "\t" + str(self.outputDict[address].opcode) + "\n"
            file.write(line)
            if(self.outputDict[address].operand != None):
                operandAddress = self.symbolTable[self.outputDict[address].operand]

            if(operandAddress == -1):
                self.printErrorMessage(errors['UNDEFINED_VARIABLE'], self.outputDict[address].lineNumber)
                file.close()
                os.remove(self.outputFile)
                sys.exit(1)
            else:
                line = str(address + 1) + "\t" + str(operandAddress) + "\n"
                file.write(line)

    def getErrorOccurred(self):
        return self.hasErrorOccurred

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
    if(assembler.getErrorOccurred() == False):
        assembler.generateOutputFile()
    else:
        sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
