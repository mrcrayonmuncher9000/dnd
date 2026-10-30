from __future__ import annotations

import copy
import json
import logging
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from typing import Any, Dict, cast
from urllib.parse import urlparse

from Gin import app_state

ROOT = Path(__file__).resolve().parent
STATE_PATH = Path(
    os.environ.get("MINDND_STATE_PATH", ROOT / "Gin" / "demo_state.json")
)


class DemoService:
    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path
        self.lock = RLock()
        self.state = app_state.load_state(state_path)

    def get_state(self) -> Dict[str, Any]:
        with self.lock:
            return copy.deepcopy(self.state)

    def roll(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            updated_state = copy.deepcopy(self.state)
            result = app_state.perform_roll(
                updated_state,
                character_id=payload["character_id"],
                dice_type=payload["dice_type"],
                quantity=payload.get("quantity", 1),
                modifier=payload.get("modifier", 0),
                advantage=payload.get("advantage", "None"),
                attribute_name=payload.get("attribute", "None"),
            )
            app_state.save_state(updated_state, self.state_path)
            self.state = updated_state
            return {
                "result": result["result"],
                "log_message": result["log_message"],
            }

    def add_room(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            updated_state = copy.deepcopy(self.state)
            room = app_state.add_room(
                updated_state,
                name=payload.get("name", ""),
                room_type=payload.get("type", ""),
            )
            app_state.save_state(updated_state, self.state_path)
            self.state = updated_state
            return {"room": room, "state": copy.deepcopy(self.state)}

    def move(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            updated_state = copy.deepcopy(self.state)
            app_state.move_character(
                updated_state,
                character_id=payload["character_id"],
                x=payload["x"],
                y=payload["y"],
                max_distance=payload.get("max_distance", 35),
            )
            app_state.save_state(updated_state, self.state_path)
            self.state = updated_state
            return copy.deepcopy(self.state)

    def reset_turn(self) -> Dict[str, Any]:
        with self.lock:
            updated_state = copy.deepcopy(self.state)
            app_state.reset_turn(updated_state)
            app_state.save_state(updated_state, self.state_path)
            self.state = updated_state
            return copy.deepcopy(self.state)

    def clear_logs(self) -> Dict[str, Any]:
        with self.lock:
            updated_state = copy.deepcopy(self.state)
            updated_state["logs"] = []
            app_state.save_state(updated_state, self.state_path)
            self.state = updated_state
            return copy.deepcopy(self.state)


class DemoRequestHandler(SimpleHTTPRequestHandler):
    server_version = "MinDND/1.0"

    def __init__(self, request: Any, client_address: Any, server: Any) -> None:
        super().__init__(request, client_address, server, directory=str(ROOT))

    @property
    def service(self) -> DemoService:
        return cast(DemoHTTPServer, self.server).service

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/UserDashboard/dashboard.html")
            self.end_headers()
            return
        if path == "/api/health":
            self._send_json({"status": "ok"})
            return
        if path == "/api/state":
            self._send_json(self.service.get_state())
            return
        if path.startswith("/api/"):
            self._send_json({"error": "API route not found."}, status=404)
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            self._send_json({"error": "POST is only supported for API routes."}, status=404)
            return

        try:
            payload = self._read_json()
            if path == "/api/roll":
                response = self.service.roll(payload)
            elif path == "/api/rooms":
                response = self.service.add_room(payload)
            elif path == "/api/move":
                response = self.service.move(payload)
            elif path == "/api/reset-turn":
                response = self.service.reset_turn()
            elif path == "/api/logs/clear":
                response = self.service.clear_logs()
            else:
                self._send_json({"error": "API route not found."}, status=404)
                return
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._send_json({"error": str(error) or "Invalid request."}, status=400)
            return
        except OSError:
            logging.exception("Could not persist demo state")
            self._send_json({"error": "Could not save demo state."}, status=500)
            return
        self._send_json(response)

    def _read_json(self) -> Dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid Content-Length header.") from error
        if content_length <= 0 or content_length > 16_384:
            raise ValueError("Request body must be between 1 and 16384 bytes.")
        payload = json.loads(self.rfile.read(content_length))
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


class DemoHTTPServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], state_path: Path) -> None:
        super().__init__(address, DemoRequestHandler)
        self.service = DemoService(state_path)


def main() -> None:
    host = os.environ.get("MINDND_HOST", "127.0.0.1")
    port = int(os.environ.get("MINDND_PORT", "8000"))
    server = DemoHTTPServer((host, port), STATE_PATH)
    print(f"MinDND demo is running at http://{host}:{port}/")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping MinDND demo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
