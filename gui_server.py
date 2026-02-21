"""Local web GUI server for SmartCodingAssistant."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any

from coding_assistant import SmartCodingAssistant


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
ASSISTANT = SmartCodingAssistant()


class GuiHandler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str = "text/plain", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"
        full = WEB_DIR / path.lstrip("/")
        if not full.exists() or not full.is_file():
            self._send(b"Not found", status=HTTPStatus.NOT_FOUND)
            return

        content_type = "text/plain"
        if full.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif full.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif full.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"

        self._send(full.read_bytes(), content_type=content_type)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/run":
            self._send(b"Not found", status=HTTPStatus.NOT_FOUND)
            return

        content_len = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_len)
        try:
            data = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(b'{"error":"invalid json"}', content_type="application/json", status=400)
            return

        task = str(data.get("task", "")).strip()
        files = data.get("files")
        apply_edits = bool(data.get("apply", False))

        if not task:
            self._send(b'{"error":"task is required"}', content_type="application/json", status=400)
            return

        if files is not None and not isinstance(files, list):
            self._send(b'{"error":"files must be a list"}', content_type="application/json", status=400)
            return

        result = ASSISTANT.run(task=task, repo_path=ROOT, files=files, apply=apply_edits)
        body = json.dumps(_result_to_dict(result), indent=2).encode("utf-8")
        self._send(body, content_type="application/json; charset=utf-8", status=200)


def _result_to_dict(result: Any) -> dict[str, Any]:
    return {
        "task": result.task,
        "intent": result.intent,
        "relevant_files": result.relevant_files,
        "plan": result.plan,
        "commands": result.commands,
        "response": result.response,
    }


def run_server(port: int = 8000) -> None:
    server = ThreadingHTTPServer(("0.0.0.0", port), GuiHandler)
    print(f"SmartCodingAssistant GUI: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
