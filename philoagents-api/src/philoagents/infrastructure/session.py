"""Signed session tokens: the only trustworthy source of a player's identity.

The client used to send its own ``player_id``, generated in the browser, so the per-player
rate limit could be dodged by simply asking again with a fresh id. Identities now come from
a token the server signs, which a caller cannot re-point at another player.
"""

import hashlib
import hmac
import time
import uuid

from philoagents.config import settings

_INVALID = "invalid session token"


class InvalidSession(Exception):
    """Raised when a token is malformed, tampered with, or expired."""


def _sign(payload: str) -> str:
    return hmac.new(
        settings.SESSION_SECRET.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()


def normalize_player_id(raw: str | None) -> str:
    """Return a canonical UUID string, minting one when ``raw`` is missing or malformed.

    A UUID never contains a dot, which is what lets ``verify`` split the token on the
    last two separators without ambiguity.
    """
    if raw:
        try:
            return str(uuid.UUID(raw))
        except (ValueError, TypeError):
            pass
    return str(uuid.uuid4())


def issue(player_id: str, ttl_seconds: int | None = None) -> tuple[str, int]:
    """Sign ``player_id`` and return ``(token, expires_at)`` as a unix timestamp."""
    ttl = settings.SESSION_TTL_SECONDS if ttl_seconds is None else ttl_seconds
    expires_at = int(time.time()) + ttl
    payload = f"{player_id}.{expires_at}"
    return f"{payload}.{_sign(payload)}", expires_at


def verify(token: str) -> str:
    """Return the player id bound to ``token``.

    Raises:
        InvalidSession: the token was not issued by this server, is expired, or was altered.
    """
    parts = token.rsplit(".", 2)
    if len(parts) != 3:
        raise InvalidSession(_INVALID)

    player_id, expires_at, signature = parts
    if normalize_player_id(player_id) != player_id:
        raise InvalidSession(_INVALID)

    try:
        deadline = int(expires_at)
    except ValueError:
        raise InvalidSession(_INVALID)

    if deadline <= int(time.time()):
        raise InvalidSession("session token has expired")

    # Not `==`: a plain comparison leaks how many leading characters were right.
    if not hmac.compare_digest(signature, _sign(f"{player_id}.{expires_at}")):
        raise InvalidSession(_INVALID)

    return player_id
