#!/usr/bin/python
import sys
import re
import enum

# opcode refrence
# key: opcode letter code
# value: 5bit opcode
opcodeRef = {
    "ADD" : 0b00001,
    "ADC" : 0b00001,
    "SUB" : 0b00001,
    "SBB" : 0b00001,
    "AND" : 0b00010,
    "OR" : 0b00010,
    "XOR" : 0b00010,
    "NOT" : 0b00010,
    "SHFL" : 0b00011,
    "SHFA" : 0b00100,
    "ADDI" : 0b00101,
    "SUBI" : 0b00110,
    "MVIH" : 0b00111,
    "MVIL" : 0b01000,
    "LDIDR" : 0b01001,
    "STIDR" : 0b01010,
    "LDIDX" : 0b01011,
    "STIDX" : 0b01100,
    "JMP" : 0b01101,
    "JMPI" : 0b01110,
    "JGEO" : 0b01111,
    "JLEO" : 0b10000,
    "JCO" : 0b10001,
    "JEO" : 0b10010,
    "PUSH" : 0b10011,
    "POP" : 0b10100,
    "CALL" : 0b10101,
    "JAL" : 0b10110,
    "MOVSP" : 0b10111,
    "RET" : 0b11000,
    "STC" : 0b11001,
    "NOP" : 0b00000,
}

