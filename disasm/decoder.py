from typing import Optional, Tuple
from .instruction import *

OPCODE_OFFSET = 0
REGS_OFFSET = 1
OFFSET_FIELD_OFFSET = 2
OFFSET_FIELD_LENGTH = 2
IMMEDIATE_OFFSET = 4

SRC_REG_OFFSET = 0xf0
DST_REG_OFFSET = 0x0f
NORMAL_OPCODE_MASK = 0b11110000
SOURCE_MASK = 0b00001000
MODE_MASK = 0b11100000
SIZE_MASK = 0b00011000
INST_CLASS_MASK = 0b00000111
OFFSET_FIELD_LENGTH = 2

SRC_REG_OFFSET = 0xf0
DST_REG_OFFSET = 0x0f
NORMAL_OPCODE_MASK = 0b11110000
SOURCE_MASK = 0b00001000
MODE_MASK = 0b11100000
SIZE_MASK = 0b00011000
INST_CLASS_MASK = 0b00000111


def get_inst_class(raw: int) -> Optional[InstructionClass]:
    for ic in iter(InstructionClass):
        if raw == ic:
            return ic

    return None


def get_alu_opcode(raw: int) -> Optional[ALUOpcode]:
    for op in iter(ALUOpcode):
        if raw == op:
            return op

    return None


def get_jmp_opcode(raw: int) -> Optional[JMPOpcode]:
    for op in iter(JMPOpcode):
        if raw == op:
            return op

    return None


def get_memory_mode(raw: int) -> Optional[MemoryMode]:
    for mode in iter(MemoryMode):
        if raw == mode:
            return mode

    return None


def get_memory_size(raw: int) -> Optional[MemorySize]:
    for sz in iter(MemorySize):
        if raw == sz:
            return sz

    return None


def decode_normal_opcode_with(ic: InstructionClass, raw: int):
    if ic in [InstructionClass.ALU, InstructionClass.ALU64]:
        return get_alu_opcode(raw)
    elif ic in [InstructionClass.JMP, InstructionClass.JMP32]:
        return get_jmp_opcode(raw)

    return None


def decode_normal_opcode_encoding(ic: InstructionClass, raw_byte: int) -> Optional[NormalOpcodeEncoding]:
    op = decode_normal_opcode_with(ic, raw_byte & NORMAL_OPCODE_MASK)
    if op is None:
        return None

    source = raw_byte & SOURCE_MASK != 0
    return NormalOpcodeEncoding(op, ic, source)


def decode_memory_opcode_encoding(ic: InstructionClass, raw_byte) -> Optional[MemoryOpcodeEncoding]:
    mode = get_memory_mode(raw_byte & MODE_MASK)
    if mode is None:
        return None

    size = get_memory_size(raw_byte & SIZE_MASK)
    if size is None:
        return None

    return MemoryOpcodeEncoding(mode, size, ic)


def decode_opcode_encoding(raw_byte):
    ic = get_inst_class(raw_byte & INST_CLASS_MASK)
    if ic is None:
        return None

    if ic in [InstructionClass.ALU, InstructionClass.ALU64, InstructionClass.JMP, InstructionClass.JMP32]:
        return decode_normal_opcode_encoding(ic, raw_byte)
    else:
        return decode_memory_opcode_encoding(ic, raw_byte)


def decode_registers(raw_byte) -> Tuple[int, int]:
    src = raw_byte & SRC_REG_OFFSET
    dst = raw_byte & DST_REG_OFFSET
    return (src >> 4, dst)


def decode_offset(raw: bytes) -> int:
    offset_start = OFFSET_FIELD_OFFSET
    offset_end = OFFSET_FIELD_OFFSET + OFFSET_FIELD_LENGTH
    raw_offset = raw[offset_start:offset_end]

    offset = int.from_bytes(raw_offset, 'little', signed=True)
    return offset


def decode_immediate(raw: bytes, long: bool) -> int:
    imm_start = IMMEDIATE_OFFSET
    imm_end = IMMEDIATE_OFFSET + 8 if long else IMMEDIATE_OFFSET + 4
    raw_imm = raw[imm_start:imm_end]
    imm = int.from_bytes(raw_imm, 'little', signed=True)
    return imm


def decode(raw: bytes) -> Instruction:
    encoding = decode_opcode_encoding(raw[OPCODE_OFFSET])
    regs = decode_registers(raw[REGS_OFFSET])
    offset = decode_offset(raw)
    immediate = decode_immediate(raw, type(encoding) == MemoryOpcodeEncoding and encoding.inst_class in [
                                 InstructionClass.LD, InstructionClass.LDX] and encoding.mode == MemoryMode.IMM)

    return Instruction(encoding, regs, offset, immediate)
