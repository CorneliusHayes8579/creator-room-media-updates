from chat_room import ContentUpdate, deliver_processed_update


class FakeClient:
    def __init__(self):
        self.calls = []

    def create_channel(self, channel):
        self.calls.append(("create", channel))
        return {"ok": True}

    def publish(self, channel, event, data, account_id):
        self.calls.append(("publish", channel, event, data, account_id))
        return {"ok": True, "data": {"event": event}}


def test_only_ready_asset_reaches_subscribers():
    client = FakeClient()
    result = deliver_processed_update(client, ContentUpdate("a1", "Draft", "processing"), "creator_42")
    assert result is None
    assert client.calls == []

    result = deliver_processed_update(client, ContentUpdate("a1", "Final", "ready"), "creator_42")
    assert result["data"]["event"] == "asset.ready"
    assert client.calls[0] == ("create", "creator-room:creator_42")
