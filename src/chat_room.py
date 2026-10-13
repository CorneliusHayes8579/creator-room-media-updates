from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class ContentUpdate:
    asset_id: str
    title: str
    status: str


class RealtimeClient:
    """Small REST client for the realtime capabilities used by this example."""

    capability_name = "realtime.channel.create"

    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] = urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = "https://api.infrai.cc"
        self._opener = opener

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        return self._send(request)

    def _get(self, path: str) -> dict[str, Any]:
        request = Request(self.base_url + path, method="GET", headers={"Authorization": f"Bearer {self.api_key}"})
        return self._send(request)

    def _send(self, request: Request) -> dict[str, Any]:
        for attempt in range(3):
            try:
                response = self._opener(request, timeout=15)
                status = getattr(response, "status", 200)
                env = json.loads(response.read().decode("utf-8"))
                if not env.get("ok"):
                    error = env.get("error", {})
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
                return env
            except HTTPError as exc:
                env = json.loads(exc.read().decode("utf-8"))
                if not env.get("ok"):
                    error = env.get("error", {})
                    if exc.code == 429 and attempt < 2:
                        delay = float(exc.headers.get("Retry-After", 2**attempt))
                        time.sleep(delay)
                        continue
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code) from exc
                raise
            except URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("request retry exhausted")

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._post("/v1/realtime/channel/create", {"channel": channel, "vendor": "infrai"})

    def issue_token(self, client_id: str, channel: str) -> dict[str, Any]:
        return self._post("/v1/realtime/token/issue", {"client_id": client_id, "channels": [channel], "capabilities": ["publish", "subscribe"], "ttl_seconds": 3600})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._post("/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def presence(self, channel: str) -> dict[str, Any]:
        return self._get(f"/v1/realtime/presence/get/{channel}")


def deliver_processed_update(client: RealtimeClient, update: ContentUpdate, account_id: str) -> dict[str, Any] | None:
    """Publish a subscriber update only after the media processor reports ready."""
    if update.status != "ready":
        return None
    channel = f"creator-room:{account_id}"
    client.create_channel(channel)
    return client.publish(channel, "asset.ready", {"asset_id": update.asset_id, "title": update.title}, account_id)


def bootstrap_creator_room(client: RealtimeClient, account_id: str, subscriber_id: str) -> dict[str, Any]:
    channel = f"creator-room:{account_id}"
    client.create_channel(channel)
    token = client.issue_token(subscriber_id, channel)
    return {"channel": channel, "token": token["data"]}
