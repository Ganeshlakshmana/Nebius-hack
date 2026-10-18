from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from app.config.settings import settings
from app.db.sqlite_store import AppStore


@dataclass
class AgentEnvelope:
    message_id: str
    sender: str
    recipient: str
    event_type: str
    payload: dict[str, Any]
    timestamp: int
    api_key_id: str
    signature: str


class EventBus:
    def __init__(self):
        self.listeners: set[asyncio.Queue[dict[str, Any]]] = set()

    async def publish(self, event: dict[str, Any]) -> None:
        stale: list[asyncio.Queue[dict[str, Any]]] = []
        for queue in tuple(self.listeners):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                stale.append(queue)
        for queue in stale:
            self.listeners.discard(queue)

    async def subscribe(self):
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=200)
        self.listeners.add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self.listeners.discard(queue)


class AgentBus:
    """Signed, audited in-process agent messaging; secrets are never emitted to clients."""
    def __init__(self, store: AppStore, events: EventBus):
        self.store, self.events = store, events

    @staticmethod
    def _canonical(message: dict[str, Any]) -> bytes:
        return json.dumps(message, sort_keys=True, separators=(",", ":"), default=str).encode()

    def send(self, sender: str, recipient: str, event_type: str, payload: dict[str, Any]) -> AgentEnvelope:
        body = {"message_id": str(uuid.uuid4()), "sender": sender, "recipient": recipient,
                "event_type": event_type, "payload": payload, "timestamp": int(time.time()),
                "api_key_id": hashlib.sha256(settings.agent_api_key.encode()).hexdigest()[:12]}
        signature = hmac.new(settings.agent_secret.encode(), self._canonical(body), hashlib.sha256).hexdigest()
        envelope = AgentEnvelope(**body, signature=signature)
        self.receive(envelope)
        return envelope

    def receive(self, envelope: AgentEnvelope) -> None:
        body = {key: getattr(envelope, key) for key in (
            "message_id", "sender", "recipient", "event_type", "payload", "timestamp", "api_key_id")}
        expected = hmac.new(settings.agent_secret.encode(), self._canonical(body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, envelope.signature):
            raise PermissionError("Invalid inter-agent message signature")
        if envelope.api_key_id != hashlib.sha256(settings.agent_api_key.encode()).hexdigest()[:12]:
            raise PermissionError("Unknown inter-agent API key")
        self.store.save_message(envelope.sender, envelope.recipient, envelope.event_type,
                                envelope.payload, envelope.signature)
        self.store.audit(envelope.sender, "agent_handoff", {"to": envelope.recipient,
                          "type": envelope.event_type, "message_id": envelope.message_id})
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.events.publish({"agent": envelope.sender, "to": envelope.recipient,
                "type": envelope.event_type, "payload": envelope.payload, "timestamp": envelope.timestamp}))
        except RuntimeError:
            pass
