#!/usr/bin/env python3
"""
tools/extract_pkg.py - PS4 Fake PKG (FPKG) Extractor & PFS Parser
Extracts eboot.bin, sce_module/libc.prx, libSceFios2.prx, sce_sys/param.sfo,
and all CPK data archives from J-Stars Victory VS+ PS4 PKG into ./extracted_game/app0/
"""

import os
import sys
import glob
import struct
import hashlib
from pathlib import Path

# Import mkpfs for PFS handling
import mkpfs.pfs
from mkpfs import consts

# Import unfself
try:
    from tools.unfself import unfself, is_self, is_elf
except ImportError:
    from unfself import unfself, is_self, is_elf

# Monkey-patch mkpfs._parse_pfsc_header to support unk8 in (0, 2, 6)
orig_parse_pfsc = mkpfs.pfs._parse_pfsc_header
def patched_parse_pfsc(head):
    magic, unk4, unk8, lbs, lbs2, offsets_off, data_off, logical = struct.unpack_from('<iiiiqqQq', head, 0)
    block_count = logical // lbs
    return (lbs, block_count, offsets_off, data_off, logical)
mkpfs.pfs._parse_pfsc_header = patched_parse_pfsc


class SubStream:
    """Wraps an open file handle at an absolute offset."""
    def __init__(self, fh, base_offset):
        self.fh = fh
        self.base = base_offset

    def seek(self, offset, whence=0):
        if whence == 0:
            return self.fh.seek(self.base + offset) - self.base
        elif whence == 1:
            return self.fh.seek(offset, 1) - self.base
        elif whence == 2:
            self.fh.seek(0, 2)
            cur = self.fh.tell()
            return self.fh.seek(cur + offset) - self.base

    def tell(self):
        return self.fh.tell() - self.base

    def read(self, n=-1):
        return self.fh.read(n)


def parse_byte_array(text, name):
    idx = text.find(name)
    if idx == -1: return None
    start = text.find('{', idx)
    end = text.find('}', start)
    sub = text[start+1:end]
    bytes_list = []
    for part in sub.split(','):
        part = part.strip()
        if part.startswith('0x') or part.startswith('0X'):
            bytes_list.append(int(part, 16))
    return bytes(bytes_list)


def load_keysets():
    """Loads RSA keysets from keys_cs.txt or embedded definitions."""
    keys_file = Path(__file__).resolve().parent.parent / "keys_cs.txt"
    if not keys_file.exists():
        keys_file = Path("keys_cs.txt")
    with open(keys_file, "r", encoding="utf-8") as f:
        cs = f.read()

    def get_keyset(block_name):
        idx = cs.find(block_name)
        sub = cs[idx:idx+15000]
        mod = parse_byte_array(sub, 'Modulus')
        e = parse_byte_array(sub, 'PublicExponent')
        d = parse_byte_array(sub, 'PrivateExponent')
        return {
            'n': int.from_bytes(mod, 'big'),
            'e': int.from_bytes(e, 'big'),
            'd': int.from_bytes(d, 'big'),
        }

    return get_keyset('PkgDerivedKey3Keyset'), get_keyset('FakeKeyset')


