from __future__ import print_function
import sys

# from logzero import logger
from elftools.elf.elffile import ELFFile
import argparse
from .dis_assembler import dis_assemble_elf
from .error import Error

APP_NAME = "eBPF dis-assembler"


def collect_cmd_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=APP_NAME)
    parser.add_argument('object_files', metavar='F', type=str, nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    args = collect_cmd_arguments()
    for obj_file in args.object_files:
        result = dis_assemble_elf(obj_file)
        if type(result) is Error:
            print(result.fatal_message(), file=sys.stderr)
            exit(1)

        print(result)
