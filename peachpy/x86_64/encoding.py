# This file is part of Peach-Py package and is licensed under the Simplified BSD license.
#    See license.rst for the full text of the license.


def optional_rex(r, rm, force_rex=False):
    assert r in {0, 1}, "REX.R must be 0 or 1"
    from peachpy.x86_64.operand import MemoryAddress
    from peachpy.x86_64.registers import Register
    assert isinstance(rm, (Register, MemoryAddress)), \
        "rm is expected to be a register or a memory address"
    b = 0
    x = 0
    if isinstance(rm, Register):
        b = rm.hcode
    else:
        if rm.base is not None:
            b = rm.base.hcode
        if rm.index is not None:
            x = rm.index.hcode
    # If REX.R, REX.X, and REX.B are all zeroes, REX prefix can be omitted
    if (r | x | b) == 0 and not force_rex:
        return bytearray()
    else:
        return bytearray([0x40 | (r << 2) | (x << 1) | b])


def rex(w, r, rm):
    assert w in {0, 1}, "REX.W must be 0 or 1"
    assert r in {0, 1}, "REX.R must be 0 or 1"
    from peachpy.x86_64.operand import MemoryAddress
    assert isinstance(rm, MemoryAddress), \
        "rm is expected to be a memory address"
    b = 0
    if rm.base is not None:
        b = rm.base.hcode
    x = 0
    if rm.index is not None:
        x = rm.index.hcode
    return bytearray([0x40 | (w << 3) | (r << 2) | (x << 1) | b])


def vex2(lpp, r, rm, vvvv=0, force_vex3=False):
    #                          2-byte VEX prefix:
    # Requires: VEX.W = 0, VEX.mmmmm = 0b00001 and VEX.B = VEX.X = 0
    #         +----------------+
    # Byte 0: | Bits 0-7: 0xC5 |
    #         +----------------+
    #
    #         +-----------+----------------+----------+--------------+
    # Byte 1: | Bit 7: ~R | Bits 3-6 ~vvvv | Bit 2: L | Bits 0-1: pp |
    #         +-----------+----------------+----------+--------------+
    #
    #
    #                          3-byte VEX prefix:
    #         +----------------+
    # Byte 0: | Bits 0-7: 0xC4 |
    #         +----------------+
    #
    #         +-----------+-----------+-----------+-------------------+
    # Byte 1: | Bit 7: ~R | Bit 6: ~X | Bit 5: ~B | Bits 0-4: 0b00001 |
    #         +-----------+-----------+-----------+-------------------+
    #
    #         +----------+-----------------+----------+--------------+
    # Byte 2: | Bit 7: 0 | Bits 3-6: ~vvvv | Bit 2: L | Bits 0-1: pp |
    #         +----------+-----------------+----------+--------------+
    assert lpp & ~0b111 == 0, "VEX.Lpp must be a 3-bit mask"
    assert r & ~0b1 == 0, "VEX.R must be a single-bit mask"
    assert vvvv & ~0b1111 == 0, "VEX.vvvv must be a 4-bit mask"
    from peachpy.x86_64.operand import MemoryAddress
    from peachpy.x86_64.registers import Register
    assert rm is None or isinstance(rm, (Register, MemoryAddress)), \
        "rm is expected to be a register, a memory address, or None"
    b = 0
    x = 0
    if rm is not None:
        if isinstance(rm, Register):
            b = rm.hcode
        else:
            if rm.base is not None:
                b = rm.base.hcode
            if rm.index is not None:
                x = rm.index.hcode
    # If VEX.B and VEX.X are zeroes, 2-byte VEX prefix can be used
    if (x | b) == 0 and not force_vex3:
        return bytearray([0xC5, 0xF8 ^ (r << 7) ^ (vvvv << 3) ^ lpp])
    else:
        return bytearray([0xC4, 0xE1 ^ (r << 7) ^ (x << 6) ^ (b << 5), 0x78 ^ (vvvv << 3) ^ lpp])


