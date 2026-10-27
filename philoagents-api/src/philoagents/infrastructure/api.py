import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from opik.integrations.langchain import OpikTracer
from pydantic import BaseModel, Field, ValidationError

from .chat_history import ensure_indexes, get_turns, save_turn
from .opik_utils import configure, tracing_enabled
from .rate_limit import allow
from .session import InvalidSession, issue, normalize_player_id, verify
from philoagents.application.conversation_service.generate_response import (
    get_response,
    get_streaming_response,
    shutdown_workflow_graph,
)
from philoagents.application.conversation_service.reset_conversation import (
    reset_conversation_state,
)
from philoagents.config import settings
from philoagents.domain.exceptions import (
    PhilosopherContextNotFound,
    PhilosopherNameNotFound,
    PhilosopherPerspectiveNotFound,
    PhilosopherStyleNotFound,
)
from philoagents.domain.philosopher_factory import PhilosopherFactory

configure()

logger = logging.getLogger(__name__)

# A browser cannot add headers to a WebSocket, so the token arrives as the first frame.
# Nobody is served while we wait for it, hence the short deadline.
_WS_AUTH_TIMEOUT_SECONDS = 10


def flush_tracing() -> None:
    if tracing_enabled():
        OpikTracer().flush()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the API."""
    if not settings.auth_enabled:
        logger.warning(
            "SESSION_SECRET is empty - every endpoint accepts unauthenticated calls and "
            "the per-player rate limit can be dodged by sending a fresh player_id."
        )
    await asyncio.to_thread(ensure_indexes)
    yield
    await shutdown_workflow_graph()
    flush_tracing()


app = FastAPI(lifespan=lifespan)

_origins = settings.cors_origins
if _origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        # Bearer tokens travel in a header, not a cookie, so credentialed CORS is not
        # needed - and "*" plus credentials is a pair browsers reject outright.
        allow_credentials=False,
        allow_methods=["*"],
        # "*" is not treated as a wildcard by browsers once a request carries Authorization.
        allow_headers=["Content-Type", "Authorization"],
    )


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)
    philosopher_id: str = Field(min_length=1, max_length=64)
    # Only honoured while SESSION_SECRET is unset; an authenticated caller's identity comes
    # from the token, so this field can no longer name somebody else's save game.
    player_id: str | None = Field(default=None, max_length=100)


class ResetRequest(BaseModel):
    player_id: str | None = Field(default=None, max_length=100)


class SessionRequest(BaseModel):
    player_id: str | None = Field(default=None, max_length=100)


def bearer_token(request: Request) -> str:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return token.strip()


def resolve_player_id(request: Request, claimed: str | None = None) -> str:
    """Return the player this request acts as.

    Raises:
        HTTPException: 401 when a token is absent, forged or expired.
    """
    if not settings.auth_enabled:
        return normalize_player_id(claimed)

    try:
        return verify(bearer_token(request))
    except InvalidSession as exc:
        raise HTTPException(status_code=401, detail=str(exc))


def too_much(key: str, limit: int | None = None) -> None:
    allowed, retry_after = allow(key, limit)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Wait before trying again.",
            headers={"Retry-After": str(retry_after)},
        )


def to_http_error(exc: Exception) -> HTTPException:
    if isinstance(
        exc,
        (
            PhilosopherNameNotFound,
            PhilosopherPerspectiveNotFound,
            PhilosopherStyleNotFound,
            PhilosopherContextNotFound,
        ),
    ):
        return HTTPException(status_code=404, detail=str(exc))

    return HTTPException(status_code=500, detail=str(exc))


@app.post("/session")
async def create_session(payload: SessionRequest, request: Request):
    """Issue a signed identity for a player.

    A recognised ``player_id`` is kept, so reopening the page does not orphan the existing
    checkpoints. There is no account system behind this, so knowing another player's UUID
    is still enough to claim it - unchanged from before, and the reason the game has no
    server-side notion of ownership over a save game.
    """
    client_ip = request.client.host if request.client else "unknown"
    too_much(f"session:{client_ip}", settings.RATE_LIMIT_MAX_SESSIONS)

    player_id = normalize_player_id(payload.player_id)
    token, expires_at = issue(player_id)
    return {"token": token, "expires_at": expires_at, "player_id": player_id}


@app.post("/chat")
async def chat(chat_message: ChatMessage, request: Request):
    player_id = resolve_player_id(request, chat_message.player_id)
    too_much(f"chat:{player_id}")

    try:
        philosopher_factory = PhilosopherFactory()
        philosopher = philosopher_factory.get_philosopher(chat_message.philosopher_id)

        response, _ = await get_response(
            messages=chat_message.message,
            philosopher_id=chat_message.philosopher_id,
            philosopher_name=philosopher.name,
            philosopher_perspective=philosopher.perspective,
            philosopher_style=philosopher.style,
            philosopher_context="",
            player_id=player_id
        )
        await asyncio.to_thread(
            save_turn,
            player_id,
            chat_message.philosopher_id,
            chat_message.message,
            response,
        )
        return {"response": response}
    except Exception as e:
        raise to_http_error(e)


async def authenticate_socket(websocket: WebSocket) -> str:
    """Consume the opening frame and return the player it names.

    The frame is always read, even unauthenticated: skipping it would let the handshake be
    parsed as a turn. Its ``player_id`` only matters while SESSION_SECRET is unset - with a
    secret configured the identity comes from the signature and the claim is ignored.

    Raises:
        HTTPException: reused only for its status code, so the caller can answer 401.
    """
    try:
        frame = await asyncio.wait_for(
            websocket.receive_json(), _WS_AUTH_TIMEOUT_SECONDS
        )
    except (TimeoutError, asyncio.TimeoutError, ValueError, ValidationError):
        raise HTTPException(status_code=401, detail="No auth frame received")

    if not isinstance(frame, dict):
        raise HTTPException(status_code=401, detail="First frame must be an object")

    if not settings.auth_enabled:
        return normalize_player_id(frame.get("player_id"))

    token = frame.get("auth")
    if not isinstance(token, str):
        raise HTTPException(status_code=401, detail='First frame must carry {"auth": token}')

    try:
        return verify(token)
    except InvalidSession as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        player_id = await authenticate_socket(websocket)
    except HTTPException as exc:
        await websocket.send_json({"error": exc.detail})
        await websocket.close(code=4401)
        return

    try:
        while True:
            data = await websocket.receive_json()

            try:
                payload = ChatMessage.model_validate(data)
            except ValidationError:
                await websocket.send_json({
                    "error": "message and philosopher_id are required"
                })
                continue

            # The socket was authorised once; every turn on it belongs to that player,
            # whatever player_id the frame itself claims.
            allowed, retry_after = allow(f"chat:{player_id}")
            if not allowed:
                await websocket.send_json({
                    "error": f"Too many messages. Try again in {retry_after}s."
                })
                continue

            try:
                philosopher_factory = PhilosopherFactory()
                philosopher = philosopher_factory.get_philosopher(
                    payload.philosopher_id
                )

                # Use streaming response instead of get_response
                response_stream = get_streaming_response(
                    messages=payload.message,
                    philosopher_id=payload.philosopher_id,
                    philosopher_name=philosopher.name,
                    philosopher_perspective=philosopher.perspective,
                    philosopher_style=philosopher.style,
                    philosopher_context="",
                    player_id=player_id
                )

                # Send initial message to indicate streaming has started
                await websocket.send_json({"streaming": True})

                # Stream each chunk of the response
                full_response = ""
                async for chunk in response_stream:
                    full_response += chunk
                    await websocket.send_json({"chunk": chunk})

                # AI 完整回复生成后，保存到 MongoDB
                if full_response.strip():
                    await asyncio.to_thread(
                        save_turn,
                        player_id,
                        payload.philosopher_id,
                        payload.message,
                        full_response,
                    )

                await websocket.send_json(
                    {"response": full_response, "streaming": False}
                )

            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        pass


@app.get("/chat-history/{philosopher_id}")
async def read_chat_history(
        philosopher_id: str,
        request: Request,
        player_id: str | None = Query(default=None, max_length=100),
):
    """获取当前玩家与指定哲学家的历史对话。"""

    player_id = resolve_player_id(request, player_id)

    try:
        # 验证 NPC 是否存在
        PhilosopherFactory().get_philosopher(philosopher_id)

        turns = await asyncio.to_thread(
            get_turns,
            player_id,
            philosopher_id,
        )

        return {"turns": turns}

    except Exception as e:
        raise to_http_error(e)


@app.post("/reset-memory")
async def reset_conversation(payload: ResetRequest, request: Request):
    """Clears one player's conversation state.

    It used to drop the checkpoint collections outright, which reset every player in the
    database at once. Only the caller's own threads are removed now, and with a session
    token they cannot even name another player.

    Returns:
        dict: the player and how many documents each collection lost.
    """
    player_id = resolve_player_id(request, payload.player_id)
    try:
        return await asyncio.to_thread(reset_conversation_state, player_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
