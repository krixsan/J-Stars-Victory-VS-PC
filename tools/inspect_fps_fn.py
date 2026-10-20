import struct
from pathlib import Path

elf_data = Path("extracted_game/app0/eboot.elf").read_bytes()
code_start = 0x4000
code_size = 0x7300a4

# Let's inspect the function at 0x24630c in eboot.elf
# VirtAddr 0x24630c -> file offset 0x24a30c
start = 0x24a200
end = 0x24a400
print("Bytes at 0x24630c function:")

# Let's use llvm-objdump around 0x24630c
