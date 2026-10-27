import time
import uuid

import pytest

from philoagents.config import settings
from philoagents.infrastructure import session

SECRET = "unit-test-secret"


@pytest.fixture(autouse=True)
def _secret(monkeypatch):
    monkeypatch.setattr(settings, "SESSION_SECRET", SECRET)
    monkeypatch.setattr(settings, "SESSION_TTL_SECONDS", 3600)


def test_issued_token_verifies_back_to_the_same_player():
    player_id = str(uuid.uuid4())
    token, expires_at = session.issue(player_id)

    assert session.verify(token) == player_id
    assert expires_at > int(time.time())


def test_replay_of_a_tampered_player_id_is_rejected():
    token, _ = session.issue(str(uuid.uuid4()))
    player_id, expires_at, signature = token.rsplit(".", 2)
    forged = f"{uuid.uuid4()}.{expires_at}.{signature}"

    with pytest.raises(session.InvalidSession):
        session.verify(forged)


def test_expired_token_is_rejected():
    token, _ = session.issue(str(uuid.uuid4()), ttl_seconds=-1)

    with pytest.raises(session.InvalidSession):
        session.verify(token)


def test_token_signed_by_another_secret_is_rejected(monkeypatch):
    token, _ = session.issue(str(uuid.uuid4()))

    # Restarting the server with a new secret must not leave old tokens usable.
    monkeypatch.setattr(settings, "SESSION_SECRET", "a-rotated-secret")

    with pytest.raises(session.InvalidSession):
        session.verify(token)


@pytest.mark.parametrize("raw", ["", "not-a-uuid", None, "00000000000000000000000000000000"])
def test_malformed_claims_become_a_fresh_uuid(raw):
    canonical = session.normalize_player_id(raw)

    assert uuid.UUID(canonical)
    assert canonical != raw


def test_uuid_claims_survive_unchanged_and_dot_free():
    claimed = str(uuid.uuid4()).upper()

    assert session.normalize_player_id(claimed) == claimed.lower()
    assert "." not in session.normalize_player_id(claimed)
