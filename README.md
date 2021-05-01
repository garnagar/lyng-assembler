# Lyng Assembler
Assembler for 16-bit [Lyng Processor](https://github.com/Zalamar/LyngProcessor) created as a part of Advanced Computer Architecture on Technical University of Denmark. It converts Lyng ISA (LISA) into machine code.

## Get Started

To use the tool run following command:

```
python3 lyng-assembler.py <source-file> <destination-file>
```

Follow README of the [Lyng Processor](https://github.com/Zalamar/LyngProcessor) project to run machine code in simulation or on FPGA.

## Assembly Syntax

Every line follows this syntax:

```
[label:] mnemonic [comma separated operands] [;comment]
```

The elements in `[]` are optional. Empty lines or lines not containing mnemonic are not allowed. Immediates are written as either decimal numbers or labels. Syntax is not case sensitive.

## LISA Reference

| Name  | Format                | Description                                                                                     |
|-------|-----------------------|-------------------------------------------------------------------------------------------------|
| ADD   | ADD Rd, Rs1, Rs2      | Adds Rs1 and Rs2 and stores the sum in Rd ignoring carry.                                       |
| ADC   | ADC Rd, Rs1 ,Rd2      | Adds Rs1 and Rs2 and stores the sum in Rd with previous carry.                                  |
| SUB   | SUB Rd, Rs1, Rs2      | Subtracts Rs2 from Rs1 and stores the difference in Rd ignoring the previous borrow.            |
| SBB   | SUB Rd, Rs1, Rs2      | Subtracts Rs2 from Rs1and stores the difference in Rd with the previous borrow.                 |
| AND   | AND Rd, Rs1, Rs2      | Performs bitwise AND of Rs1 and Rs2 and stores the result in Rd.                                |
| OR    | OR  Rd, Rs1, Rs2      | Performs bitwise OR of Rs1 and Rs2 and stores the result in Rd.                                 |
| XOR   | XOR  Rd, Rs1, Rs2     | Performs bitwise XOR of Rs1 and Rs2 and stores the result in Rd.                                |
| NOT   | NOT  Rd, Rs1          | Performs complement of Rs1 and stores the result in Rd.                                         |
| SHFL  | SHFL Rd, Rs1, #5-bit  | Shifts logically Rs1 by 5 bit signed immediate places left and store it in Rd.                  |
| SHFA  | SHFA Rd, Rs1, #5-bit  | Shifts arithmetically Rs1 by 5 bit signed immediate right and store it in Rd.                   |
| ADDI  | ADDI Rd, Rs1, #5-bit  | Adds a 5-bit unsigned value to Rs1 and stores the sum in Rd.                                    |
| SUBI  | SUBI Rd, Rs1, #5-bit  | Subtracts a 5-bit unsigned value from Rs1 and stores the difference in Rd.                      |
| MVIH  | MVIH Rd,#8-bit        | Copies immediate value into higher byte of Rd.                                                  |
| MVIL  | MVIL Rd,#8-bit        | Copies immediate value into lower byte of Rd.                                                   |
| LDIDR | LDIDR Rd, Rs1, #5-bit | Loads Rd with a word (2 bytes) at address given by [Rs1 + 5 bit immediate value].               |
| STIDR | STIDR Rd, Rs1, #5-bit | Stores Rd with a word (2 bytes) at address given by [Rs + 5 bit immediate value].               |
| LDIDX | LDIDX Rd, Rs1, Rs2    | Loads Rd with a word (2 bytes) at address given by [Rs1 + Rs2].                                 |
| STIDX | STIDX Rd, Rs1, Rs2    | Stores Rd with a word (2 bytes) at address given by [Rs1 + Rs2].                                |
| JMP   | JMP Rd                | Unconditional jump to address Rd.                                                               |
| JMPI  | JMPI #11-bit          | Unconditional jump to address offset by 11 bit signed value from current PC value.              |
| JGEO  | JGEO Rd, Rs1, #5-bit  | Conditional Jump to PC + 5 bit signed offset if Rs1 is greater than or equal to Rd.             |
| JLEO  | JLEO Rd, Rs1, #5-bit  | Conditional Jump to PC + 5 bit signed offset if Rs1 is less than or equal to Rd.                |
| JCO   | JCO #11-bit           | Conditional Jump to PC + 11 bit signed offset if carry is set.                                  |
| JEO   | JEO Rd, Rs1, #5-bit   | Conditional Jump to PC + 5 bit signed offset if Rs equals to Rd.                                |
| PUSH  | PUSH Rd               | Push Rd to the stack top and update stack top.                                                  |
| POP   | POP Rd                | Pop from the stack top and store the value to Rd and update stack top.                          |
| CALL  | CALL Rd               | Calls a subroutine located at Rd. Return address is pushed onto stack.                          |
| JAL   | JAL #11-bit           | Calls a subroutine located at [PC + 11 bit signed offset]. Return address is pushed onto stack. |
| MOVSP | MOVSP Rd              | Copies value at Rd to stack pointer SP.                                                         |
| RET   | RET                   | Return from a function. Return address is popped from the stack.                                |
| STC   | STC                   | Set the carry flag.                                                                             |
| NOP   | NOP                   | No operation. Idle machine cycle should be executed.                                            |

ISA was inspired by ([Bhavsar, Rao & Joshi, 2013](http://www.ijsrp.org/research-paper-0413/ijsrp-p16126.pdf)), but substantially modified to fit our needs.

## Project Team

* [Lukas Kyzlik](https://github.com/garnagar)
* [Dario Pasarello](https://github.com/dario-passarello)
* [Tobias Rydberg](https://github.com/Zalamar)
