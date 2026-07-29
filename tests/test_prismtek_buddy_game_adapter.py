from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from adapters.prismtek_buddy_game import (
    BuddyGameAdapterError,
    BuddyGameClient,
    PROTOCOL_VERSION,
)


class FixtureHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, Any]] = []

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path == "/v1/tools":
            self._send(
                200,
                {
                    "ok": True,
                    "tools": [
                        {"name": "buddy.game.chat"},
                        {"name": "buddy.task.create"},
                    ],
                },
            )
            return
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.headers.get("authorization") != "Bearer fixture-token":
            self._send(401, {"ok": False, "error": "authorization required"})
            return
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        type(self).requests.append(payload)
        tool = payload.get("tool")
        if tool == "buddy.game.status":
            result = {
                "protocol_version": PROTOCOL_VERSION,
                "provider": {"provider": "fixture"},
                "capabilities": {"omni_buddy_transport_contract": True},
            }
        elif tool == "buddy.game.chat":
            result = {
                "protocol_version": PROTOCOL_VERSION,
                "reply": "Game Buddy received the embodied context.",
                "commands": [],
            }
        elif tool == "buddy.task.list":
            result = {"tasks": [], "count": 0}
        elif tool == "buddy.task.create":
            result = {"id": "task-fixture", "status": "created"}
        else:
            self._send(400, {"ok": False, "error": "unknown fixture tool"})
            return
        self._send(200, {"ok": True, "result": result})


class BuddyGameAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self) -> None:
        FixtureHandler.requests.clear()
        self.client = BuddyGameClient(
            base_url=self.base_url,
            token="fixture-token",
            timeout_seconds=5,
        )

    def test_status_validates_protocol_and_authentication(self) -> None:
        status = self.client.status()
        self.assertEqual(status["protocol_version"], PROTOCOL_VERSION)
        self.assertTrue(status["capabilities"]["omni_buddy_transport_contract"])

        without_token = BuddyGameClient(base_url=self.base_url, timeout_seconds=5)
        with self.assertRaisesRegex(BuddyGameAdapterError, "authorization"):
            without_token.status()

    def test_voice_routes_chat_and_vision_context(self) -> None:
        result = self.client.voice_command(
            "game please ask the room Buddy what is near the desk",
            vision_summary="A desk and a laptop are visible.",
            context={"device": "raspberry-pi", "input_mode": "wake-word"},
        )
        self.assertEqual(result["reply"], "Game Buddy received the embodied context.")
        request = FixtureHandler.requests[-1]
        self.assertEqual(request["tool"], "buddy.game.chat")
        arguments = request["arguments"]
        self.assertEqual(arguments["context"]["source"], "omni-buddy")
        self.assertEqual(arguments["context"]["device"], "raspberry-pi")
        self.assertIn("desk and a laptop", arguments["context"]["vision_summary"])

    def test_voice_task_and_task_list_use_persistent_tool_family(self) -> None:
        created = self.client.voice_command("game task remember the bedroom layout")
        self.assertEqual(created["status"], "created")
        self.assertEqual(FixtureHandler.requests[-1]["tool"], "buddy.task.create")

        listed = self.client.voice_command("game tasks")
        self.assertEqual(listed["count"], 0)
        self.assertEqual(FixtureHandler.requests[-1]["tool"], "buddy.task.list")

    def test_adapter_refuses_repository_or_shell_tools(self) -> None:
        for tool in ("buddy.codex_delegate", "buddy-exec", "shell.exec"):
            with self.subTest(tool=tool):
                with self.assertRaisesRegex(BuddyGameAdapterError, "outside"):
                    self.client.call(tool, {})

    def test_tools_are_discoverable_without_exposing_credentials(self) -> None:
        tools = self.client.tools()
        self.assertEqual([tool["name"] for tool in tools], ["buddy.game.chat", "buddy.task.create"])
        self.assertNotIn("fixture-token", json.dumps(tools))


if __name__ == "__main__":
    unittest.main()
