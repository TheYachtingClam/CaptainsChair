"""Bug reports (requirements/19-technical-architecture.md §5.5, REQ-BUG-01 to -08)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import bugs
from tests.conftest import another_browser, sign_in_as

ROOT = Path(__file__).resolve().parents[2]


def solo_game(client, **overrides):
    body = {"deck_id": "kirk", "mode": "solo",
            "bot": {"deck_id": "soval", "difficulty": "ensign"}, **overrides}
    r = client.post("/api/games", json=body)
    assert r.status_code == 201, r.text
    return r.json()["game"]["id"]


def play_some(client, game_id, moves=6):
    """Make a few moves: the first option each time, never ending the game."""
    for _ in range(moves):
        state = client.get(f"/api/games/{game_id}/state").json()
        options = state["decision"]["options"]
        pick = next((o for o in options if o["id"].startswith("play:")), options[0])
        assert client.post(f"/api/games/{game_id}/commands", json={"option": pick["id"]}).status_code == 200
    return client.get(f"/api/games/{game_id}/state").json()


def report(client, game_id, text="The Glory did not arrive."):
    return client.post(f"/api/games/{game_id}/bugs", json={"description": text})


def test_a_seated_player_reports_a_bug(authed):
    game_id = solo_game(authed)
    other = sign_in_as(another_browser(authed), "sam@example.com", "Sam")
    assert report(other, game_id).status_code == 403  # no seat
    assert report(authed, game_id, "   ").status_code == 422
    r = report(authed, game_id)
    assert r.status_code == 201 and r.json()["id"]


def test_the_report_recreates_the_game_exactly(admin):
    """The admin plays a game of their own, then reports on it."""
    authed = admin
    game_id = solo_game(authed)
    seen = play_some(authed, game_id)
    bug_id = report(authed, game_id).json()["id"]
    play_some(authed, game_id, moves=3)  # the game moves on; the report does not

    listed = authed.get("/api/admin/bugs").json()
    assert [b["id"] for b in listed] == [bug_id]
    assert listed[0]["reporter"] == "Admin" and listed[0]["status"] == "open" and listed[0]["moves"] == 6
    full = authed.get(f"/api/admin/bugs/{bug_id}").json()
    data = full["bundle"]
    assert data["game"]["seed"] and len(data["commands"]) == 6 and data["recent_log"]
    assert data["view"]["decision"] == seen["decision"]  # what the reporter was looking at

    state = bugs.rebuild(data)
    assert state.turn == data["turn"] and state.step == data["step"]
    assert [o.id for o in state.decision.options] == [o["id"] for o in data["decision"]["options"]]
    earlier = bugs.rebuild(data, moves=2)
    assert len(earlier.log) < len(state.log)  # a little way back in time


def test_reports_need_the_admin(authed):
    game_id = solo_game(authed)
    bug_id = report(authed, game_id).json()["id"]
    assert authed.get("/api/admin/bugs").status_code in (401, 403, 404)
    assert authed.get(f"/api/admin/bugs/{bug_id}").status_code in (401, 403, 404)


def test_a_report_outlives_its_game_and_can_be_recreated(admin):
    authed = admin
    game_id = solo_game(authed)
    seen = play_some(authed, game_id)
    bug_id = report(authed, game_id).json()["id"]
    assert authed.delete(f"/api/games/{game_id}").status_code == 204

    r = authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={})
    assert r.status_code == 200, r.text
    copy = r.json()
    assert copy["game_id"] != game_id and copy["reporter_seat"] == 0
    state = authed.get(f"/api/games/{copy['game_id']}/state").json()
    assert state["decision"] == seen["decision"] and state["you"] == 0
    # The copy is an ordinary game: it can be played on.
    option = state["decision"]["options"][0]["id"]
    assert authed.post(f"/api/games/{copy['game_id']}/commands", json={"option": option}).status_code == 200

    back = authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={"moves": 3}).json()
    earlier = authed.get(f"/api/games/{back['game_id']}/state").json()
    assert len(earlier["log"]) < len(state["log"])
    assert authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={"moves": 99}).status_code == 422


def test_resolving_and_deleting_a_report(admin):
    authed = admin
    game_id = solo_game(authed)
    bug_id = report(authed, game_id).json()["id"]
    r = authed.post(f"/api/admin/bugs/{bug_id}/status", json={"status": "resolved"})
    assert r.status_code == 200 and r.json()["status"] == "resolved"
    assert authed.post(f"/api/admin/bugs/{bug_id}/status", json={"status": "fixed"}).status_code == 422
    assert authed.delete(f"/api/admin/bugs/{bug_id}").status_code == 204
    assert authed.get("/api/admin/bugs").json() == []
    assert authed.get(f"/api/admin/bugs/{bug_id}").status_code == 404


def test_a_two_player_copy_seats_the_admin_in_every_seat(admin):
    """REQ-BUG-07: the admin plays both sides of the copy; each request acts in the seat whose decision is pending."""
    ann = sign_in_as(another_browser(admin), "ann@example.com", "Ann")
    game_id = ann.post("/api/games", json={"deck_id": "georgiou", "mode": "two_player"}).json()["game"]["id"]
    assert report(ann, game_id).status_code == 409  # not started
    bob = sign_in_as(another_browser(admin), "bob@example.com", "Bob")
    bob.post(f"/api/games/{game_id}/join", json={"deck_id": "soval"})
    bug_id = report(bob, game_id, "Seen from the second seat.").json()["id"]
    copy = admin.post(f"/api/admin/bugs/{bug_id}/recreate", json={}).json()
    assert copy["reporter_seat"] == 1
    view = admin.get(f"/api/games/{copy['game_id']}/state").json()
    assert view["you"] == view["decision"]["seat"]
    option = view["decision"]["options"][0]["id"]
    assert admin.post(f"/api/games/{copy['game_id']}/commands", json={"option": option}).status_code == 200


def test_replay_script_reads_a_downloaded_report(admin, tmp_path):
    authed = admin
    game_id = solo_game(authed)
    play_some(authed, game_id)
    bug_id = report(authed, game_id).json()["id"]
    path = tmp_path / "report.json"
    download = authed.get(f"/api/admin/bugs/{bug_id}/download")
    assert download.status_code == 200 and "attachment" in download.headers["content-disposition"]
    path.write_bytes(download.content)
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "replay_bug.py"), str(path), "--back", "2",
                          "--state", str(tmp_path / "state.json")], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    assert "Replayed 4 of 6 commands" in out.stdout and "The Glory did not arrive." in out.stdout
    assert "Waiting for seat 0" in out.stdout and json.loads((tmp_path / "state.json").read_text())["seed"]


def test_the_seed_survives_the_download_exactly(admin):
    """A 63-bit seed rounded by JavaScript made a downloaded report replay a different game (bug e5ee84fa)."""
    from app.db import get_db
    from app.main import app
    from app.models import Game

    authed = admin
    game_id = solo_game(authed)
    db = next(app.dependency_overrides.get(get_db, get_db)())
    game = db.get(Game, game_id)
    game.seed = 6233931749992975690  # above 2**53: a JavaScript number would round it to ...975000
    db.commit()
    play_some(authed, game_id)
    bug_id = report(authed, game_id).json()["id"]
    raw = authed.get(f"/api/admin/bugs/{bug_id}/download").content.decode()
    assert '"6233931749992975690"' in raw  # written as text, so no client can round it
    data = json.loads(raw)["bundle"]
    assert bugs.as_game(data).seed == 6233931749992975690
    assert bugs.rebuild(data).log[-1].text.startswith("The rules engine changed") is False


def test_a_feature_request_keeps_the_game_too(admin):
    """REQ-BUG-09."""
    authed = admin
    game_id = solo_game(authed)
    play_some(authed, game_id, moves=3)
    r = authed.post(f"/api/games/{game_id}/bugs", json={"description": "Show the Bot's hand size.", "kind": "feature"})
    assert r.status_code == 201
    assert report(authed, game_id).status_code == 201  # a bug, by default
    assert authed.post(f"/api/games/{game_id}/bugs", json={"description": "x", "kind": "wish"}).status_code == 422
    listed = {b["description"]: b for b in authed.get("/api/admin/bugs").json()}
    feature = listed["Show the Bot's hand size."]
    assert feature["kind"] == "feature" and feature["moves"] == 3 and listed["The Glory did not arrive."]["kind"] == "bug"
    data = authed.get(f"/api/admin/bugs/{feature['id']}").json()["bundle"]
    assert bugs.rebuild(data).turn == data["turn"]
