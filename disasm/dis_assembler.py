from typing import Union

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import Section
from elftools.elf.constants import SH_FLAGS

from .error import Error, ErrorReason
from .decoder import decode


def dis_assemble_elf(file_path: str) -> Union[str, Error]:
    f = open(file_path, 'rb')

    elf = ELFFile(f)
    ebpf_symbols = list(filter(is_ebpf_function, elf.iter_sections()))

    if len(ebpf_symbols) == 0:
        return Error(ErrorReason.CANNOT_FOUND_EBPF_FUNCTION, "")

    dis_assembled = '\n'.join(
        map(dis_assemble_symbol, filter(lambda symbol: not symbol.name.startswith('.'), ebpf_symbols)))

    f.close()
    return dis_assembled


def dis_assemble_symbol(ebpf_symbol: Section) -> Union[str, Error]:
    if ebpf_symbol.name == "license":
        return f"LICENSE: {ebpf_symbol.data().decode('utf-8')}"

    return dis_assemble_ebpf_fn(ebpf_symbol)


def dis_assemble_ebpf_fn(ebpf_fn: Section) -> Union[str, Error]:
    ebpf_codes = ebpf_fn.data()
    instruction_number = ebpf_fn.data_size // 8

    for i in range(instruction_number):
        raw_inst = ebpf_codes[i * 8:(i + 1) * 8]
        decode(raw_inst)

    return ""


def is_ebpf_function(sct: Section) -> bool:
    return sct['sh_type'] == 'SHT_PROGBITS' and sct['sh_flags'] & SH_FLAGS.SHF_ALLOC != 0 and sct['sh_flags'] & SH_FLAGS.SHF_EXECINSTR