# instruction format referefrence
# key: opcode letter code
# value: instruction fomat string (R = register, U = unsigned immedaete, S = singed immedaete)
instrFormatRef = {
    "ADD" : "RRR",
    "ADC" : "RRR",
    "SUB" : "RRR",
    "SBB" : "RRR",
    "AND" : "RRR",
    "OR" : "RRR",
    "XOR" : "RRR",
    "NOT" : "RR",
    "SHFL" : "RRS",
    "SHFA" : "RRS",
    "ADDI" : "RRU",
    "SUBI" : "RRU",
    "MVIH" : "RU",
    "MVIL" : "RU",
    "LDIDR" : "RRS",
    "STIDR" : "RRS",
    "LDIDX" : "RRR",
    "STIDX" : "RRR",
    "JMP" : "R",
    "JMPI" : "S",
    "JGEO" : "RRS",
    "JLEO" : "RRS",
    "JCO" : "S",
    "JEO" : "RRS",
    "PUSH" : "R",
    "POP" : "R",
    "CALL" : "R",
    "JAL" : "S",
    "MOVSP" : "R",
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

# global error list and error flag
errorList = []
compilationError = False

def getOpcode(mnemonic):
    """Return opcode based on mnemonic of the instruction"""
    try:
        return opcodeRef[mnemonic.upper()]
    except:
        return None

def getInstrFomat(mnemonic):
    """Return instruction fomat string (R = register, U = unsigned immedaete, S = singed immedaete) based on the mnemonic"""
    try:
        return instrFormatRef[mnemonic.upper()]
    except:
        return None

def getFunc(code):
    """Return instruction func (bits [0:2]) based on the letter opcode or 0 if code is not in referefrence"""
    try:
        return funcRef[code]
    except:
        return 0

def addError(text, lineNum):
    """Add error to error list and makrk compilation as failed"""
    errorList.append((text, lineNum))
    global compilationError
    compilationError = True

def printErrors():
    """Print out error list"""
    for err in errorList:
        print("[error] line {}: {}".format(err[1], err[0]))

def decStrToBin(numStr, bits):
    """Convert sring into int of n-bits (negative numbers as 2's complement)"""
    return int(int(numStr) & 2**bits-1)

def isInBitRange(num, bits, signed):
    """
    Check if number is encodable in n-bits
    num     - number to check
    bits    - max number of bits
    signed  - 'S' = signed, 'U' = unsigned
    return: True if is in range
    """
    if signed == "S":
        return (2**(bits-1) > int(num) and -(2**(bits-1)) <= int(num))
    elif signed == "U":
        return 2**bits > int(num)
    else:
        raise ValueError("invalid signedness mark")

def verifyInstrFomat(expresions, fomatStr, lineNum):
    """
    Verify if instruction has a correct format and add errors to error list if not
    expresions - array of srings as parts of instruction (letter code followed by parametrs)
    fomatStr   - format string of the instruction
    lineNum    - source file line number
    return: none
    """
    # check number of parametrs
    if len(expresions) != len(fomatStr) + 1:
        addError("invalid number of instruction parametrs, given: {}, expected: {}".format(len(expresions)-1, len(fomatStr)), lineNum)
    # check parametr fomats
    for i,ch in enumerate(fomatStr):
        if ch == "R":
            if re.match(r"[$][0-7]",expresions[i+1]):
                continue
        elif ch == "U":
            if re.match(r"^[0-9]*$",expresions[i+1]):
                continue
        elif ch == "S":
            if re.match(r"^-?[0-9]*$",expresions[i+1]):
                continue
        addError("invalid parametr number {}".format(i+1), lineNum)

def extractInstrValues(expresions, fomatStr):
    """
    Extracts values of register addresses and immedaete
    expresions - array of srings as parts of instruction (letter code followed by parametrs)
    fomatStr   - format string of the instruction
    return: reg - array of register addr in oreder Rd, Rs1, Rs2
            imm - value of immedaete
    """
    reg = []
    imm = None
    for i,ch in enumerate(fomatStr):
        if ch == "R":
            reg.append(int(expresions[i+1][1:]))
        elif ch == "U" or ch == "S":
            imm = expresions[i+1]
    return reg, imm

def instrToBinary(expresions, fomatStr, lineNum):
    """
    Convert instruction from expresions (string parts) to binary
    expresions - array of srings as parts of instruction (letter code followed by parametrs)
    fomatStr   - format string of the instruction
    lineNum    - source file line number
    return: instruction as binary int
    """
    # extract values of parametrs
    reg, imm = extractInstrValues(expresions, fomatStr)
    # convert to binary
    binaryLine = getOpcode(expresions[0]) << 11 # opcode from lookup dict
    binaryLine += getFunc(expresions[0]) # func from lookup dict
    if fomatStr.count("R") == 3: # Rd,Rs1,Rs2
        binaryLine += reg[0] << 5
        binaryLine += reg[1] << 8
        binaryLine += reg[2] << 2
    elif fomatStr.count("R") == 2: # Rd, Rs1
        binaryLine += reg[0] << 5
        binaryLine += reg[1] << 8
        if fomatStr[-1] == "U" or fomatStr[-1] == "S": # Rd,Rs1,#5bit
            if isInBitRange(imm, 5, fomatStr[-1]): # check if imm fits in 5 bits
                imm = decStrToBin(imm, 5)
                binaryLine += imm
            else:
                addError("immedaete bigger than 5 bits", lineNum)
    elif fomatStr.count("R") == 1: # Rd
        binaryLine += reg[0] << 5
        if fomatStr[-1] == "U" or fomatStr[-1] == "S": # Rd,#8bit
            if isInBitRange(imm, 8, fomatStr[-1]): # check if imm fits in 8 bits
                imm = decStrToBin(imm, 8)
                binaryLine += imm & 0b11111
                binaryLine += ((imm >> 5) & 0b111) << 8
            else:
                addError("immedaete bigger than 8 bits", lineNum)
    elif fomatStr == "U" or fomatStr == "S": # #11bit
        if isInBitRange(imm, 11, fomatStr[-1]): # check if imm fits in 11 bits
            imm = decStrToBin(imm, 11)
            binaryLine += imm
        else:
            addError("immedaete bigger than 11 bits", lineNum)
    return binaryLine

def lineToExpresions(line):
    line = line.split(";")[0] # trim comments
    line = line.strip() # trim spaces
    preex = line.split(",") # split line into expesions
    expresions = re.sub(" +"," ", preex[0]).split(" ")
    preex = preex[1:]
    for pe in preex:
        expresions.append(pe.strip())
    for ex in expresions:
        ex = ex.strip() # trim spaces
    return expresions

def lineToBinary(line, lineNum):
    """
    Verify line fomat and convert it to binary instruction
    line       - line as string
    lineNum    - source file line number
    return: instruction as binary int
    """
    # preprocessing
    expresions = lineToExpresions(line)

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

def replaceLabels(sourceLines):
    # extract labels
    labelLocation = []
    for i, line in enumerate(sourceLines):
        if (":" in line):
            label = line.split(":")[0].strip()
            if(label !=  ""):
                labelLocation.append([label, i])

    return labelLocation


def main():
    # fetch cmd arguments
    source = sys.argv[1]
    dest = sys.argv[2]

    print("Lyng Assembler v0.1")

    #open files
    try:
        sourceFile = open(source, "r") # assembly file
    except:
        print("Opening {} failed".format(source))
        return
    try:
        destFile = open(dest, "wb") # bytecode file
    except:
        print("Opening {} failed".format(dest))
        return

    print("Compiling {}...".format(source))

    sourceLines = sourceFile.readlines()

    # replace labels with numeric values
    #print(replaceLabels(sourceLines))

    # convert instructions to binary line by line
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
