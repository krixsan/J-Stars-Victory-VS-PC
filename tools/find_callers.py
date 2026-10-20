import struct
from pathlib import Path

elf_path = Path("extracted_game/app0/eboot.elf")
elf_data = elf_path.read_bytes()

code_offset_start = 0x4000
code_size = 0x7300a4
target_vaddr = 0x539b80
print(f"Finding callers to VirtAddr {hex(target_vaddr)} (PLT sceVideoOutSetFlipRate)...")

callers = []
for offset in range(code_offset_start, code_offset_start + code_size - 5):
    if elf_data[offset] == 0xe8:
        disp = struct.unpack('<i', elf_data[offset+1:offset+5])[0]
        vaddr = offset - code_offset_start
        call_target = vaddr + 5 + disp
        if call_target == target_vaddr:
            callers.append((vaddr, offset))
            print(f"Call at VirtAddr {hex(vaddr)} (file offset {hex(offset)})")
            # Print 32 bytes before the call to see arguments (rdi = handle, rsi = rate)
            pre_start = max(code_offset_start, offset - 32)
            print("  Preceding code:", elf_data[pre_start:offset+5].hex(' '))

print(f"Total calls found: {len(callers)}")
