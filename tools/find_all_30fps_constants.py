import struct
from pathlib import Path

elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()
code_start = 0x4000
code_size = 0x7300a4

# Let's search for float constants around 30 FPS or frame step
# 30.0f = 0x41f00000
# 1/30.0f = 0x3d088889
# 0.5f = 0x3f000000
# 2.0f = 0x40000000

# Let's search where 1/30.0f or 30.0f is used in instructions:
# mulss / divss with 30.0 or 0.03333334
def search_imm32(val_bytes, name):
    matches = []
    idx = 0
    while True:
        pos = elf_data.find(val_bytes, idx)
        if pos == -1:
            break
        vaddr = pos - code_start if pos >= code_start and pos < code_start + code_size else None
        matches.append((pos, vaddr))
        idx = pos + 1
    print(f"Total {name} matches: {len(matches)}")
    for pos, vaddr in matches[:15]:
        if vaddr:
            print(f"  Code VirtAddr: {hex(vaddr)}, context: {elf_data[pos-8:pos+8].hex(' ')}")

search_imm32(bytes.fromhex("8988083d"), "1.0/30.0f (0x3d088889)")
search_imm32(bytes.fromhex("0000f041"), "30.0f (0x41f00000)")
