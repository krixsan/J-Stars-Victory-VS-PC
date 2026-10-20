import struct
from pathlib import Path

elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()
code_start = 0x4000
code_size = 0x7300a4

# Let's check functions between 0x41f690 and 0x421000
# which manipulate the timer structure allocated at 0x246302 (0x8214a8)
print("Scanning 0x41f690..0x422000 for reads of +4, +8, +0xc...")
# Instructions like:
# movss xmm0, [rdi + 8] / movss xmm0, [rax + 8] / movss xmm0, [rbx + 8]
# or flds
for pc in range(0x41f690 + code_start, 0x423000 + code_start):
    # vmovss xmm0, 8(%rax/%rdi/%rbx) or movss
    b = elf_data[pc:pc+8]
    # vmovss xmm?, 8(r?)
    # c5 f? 10 ?? 08
    if len(b) >= 5 and b[0] == 0xc5 and b[2] == 0x10 and b[4] == 0x08:
        vaddr = pc - code_start
        print(f"vmovss from +8 at VirtAddr {hex(vaddr)}: {b[:5].hex(' ')}")
    if len(b) >= 5 and b[0] == 0xc5 and b[2] == 0x10 and b[4] == 0x04:
        vaddr = pc - code_start
        print(f"vmovss from +4 at VirtAddr {hex(vaddr)}: {b[:5].hex(' ')}")
