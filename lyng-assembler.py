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
}

# instruction format referefrence
# key: opcode letter code
# value: instruction fomat string ($ = register param, # = immedaete param)
instrFormatRef = {
    "ADD" : "$$$",
    "ADC" : "$$$",
}

# func referefrence
# key: opcode letter code
# value: 2bit func code
funcRef = {
    "ADD" : 0b00,
    "ADC" : 0b01,
}

def getOpcode(code, lineNum):
    """Returns instruction opcode number based on the letter opcode."""
    try:
        return opcodeRef[code]
    except:
        print("Error! Invalid instruction code '{}'on line {}".format(code, lineNum))
        raise

def getInstrFomat(code, lineNum):
    """Returns instruction fomat as string based on the letter opcode."""
    try:
        return instrFormatRef[code]
    except:
        print("Error! Invalid instruction code '{}'on line {}".format(code, lineNum))
        raise

def getFunc(code):
    """Returns instruction func (bits [0:2]) based on the letter opcode or 0 if code is not in referefrence."""
    try:
        return funcRef[code]
    except:
        return 0

def main():
    # fetch cmd arguments
    source = sys.argv[1]
    dest = sys.argv[2]

    sourceFile = open(source, "r") # open assembly file
    destFile = open(dest, "wb") # open bytecode file

    # convert instructions to binary line by line
    sourceLines = sourceFile.readlines()
    l = 0 # line counter
    for line in sourceLines:
        l += 1
        # preprocessing
        line = line.split("#")[0] # trim comments
        line = line.rstrip() # trim spaces at the end
        expr = re.split(" |,", line) # split line into expesions
        # opcode to binary
        opcode = getOpcode(expr[0].upper(), l)
        # instruction format varification
        fomatStr = getInstrFomat(expr[0], l)
        if len(expr) != len(fomatStr) + 1:
            print("Error! Invalid number of instruction paremtrs on line {}, expected: {}".format(l, len(fomatStr) + 1))
            return
        for i,ch in enumerate(fomatStr):
            if ch == "$":
                if re.match(r"[$][0-8]",expr[i+1]):
                    continue
            elif ch == "#":
                if re.match(r"[0-9]*",expr[i+1]):
                    continue
            print("Error! Invalid parametr {} on line {}, expected fomat: {}".format(i+1, l, fomatStr))
            return
        # extract values
        # order is always: Rd, Rs1, Rs2, Imm
        reg = []
        imm = None
        for i,ch in enumerate(fomatStr):
            if ch == "$":
                reg.append(int(expr[i+1][1:]))
            elif ch == "#":
                imm = int(expr[i+1])
        # convert to binary
        binaryLine = getOpcode(expr[0].upper(), l) << 11 # opcode from lookup dict
        binaryLine += getFunc(expr[0].upper()) # func from lookup dict
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
                    print("Error! Immedaete bigger than 5 bits on line {}".format(l))
                    return
        elif fomatStr.count("$") == 1: # Rd
            binaryLine += reg[0] << 5
            if fomatStr[-1] == "#": # Rd,#8bit
                if imm < 2**8: # check if imm fits in 8 bits
                    binaryLine += imm & 0b11111
                    binaryLine += ((imm >> 5) & 0b111) << 8
                else:
                    print("Error! Immedaete bigger than 8 bits on line {}".format(l))
                    return
        elif fomatStr == "#": # #11bit
            if imm < 2**11: # check if imm fits in 11 bits
                binaryLine += imm
            else:
                print("Error! Immedaete bigger than 11 bits on line {}".format(l))
                return
        # write binary line
        binaryArr = bytearray(binaryLine.to_bytes(2, "big"))
        destFile.write(binaryArr)

    sourceFile.close()
    destFile.close()
    print("Bytecode ready")

if __name__ == "__main__":
    main()
