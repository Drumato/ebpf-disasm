from enum import IntEnum
import dataclasses

from typing import Optional


class InstructionClass(IntEnum):
    LD = 0x00
    LDX = 0x01
    ST = 0x02
    STX = 0x03
    ALU = 0x04
    JMP = 0x05
    JMP32 = 0x06
    ALU64 = 0x07


@dataclasses.dataclass
class NormalOpcodeEncoding:
    opcode: IntEnum
    inst_class: InstructionClass
    source: bool


class MemoryMode(IntEnum):
    IMM = 0x00
    ABS = 0x20
    IND = 0x40
    MEM = 0x60
    RESERVED1 = 0x80
    RESERVED2 = 0xa0
    XADD = 0xc0


class MemorySize(IntEnum):
    W = 0x00
    H = 0x08
    B = 0x10
    DW = 0x18


@dataclasses.dataclass
class MemoryOpcodeEncoding:
    mode: MemoryMode
    size: MemorySize
    inst_class: InstructionClass


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


class Instruction:
    def __init__(self, encoding, regs, offset: int, immediate: int):
        self.encoding = encoding
        self.src_reg, self.dst_reg = regs
        self.offset = offset
        self.immediate = immediate

    def string(self) -> str:
        if type(self.encoding) == NormalOpcodeEncoding:
            return self.normal_string()
        elif type(self.encoding) == MemoryOpcodeEncoding:
            return self.memory_string()
        else:
            return "unreachable"

    def memory_string(self) -> str:
        if self.encoding.inst_class == InstructionClass.LD:
            return self.load_inst_string('ld')
        elif self.encoding.inst_class == InstructionClass.LDX:
            return self.load_inst_string('ldx')
        elif self.encoding.inst_class == InstructionClass.ST:
            return self.store_inst_string('st')
        elif self.encoding.inst_class == InstructionClass.STX:
            return self.store_inst_string('stx')
        else:
            return "unreachable"

    def load_inst_string(self, mnemonic) -> str:
        if self.encoding.mode == MemoryMode.IMM:
            return f"{self.dst_string()} <- {self.src_string(True)} ll"
        if self.encoding.mode == MemoryMode.ABS:
            return f"{self.dst_string()} <- *({self.size_string()} *)sk_buff[{self.immediate + self.offset}]"
        elif self.encoding.mode == MemoryMode.MEM:
            return f"{self.dst_string()} <- *({self.size_string()} *)({self.src_string(False)} + {self.offset})"
        else:
            return "unreachable"

    def store_inst_string(self, mnemonic) -> str:
        if self.encoding.mode == MemoryMode.XADD:
            return f"lock *({self.size_string()} *)({self.dst_string()} + {self.offset}) <- {self.dst_string()} + {self.src_string(False)}"
        elif self.encoding.mode == MemoryMode.MEM:
            return f"*({self.size_string()} *)({self.dst_string()} + {self.offset}) <- {self.src_string(False)}"
        else:
            return "unreachable"

    def normal_string(self) -> str:
        if self.encoding.inst_class in [InstructionClass.ALU, InstructionClass.ALU64]:
            return self.normal_alu_string()
        elif self.encoding.inst_class in [InstructionClass.JMP, InstructionClass.JMP32]:
            return self.normal_jmp_string()
        else:
            return "unreachable"

    def normal_alu_string(self) -> str:
        # binary operands
        if self.encoding.opcode == ALUOpcode.ADD:
            return self.binary_operands_inst_string('+')
        elif self.encoding.opcode == ALUOpcode.SUB:
            return self.binary_operands_inst_string('-')
        elif self.encoding.opcode == ALUOpcode.MUL:
            return self.binary_operands_inst_string('*')
        elif self.encoding.opcode == ALUOpcode.DIV:
            return self.binary_operands_inst_string('/')
        elif self.encoding.opcode == ALUOpcode.MOD:
            return self.binary_operands_inst_string('%')
        elif self.encoding.opcode == ALUOpcode.AND:
            return self.binary_operands_inst_string('&')
        elif self.encoding.opcode == ALUOpcode.OR:
            return self.binary_operands_inst_string('|')
        elif self.encoding.opcode == ALUOpcode.XOR:
            return self.binary_operands_inst_string('^')
        elif self.encoding.opcode == ALUOpcode.LSH:
            return self.binary_operands_inst_string('<<')
        elif self.encoding.opcode == ALUOpcode.RSH:
            return self.binary_operands_inst_string('>>(logic)')
        elif self.encoding.opcode == ALUOpcode.ARSH:
            return self.binary_operands_inst_string('>>(arith)')
        # unary operands
        elif self.encoding.opcode == ALUOpcode.MOV:
            return self.unary_operand_inst_string('')
        elif self.encoding.opcode == ALUOpcode.NEG:
            return self.unary_operand_inst_string('-')
        # misc
        elif self.encoding.opcode == ALUOpcode.END:
            return self.endian_conversion_inst_string()
        else:
            return "unreachable!"

    def normal_jmp_string(self) -> str:
        if self.encoding.opcode == JMPOpcode.EXIT:
            return "exit"
        elif self.encoding.opcode == JMPOpcode.JA:
            return self.jmp_inst_string('')
        elif self.encoding.opcode == JMPOpcode.JGE:
            return self.jmp_inst_string('>=')
        elif self.encoding.opcode == JMPOpcode.JLE:
            return self.jmp_inst_string('<=')
        elif self.encoding.opcode == JMPOpcode.JGT:
            return self.jmp_inst_string('>')
        elif self.encoding.opcode == JMPOpcode.JLT:
            return self.jmp_inst_string('<')
        elif self.encoding.opcode == JMPOpcode.JSGE:
            return self.jmp_inst_string('>=(signed)')
        elif self.encoding.opcode == JMPOpcode.JSLE:
            return self.jmp_inst_string('<=(signed)')
        elif self.encoding.opcode == JMPOpcode.JSGT:
            return self.jmp_inst_string('>(signed)')
        elif self.encoding.opcode == JMPOpcode.JSLT:
            return self.jmp_inst_string('<(signed)')
        elif self.encoding.opcode == JMPOpcode.JEQ:
            return self.jmp_inst_string('==')
        elif self.encoding.opcode == JMPOpcode.JNE:
            return self.jmp_inst_string('!=')
        elif self.encoding.opcode == JMPOpcode.JSET:
            return self.jmp_inst_string('&')
        elif self.encoding.opcode == JMPOpcode.CALL:
            return f"call {self.immediate}"
        else:
            return "unreachable!"

    def jmp_inst_string(self, operator: str) -> str:
        plus_sign = '' if self.offset < 0 else '+'
        if operator == '':
            return f"goto {plus_sign}{self.offset}"

        return f"goto {plus_sign}{self.offset} if {self.dst_string()} {operator} {self.src_string(not self.encoding.source)}"

    def unary_operand_inst_string(self, operator: str) -> str:
        return f"{self.dst_string()} <- {operator}{self.src_string(not self.encoding.source)}"

    def binary_operands_inst_string(self, operator: str) -> str:
        return f"{self.dst_string()} <- {self.dst_string()} {operator} {self.src_string(not self.encoding.source)}"

    def endian_conversion_inst_string(self) -> str:
        conv_f = 'htobe' if self.encoding.source else 'htole'
        return self.unary_operand_inst_string(conv_f + str(self.immediate))

    def src_string(self, is_imm: bool) -> str:
        if is_imm:
            return self.immediate
        else:
            return self.num_to_reg(self.src_reg)

    def dst_string(self) -> str:
        return self.num_to_reg(self.dst_reg)

    def size_string(self) -> str:
        if self.encoding.size == MemorySize.B:
            return "u8"
        if self.encoding.size == MemorySize.H:
            return "u16"
        if self.encoding.size == MemorySize.W:
            return "u32"
        if self.encoding.size == MemorySize.DW:
            return "u64"
        else:
            return "unknown"

    def num_to_reg(self, number: int) -> str:
        return f"r{number}"
