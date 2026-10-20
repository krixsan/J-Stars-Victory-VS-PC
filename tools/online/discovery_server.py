#!/usr/bin/env python3
"""SacredFire online, step 3: a private "discovery" server that only listens and writes down
what the game sends (docs/sacredfire/15-online.md).

The port answers every host name it resolves with BB_ONLINE_SERVER's address, sends HTTP and
HTTPS as plain HTTP to BB_ONLINE_HTTP_PORT, and refuses every other destination. Run this on the
same PC (BB_ONLINE_SERVER=127.0.0.1) to see which services, ports and messages the game uses:

    python tools/online/discovery_server.py
    python tools/online/discovery_server.py --tcp 3074-3080,443 --udp 3074 --http 8080

Every connection, datagram and HTTP request goes to the console and to online-discovery.log
(hex and text). HTTP requests are answered with --http-status (404 by default, empty body);
TCP and UDP traffic is only read, never answered. Standard library only.

M4: HTTP captures are also saved raw under --save-dir (one .bin body + one .meta.json per
request) so a run is reproducible and can feed tests. Console output redacts PSN ID tokens
and ticket-like values (length shown, prefix only); the full bytes stay in the local file.
Nothing is ever sent to official servers; the reply stays an empty --http-status so the
client's transport-vs-protocol-vs-auth decision can be observed without faking a login.
"""

import argparse
import asyncio
import datetime
import hashlib
import itertools
import json
import os
import re
import sys

LOG = None
SEQ = itertools.count(1)
SAVE_DIR = ""


def log(line):
    stamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    text = f"{stamp} {line}"
    print(text, flush=True)
    if LOG:
        LOG.write(text + "\n")
        LOG.flush()


def dump(data, limit=4096):
    """Hex and printable text, 16 bytes a line."""
    lines = []
    shown = data[:limit]
    for offset in range(0, len(shown), 16):
        chunk = shown[offset:offset + 16]
        hexpart = " ".join(f"{b:02x}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"    {offset:06x}  {hexpart:<47}  {text}")
    if len(data) > limit:
        lines.append(f"    ... {len(data) - limit} more bytes")
    return "\n".join(lines)


def ports(text):
    """'3074-3080,443' -> [3074, ..., 3080, 443]."""
    result = []
    for part in filter(None, (p.strip() for p in text.split(","))):
        if "-" in part:
            first, last = part.split("-", 1)
            result.extend(range(int(first), int(last) + 1))
        else:
            result.append(int(part))
    return result


def redact(value, keep=16):
    """Prefix + length + sha1 for token-like values (never full plaintext on console)."""
    if not isinstance(value, str):
        value = str(value)
    if len(value) <= keep + 8:
        return value
    digest = hashlib.sha1(value.encode("utf-8", "replace")).hexdigest()[:12]
    return f"{value[:keep]}...<len={len(value)} sha1={digest}>"


def safe_name(text, limit=64):
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text or "")
    return text[:limit].strip("_") or "root"


def summarize_auth(body):
    """Nested Demonware auth JSON -> short console lines (keys + redacted values)."""
    try:
        outer = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        return [f"auth body is not UTF-8 JSON ({error}); see hex dump and .bin file"]
    lines = []
    for key in ("auth_task", "title_id", "iv_seed", "identity"):
        if key in outer:
            value = outer[key]
            shown = redact(value) if key in ("iv_seed", "identity") else value
            lines.append(f"auth.{key} = {shown!r}")
    extra = outer.get("extra_data")
    if isinstance(extra, str):
        lines.append(f"auth.extra_data = JSON string ({len(extra)} chars)")
        try:
            inner = json.loads(extra)
        except ValueError:
            lines.append(f"auth.extra_data raw = {redact(extra, 48)!r}")
            return lines
        for key in ("version", "extended_data"):
            if key in inner:
                lines.append(f"auth.extra_data.{key} = {inner[key]!r}")
        token = inner.get("token")
        if isinstance(token, str):
            try:
                token_json = json.loads(token)
            except ValueError:
                lines.append(f"auth.extra_data.token raw = {redact(token, 24)!r}")
            else:
                lines.append(f"auth.extra_data.token.scope = {token_json.get('scope')!r}")
                if "id_token" in token_json:
                    lines.append(f"auth.extra_data.token.id_token = {redact(token_json['id_token'])!r}")
        elif token is not None:
            lines.append(f"auth.extra_data.token = {type(token).__name__}")
    elif extra is not None:
        lines.append(f"auth.extra_data = {type(extra).__name__}")
    unknown = sorted(set(outer) - {"auth_task", "title_id", "iv_seed", "identity", "extra_data"})
    if unknown:
        lines.append(f"auth.unknown_keys = {unknown!r}")
    return lines or ["auth body parsed but has none of the expected keys"]


