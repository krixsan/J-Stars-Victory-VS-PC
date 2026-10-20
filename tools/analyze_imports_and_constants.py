import struct
import re
from pathlib import Path

here = Path(".")
data = (here / 'out/boot.bin').read_bytes()
size, entry, ns, nr, ni, caps = struct.unpack_from('<QQQQQQ', data, 8)
print(f"boot.bin header: size={hex(size)}, entry={hex(entry)}, sections={ns}, relocs={nr}, imports={ni}")

pos = 56 + ns * 24
names = [data[pos + i * 128:pos + (i + 1) * 128].split(b'\0')[0].decode(errors='replace') for i in range(ni)]
pos += ni * 128
symbols = dict(re.findall(r'\{"([^"]+)","([^"]+)"\}', (here / 'src/import_names.inc').read_text(encoding='utf-8', errors='replace')))

print("Searching names for Video or Flip or Rate:")
for i, n in enumerate(names):
    sym = symbols.get(n, "")
    for k in symbols:
        if k.startswith(n.split("#")[0]):
            sym = symbols[k]
            break
    if "Video" in sym or "Flip" in sym or "video" in sym.lower() or "CBiu" in n:
        print(f"Import {i}: NID='{n}', Symbol='{sym}'")

for i in range(nr):
    target, kind, value, addend = struct.unpack_from('<QQqq', data, pos + i * 32)
    if kind and value < len(names):
        nid = names[value]
        if "CBiu" in nid or "Video" in nid:
            print(f"Reloc at target={hex(target)}, kind={kind}, import_idx={value}, nid={nid}")
