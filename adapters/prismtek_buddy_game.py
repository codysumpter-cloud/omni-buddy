#!/usr/bin/env python3
"""Omni Buddy transport adapter for Prismtek Buddies.

This adapter routes transcribed voice, vision summaries, and explicit task commands
through the canonical ``prismtek-buddy-game-v1`` runtime. It does not execute game
commands, repository actions, or provider calls itself; the owning Buddy runtime and
Godot client retain those boundaries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, cast

PROTOCOL_VERSION = "prismtek-buddy-game-v1"
DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_TIMEOUT_SECONDS = 45.0
MAX_RESPONSE_BYTES = 1_000_000
SAFE_TOOLS = {
    "buddy.game.status",
    "buddy.game.chat",
    "buddy.task.create",
    "buddy.task.list",
    "buddy.task.get",
    "buddy.task.plan",
    "buddy.task.approval",
    "buddy.task.start",
    "buddy.task.step",
    "buddy.task.complete",
    "buddy.task.cancel",
    "buddy.task.resume",
}


class BuddyGameAdapterError(RuntimeError):
    """A public-safe game bridge error."""


@dataclass(frozen=True)
class BuddyGameClient:
    base_url: str = DEFAULT_BASE_URL
    token: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "BuddyGameClient":
        return cls(
            base_url=os.getenv("BUDDY_GAME_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
            or DEFAULT_BASE_URL,
            token=os.getenv("BUDDY_GAME_TOKEN", "").strip() or None,
            timeout_seconds=float(
                os.getenv("BUDDY_GAME_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
            ),
        )

    def _headers(self) -> dict[str, str]:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": "omni-buddy-game-adapter/1",
        }
        if self.token:
            headers["authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        method = "POST" if payload is not None else "GET"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            method=method,
            data=body,
            headers=self._headers(),
        )
        try:
            with urllib.request.urlopen(request, timeout=max(1.0, self.timeout_seconds)) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except urllib.error.HTTPError as error:
            try:
                detail = json.loads(error.read(MAX_RESPONSE_BYTES).decode("utf-8", "replace"))
                message = str(detail.get("error") or f"Buddy bridge returned HTTP {error.code}")
            except Exception:
                message = f"Buddy bridge returned HTTP {error.code}"
            raise BuddyGameAdapterError(message) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise BuddyGameAdapterError("Buddy game bridge is unavailable") from error
        if len(raw) > MAX_RESPONSE_BYTES:
            raise BuddyGameAdapterError("Buddy bridge response exceeded the size limit")
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise BuddyGameAdapterError("Buddy bridge returned invalid JSON") from error
        if not isinstance(decoded, dict):
            raise BuddyGameAdapterError("Buddy bridge returned a non-object response")
        if decoded.get("ok") is not True:
            raise BuddyGameAdapterError(str(decoded.get("error") or "Buddy bridge failed safely"))
        return cast(dict[str, Any], decoded)

    def status(self) -> dict[str, Any]:
        payload = self.call("buddy.game.status", {})
        version = str(payload.get("protocol_version") or "")
        if version != PROTOCOL_VERSION:
            raise BuddyGameAdapterError(
                f"Buddy protocol mismatch: expected {PROTOCOL_VERSION}, received {version or 'missing'}"
            )
        return payload

    def tools(self) -> list[dict[str, Any]]:
        payload = self._request("/v1/tools")
        tools = payload.get("tools", [])
        return [item for item in tools if isinstance(item, dict)] if isinstance(tools, list) else []

    def call(self, tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if tool not in SAFE_TOOLS:
            raise BuddyGameAdapterError("tool is outside the Omni Buddy game-safe surface")
        payload = self._request(
            "/v1/call",
            {"tool": tool, "arguments": arguments or {}},
        )
        result = payload.get("result", {})
        if not isinstance(result, dict):
            raise BuddyGameAdapterError("Buddy bridge returned a non-object tool result")
        return cast(dict[str, Any], result)

    def chat(
        self,
        message: str,
        *,
        vision_summary: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        clean = " ".join(str(message or "").split()).strip()
        if not clean:
            raise BuddyGameAdapterError("message is required")
        game_context: dict[str, Any] = {
            "source": "omni-buddy",
            "input_mode": "voice-or-text",
            **(context or {}),
        }
        if vision_summary:
            game_context["vision_summary"] = " ".join(str(vision_summary).split())[:2000]
        return self.call(
            "buddy.game.chat",
            {"message": clean[:4000], "context": game_context},
        )

    def create_task(self, objective: str, *, risk: str = "draft-only") -> dict[str, Any]:
        clean = " ".join(str(objective or "").split()).strip()
        if not clean:
            raise BuddyGameAdapterError("task objective is required")
        return self.call(
            "buddy.task.create",
            {"objective": clean[:4000], "risk": risk},
        )

    def voice_command(
        self,
        text: str,
        *,
        vision_summary: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route an explicit voice/text command into the game-safe protocol.

        Supported forms:
        - ``game status``
        - ``game tasks``
        - ``game task <objective>``
        - ``game <message>``
        """
        clean = " ".join(str(text or "").split()).strip()
        lowered = clean.lower()
        for prefix in ("/game ", "game ", "prismtek buddies "):
            if lowered.startswith(prefix):
                command = clean[len(prefix) :].strip()
                break
        else:
            command = clean
        lowered_command = command.lower()
        if lowered_command in {"status", "doctor", "health"}:
            return self.status()
        if lowered_command in {"tasks", "list tasks"}:
            return self.call("buddy.task.list", {})
        if lowered_command.startswith("task "):
            return self.create_task(command[5:].strip())
        return self.chat(command, vision_summary=vision_summary, context=context)


def _json_object(value: str) -> dict[str, Any]:
    if not value:
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as error:
        raise argparse.ArgumentTypeError("context must be valid JSON") from error
    if not isinstance(payload, dict):
        raise argparse.ArgumentTypeError("context must be a JSON object")
    return cast(dict[str, Any], payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Route Omni Buddy into Prismtek Buddies")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--timeout", type=float, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("tools")
    tasks = subparsers.add_parser("tasks")
    tasks.add_argument("task_id", nargs="?")

    chat = subparsers.add_parser("chat")
    chat.add_argument("message")
    chat.add_argument("--vision-summary", default=None)
    chat.add_argument("--context-json", type=_json_object, default={})

    voice = subparsers.add_parser("voice")
    voice.add_argument("text")
    voice.add_argument("--vision-summary", default=None)
    voice.add_argument("--context-json", type=_json_object, default={})

    task = subparsers.add_parser("task")
    task.add_argument("objective")
    task.add_argument("--risk", default="draft-only")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    env_client = BuddyGameClient.from_env()
    client = BuddyGameClient(
        base_url=(args.base_url or env_client.base_url).rstrip("/"),
        token=args.token if args.token is not None else env_client.token,
        timeout_seconds=args.timeout if args.timeout is not None else env_client.timeout_seconds,
    )
    try:
        if args.command == "status":
            result = client.status()
        elif args.command == "tools":
            result = {"tools": client.tools()}
        elif args.command == "tasks":
            result = (
                client.call("buddy.task.get", {"task_id": args.task_id})
                if args.task_id
                else client.call("buddy.task.list", {})
            )
        elif args.command == "chat":
            result = client.chat(
                args.message,
                vision_summary=args.vision_summary,
                context=args.context_json,
            )
        elif args.command == "voice":
            result = client.voice_command(
                args.text,
                vision_summary=args.vision_summary,
                context=args.context_json,
            )
        else:
            result = client.create_task(args.objective, risk=args.risk)
    except BuddyGameAdapterError as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "result": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