def classify(scheme, host, path):
    """Transport vs PSN vs Demonware stage, from addressing only (no guessing)."""
    host = (host or "").lower()
    path = path or "/"
    if "demonware.net" in host:
        if "auth" in host and path.startswith("/auth/"):
            return "demonware-auth"
        if "lobby" in host:
            return "demonware-lobby"
        if host.startswith("stun."):
            return "demonware-stun(expected over UDP, not HTTP)"
        return "demonware-other"
    if "playstation.net" in host:
        return "psn-webapi"
    return "other-http"


class Tcp:
    def __init__(self, port, hold_seconds=0.0, echo_lobby=False, lobby_84=False, lobby_81=False,
                 lobby_u32=210):
        self.port = port
        self.hold_seconds = hold_seconds
        self.echo_lobby = echo_lobby and port == 3074
        self.lobby_84 = lobby_84 and port == 3074
        self.lobby_81 = lobby_81 and port == 3074
        self.lobby_u32 = lobby_u32

    async def handle(self, reader, writer):
        peer = writer.get_extra_info("peername")
        log(f"TCP {self.port}: connection from {peer[0]}:{peer[1]}")
        total = 0
        chunks = 0
        probed = False
        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(65536),
                                                  self.hold_seconds or None)
                except asyncio.TimeoutError:
                    log(f"TCP {self.port}: hold expired after {self.hold_seconds}s "
                        f"({total} bytes in {chunks} chunks)")
                    break
                if not data:
                    break
                total += len(data)
                chunks += 1
                log(f"TCP {self.port}: chunk #{chunks}, {len(data)} bytes\n{dump(data)}")
                if not probed:
                    probed = True
                    if self.lobby_81:
                        import os
                        import struct
                        reply = (struct.pack("<I", 22) + bytes((0x81,)) +
                                 struct.pack("<I", self.lobby_u32) + os.urandom(17))
                        log(f"TCP {self.port}: PROBE 0x81 greeting "
                            f"({len(reply)} bytes, not a confirmed reply)")
                        writer.write(reply)
                        await writer.drain()
                    elif self.lobby_84:
                        import struct
                        reply = struct.pack("<I", 6) + bytes((0x84, 0, 0, 0, 0, 0))
                        log(f"TCP {self.port}: PROBE 0x84 challenge "
                            f"({len(reply)} bytes, not a confirmed reply)")
                        writer.write(reply)
                        await writer.drain()
                    elif self.echo_lobby:
                        log(f"TCP {self.port}: PROBE echoing {len(data)} bytes back "
                            f"(not a valid reply, only framing test)")
                        writer.write(data)
                        await writer.drain()
        except (ConnectionError, OSError) as error:
            log(f"TCP {self.port}: {error}")
        log(f"TCP {self.port}: closed after {total} bytes in {chunks} chunks")
        writer.close()


class Udp(asyncio.DatagramProtocol):
    def __init__(self, port):
        self.port = port

    def datagram_received(self, data, addr):
        log(f"UDP {self.port}: {len(data)} bytes from {addr[0]}:{addr[1]}\n{dump(data)}")

    def error_received(self, exc):
        log(f"UDP {self.port}: {exc}")