def vex3(escape, mmmmm, w____lpp, r, rm, vvvv=0):
    #                         3-byte VEX/XOP prefix
    #         +-----------------------------------+
    # Byte 0: | Bits 0-7: 0xC4 (VEX) / 0x8F (XOP) |
    #         +-----------------------------------+
    #
    #         +-----------+-----------+-----------+-----------------+
    # Byte 1: | Bit 7: ~R | Bit 6: ~X | Bit 5: ~B | Bits 0-4: mmmmm |
    #         +-----------+-----------+-----------+-----------------+
    #
    #         +----------+-----------------+----------+--------------+
    # Byte 2: | Bit 7: W | Bits 3-6: ~vvvv | Bit 2: L | Bits 0-1: pp |
    #         +----------+-----------------+----------+--------------+
    assert escape in {0xC4, 0x8F}, "escape must be a 3-byte VEX (0xC4) or XOP (0x8F) prefix"
    assert w____lpp & ~0b10000111 == 0, "VEX.W____Lpp is expected to have no bits set except 0, 1, 2 and 7"
    assert mmmmm & ~0b11111 == 0, "VEX.m-mmmm is expected to be a 5-bit mask"
    assert r & ~0b1 == 0, "VEX.R must be a single-bit mask"
    assert vvvv & ~0b1111 == 0, "VEX.vvvv must be a 4-bit mask"
    from peachpy.x86_64.operand import MemoryAddress
    assert isinstance(rm, MemoryAddress), \
        "rm is expected to be a memory address"
    b = 0
    x = 0
    if rm.base is not None:
        b = rm.base.hcode
    if rm.index is not None:
        x = rm.index.hcode
    return bytearray([escape, 0xE0 ^ (r << 7) ^ (x << 6) ^ (b << 5) ^ mmmmm, 0x78 ^ (vvvv << 3) ^ w____lpp])


