import struct
from pathlib import Path

elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()
code_start = 0x4000
code_size = 0x7300a4
target_vaddr = 0x8214a8

# Let's inspect all places in code that load 0x8214a8 and see what they do with it
# We found 8 references in find_timer_refs:
# 0x246301 (the one we patched)
# Let's look at the other ones!
refs = [0x244ae7, 0x246301, 0x2464bb, 0x246fbb, 0x246ff8, 0x2487d5, 0x2488ee, 0x24a31a]
for r in refs:
    print(f"\n--- Disassembling around ref {hex(r)} ---")
    start = max(code_start, r - 32)
    end = min(len(elf_data), r + 48)
    # print file offset
    file_off = r + code_start
    print(f"VirtAddr {hex(r)} (file offset {hex(file_off)})")
