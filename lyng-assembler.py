#!/usr/bin/python
import sys
import re
import enum

# opcode refrence
# key: opcode letter code
# value: 5bit opcode
opcodeRef = {
    "ADD" : 0b00000,
    "ADC" : 0b00000,
    "SUB" : 0b00000,
    "SBB" : 0b00000,
    "AND" : 0b00001,
    "OR" : 0b00001,
    "XOR" : 0b00001,
    "NOT" : 0b00001,
    "SHFL" : 0b00010,
    "SHFA" : 0b00011,
    "ADDI" : 0b00100,
    "SUBI" : 0b00101,
    "MVIH" : 0b00110,
    "MVIL" : 0b00111,
    "LDIDR" : 0b01000,
    "STIDR" : 0b01001,
    "LDIDX" : 0b01010,
    "STIDX" : 0b01011,
    "JMP" : 0b01100,
    "JMPI" : 0b01101,
    "JGEO" : 0b01110,
    "JLEO" : 0b01111,
    "JCO" : 0b10000,
    "JEO" : 0b10001,
    "PUSH" : 0b10010,
    "POP" : 0b10011,
    "CALL" : 0b10100,
    "JAL" : 0b10101,
    "MOVSP" : 0b10110,
    "RET" : 0b10111,
    "STC" : 0b10111,
    "NOP" : 0b11001,
}

# instruction format referefrence
# key: opcode letter code
# value: instruction fomat string ($ = register param, # = immedaete param)
instrFormatRef = {
    "ADD" : "$$$",
    "ADC" : "$$$",
    "SUB" : "$$$",
    "SBB" : "$$$",
    "AND" : "$$$",
    "OR" : "$$$",
    "XOR" : "$$$",
    "NOT" : "$$",
    "SHFL" : "$$#",
    "SHFA" : "$$#",
    "ADDI" : "$$#",
    "SUBI" : "$$#",
    "MVIH" : "$#",
    "MVIL" : "$#",
    "LDIDR" : "$$#",
    "STIDR" : "$$#",
    "LDIDX" : "$$$",
    "STIDX" : "$$$",
    "JMP" : "#",
    "JMPI" : "$",
    "JGEO" : "$$#",
    "JLEO" : "$$#",
    "JCO" : "#",
    "JEO" : "$$#",
    "PUSH" : "$",
    "POP" : "$",
    "CALL" : "$",
    "JAL" : "#",
    "MOVSP" : "",
    "RET" : "",
    "STC" : "",
    "NOP" : "",
}

# func referefrence
# key: opcode letter code
# value: 2bit func code
funcRef = {
    "ADD" : 0b00,
    "ADC" : 0b01,
    "SUB" : 0b10,
    "SBB" : 0b11,
    "AND" : 0b00,
    "OR" : 0b01,
    "XOR" : 0b10,
    "NOT" : 0b11,
}

errorList = []
compilationError = False

def getOpcode(code):
    """Returns instruction opcode number based on the letter opcode."""
    try:
        return opcodeRef[code.upper()]
    except:
        return None

def getInstrFomat(code):
    """Returns instruction fomat as string based on the letter opcode."""
    try:
        return instrFormatRef[code.upper()]
    except:
        return None

def getFunc(code):
    """Returns instruction func (bits [0:2]) based on the letter opcode or 0 if code is not in referefrence."""
    try:
        return funcRef[code]
    except:
        return 0

def addError(text, lineNum):
    errorList.append((text, lineNum))
    global compilationError
    compilationError = True

def printErrors():
    for err in errorList:
        print("[error] line {}: {}".format(err[1], err[0]))

