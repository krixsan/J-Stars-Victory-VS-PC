#!/usr/bin/env python3
"""Live check: signed /auth/ reply from discovery_server.py --sign-key.

    python tools/online/test_signed_server.py [--http 18081]
"""

import argparse
import base64
import json
import urllib.request
import urllib.error

AUTH_BODY = json.dumps({
    "auth_task": "46", "iv_seed": "1", "title_id": "5760",
    "identity": "356c4bc3", "extra_data": "{}",
}).encode()


def post(port, host, target):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{target}", data=AUTH_BODY, method="POST",
        headers={"Host": host, "X-SacredFire-Scheme": "https",
                 "Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=5)
        return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, default=18081)
    args = parser.parse_args()
    status, headers, body = post(args.http, "lavender-ps4-auth3.prod.demonware.net", "/auth/")
    assert status == 200, f"auth status {status}"
    signature = next((v for k, v in headers.items() if k.lower() == "x-signature"), None)
    assert signature, "missing X-Signature"
    reply = json.loads(body)
    assert reply["code"] == 700 and reply["auth_task"] == 46, reply
    assert len(base64.b64decode(reply["client_ticket"])) == 128, "ticket length"
    print(f"signed-server check: PASS (200, X-Signature {len(signature)} chars, code 700)")
    status, _, _ = post(args.http, "sdk:entitlement.np.community.playstation.net",
                        "/v1/users/me/entitlements")
    assert status == 404, f"non-auth status {status} (must stay unsigned)"
    print("signed-server check: PASS (non-auth still 404)")


if __name__ == "__main__":
    main()
