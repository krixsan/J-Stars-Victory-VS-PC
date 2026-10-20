import struct
from pathlib import Path

elf_path = Path("extracted_game/app0/eboot.elf")
elf_data = elf_path.read_bytes()

got_addr = 0x7e48a0
print(f"Searching eboot.elf ({len(elf_data)} bytes) for any references to {hex(got_addr)}...")

# 1. Search for absolute 32-bit or 64-bit
got_u32 = struct.pack('<I', got_addr)
got_u64 = struct.pack('<Q', got_addr)

idx = 0
while True:
    pos = elf_data.find(got_u32, idx)
    if pos == -1:
        break
    print(f"Found got_u32 at file offset {hex(pos)}")
    idx = pos + 1

idx = 0
while True:
    pos = elf_data.find(got_u64, idx)
    if pos == -1:
        break
    print(f"Found got_u64 at file offset {hex(pos)}")
    idx = pos + 1

# 2. Search for any RIP relative reference to 0x7e48a0
# In x86-64, rip-rel instructions have length 5..8 bytes.
# Target = instruction_start + insn_len + disp32 == got_addr
# So disp32 = got_addr - instruction_start - insn_len
for insn_len in range(5, 9):
    for pc in range(0, min(len(elf_data)-insn_len, 0x730000)):
        disp = got_addr - (pc + insn_len)
        disp_bytes = struct.pack('<i', disp)
        if elf_data[pc+insn_len-4:pc+insn_len] == disp_bytes:
            print(f"RIP-relative reference to GOT at pc={hex(pc)}, insn_len={insn_len}: {elf_data[pc:pc+insn_len].hex(' ')}")
