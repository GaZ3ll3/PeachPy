# This file is part of Peach-Py package and is licensed under the Simplified BSD license.
#    See license.rst for the full text of the license.

from __future__ import print_function
from opcodes.x86_64 import *
from codegen.code import CodeWriter, CodeBlock
import os
import json
import subprocess
import tempfile


instruction_set = read_instruction_set()

instruction_groups = json.load(open(os.path.join(os.path.dirname(__file__), "x86_64.json")))


def filter_instruction_forms(instruction_forms):
    """Removes the instruction forms that are currently not supported"""

    new_instruction_forms = list()
    for instruction_form in instruction_forms:
        if all([operand.type not in {"r8l", "r16l", "r32l", "moffs32", "moffs64"} for operand in instruction_form.operands]):
            new_instruction_forms.append(instruction_form)
    return new_instruction_forms


def objcopy(*args):
    objdump_path = os.environ.get("OBJCOPY_FOR_X86", os.environ.get("OBJCOPY"))
    objdump_process = subprocess.Popen([objdump_path] + list(args),
                                       shell=False,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = objdump_process.communicate()
    if objdump_process.returncode != 0:
        print(stdoutdata)
        print(stderrdata)


def gas(*args):
    gas_path = os.environ.get("AS_FOR_X86", os.environ.get("GAS"))
    gas_process = subprocess.Popen([gas_path] + list(args),
                                   shell=False,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = gas_process.communicate()
    if gas_process.returncode != 0:
        print(stdoutdata)
        print(stderrdata)
    return stdoutdata


def binutils_encode(assembly):
    with tempfile.NamedTemporaryFile(delete=False) as asm_file:
        print(".text", file=asm_file)
        print(".intel_syntax noprefix", file=asm_file)
        print(assembly, file=asm_file)
    obj_file = tempfile.NamedTemporaryFile(delete=False)
    obj_file.close()
    bin_file = tempfile.NamedTemporaryFile(delete=False)
    bin_file.close()
    try:
        gas("-o", obj_file.name, asm_file.name)
        os.remove(asm_file.name)
        objcopy("-O", "binary", "-j", ".text", obj_file.name, bin_file.name)
        os.remove(obj_file.name)
    except OSError:
        print(assembly)
        raise
    bytecode = bytearray(open(bin_file.name, "rb").read())
    os.remove(bin_file.name)
    return "bytearray([%s])" % ", ".join(["0x%02X" % b for b in bytecode])


def generate_operand(operand, operand_number, peachpy=True):
    value_map = {
        "r8": ["bl", "r9b", "dl", "r11b"],
        "r16": ["si", "r12w", "di", "r14w"],
        "r32": ["ebp", "r8d", "eax", "r10d"],
        "r64": ["rcx", "r15", "rax", "r13"],
        "mm": ["mm3", "mm5"],
        "xmm": ["xmm1", "xmm14", "xmm3", "xmm9"],
        "ymm": ["ymm2", "ymm15", "ymm4", "ymm10"],
        "m": "[r15 + rsi*8 - 128]",
        "m8": "byte[r14 + rdi*4 - 123]",
        "m16": "word[r13 + rbp*8 - 107]",
        "m32": "dword[r12 + rcx*8 - 99]",
        "m64": "qword[r11 + rdx*8 - 88]",
        "m128": "oword[r10 + rax*8 - 77]",
        "m256": "hword[r9 + rbx*8 - 66]",
        "imm4": "0b11",
        "imm8": "2",
        "imm16": "32000",
        "imm32": "0x10000000",
        "imm64": "0x100000000",
        # "rel32": "rip+0x11223344",
        # "rel8": "rip-100",
        "al": "al",
        "cl": "cl",
        "ax": "ax",
        "eax": "eax",
        "rax": "rax",
        "xmm0": "xmm0",
        "1": "1",
        "3": "3"
    }
    optype = operand.type
    operand = value_map.get(optype)
    if isinstance(operand, list):
        operand = operand[operand_number]
    if operand is not None and not peachpy:
        operand = operand.\
            replace("byte", "BYTE PTR ").\
            replace("dword", "DWORD PTR").\
            replace("qword", "QWORD PTR").\
            replace("oword", "XMMWORD PTR").\
            replace("hword", "YMMWORD PTR").\
            replace("word", "WORD PTR").\
            replace("rip", "$+2")
    return operand


tab = " " * 4


for group, instruction_names in instruction_groups.iteritems():
    with open("test/x86_64/encoding/test_%s.py" % group, "w") as out:
        with CodeWriter() as code:
            code.line("# This file is auto-generated by /codegen/x86_64_test_encoding.py")
            code.line("# Reference opcodes are generated by:")
            code.line("#     " + gas("--version").splitlines()[0])
            code.line()
            code.line("from peachpy.x86_64 import *")
            code.line("import unittest")
            code.line()
            code.line()
            for name in instruction_names:
                code.line("class Test%s(unittest.TestCase):" % name)
                with CodeBlock():
                    code.line("def runTest(self):")
                    with CodeBlock():
                        # Instructions with `name` name
                        name_instructions = filter(lambda i: i.name == name, instruction_set)
                        if not name_instructions:
                            print("No forms for instruction: " + name)
                            continue
                        assert len(name_instructions) == 1
                        name_instruction = name_instructions[0]

                        has_assertions = False
                        for instruction_form in filter_instruction_forms(name_instruction.forms):
                            peachpy_operands = [generate_operand(o, i, peachpy=True) for (i, o)
                                                in enumerate(instruction_form.operands)]
                            gas_operands = [generate_operand(o, i, peachpy=False) for (i, o)
                                            in enumerate(instruction_form.operands)]
                            if not any(map(lambda op: op is None, gas_operands)):
                                gas_assembly = "%s %s" % (instruction_form.name, ", ".join(gas_operands))
                                peachpy_assembly = "%s(%s)" % (instruction_form.name, ", ".join(peachpy_operands))
                                reference_bytecode = binutils_encode(gas_assembly)
                                code.line("self.assertEqual(%s, %s.encode())" %
                                          (reference_bytecode, peachpy_assembly))
                                has_assertions = True
                        if not has_assertions:
                            code.line("pass")
                        code.line()
                        code.line()

        print(str(code), file=out)
