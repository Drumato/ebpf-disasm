from enum import IntEnum
import dataclasses

from typing import Optional


class Instruction:
    def __init__(self, encoding):
        self.encoding = encoding


class NormalInstructionClass(IntEnum):
    ALU = 0x04
    JMP = 0x05
    JMP32 = 0x06
    ALU64 = 0x07


@dataclasses.dataclass
class NormalOpcodeEncoding:
    opcode: IntEnum
    inst_class: NormalInstructionClass
    Source: bool


class MemoryInstructionClass(IntEnum):
    LD = 0x00
    LDX = 0x01
    ST = 0x02
    STX = 0x03


class MemoryMode(IntEnum):
    IMM = 0x00
    ABS = 0x20
    IND = 0x40
    MEM = 0x60
    RESERVED1 = 0x80
    RESERVED2 = 0xa0
    XADD = 0xc0


class MemorySize(IntEnum):
    B = 0x00
    H = 0x08
    W = 0x10
    DW = 0x18


@dataclasses.dataclass
class MemoryOpcodeEncoding:
    mode: MemoryMode
    size: MemorySize
    inst_class: MemoryInstructionClass


class ALUOpcode(IntEnum):
    ADD = 0x00
    SUB = 0x10
    MUL = 0x20
    DIV = 0x30
    OR = 0x40
    AND = 0x50
    LSH = 0x60
    RSH = 0x70
    NEG = 0x80
    MOD = 0x90
    XOR = 0xa0
    MOV = 0xb0
    ARSH = 0xc0
    END = 0xd0


class JMPOpcode(IntEnum):
    JA = 0x00
    JEQ = 0x10
    JGT = 0x20
    JGE = 0x30
    JSET = 0x40
    JNE = 0x50
    JSGT = 0x60
    JSGE = 0x70
    CALL = 0x80
    EXIT = 0x90
    JLT = 0xa0
    JLE = 0xb0
    JSLT = 0xc0
    JSLE = 0xd0
