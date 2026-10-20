#!/usr/bin/env python3
"""Self-test for auth_dev.py (dev only): reply shape + RSA/SHA-256 round-trip.

    python tools/online/test_auth_dev.py [--key out/dw-test.key]

Needs openssl on PATH. Fails loudly on any mismatch the client would reject
(status/keys/types/ticket lengths/magic/signature).
"""

import argparse
import base64
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auth_dev


def check(condition, message):
    if not condition:
        sys.exit(f"FAIL: {message}")
    print(f"ok: {message}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", default=os.path.join(HERE, "..", "..", "out", "dw-test.key"))
    args = parser.parse_args()

    body = auth_dev.build_auth_reply(46)
    reply = json.loads(body.decode("utf-8"))
    check(set(reply) == {"auth_task", "code", "iv_seed", "client_id", "account_type",
                         "client_ticket", "server_ticket", "identity"},
          f"reply keys {sorted(reply)}")
    check(reply["auth_task"] == 46 and isinstance(reply["auth_task"], int), "auth_task numeric 46")
    check(reply["code"] == 700 and isinstance(reply["code"], int), "code numeric 700")
    check(len(reply["client_id"]) <= 64 and len(reply["account_type"]) <= 10, "string length caps")
    client_ticket = base64.b64decode(reply["client_ticket"])
    server_ticket = base64.b64decode(reply["server_ticket"])
    check(len(client_ticket) == 128 and len(server_ticket) == 128, "tickets decode to 128 bytes")
    check(struct.unpack_from("<I", client_ticket)[0] == auth_dev.TICKET_MAGIC, "ticket magic DEADBDEF")
    check(b'"auth_task":46' in body and b'"code":700' in body, "numbers unquoted in JSON")
    check(b'"iv_seed":3139301806' in auth_dev.build_auth_reply(7, 3139301806), "iv_seed echoed numeric")
    check(auth_dev.request_iv_seed(b'{"iv_seed":"3139301806"}') == 3139301806, "iv_seed parsed from request")
    marked = auth_dev.build_auth_reply(46, 0, ticket_markers=True)
    decoded = json.loads(marked.decode("utf-8"))
    client_raw = base64.b64decode(decoded["client_ticket"])
    server_raw = base64.b64decode(decoded["server_ticket"])
    check(client_raw[4:12] == b"CLI04___" and server_raw[4:12] == b"SRV04___",
          "position markers in tickets")

    signature = auth_dev.sign_body(args.key, body)
    pub = subprocess.run(["openssl", "rsa", "-in", args.key, "-pubout"],
                         capture_output=True)
    check(pub.returncode == 0, "openssl reads test key")
    sig_raw = base64.b64decode(signature)
    check(len(sig_raw) == 256, f"signature is 2048-bit ({len(sig_raw)} bytes)")
    with open(os.path.join(HERE, ".selftest-body.bin"), "wb") as stream:
        stream.write(body)
    with open(os.path.join(HERE, ".selftest-sig.bin"), "wb") as stream:
        stream.write(sig_raw)
    with open(os.path.join(HERE, ".selftest-pub.pem"), "wb") as stream:
        stream.write(pub.stdout)
    verify = subprocess.run(["openssl", "dgst", "-sha256", "-verify",
                             os.path.join(HERE, ".selftest-pub.pem"), "-signature",
                             os.path.join(HERE, ".selftest-sig.bin"),
                             os.path.join(HERE, ".selftest-body.bin")], capture_output=True)
    check(verify.returncode == 0, f"openssl verifies signature ({verify.stdout.decode().strip()})")
    for name in (".selftest-body.bin", ".selftest-sig.bin", ".selftest-pub.pem"):
        os.remove(os.path.join(HERE, name))
    print("auth-dev self-test: PASS")


if __name__ == "__main__":
    main()
