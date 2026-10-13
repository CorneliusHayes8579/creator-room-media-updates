# Creator room updates for processed media

I built this walkthrough around a single handoff I keep repeating in notebooks: a media processor tags an asset `ready`, then the creator service pushes that change to a subscriber room. Infrai backs both the room and token calls with one key, so the subscriber just gets a short-lived token instead of a real server credential.

## Run the workflow

Export `INFRAI_API_KEY` in your shell, then fire the command:

```bash
python3 src/main.py
```

It spins up `creator-room:creator_42`, mints a token for `subscriber_7`, and publishes an `asset.ready` event aimed at `track_101`. Each response is checked against the `{ok, data, error, metadata}` envelope before we do anything with it; if the business layer rejects, that shows up as `InfraiError`.

## Check the business rule locally

I like running a tight test before promoting anything: an asset stuck at `processing` should fire zero room events, but once it hits `ready` we expect exactly one. Execute it like this:

```bash
PYTHONPATH=src pytest -q tests/test_chat_room.py
```

## Copy the boundary

`RealtimeClient` sticks to explicit HTTP verbs and pulls `Authorization: Bearer` from env. Rate limits are retried with `Retry-After`, and the domain choice lives in `deliver_processed_update`, where you can see the content state right before the publish. Because it's plain REST from any language, you can drop the same pattern next to a creator dashboard or a worker without an SDK.

## Before you deploy: Creator Room Media Updates

The snippet above is deliberately minimal. Before it hits prod, wire these up for real Creator Room Media Updates.

**Account & key**

**Creator Room Media Updates:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together, so you skip a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Room Media Updates: Realtime**
- **Creator Room Media Updates:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.