def verifyInstrFomat(expresions, fomatStr, lineNum):
    """
    Verifies if instruction has a correct format
    """
    # check number of parametrs
    if len(expresions) != len(fomatStr) + 1:
        addError("invalid number of instruction parametrs, given: {}, expected: {}".fomat(len(expresions)-1, len(fomatStr)), lineNum)
    # check parametr fomats
    for i,ch in enumerate(fomatStr):
        if ch == "$":
            if re.match(r"[$][0-8]",expresions[i+1]):
                continue
        elif ch == "#":
            if re.match(r"[0-9]*",expresions[i+1]):
                continue
        addError("invalid parametr number {}".format(i+1), lineNum)

def extractInstrValues(expresions, fomatStr):
    """
    Extracts values of register addresses and immedaete
    RETURN: reg - array of register addr in oreder Rd, Rs1, Rs2
            imm - value of immedaete
    """
    reg = []
    imm = None
    for i,ch in enumerate(fomatStr):
        if ch == "$":
            reg.append(int(expresions[i+1][1:]))
        elif ch == "#":
            imm = int(expresions[i+1])
    return reg, imm

def instrToBinary(expresions, fomatStr, lineNum):
    # extract values of parametrs
    reg, imm = extractInstrValues(expresions, fomatStr)
    # convert to binary
    binaryLine = getOpcode(expresions[0]) << 11 # opcode from lookup dict
    binaryLine += getFunc(expresions[0]) # func from lookup dict
    if fomatStr.count("$") == 3: # Rd,Rs1,Rs2
        binaryLine += reg[0] << 5
        binaryLine += reg[1] << 8
        binaryLine += reg[2] << 2
    elif fomatStr.count("$") == 2: # Rd, Rs1
        binaryLine += reg[0] << 5
        binaryLine += reg[1] << 8
        if fomatStr[-1] == "#": # Rd,Rs1,#5bit
            if imm < 2**5: # check if imm fits in 5 bits
                binaryLine += imm
            else:
                addError("immedaete bigger than 5 bits", lineNum)
    elif fomatStr.count("$") == 1: # Rd
        binaryLine += reg[0] << 5
        if fomatStr[-1] == "#": # Rd,#8bit
            if imm < 2**8: # check if imm fits in 8 bits
                binaryLine += imm & 0b11111
                binaryLine += ((imm >> 5) & 0b111) << 8
            else:
                addError("immedaete bigger than 8 bits", lineNum)
    elif fomatStr == "#": # #11bit
        if imm < 2**11: # check if imm fits in 11 bits
            binaryLine += imm
        else:
            addError("immedaete bigger than 11 bits", lineNum)
    return binaryLine

def lineToBinary(line, lineNum):
    # preprocessing
    line = line.split("#")[0] # trim comments
    line = line.rstrip() # trim spaces at the end
    expresions = re.split(" |,", line) # split line into expesions
    # get fomat
    fomatStr = getInstrFomat(expresions[0])
    if (fomatStr == None):
        addError("{} is not a valid instruction code".format(expresions[0]), lineNum)
        return None
    # check if format of the instruction is correct
    verifyInstrFomat(expresions, fomatStr, lineNum)
    if (compilationError):
        return None
    # get binary value of the instruction
    return instrToBinary(expresions, fomatStr, lineNum)

def main():
    # fetch cmd arguments
    source = sys.argv[1]
    dest = sys.argv[2]

    #open files
    sourceFile = open(source, "r") # assembly file
    destFile = open(dest, "wb") # bytecode file

    print("Lyng Assembler v1.0")
    print("Compiling {}...".format(source))

    # convert instructions to binary line by line
    sourceLines = sourceFile.readlines()
    for i, line in enumerate(sourceLines):
        # convert line to binary
        binaryLine = lineToBinary(line, i+1)
        if (compilationError):
            continue
        # write binary line
        binaryArr = bytearray(binaryLine.to_bytes(2, "big"))
        destFile.write(binaryArr)

    # close failes
    sourceFile.close()
    destFile.close()

    # print results
    if (compilationError):
        printErrors()
        print("Compilation failed")
    else:
        print("Compilation successful, bytecode wrriten to {}".format(dest))

if __name__ == "__main__":
    main()
