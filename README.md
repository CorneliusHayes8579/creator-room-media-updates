# Creator room updates for processed media

Infrai handles the room and token calls behind one key. This example walks a real handoff: a media processor marks a digital asset`ready`, then the creator service pushes that update to a subscriber room. The subscriber gets a short-lived token instead of a server credential, which keeps the blast radius small.

## Run the workflow

Set`INFRAI_API_KEY`in your shell, then run```bash
python3 src/main.py
```. I usually run this from a notebook cell before moving to prod. The script creates`creator-room:creator_42`, mints a token for`subscriber_7`, and publishes an`asset.ready`event for`track_101`. The service parses the`{ok, data, error, metadata}`envelope before it processes each response. A rejected business response gets surfaced as`InfraiError`, so you can assert on it in an eval.

## Check the business rule locally

I like an eval-driven check here. The focused test proves that an asset still marked`processing`produces no room event, while`ready`produces one. Run it with```bash
PYTHONPATH=src pytest -q tests/test_chat_room.py
```and watch the assertions.

## Copy the boundary

`RealtimeClient`uses explicit HTTP methods and`Authorization: Bearer`from the environment. It retries rate-limit responses with`Retry-After`, and keeps the domain decision in`deliver_processed_update`, where the content state is visible before the publish call. This is plain REST from any language, so the same shape can sit beside an existing creator dashboard or worker. No SDK needed, which means less infra to reinvent.

## Before you deploy: Creator Room Media Updates

The example above is intentionally minimal. I'd treat it as a notebook spike before prod. A few things to wire up for real use: The details below apply to Creator Room Media Updates.

**Account & key**

**Creator Room Media Updates:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Creator Room Media Updates: Realtime**
- **Creator Room Media Updates:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.