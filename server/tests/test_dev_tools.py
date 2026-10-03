"""Developer panel commands (engine/dev.py) and the scenario helper used by card tests."""

import pytest

from app.config import get_settings
from engine import dev
from engine.state import Inst
from tests.scenario import card, given, play


def uids(cards: list[Inst]) -> list[str]:
    return [i.uid for i in cards]


def test_given_builds_a_position():
    s = given(hand=["2GEO15"], duty=["2GEO21"], dilithium=3, tracks={"military": 4}, opp={"duty": ["2SOV05"]})
    me, opp = s.players
    assert s.decision.kind == "action" and s.decision.seat == 0
    assert card(s, "2GEO15").uid in uids(me.hand) and card(s, "2GEO21").uid in uids(me.duty)
    assert me.dilithium == 4 and me.tracks["military"] == 4
    assert any(i.card == "2SOV05" for i in opp.duty)


def test_a_given_card_is_immediately_playable():
    s = given(hand=["2GEO15"])
    analyze = card(s, "2GEO15")
    play(s, analyze, 2)
    assert analyze.uid in uids(s.players[0].staging)


def test_placing_a_card_triggers_nothing():
    s = given(duty=["2GEO21"])
    assert not s.pending_events and not s.op_queue and s.offer is None


def test_bad_commands_are_rejected():
    s = given()
    with pytest.raises(dev.DevCommandError):
        dev.apply(s, 0, {"kind": "card", "card": "NOPE", "zone": "hand"})
    with pytest.raises(dev.DevCommandError):
        dev.apply(s, 0, {"kind": "card", "card": "2GEO15", "zone": "nowhere"})
    with pytest.raises(dev.DevCommandError):
        dev.apply(s, 0, {"kind": "track", "track": "piloting", "amount": 1})


def test_no_dev_commands_while_a_card_resolves():
    s = given(hand=["2GEO15"])
    play(s, card(s, "2GEO15"), 0)  # asks which Ship to gain
    assert s.decision.kind == "op"
    with pytest.raises(dev.DevCommandError):
        dev.apply(s, 0, {"kind": "resource", "resource": "glory", "amount": 1})


# --------------------------------------------------------------------------- API


@pytest.fixture
def dev_on(monkeypatch):
    monkeypatch.setenv("DEV_TOOLS", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def cadet(authed):
    grant = authed.post("/api/games", json={"display_name": "Dev", "deck_id": "georgiou", "mode": "cadet"}).json()
    return grant["game"]["id"], {"X-Seat-Token": grant["seat_token"]}


def test_dev_endpoint_is_off_by_default(authed):
    get_settings.cache_clear()
    game_id, h = cadet(authed)
    r = authed.post(f"/api/games/{game_id}/dev", json={"kind": "resource", "resource": "glory", "amount": 1}, headers=h)
    assert r.status_code == 404
    assert authed.get(f"/api/games/{game_id}/state", headers=h).json()["dev_tools"] is False


def test_dev_commands_replay_and_undo(authed, dev_on):
    game_id, h = cadet(authed)
    r = authed.post(f"/api/games/{game_id}/dev", json={"kind": "card", "card": "2PER07", "zone": "hand"}, headers=h)
    assert r.status_code == 200
    view = r.json()
    assert view["dev_tools"] is True
    assert any(c["id"] == "2PER07" for c in view["players"][0]["hand"])
    # A fresh rebuild (no cache) replays the developer command.
    from app import play

    play._cache.clear()
    view = authed.get(f"/api/games/{game_id}/state", headers=h).json()
    assert any(c["id"] == "2PER07" for c in view["players"][0]["hand"]) and view["can_undo"]
    view = authed.post(f"/api/games/{game_id}/undo", headers=h).json()
    assert not any(c["id"] == "2PER07" for c in view["players"][0]["hand"])


def test_dev_command_needs_a_seat(authed, dev_on):
    game_id, _ = cadet(authed)
    r = authed.post(f"/api/games/{game_id}/dev", json={"kind": "resource", "resource": "glory", "amount": 1})
    assert r.status_code == 403
    r = authed.post(f"/api/games/{game_id}/dev", json={"kind": "card", "card": "XX", "zone": "hand"},
                    headers=cadet(authed)[1])
    assert r.status_code in (403, 409)