class Http:
    def __init__(self, port, status, save_dir="", auth_status=None, sign_key=None, reply_task=None,
                 ticket_fill=0, ticket_markers=False, lobby_u32=210):
        self.port = port
        self.status = status
        self.save_dir = save_dir
        self.auth_status = status if auth_status is None else auth_status
        self.sign_key = sign_key
        self.reply_task = reply_task
        self.ticket_fill = ticket_fill
        self.ticket_markers = ticket_markers
        self.lobby_u32 = lobby_u32

    async def handle(self, reader, writer):
        try:
            head = await reader.readuntil(b"\r\n\r\n")
        except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, ConnectionError):
            writer.close()
            return
        lines = head.decode("latin-1").split("\r\n")
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                name, value = line.split(":", 1)
                headers[name.strip().lower()] = value.strip()
        try:
            length = int(headers.get("content-length", "0") or 0)
        except ValueError:
            length = 0
        if length < 0 or length > 8 * 1024 * 1024:
            log(f"HTTP: implausible Content-Length {length}; closing without reply")
            writer.close()
            return
        try:
            body = await reader.readexactly(length) if length else b""
        except (asyncio.IncompleteReadError, ConnectionError):
            writer.close()
            return
        parts = lines[0].split(" ")
        method = parts[0] if parts else "?"
        target = parts[1] if len(parts) > 1 else "/"
        scheme = headers.get("x-sacredfire-scheme", "http")
        host = headers.get("host", "?")
        stage = classify(scheme, host, target)
        seq = next(SEQ)
        log(f"HTTP #{seq} {method} {scheme}://{host}{target} [{stage}]")
        for line in lines[1:]:
            if line:
                log(f"    {line}")
        if body:
            log(f"    body ({len(body)} bytes)\n{dump(body)}")
        if stage == "demonware-auth" and body:
            for summary in summarize_auth(body):
                log(f"    {summary}")
        elif stage == "demonware-auth":
            log("    auth endpoint with empty body (note the method and Content-Length)")
        self.save_capture(seq, method, scheme, host, target, headers, body, stage,
                            self.auth_status if stage == "demonware-auth" else self.status)
        signed = self.signed_auth_reply(seq, method, stage, body)
        if signed is not None:
            signature, reply_body = signed
            writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                         f"X-Signature: {signature}\r\n"
                         f"Content-Length: {len(reply_body)}\r\nConnection: close\r\n\r\n"
                         .encode() + reply_body)
            await writer.drain()
            writer.close()
            return
        status = self.auth_status if stage == "demonware-auth" else self.status
        reason = {200: "OK", 404: "Not Found", 500: "Internal Server Error",
                  503: "Service Unavailable"}.get(status, "Status")
        writer.write(f"HTTP/1.1 {status} {reason}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                     .encode())
        await writer.drain()
        writer.close()

    def signed_auth_reply(self, seq, method, stage, body):
        """Dev-only signed auth reply (test key). Returns (signature, body) or None.

        Only for POST /auth/ with --sign-key; any failure falls back to the plain
        --auth-status reply so a broken signer never blocks discovery. Ticket field
        values are v1 placeholders (auth_dev.py); the signature itself is real.
        """
        if not self.sign_key or stage != "demonware-auth" or method != "POST":
            return None
        try:
            import auth_dev  # tools/online/, lazy so the base server stays dependency-free
        except ImportError as error:
            log(f"    auth-dev #{seq}: no signer ({error}); unsigned reply")
            return None
        try:
            task = self.reply_task if self.reply_task is not None else auth_dev.request_task_id(body)
            reply_body = auth_dev.build_auth_reply(task, auth_dev.request_iv_seed(body),
                                                   ticket_fill=self.ticket_fill,
                                                   ticket_markers=self.ticket_markers)
            signature = auth_dev.sign_body(self.sign_key, reply_body)
        except (ValueError, RuntimeError, OSError) as error:
            log(f"    auth-dev #{seq}: signer failed ({error}); unsigned reply")
            return None
        log(f"    auth-dev #{seq}: signed reply ({len(reply_body)} bytes, "
            f"X-Signature {signature[:16]}...<len={len(signature)}>)")
        return signature, reply_body

    def save_capture(self, seq, method, scheme, host, target, headers, body, stage, reply_status):
        if not self.save_dir:
            return
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            base = f"{seq:04d}_{stamp}_{safe_name(method, 8)}_{safe_name(host, 48)}"
            body_path = os.path.join(self.save_dir, base + ".bin")
            meta_path = os.path.join(self.save_dir, base + ".meta.json")
            with open(body_path, "wb") as stream:
                stream.write(body)
            meta = {
                "seq": seq,
                "method": method,
                "scheme": scheme,
                "host": host,
                "target": target,
                "stage": stage,
                "request_headers": headers,
                "body_file": os.path.basename(body_path),
                "body_len": len(body),
                "body_sha1": hashlib.sha1(body).hexdigest() if body else None,
                "reply_status": reply_status,
            }
            with open(meta_path, "w", encoding="utf-8") as stream:
                json.dump(meta, stream, indent=2)
            log(f"    capture #{seq}: {body_path} ({len(body)} bytes) + .meta.json")
        except OSError as error:
            log(f"    capture #{seq} not saved ({error})")


async def main(args):
    loop = asyncio.get_running_loop()
    servers = []
    http = Http(args.http, args.http_status, args.save_dir, args.auth_status, args.sign_key,
                args.reply_task, args.ticket_fill, args.ticket_markers, args.lobby_u32)
    servers.append(await asyncio.start_server(http.handle, args.bind, args.http))
    log(f"HTTP on {args.bind}:{args.http} (answers {args.http_status}, captures to {args.save_dir or '(disabled)'})")
    for port in ports(args.tcp):
        if port == args.http:
            continue
        try:
            handler = Tcp(port, args.hold_seconds, args.tcp_echo, args.lobby_84, args.lobby_81,
                            args.lobby_u32)
            servers.append(await asyncio.start_server(handler.handle, args.bind, port))
        except OSError as error:
            log(f"TCP {port}: cannot listen ({error})")
    log(f"TCP on {args.tcp}")
    for port in ports(args.udp):
        try:
            await loop.create_datagram_endpoint(lambda p=port: Udp(p), local_addr=(args.bind, port))
        except OSError as error:
            log(f"UDP {port}: cannot listen ({error})")
    log(f"UDP on {args.udp}")
    log("Waiting for the game (Ctrl+C to stop)")
    await asyncio.gather(*(s.serve_forever() for s in servers))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bind", default="127.0.0.1", help="address to listen on (0.0.0.0 for the LAN)")
    parser.add_argument("--http", type=int, default=8080, help="HTTP port (BB_ONLINE_HTTP_PORT)")
    parser.add_argument("--http-status", type=int, default=404, help="status of every HTTP reply")
    parser.add_argument("--auth-status", type=int, default=None,
                        help="status only for Demonware /auth/ replies (default: same as --http-status); "
                             "H2 test: 200-empty vs 404 vs 503 with an empty body, no invented content")
    parser.add_argument("--tcp", default="3074-3080,443", help="TCP ports to listen on")
    parser.add_argument("--hold-seconds", type=float, default=0.0,
                        help="keep TCP connections open this long after last data (0: close on EOF); "
                             "reveals client follow-ups/timeouts on the lobby port")
    parser.add_argument("--tcp-echo", action="store_true",
                        help="PROBE only: echo the first chunk back once on TCP 3074 "
                             "(framing test, NOT a valid lobby reply)")
    parser.add_argument("--lobby-84", action="store_true",
                        help="PROBE only: answer the lobby handshake with a framed 0x84 "
                             "challenge ([len=6][84 00 00 00 00 00]) on TCP 3074; "
                             "client should answer with 8 bytes (FUN_0001a120)")
    parser.add_argument("--lobby-81", action="store_true",
                        help="PROBE only: answer the lobby handshake with a framed 0x81 "
                             "greeting ([len=22][81][u32 --lobby-u32][16 zero bytes]) on TCP 3074; "
                             "client crypto core (FUN_0001b060) should answer (FUN_0001b8e0)")
    parser.add_argument("--lobby-u32", type=int, default=210,
                        help="u32 value in the 0x81 probe (client accepts 210-220)")
    parser.add_argument("--ticket-fill", type=int, default=0,
                        help="dev-only: fill byte for ticket bodies after the magic "
                             "(0-255; PROBE whether zero bodies stall the crypto core)")
    parser.add_argument("--ticket-markers", action="store_true",
                        help="dev-only: ticket bodies carry position markers (CLI/SRV) to "
                             "trace the ticket->session flow in BB_DW_DUMPTASK dumps")
    parser.add_argument("--udp", default="3074-3080", help="UDP ports to listen on")
    parser.add_argument("--log", default="online-discovery.log", help="log file")
    parser.add_argument("--save-dir", default="captures-online", help="directory for raw HTTP bodies ('': disabled)")
    parser.add_argument("--sign-key", default=None, metavar="DW-TEST.KEY",
                        help="dev-only: sign Demonware /auth/ replies with this test RSA key "
                             "(needs BB_DW_TEST_KEY with the matching .spki.der in the game); "
                             "without it, /auth/ gets the plain --auth-status reply")
    parser.add_argument("--reply-task", type=int, default=None, metavar="N",
                        help="dev-only: auth_task value in signed replies (default: echo the "
                             "request's; try 47: the client passes 0x2f to its task check)")
    args = parser.parse_args()
    SAVE_DIR = args.save_dir
    LOG = open(args.log, "a", encoding="utf-8")
    log(f"--- discovery server, Python {sys.version.split()[0]}, pid {os.getpid()}")
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        log("stopped")
