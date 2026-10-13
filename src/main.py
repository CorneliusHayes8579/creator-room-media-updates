from chat_room import ContentUpdate, RealtimeClient, bootstrap_creator_room, deliver_processed_update


def main() -> None:
    client = RealtimeClient()
    room = bootstrap_creator_room(client, "creator_42", "subscriber_7")
    update = ContentUpdate(asset_id="track_101", title="Studio cut", status="ready")
    published = deliver_processed_update(client, update, "creator_42")
    print({"room": room["channel"], "published": bool(published)})


if __name__ == "__main__":
    main()