def derive_ekpfs(pkg_file_path, k_dk3, k_fake):
    """Derives the 32-byte EKPFS key from an FPKG container."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    with open(pkg_file_path, "rb") as f:
        f.seek(0x10)
        entry_count, sc_entry_count, entry_count_2, table_offset, data_size = struct.unpack('>IHHI I', f.read(16))
        f.seek(table_offset)
        entries = {}
        for _ in range(entry_count):
            raw_meta = f.read(32)
            eid, name_off, flags1, flags2, offset, size = struct.unpack('>IIIIII', raw_meta[:24])
            entries[eid] = (raw_meta, offset, size)

        # Entry 0x10: ENTRY_KEYS
        meta_0x10, off_0x10, sz_0x10 = entries[0x10]
        f.seek(off_0x10)
        seed_digest = f.read(32)
        digests = [f.read(32) for _ in range(7)]
        keys = [f.read(256) for _ in range(7)]
        key3_enc = keys[3]

        # Entry 0x20: IMAGE_KEY
        meta_0x20, off_0x20, sz_0x20 = entries[0x20]
        f.seek(off_0x20)
        image_key_data = f.read(sz_0x20)

    # Decrypt key3 with PkgDerivedKey3Keyset
    c = int.from_bytes(key3_enc, 'big')
    m = pow(c, k_dk3['d'], k_dk3['n'])
    m_bytes = m.to_bytes(256, 'big')
    idx = m_bytes.find(b'\x00', 2)
    dk3 = m_bytes[idx+1:]

    # iv_key = SHA256(meta_0x20 + dk3)
    iv_key = hashlib.sha256(meta_0x20 + dk3).digest()
    iv = iv_key[:16]
    key = iv_key[16:32]

    # AES-128-CBC decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    dec = cipher.decryptor()
    image_key_dec = dec.update(image_key_data) + dec.finalize()

    # RSA Decrypt with FakeKeyset
    c2 = int.from_bytes(image_key_dec, 'big')
    m2 = pow(c2, k_fake['d'], k_fake['n'])
    m2_bytes = m2.to_bytes(256, 'big')
    idx2 = m2_bytes.find(b'\x00', 2)
    ekpfs = m2_bytes[idx2+1:]

    return ekpfs, entries


def extract_pkg(pkg_path, output_dir, extract_data_files=True):
    """
    Extracts all game files from a PS4 FPKG to output_dir.
    """
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sce_sys").mkdir(parents=True, exist_ok=True)
    (output_dir / "sce_module").mkdir(parents=True, exist_ok=True)

    print(f"\n[PKG Extractor] Opening {pkg_path}...")
    k_dk3, k_fake = load_keysets()
    ekpfs, entries = derive_ekpfs(pkg_path, k_dk3, k_fake)
    print(f"[PKG Extractor] Derived EKPFS: {ekpfs.hex()}")

    # 1. Extract outer PKG entries: param.sfo (0x1000), icon0.png (0x1200), etc.
    with open(pkg_path, "rb") as f:
        # Check param.sfo
        if 0x1000 in entries:
            _, sfo_off, sfo_sz = entries[0x1000]
            f.seek(sfo_off)
            sfo_data = f.read(sfo_sz)
            sfo_out = output_dir / "sce_sys" / "param.sfo"
            with open(sfo_out, "wb") as out_f:
                out_f.write(sfo_data)
            print(f"[PKG Extractor] Extracted sce_sys/param.sfo ({sfo_sz} bytes)")

        # Outer icons/pics if present
        for eid, name in [(0x1200, "icon0.png"), (0x1220, "pic0.png"), (0x1006, "pic1.png")]:
            if eid in entries:
                _, off, sz = entries[eid]
                f.seek(off)
                data = f.read(sz)
                with open(output_dir / "sce_sys" / name, "wb") as out_f:
                    out_f.write(data)

    # 2. Extract inner PFS image
    with open(pkg_path, "rb") as f:
        sub = SubStream(f, 0xb00000)
        hdr = mkpfs.pfs.parse_image_header(sub)
        inodes = mkpfs.pfs.parse_image_inodes(sub, hdr, ekpfs=ekpfs)
        payload_inode = inodes[3]
        view = mkpfs.pfs._LogicalFileView(sub, hdr, payload_inode, ekpfs=ekpfs)

        view.seek(0)
        inner_hdr = mkpfs.pfs.parse_image_header(view)
        inner_inodes = mkpfs.pfs.parse_image_inodes(view, inner_hdr)

        # Build directory tree mapping: inode_num -> dir_path
        # Inode 2 is uroot (root)
        dir_map = {2: output_dir}

        # First pass: map directories
        def map_directories():
            changed = True
            while changed:
                changed = False
                for i, ino in enumerate(inner_inodes):
                    if (ino.mode & 0o40000) and i in dir_map:
                        payload = mkpfs.pfs.read_image_inode_payload(view, inner_hdr, ino)
                        dirents, _ = mkpfs.pfs.parse_image_dirents(payload)
                        parent_path = dir_map[i]
                        for d in dirents:
                            if d.name in (".", ".."):
                                continue
                            target_ino = inner_inodes[d.inode_number]
                            if (target_ino.mode & 0o40000) and (d.inode_number not in dir_map):
                                child_path = parent_path / d.name
                                child_path.mkdir(parents=True, exist_ok=True)
                                dir_map[d.inode_number] = child_path
                                changed = True

        map_directories()

        # Second pass: extract files
        # Collect all files to extract
        files_to_extract = []
        for i, ino in enumerate(inner_inodes):
            if (ino.mode & 0o40000) and i in dir_map:
                payload = mkpfs.pfs.read_image_inode_payload(view, inner_hdr, ino)
                dirents, _ = mkpfs.pfs.parse_image_dirents(payload)
                parent_path = dir_map[i]
                for d in dirents:
                    if d.name in (".", ".."):
                        continue
                    target_ino = inner_inodes[d.inode_number]
                    if not (target_ino.mode & 0o40000):
                        file_dest = parent_path / d.name
                        files_to_extract.append((d.name, target_ino, file_dest))

        # Sort so that executables/binaries come first
        def file_priority(item):
            name, ino, dest = item
            if name == "eboot.bin": return 0
            if name.endswith(".prx") or name.endswith(".sprx"): return 1
            if name.endswith(".sfo") or name.endswith(".plt") or name == "keystone": return 2
            return 10

        files_to_extract.sort(key=file_priority)

        print(f"\n[PKG Extractor] Total files to extract from PFS: {len(files_to_extract)}")
        for name, target_ino, file_dest in files_to_extract:
            is_large = target_ino.size > 50 * 1024 * 1024
            if is_large and not extract_data_files:
                print(f"[PKG Extractor] Skipping large data file: {name} ({target_ino.size / (1024*1024):.1f} MB)")
                continue

            file_dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"[PKG Extractor] Extracting {file_dest.relative_to(output_dir)} ({target_ino.size} bytes)...")
            payload = mkpfs.pfs.read_image_inode_payload(view, inner_hdr, target_ino)
            with open(file_dest, "wb") as out_f:
                out_f.write(payload)

    print("\n[PKG Extractor] Extraction complete!")

    # 3. Validate & un-fself binaries
    binaries = [
        output_dir / "eboot.bin",
        output_dir / "sce_module" / "libc.prx",
        output_dir / "sce_module" / "libSceFios2.prx",
    ]

    print("\n[PKG Extractor] Validating binary headers...")
    for bin_path in binaries:
        if not bin_path.exists():
            print(f"[WARNING] Expected binary not found: {bin_path}")
            continue
        with open(bin_path, "rb") as bf:
            magic = bf.read(4)

        if magic == b'\x7f\x45\x4c\x46':
            print(f"  [ELF VALID] {bin_path.name} is already a pure ELF64!")
        elif magic == b'\x4f\x15\x3d\x1d':
            print(f"  [SELF DETECTED] {bin_path.name} is a Signed ELF (FPKG SELF). Un-fselfing...")
            elf_out = bin_path.with_suffix(".elf")
            unfself(str(bin_path), str(elf_out))
            # Also overwrite original with pure ELF so loader can load it directly
            unfself(str(bin_path), str(bin_path))
            print(f"  [SUCCESS] {bin_path.name} converted to valid ELF64!")
        else:
            print(f"  [UNKNOWN] {bin_path.name} has unexpected magic: {magic.hex()}")

    return output_dir


def main():
    workspace = Path(".").resolve()
    # Search for pkg
    pkg_files = list(workspace.glob("*.pkg")) + list(workspace.glob("game_dump/*.pkg"))
    if not pkg_files:
        print("[ERROR] No .pkg files found in workspace or game_dump/!")
        sys.exit(1)

    target_pkg = None
    for p in pkg_files:
        if "CUSA01593" in p.name and "Update" not in p.name:
            target_pkg = p
            break
    if not target_pkg:
        target_pkg = pkg_files[0]

    dest_dir = workspace / "extracted_game" / "app0"
    extract_pkg(str(target_pkg), str(dest_dir), extract_data_files=True)


if __name__ == "__main__":
    main()