def modrm_sib_disp(reg, rm, force_sib=False, min_disp=0):
    from peachpy.x86_64.operand import MemoryAddress
    from peachpy.x86_64.registers import rsp, rbp, r12, r13
    from peachpy.util import is_int, is_sint8, ilog2

    assert is_int(reg) and 0 <= reg <= 7, \
        "Constant reg value expected, got " + str(reg)
    assert isinstance(rm, MemoryAddress)

    # TODO: support global addresses, including rip-relative addresses
    assert rm.base is not None or rm.index is not None, \
        "Global addressing is not yet supported"

    #                    ModR/M byte
    # +----------------+---------------+--------------+
    # | Bits 6-7: mode | Bits 3-5: reg | Bits 0-2: rm |
    # +----------------+---------------+--------------+
    #
    #                         SIB byte
    # +-----------------+-----------------+----------------+
    # | Bits 6-7: scale | Bits 3-5: index | Bits 0-2: base |
    # +-----------------+-----------------+----------------+
    if not force_sib and rm.index is None and rm.base.lcode != 0b100:
        # No SIB byte
        if rm.displacement == 0 and rm.base != rbp and rm.base != r13 and min_disp <= 0:
            # ModRM.mode = 0 (no displacement)

            assert rm.base.lcode != 0b100, "rsp/r12 are not encodable as a base register (interpreted as SIB indicator)"
            assert rm.base.lcode != 0b101, "rbp/r13 is not encodable as a base register (interpreted as disp32 address)"
            return bytearray([(reg << 3) | rm.base.lcode])
        elif is_sint8(rm.displacement) and min_disp <= 1:
            # ModRM.mode = 1 (8-bit displacement)

            assert rm.base.lcode != 0b100, "rsp/r12 are not encodable as a base register (interpreted as SIB indicator)"
            return bytearray([0x40 | (reg << 3) | rm.base.lcode, rm.displacement & 0xFF])
        else:
            # ModRM.mode == 2 (32-bit displacement)

            assert rm.base.lcode != 0b100, "rsp/r12 are not encodable as a base register (interpreted as SIB indicator)"
            return bytearray([0x80 | (reg << 3) | rm.base.lcode,
                             rm.displacement & 0xFF, (rm.displacement >> 8) & 0xFF,
                             (rm.displacement >> 16) & 0xFF, (rm.displacement >> 24) & 0xFF])
    else:
        # All encodings below use ModRM.rm = 4 (0b100) to indicate the presence of SIB

        assert rsp != rm.index, "rsp is not encodable as an index register (interpreted as no index)"
        # Index = 4 (0b100) denotes no-index encoding
        index = 0x4 if rm.index is None else rm.index.lcode
        scale = 0 if rm.scale is None else ilog2(rm.scale)
        if rm.base is None:
            # SIB.base = 5 (0b101) and ModRM.mode = 0 indicates no-base encoding with disp32

            return bytearray([(reg << 3) | 0x4, (scale << 6) | (index << 3) | 0x5,
                             rm.displacement & 0xFF, (rm.displacement >> 8) & 0xFF,
                             (rm.displacement >> 16) & 0xFF, (rm.displacement >> 24) & 0xFF])
        else:
            if rm.displacement == 0 and rm.base.lcode != 0b101 and min_disp <= 0:
                # ModRM.mode == 0 (no displacement)

                assert rm.base.lcode != 0b101, \
                    "rbp/r13 is not encodable as a base register (interpreted as disp32 address)"
                return bytearray([(reg << 3) | 0x4, (scale << 6) | (index << 3) | rm.base.lcode])
            elif is_sint8(rm.displacement) and min_disp <= 1:
                # ModRM.mode == 1 (8-bit displacement)

                return bytearray([(reg << 3) | 0x44, (scale << 6) | (index << 3) | rm.base.lcode, rm.displacement & 0xFF])
            else:
                # ModRM.mode == 2 (32-bit displacement)

                return bytearray([(reg << 3) | 0x84, (scale << 6) | (index << 3) | rm.base.lcode,
                                 rm.displacement & 0xFF, (rm.displacement >> 8) & 0xFF,
                                 (rm.displacement >> 16) & 0xFF, (rm.displacement >> 24) & 0xFF])


def nop(length):
    assert 1 <= length <= 15
    # Note: the generated NOPs must be allowed by NaCl validator, see
    # https://src.chromium.org/viewvc/native_client/trunk/src/native_client/src/trusted/validator_ragel/instruction_definitions/general_purpose_instructions.def
    # https://src.chromium.org/viewvc/native_client/trunk/src/native_client/src/trusted/validator_ragel/instruction_definitions/nops.def
    return {
        1: bytearray([0x90]),
        2: bytearray([0x40, 0x90]),
        3: bytearray([0x0F, 0x1F, 0x00]),
        4: bytearray([0x0F, 0x1F, 0x40, 0x00]),
        5: bytearray([0x0F, 0x1F, 0x44, 0x00, 0x00]),
        6: bytearray([0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00]),
        7: bytearray([0x0F, 0x1F, 0x80, 0x00, 0x00, 0x00, 0x00]),
        8: bytearray([0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        9: bytearray([0x66, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        10: bytearray([0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        11: bytearray([0x66, 0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        12: bytearray([0x66, 0x66, 0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        13: bytearray([0x66, 0x66, 0x66, 0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        14: bytearray([0x66, 0x66, 0x66, 0x66, 0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]),
        15: bytearray([0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x2E, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00])
    }[length]


class Flags:
    AccumulatorOp0 = 0x01
    AccumulatorOp1 = 0x02
    Rel8Label = 0x04
    Rel32Label = 0x08
    ModRMSIBDisp = 0x10
    OptionalREX = 0x20
    VEX2 = 0x40


class Options:
    Disp8 = 0x01
    Disp32 = 0x02
    SIB = 0x04
    REX = 0x08
    VEX3 = 0x10