"""End-to-end smoke check against a running API.

Exercises the paths the game uses (session minting, REST, WebSocket streaming, RAG, two-turn
memory, rate limiting, reset scoping) and prints what the model actually said, so a human can
judge the answer.

Works whether or not the server has SESSION_SECRET set: the unauthenticated checks are then
reported as skipped rather than failing.

Run it with the services up (PYTHONPATH makes the `philoagents` package importable from
inside the api image, where it lives at /app/philoagents):

    docker compose exec -e PYTHONPATH=/app api /app/.venv/bin/python scripts/smoke_chat.py
"""

import asyncio
import json
import os
import re
import uuid

import httpx
import websockets
from philoagents.config import settings

BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws/chat")
TIMEOUT = float(os.getenv("SMOKE_TIMEOUT", "180"))


def new_player_id() -> str:
    # The server only keeps a claimed identity it can parse as a UUID.
    return str(uuid.uuid4())


def mint_session(player_id: str) -> str:
    """Ask for a signed identity and return the token for it."""
    response = httpx.post(
        f"{BASE}/session", json={"player_id": player_id}, timeout=TIMEOUT
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["player_id"] == player_id, (data["player_id"], player_id)
    print(f"  session for player_id={player_id}")
    return data["token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def rest_chat(
    player_id: str, philosopher_id: str, message: str, token: str | None = None
) -> httpx.Response:
    response = httpx.post(
        f"{BASE}/chat",
        json={
            "message": message,
            "philosopher_id": philosopher_id,
            "player_id": player_id,
        },
        headers=auth_headers(token) if token else {},
        timeout=TIMEOUT,
    )
    print(f"  HTTP {response.status_code} {response.text[:500]}")
    return response


def auth_is_required() -> bool:
    """Decide by probing, so the script cannot drift out of step with the container's env."""
    probe = httpx.post(
        f"{BASE}/chat",
        json={"message": "hi", "philosopher_id": "socrates"},
        timeout=TIMEOUT,
    )
    print(f"  unauthenticated probe: HTTP {probe.status_code}")
    return probe.status_code == 401


async def _handshake(ws, player_id: str, token: str) -> None:
    """Open with the frame the server expects; player_id only matters without a secret."""
    await ws.send(json.dumps({"auth": token, "player_id": player_id}))


async def ws_chat(player_id: str, philosopher_id: str, message: str, token: str) -> str:
    chunks: list[str] = []
    async with websockets.connect(WS_URL, open_timeout=TIMEOUT) as ws:
        await _handshake(ws, player_id, token)
        await ws.send(json.dumps({"message": message, "philosopher_id": philosopher_id}))
        while True:
            event = json.loads(await asyncio.wait_for(ws.recv(), timeout=TIMEOUT))
            if "error" in event:
                raise AssertionError(f"websocket returned an error: {event['error']}")
            if "chunk" in event:
                chunks.append(event["chunk"])
            if event.get("streaming") is False and event.get("response") is not None:
                break
    print(f"  {len(chunks)} chunks -> {event['response'][:500]}")
    assert len(chunks) > 1, "expected the reply to arrive as several chunks"
    return event["response"]


async def ws_reject_bad_frame(player_id: str, token: str) -> None:
    async with websockets.connect(WS_URL, open_timeout=TIMEOUT) as ws:
        await _handshake(ws, player_id, token)
        await ws.send(json.dumps({"message": "x"}))
        event = json.loads(await asyncio.wait_for(ws.recv(), timeout=TIMEOUT))
    assert "error" in event, event
    print(f"  rejected with: {event['error']}")


async def ws_refuses_a_turn_before_auth(player_id: str) -> None:
    """The handshake is mandatory, so a socket that skips it gets no reply."""
    async with websockets.connect(WS_URL, open_timeout=TIMEOUT) as ws:
        await ws.send(
            json.dumps({"message": "hi", "philosopher_id": "socrates", "player_id": player_id})
        )
        event = json.loads(await asyncio.wait_for(ws.recv(), timeout=TIMEOUT))
    assert "error" in event, event
    print(f"  refused with: {event['error']}")


def _thread_counts(db, *player_ids: str) -> dict:
    return {
        player_id: db["philosopher_state_checkpoints"].count_documents(
            {"thread_id": {"$regex": f"^{re.escape(player_id)}:"}}
        )
        for player_id in player_ids
    }


def reset_is_scoped(player_id: str, other_player: str, token: str) -> None:
    """Read the checkpoint collections through Mongo directly to prove the blast radius.

    The request deliberately claims `other_player`: an authenticated server must ignore the
    claim and clear the caller instead.
    """
    from pymongo import MongoClient

    db = MongoClient(settings.MONGO_URI)[settings.MONGO_DB_NAME]
    before = _thread_counts(db, player_id, other_player)
    print(f"  before: {before}")

    response = httpx.post(
        f"{BASE}/reset-memory",
        json={"player_id": other_player},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    print(f"  reset says: {response.json()}")

    after = _thread_counts(db, player_id, other_player)
    print(f"  after:  {after}")
    assert after[other_player] == before[other_player], "a claim reset another player"
    assert after[player_id] == 0, f"{player_id} was not cleared: {after}"


def main() -> None:
    print(f"smoke target: {BASE}")

    print("\n[1] is this server authenticated?")
    authenticated = auth_is_required()
    if not authenticated:
        print("  SESSION_SECRET is unset - checks that need a token will be skipped")

    print("\n[2] a forged token is refused")
    if authenticated:
        victim = new_player_id()
        token = mint_session(victim)
        player_id_part, expires_at, signature = token.rsplit(".", 2)
        forged = f"{new_player_id()}.{expires_at}.{signature}"
        code = httpx.post(
            f"{BASE}/chat",
            json={"message": "hi", "philosopher_id": "socrates"},
            headers=auth_headers(forged),
            timeout=TIMEOUT,
        ).status_code
        print(f"  HTTP {code}")
        assert code == 401, code
    else:
        print("  skipped")

    player_id = new_player_id()
    token = mint_session(player_id)
    print(f"\n[3] session minted for player_id={player_id}")

    print("\n[4] unknown philosopher is 404, not 500")
    probe = rest_chat(new_player_id(), "miguel", "hi", token)
    assert probe.status_code == 404, probe.text

    print("\n[5] oversized message is rejected before it reaches the model")
    big = httpx.post(
        f"{BASE}/chat",
        json={"message": "啊" * 2001, "philosopher_id": "socrates", "player_id": player_id},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    print(f"  HTTP {big.status_code}")
    assert big.status_code == 422, big.text

    print("\n[6] a burst of requests trips the rate limiter (no LLM cost: unknown NPC)")
    spammer = new_player_id()
    spammer_token = mint_session(spammer)
    codes = set()
    for _ in range(settings.RATE_LIMIT_MAX_MESSAGES + 1):
        codes.add(
            httpx.post(
                f"{BASE}/chat",
                json={
                    "message": "hi",
                    "philosopher_id": "miguel",
                    "player_id": spammer,
                },
                headers=auth_headers(spammer_token),
                timeout=TIMEOUT,
            ).status_code
        )
    print(f"  status codes seen: {sorted(codes)}")
    assert codes == {404, 429}, codes

    print("\n[7] first turn")
    first = rest_chat(player_id, "socrates", "你好，我叫小明，我正在研究塞尔的中文屋论证。", token)
    assert first.status_code == 200, first.text
    assert first.json()["response"].strip(), "empty reply"

    print("\n[8] second turn on the same thread: quoting the topic proves the player's")
    print("    message reached the model and the checkpoint remembered it")
    second = rest_chat(player_id, "socrates", "我刚才说我正在研究什么？", token)
    assert second.status_code == 200, second.text

    other_player = new_player_id()
    other_token = mint_session(other_player)
    print("\n[9] a second player talks to the same NPC, for the reset check")
    rest_chat(other_player, "socrates", "你好，我是另一个人。", other_token)

    print("\n[10] retrieval-augmented turn for a philosopher with a corpus")
    rag_player = new_player_id()
    rag = rest_chat(
        rag_player,
        "searle",
        "中文屋论证到底是什么，请依据资料解释",
        mint_session(rag_player),
    )
    assert rag.status_code == 200, rag.text

    print("\n[11] websocket streaming, the path the game actually uses")
    ws_player = new_player_id()
    asyncio.run(
        ws_chat(ws_player, "turing", "图灵测试能证明机器有意识吗？", mint_session(ws_player))
    )

    print("\n[12] websocket rejects a malformed frame instead of dropping the socket")
    asyncio.run(ws_reject_bad_frame(player_id, token))

    print("\n[13] websocket demands the handshake before any turn")
    if authenticated:
        asyncio.run(ws_refuses_a_turn_before_auth(new_player_id()))
    else:
        print("  skipped")

    print("\n[14] /reset-memory clears the caller, not the identity it claims")
    reset_is_scoped(player_id, other_player, token)

    print("\nall smoke checks passed. Rows written under the player ids printed above.")


if __name__ == "__main__":
    main()
