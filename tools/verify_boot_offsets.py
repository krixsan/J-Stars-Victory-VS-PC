import struct
from pathlib import Path

data = Path("out/boot-linked.bin").read_bytes()
# Look for pattern at 0x43d8e6 in eboot:
# 41 83 ff 03 75 07 be 02 00 00 00 eb 0d 31 f6 41 83 ff 02 75 05 be 01 00 00 00
pat1 = bytes.fromhex("41 83 ff 03 75 07 be 02 00 00 00 eb 0d 31 f6 41 83 ff 02 75 05 be 01 00 00 00")
idx1 = data.find(pat1)
print(f"Pattern 1 (flip rate check) found at file offset in boot-linked.bin: {hex(idx1)}")

# Look for pattern at 0x24630c in eboot:
# c7 40 04 00 00 f0 41 c7 40 08 89 88 08 3d c7 40 0c cd cc cc 3d
pat2 = bytes.fromhex("c7 40 04 00 00 f0 41 c7 40 08 89 88 08 3d c7 40 0c cd cc cc 3d")
idx2 = data.find(pat2)
print(f"Pattern 2 (FPS struct setup) found at file offset in boot-linked.bin: {hex(idx2)}")

# Let's find header offset
# In boot-linked.bin, if pat1 is at idx1, what is idx1 - 0x43d8e6?
print("Header size inferred from idx1:", hex(idx1 - 0x43d8e6))
print("Header size inferred from idx2:", hex(idx2 - 0x24630c))
