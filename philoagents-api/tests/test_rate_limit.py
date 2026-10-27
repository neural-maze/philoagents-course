from philoagents.infrastructure import rate_limit


def _reset(settings, monkeypatch, limit=3, window=60):
    monkeypatch.setattr(settings, "RATE_LIMIT_MAX_MESSAGES", limit)
    monkeypatch.setattr(settings, "RATE_LIMIT_WINDOW_SECONDS", window)
    rate_limit._recent.clear()


def test_blocks_once_the_window_is_full(monkeypatch):
    from philoagents.config import settings

    _reset(settings, monkeypatch, limit=2)

    assert rate_limit.allow("player-a")[0] is True
    assert rate_limit.allow("player-a")[0] is True

    allowed, retry_after = rate_limit.allow("player-a")
    assert allowed is False
    assert retry_after > 0

    # A different player has their own budget.
    assert rate_limit.allow("player-b")[0] is True


def test_window_expiry_frees_the_slot(monkeypatch):
    from philoagents.config import settings

    _reset(settings, monkeypatch, limit=1, window=60)
    assert rate_limit.allow("player-a")[0] is True

    stamps = rate_limit._recent["player-a"]
    stamps[:] = [stamps[0] - 61]

    assert rate_limit.allow("player-a")[0] is True
