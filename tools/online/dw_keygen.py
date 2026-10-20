#!/usr/bin/env python3
"""SacredFire online (dev only): generate the test RSA keypair used to sign
Demonware auth replies for the private server (docs/sacredfire/15-online.md).

The game embeds Demonware's RSA-2048 public key (294-byte SPKI, unique in the
image) and verifies the auth reply signature before reading any ticket. A
private server cannot forge that signature, so development uses an explicit
test mode: the runtime swaps the embedded key for OURS (same 294 bytes, so the
swap is in place) and this server signs with OUR private key. Official
servers, credentials and keys are never involved.

    python tools/online/dw_keygen.py [--out-dir out] [--force]

Writes <out-dir>/dw-test.key (PRIVATE: never commit, never share) and
<out-dir>/dw-test.spki.der (public, 294 bytes: BB_DW_TEST_KEY points here).
Requires openssl on PATH. Standard library only otherwise.
"""

import argparse
import hashlib
import os
import subprocess
import sys

SPKI_LEN = 294  # in-place swap requires exactly Demonware's SPKI length


def run(*args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode:
        sys.exit(f"dw_keygen: {' '.join(args)} failed:\n{r.stderr.decode()}")
    return r


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_out = os.path.normpath(os.path.join(here, "..", "..", "out"))
    args_parser = argparse.ArgumentParser(description=__doc__,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    args_parser.add_argument("--out-dir", default=default_out)
    args_parser.add_argument("--bits", type=int, default=2048)
    args_parser.add_argument("--force", action="store_true")
    args = args_parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    key = os.path.join(args.out_dir, "dw-test.key")
    spki = os.path.join(args.out_dir, "dw-test.spki.der")
    if not args.force and (os.path.exists(key) or os.path.exists(spki)):
        sys.exit("dw_keygen: key already exists (use --force to rotate; "
                 "rotating requires restarting game+server together)")
    run("openssl", "genrsa", "-out", key, str(args.bits))
    try:
        os.chmod(key, 0o600)
    except OSError:
        pass
    run("openssl", "rsa", "-in", key, "-pubout", "-outform", "DER", "-out", spki)
    raw = open(spki, "rb").read()
    if len(raw) != SPKI_LEN:
        os.remove(spki)
        sys.exit(f"dw_keygen: test SPKI is {len(raw)} bytes, need {SPKI_LEN} "
                 "(in-place swap impossible with these RSA parameters)")
    print(f"private: {key} (keep secret, never commit)")
    print(f"public:  {spki} ({len(raw)} bytes, sha1={hashlib.sha1(raw).hexdigest()})")
    print(f"export BB_DW_TEST_KEY={spki}")


if __name__ == "__main__":
    main()
