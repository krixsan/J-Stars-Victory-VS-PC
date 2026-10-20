import struct
from pathlib import Path

# Let's inspect each match in extracted_game/app0/eboot.elf
elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()

# 1.0/30.0f is 0x3d088889
needle = bytes.fromhex("8988083d")
matches = []
pos = 0
while True:
    idx = elf_data.find(needle, pos)
    if idx == -1:
        break
    matches.append(idx)
    pos = idx + 1

print(f"Matches in eboot.elf: {[hex(m) for m in matches]}")

for m in matches:
    # Check if this offset is in code (offset 0x4000 .. 0x7340a4)
    vaddr = m - 0x4000 if m >= 0x4000 and m < 0x7340a4 else None
    print(f"\n--- Match at offset {hex(m)} (VirtAddr: {hex(vaddr) if vaddr else 'Non-code/data'}) ---")
    start = max(0, m - 16)
    end = min(len(elf_data), m + 20)
    print("Bytes:", elf_data[start:end].hex(' '))
