import struct
from pathlib import Path

elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()
code_offset_start = 0x4000
code_size = 0x7300a4
target_vaddr = 0x585bc8

print(f"Finding references to VirtAddr {hex(target_vaddr)} in code...")
for insn_len in range(5, 9):
    for offset in range(code_offset_start, code_offset_start + code_size - insn_len):
        vaddr = offset - code_offset_start
        disp = target_vaddr - (vaddr + insn_len)
        disp_bytes = struct.pack('<i', disp)
        if elf_data[offset + insn_len - 4 : offset + insn_len] == disp_bytes:
            print(f"Ref at VirtAddr {hex(vaddr)} (file offset {hex(offset)}): {elf_data[offset:offset+insn_len].hex(' ')}")
