from typing import Optional
from .instruction import *

OPCODE_OFFSET = 0
NORMAL_OPCODE_MASK = 0xf0
SOURCE_MASK = 0x08
MODE_MASK = 0xe0
SIZE_MASK = 0x18
INST_CLASS_MASK = 0x07


def get_normal_inst_class(raw: int) -> Optional[NormalInstructionClass]:
    for ic in iter(NormalInstructionClass):
        if raw == ic:
            return ic

    return None


def get_memory_inst_class(raw: int) -> Optional[MemoryInstructionClass]:
    for ic in iter(MemoryInstructionClass):
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
    for op in iter(MemoryMode):
        if raw == op:
            return op

    return None


def get_memory_size(raw: int) -> Optional[MemorySize]:
    for op in iter(MemorySize):
        if raw == op:
            return op

    return None


def get_normal_opcode_with(inst_class: NormalInstructionClass, raw: int):
    if inst_class in [NormalInstructionClass.ALU, NormalInstructionClass.ALU64]:
        return get_alu_opcode(raw)
    elif inst_class in [NormalInstructionClass.JMP, NormalInstructionClass.JMP32]:
        return get_jmp_opcode(raw)

    return None


def get_normal_opcode_encoding(raw_byte) -> Optional[NormalOpcodeEncoding]:
    ic = get_normal_inst_class(raw_byte & INST_CLASS_MASK)
    if ic is None:
        return None

    op = get_normal_opcode_with(ic, raw_byte & NORMAL_OPCODE_MASK)
    if op is None:
        return None

    source = raw_byte & SOURCE_MASK != 0
    return NormalOpcodeEncoding(op, ic, source)


def get_memory_opcode_encoding(raw_byte) -> Optional[MemoryOpcodeEncoding]:
    ic = get_memory_inst_class(raw_byte & INST_CLASS_MASK)
    if ic is None:
        return None

    mode = get_memory_mode(raw_byte & MODE_MASK)
    if mode is None:
        return None

    size = get_memory_size(raw_byte & SIZE_MASK)
    if size is None:
        return None

    return MemoryOpcodeEncoding(mode, size, ic)


def get_opcode_encoding(raw_byte):
    encoding = get_normal_opcode_encoding(raw_byte)
    if encoding is not None:
        return encoding

    return get_memory_opcode_encoding(raw_byte)


def decode(raw: bytes) -> Instruction:
    encoding = get_opcode_encoding(raw[OPCODE_OFFSET])
    inst = Instruction(encoding)
    print(inst.encoding)
