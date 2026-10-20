import struct
import os

boot_path = "out/boot-linked.bin"
if not os.path.exists(boot_path):
    boot_path = "out/boot.bin"

with open(boot_path, "rb") as f:
    data = f.read()

print("Loaded binary length:", len(data))

# 1. Check PLT stub at 0x539b80
if len(data) > 0x539b80 + 16:
    print("Bytes at 0x539b80:", data[0x539b80:0x539b80+16].hex(' '))

# 2. Search for calls to 0x539b80
plt_target = 0x539b80
calls = []
for pc in range(0, min(len(data)-5, 0x700000)):
    if data[pc] == 0xe8:
        rel32 = struct.unpack('<i', data[pc+1:pc+5])[0]
        if pc + 5 + rel32 == plt_target:
            calls.append(pc)

print("Calls to PLT 0x539b80:", [hex(c) for c in calls])

for c in calls:
    start = max(0, c - 24)
    end = min(len(data), c + 24)
    print("Context around", hex(c), ":", data[start:end].hex(' '))

# 3. Check GOT refs
got_addr = 0x7e48a0
got_refs = []
for pc in range(0, min(len(data)-7, 0x700000)):
    for insn_len in [6, 7]:
        disp = got_addr - (pc + insn_len)
        disp_bytes = struct.pack('<i', disp)
        if data[pc+insn_len-4:pc+insn_len] == disp_bytes:
            got_refs.append((hex(pc), data[pc:pc+insn_len].hex(' ')))

print("References to GOT 0x7e48a0:", got_refs)

# 4. Search for float 30 FPS constants:
# 1/30 = 0.03333333432674408 -> float32 hex is 0x3d088889 or 0x3d088888
# 30.0f = 0x41f00000
# 60.0f = 0x42700000
# double 1/30 = 0x3fa1111111111111
float_1_30 = struct.pack('<f', 1.0/30.0)
float_1_30_alt = bytes.fromhex("8988083d")
float_1_30_alt2 = bytes.fromhex("8888083d")

def find_all(needle, name):
    pos = 0
    matches = []
    while True:
        idx = data.find(needle, pos)
        if idx == -1:
            break
        matches.append(idx)
        pos = idx + 1
    print(f"Matches for {name} ({len(matches)}):", [hex(m) for m in matches[:20]])
    return matches

find_all(float_1_30, "float 1.0/30.0 (struct.pack)")
find_all(float_1_30_alt, "float 1.0/30.0 (0x3d088889)")
find_all(float_1_30_alt2, "float 1.0/30.0 (0x3d088888)")
find_all(struct.pack('<d', 1.0/30.0), "double 1.0/30.0")
