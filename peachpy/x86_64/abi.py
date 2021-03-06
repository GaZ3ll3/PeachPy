# This file is part of Peach-Py package and is licensed under the Simplified BSD license.
#    See license.rst for the full text of the license.

from peachpy.abi import ABI
from peachpy.abi import Endianness
from peachpy.x86_64.registers import rax, rbx, rcx, rdx, rsi, rdi, rbp, r8, r9, r10, r11, r12, r13, r14, r15, \
    xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15, \
    mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7
import peachpy.formats.elf.file
import peachpy.formats.mscoff.file


microsoft_x64_abi = ABI("Microsoft x64 ABI", endianness=Endianness.Little,
                        bool_size=1, wchar_size=2, short_size=2, int_size=4, long_size=4, longlong_size=8,
                        pointer_size=8, index_size=8,
                        stack_alignment=16, red_zone=0,
                        callee_save_registers=[rbx, rsi, rdi, rbp,
                                               r12, r13, r14, r15,
                                               xmm6, xmm7, xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15],
                        argument_registers=[rcx, rdx, r8, r9,
                                            xmm0, xmm1, xmm2, xmm3],
                        volatile_registers=[rax, r10, r11,
                                            mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                            xmm4, xmm5],
                        mscoff_machine_type=peachpy.formats.mscoff.file.MachineType.x86_64)

system_v_x86_64_abi = ABI("SystemV x86-64 ABI", endianness=Endianness.Little,
                          bool_size=1, wchar_size=4, short_size=2, int_size=4, long_size=8, longlong_size=8,
                          pointer_size=8, index_size=8,
                          stack_alignment=16, red_zone=128,
                          callee_save_registers=[rbx, rbp, r12, r13, r14, r15],
                          argument_registers=[rdi, rsi, rdx, rcx, r8, r9, xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7],
                          volatile_registers=[rax, r10, r11,
                                              mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                              xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15],
                          elf_class=peachpy.formats.elf.file.ElfClass.Class64,
                          elf_data_encoding=peachpy.formats.elf.file.DataEncoding.LittleEndian,
                          elf_machine_type=peachpy.formats.elf.file.MachineType.X86_64)

linux_x32_abi = ABI("Linux X32 ABI", endianness=Endianness.Little,
                    bool_size=1, wchar_size=4, short_size=2, int_size=4, long_size=4, longlong_size=8,
                    pointer_size=4, index_size=4,
                    stack_alignment=16, red_zone=128,
                    callee_save_registers=[rbx, rbp, r12, r13, r14, r15],
                    argument_registers=[rdi, rsi, rdx, rcx, r8, r9,
                                        xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7],
                    volatile_registers=[rax, r10, r11,
                                        mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                        xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15],
                    elf_class=peachpy.formats.elf.file.ElfClass.Class32,
                    elf_data_encoding=peachpy.formats.elf.file.DataEncoding.LittleEndian,
                    elf_machine_type=peachpy.formats.elf.file.MachineType.X86_64)

native_client_x86_64_abi = ABI("Native Client x86-64 ABI", endianness=Endianness.Little,
                               bool_size=1, wchar_size=4, short_size=2, int_size=4, long_size=4, longlong_size=8,
                               pointer_size=4, index_size=4,
                               stack_alignment=16, red_zone=0,
                               callee_save_registers=[rbx, rbp, r12, r13, r14, r15],
                               argument_registers=[rdi, rsi, rdx, rcx, r8, r9,
                                                   xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7],
                               volatile_registers=[rax, r10, r11,
                                                   mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                                   xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15],
                               elf_class=peachpy.formats.elf.file.ElfClass.Class64,
                               elf_data_encoding=peachpy.formats.elf.file.DataEncoding.LittleEndian,
                               elf_machine_type=peachpy.formats.elf.file.MachineType.X86_64)

golang_amd64_abi = ABI("Go x86-64 ABI", endianness=Endianness.Little,
                       bool_size=1, wchar_size=4, short_size=2, int_size=4, long_size=8, longlong_size=8,
                       pointer_size=8, index_size=8,
                       stack_alignment=8, red_zone=0,
                       callee_save_registers=[],
                       argument_registers=[],
                       volatile_registers=[rax, rbx, rcx, rdx, rdi, rsi, rbp, r8, r9, r10, r11, r12, r13, r14, r15,
                                           mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                           xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, xmm8,
                                           xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15])

golang_amd64p32_abi = ABI("Go x32 ABI", endianness=Endianness.Little,
                          bool_size=1, wchar_size=4, short_size=2, int_size=4, long_size=8, longlong_size=8,
                          pointer_size=4, index_size=4,
                          stack_alignment=4, red_zone=0,
                          callee_save_registers=[],
                          argument_registers=[],
                          volatile_registers=[rax, rbx, rcx, rdx, rdi, rsi, rbp, r8, r9, r10, r11, r12, r13, r14, r15,
                                              mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7,
                                              xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, xmm8,
                                              xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15])


def detect():
    import platform
    import struct
    (osname, node, release, version, machine, processor) = platform.uname()  # pylint:disable=unpacking-non-sequence
    pointer_size = struct.calcsize("P")
    if osname == "Darwin" and machine == "x86_64" and pointer_size == 8:
        return system_v_x86_64_abi
    elif osname == "Linux" and machine == "x86_64":
        if pointer_size == 8:
            return system_v_x86_64_abi
        else:
            return linux_x32_abi
    elif osname == "Windows" and machine == "AMD64" and pointer_size == 8:
        return microsoft_x64_abi
