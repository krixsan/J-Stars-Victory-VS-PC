import struct
from pathlib import Path

elf_path = Path("extracted_game/app0/eboot.elf")
elf_data = elf_path.read_bytes()

# Segment 0: file offset 0x4000 corresponds to VirtAddr 0x0, size 0x7300a4
# Segment 1: file offset 0x738000 corresponds to VirtAddr 0x734000
got_vaddr = 0x7e48a0
print(f"Target GOT VirtAddr: {hex(got_vaddr)}")

# Search segment 0 (code) for rip-relative references to got_vaddr
code_offset_start = 0x4000
code_size = 0x7300a4

for insn_len in range(5, 9):
    for offset in range(code_offset_start, code_offset_start + code_size - insn_len):
        vaddr = offset - code_offset_start
        disp = got_vaddr - (vaddr + insn_len)
        disp_bytes = struct.pack('<i', disp)
        if elf_data[offset + insn_len - 4 : offset + insn_len] == disp_bytes:
            insn_bytes = elf_data[offset : offset + insn_len]
            print(f"Found GOT reference at VirtAddr {hex(vaddr)} (file offset {hex(offset)}), len {insn_len}: {insn_bytes.hex(' ')}")
            # Print context: 32 bytes before and after
            ctx = elf_data[max(0, offset-32) : min(len(elf_data), offset+insn_len+32)]
            print(f"  Context: {ctx.hex(' ')}")
