# SPDX-License-Identifier: MIT
"""Serve the floor review demo on this computer only."""

from __future__ import annotations

import argparse
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from demo_intake import handle_demo_intake

from structural_lib.services.floor_review import review_floor_v1

_EXAMPLE = Path(__file__).resolve().parent
_STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
_MAX_REQUEST = 20 * 1024 * 1024  # Includes base64 encoding and JSON framing.


class FloorDemoServer(ThreadingHTTPServer):
    """A loopback-only HTTP server for the synthetic example and user-selected exports."""

    daemon_threads = True

    def __init__(self, port: int) -> None:
        super().__init__(("127.0.0.1", port), FloorDemoHandler)
        self.host_header = f"127.0.0.1:{self.server_port}"
        self.origin = f"http://{self.host_header}"


class FloorDemoHandler(BaseHTTPRequestHandler):
    """Serve fixed local routes without a file browser or persistent uploads."""

    server: FloorDemoServer

    def setup(self) -> None:
        self.request.settimeout(20)
        super().setup()

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler protocol
        if not self._valid_host():
            return
        if self.path == "/api/sample":
            packet = _EXAMPLE / "etabs-paired" / "packet.json"
            result = review_floor_v1(packet, profile="etabs-paired", evaluate=True)
            self._json(200, {"kind": "review", "sample": True, "result": result})
            return
        asset = _STATIC.get(self.path)
        if asset:
            name, content_type = asset
            try:
                content = (_EXAMPLE / "web" / name).read_bytes()
            except OSError:
                self._error(404, "This demo asset is missing from the checkout.")
            else:
                self._response(200, content_type, content)
            return
        self._error(404, "This page is unavailable.")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler protocol
        if not self._valid_host():
            return
        if self.path != "/api/intake":
            self._error(404, "This page is unavailable.")
            return
        if self.headers.get("Origin") != self.server.origin:
            self._error(403, "Open the demo from its local address to preview files.")
            return
        if self.headers.get_content_type() != "application/json":
            self._error(415, "Use the demo file picker to send an intake request.")
            return
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(411, "The file request length was missing.")
            return
        if content_length < 1 or content_length > _MAX_REQUEST:
            self._error(413, "Select a smaller floor subset or fewer export files.")
            return
        try:
            payload = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, ValueError, RecursionError):
            self._error(400, "The file request could not be read.")
            return
        result = handle_demo_intake(payload)
        self._json(400 if result["kind"] == "error" else 200, result)

    def _valid_host(self) -> bool:
        if self.headers.get("Host") == self.server.host_header:
            return True
        self._error(403, "Open the demo using the printed loopback address.")
        return False

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"kind": "error", "message": message})

    def _json(self, status: int, result: dict) -> None:
        self._response(
            status,
            "application/json; charset=utf-8",
            json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8"),
        )

    def _response(self, status: int, content_type: str, data: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'none'",
        )
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        # The UI displays request errors. Keep request lines out of operator logs.
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="Local port to bind")
    parser.add_argument("--open", action="store_true", help="Open the default browser")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    try:
        with FloorDemoServer(args.port) as server:
            print(f"Floor Review Demo: {server.origin}/", flush=True)
            if args.open:
                webbrowser.open(f"{server.origin}/")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                return 0
    except OSError as exc:
        parser.error(f"Unable to start the local demo: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
