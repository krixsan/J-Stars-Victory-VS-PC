#!/usr/bin/env python3
"""
tools/unfself.py - PS4 Fake SELF to ELF Converter
Converts PS4 FPKG Signed ELF (SELF) files with magic 0x1D3D154F ('4F 15 3D 1D')
back into standard pure ELF64 executables ('7F 45 4C 46').
"""

import sys
import os
import struct
from binascii import hexlify as hx

SELF_MAGIC = b'\x4f\x15\x3d\x1d'
ELF_MAGIC = b'\x7f\x45\x4c\x46'

def is_self(data_or_file):
    if isinstance(data_or_file, bytes):
        return data_or_file[:4] == SELF_MAGIC
    pos = data_or_file.tell()
    magic = data_or_file.read(4)
    data_or_file.seek(pos)
    return magic == SELF_MAGIC

def is_elf(data_or_file):
    if isinstance(data_or_file, bytes):
        return data_or_file[:4] == ELF_MAGIC
    pos = data_or_file.tell()
    magic = data_or_file.read(4)
    data_or_file.seek(pos)
    return magic == ELF_MAGIC

def convert_self_to_elf(input_file, output_file):
    """
    Parses a PS4 SELF file and writes a clean standard ELF64 to output_file.
    """
    # 1. Read SELF Header
    FMT_SELF_HDR = '<4s4B'
    magic, version, mode, endian, attributes = struct.unpack(
        FMT_SELF_HDR, input_file.read(struct.calcsize(FMT_SELF_HDR))
    )
    if magic != SELF_MAGIC:
        raise ValueError(f"Invalid SELF magic: {magic.hex()}")

    EXTENDED_FMT = '<2B2x2HQ2H4x'
    content_type, key_type, header_size, meta_size, file_size, entry_count, flag = struct.unpack(
        EXTENDED_FMT, input_file.read(struct.calcsize(EXTENDED_FMT))
    )

    # 2. Read SELF Entries
    FMT_ENTRY = '<4Q'
    entries_payloads = []
    last_file_end = 0
    for i in range(entry_count):
        props, f_offset, f_size, m_size = struct.unpack(
            FMT_ENTRY, input_file.read(struct.calcsize(FMT_ENTRY))
        )
        cur_pos = input_file.tell()
        input_file.seek(f_offset)
        payload = input_file.read(f_size)
        entries_payloads.append((props, f_offset, f_size, m_size, payload))
        input_file.seek(cur_pos)
        end_pos = f_offset + f_size
        if end_pos > last_file_end:
            last_file_end = end_pos

    # SCE Version info
    cur_pos = input_file.tell()
    if last_file_end > 0:
        input_file.seek(last_file_end)
        sce_ver_data = input_file.read()
        entries_payloads.append((0, last_file_end, len(sce_ver_data), len(sce_ver_data), sce_ver_data))
    input_file.seek(cur_pos)

    # 3. Read & Write ELF Header
    ELF_HDR_FMT = '<4s5B6xB'
    e_ident = input_file.read(struct.calcsize(ELF_HDR_FMT))
    output_file.write(e_ident)

    ELF_EX_FMT = '<2HI3QI6H'
    (
        e_type, e_machine, e_version, e_entry,
        e_phoff, e_shoff, e_flags, e_ehsize,
        e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx
    ) = struct.unpack(ELF_EX_FMT, input_file.read(struct.calcsize(ELF_EX_FMT)))

    output_file.write(struct.pack(
        ELF_EX_FMT,
        e_type, e_machine, e_version, e_entry,
        e_phoff, e_shoff, e_flags, e_ehsize,
        e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx
    ))

    # 4. Read ELF Program Headers & Write Segments
    PHDR_FMT = '<2I6Q'
    phdrs = []
    for p in range(e_phnum):
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack(
            PHDR_FMT, input_file.read(struct.calcsize(PHDR_FMT))
        )
        phdrs.append({
            'type': p_type, 'flags': p_flags, 'offset': p_offset,
            'vaddr': p_vaddr, 'paddr': p_paddr, 'filesz': p_filesz,
            'memsz': p_memsz, 'align': p_align
        })
        output_file.write(struct.pack(
            PHDR_FMT, p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align
        ))

    # Write segment contents to ELF offsets
    remaining_entries = list(entries_payloads)
    saved_pos = output_file.tell()
    for ph in phdrs:
        p_offset = ph['offset']
        p_filesz = ph['filesz']
        if p_filesz == 0:
            continue
        # Find matching entry
        matched_entry = None
        for item in remaining_entries:
            _, _, _, _, payload = item
            if len(payload) == p_filesz:
                matched_entry = item
                break
        if matched_entry:
            output_file.seek(p_offset)
            output_file.write(matched_entry[4])
            remaining_entries.remove(matched_entry)

    output_file.seek(saved_pos)
    print(f"Successfully converted SELF ({file_size} bytes) -> pure ELF64.")

def unfself(in_path, out_path=None):
    if out_path is None:
        if in_path.endswith('.bin') or in_path.endswith('.prx') or in_path.endswith('.self'):
            base = os.path.splitext(in_path)[0]
            out_path = base + '.elf'
        else:
            out_path = in_path + '.elf'

    is_inplace = os.path.abspath(in_path) == os.path.abspath(out_path)
    actual_out = out_path + ".tmp" if is_inplace else out_path

    with open(in_path, 'rb') as f_in:
        magic = f_in.read(4)
        f_in.seek(0)
        if magic == ELF_MAGIC:
            print(f"[unfself] {in_path} is already a pure ELF file!")
            if not is_inplace:
                import shutil
                shutil.copy2(in_path, out_path)
            return out_path
        elif magic == SELF_MAGIC:
            print(f"[unfself] Converting SELF -> ELF: {in_path} -> {out_path}")
            with open(actual_out, 'wb') as f_out:
                convert_self_to_elf(f_in, f_out)
            if is_inplace:
                import shutil
                shutil.move(actual_out, out_path)
            return out_path
        else:
            raise ValueError(f"Unknown file format magic: {magic.hex()}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tools/unfself.py <input.bin|prx|self> [output.elf]")
        sys.exit(1)
    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    unfself(in_file, out_file)
