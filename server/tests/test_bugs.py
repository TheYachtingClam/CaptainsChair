"""Bug reports (requirements/19-technical-architecture.md §5.5, REQ-BUG-01 to -08)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import bugs
from tests.test_admin import admin_on  # noqa: F401  (fixture)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def admin(authed, admin_on):  # noqa: F811
    """A session that is also signed in as the admin."""
    assert authed.post("/api/admin/login", json={"password": "admin-secret"}).status_code == 204
    return authed


def solo_game(client, **overrides):
    body = {"display_name": "Nick", "deck_id": "kirk", "mode": "solo",
            "bot": {"deck_id": "soval", "difficulty": "ensign"}, **overrides}
    r = client.post("/api/games", json=body)
    assert r.status_code == 201, r.text
    return r.json()["game"]["id"], {"X-Seat-Token": r.json()["seat_token"]}


def play_some(client, game_id, headers, moves=6):
    """Make a few moves: the first option each time, never ending the game."""
    for _ in range(moves):
        state = client.get(f"/api/games/{game_id}/state", headers=headers).json()
        options = state["decision"]["options"]
        pick = next((o for o in options if o["id"].startswith("play:")), options[0])
        assert client.post(f"/api/games/{game_id}/commands", json={"option": pick["id"]}, headers=headers).status_code == 200
    return client.get(f"/api/games/{game_id}/state", headers=headers).json()


def report(client, game_id, headers, text="The Glory did not arrive."):
    return client.post(f"/api/games/{game_id}/bugs", json={"description": text}, headers=headers)


def test_a_seated_player_reports_a_bug(authed):
    game_id, headers = solo_game(authed)
    assert report(authed, game_id, {}).status_code == 403  # no seat
    assert report(authed, game_id, headers, "   ").status_code == 422
    r = report(authed, game_id, headers)
    assert r.status_code == 201 and r.json()["id"]


def test_the_report_recreates_the_game_exactly(admin):
    authed = admin
    game_id, headers = solo_game(authed)
    seen = play_some(authed, game_id, headers)
    bug_id = report(authed, game_id, headers).json()["id"]
    play_some(authed, game_id, headers, moves=3)  # the game moves on; the report does not

    listed = authed.get("/api/admin/bugs").json()
    assert [b["id"] for b in listed] == [bug_id]
    assert listed[0]["reporter"] == "Nick" and listed[0]["status"] == "open" and listed[0]["moves"] == 6
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
    game_id, headers = solo_game(authed)
    bug_id = report(authed, game_id, headers).json()["id"]
    assert authed.get("/api/admin/bugs").status_code in (401, 403, 404)
    assert authed.get(f"/api/admin/bugs/{bug_id}").status_code in (401, 403, 404)


def test_a_report_outlives_its_game_and_can_be_recreated(admin):
    authed = admin
    game_id, headers = solo_game(authed)
    seen = play_some(authed, game_id, headers)
    bug_id = report(authed, game_id, headers).json()["id"]
    assert authed.delete(f"/api/games/{game_id}", headers=headers).status_code == 204

    r = authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={})
    assert r.status_code == 200, r.text
    copy = r.json()
    assert copy["game_id"] != game_id and copy["reporter_seat"] == 0
    copy_headers = {"X-Seat-Token": copy["seat_tokens"]["0"]}
    state = authed.get(f"/api/games/{copy['game_id']}/state", headers=copy_headers).json()
    assert state["decision"] == seen["decision"] and state["you"] == 0
    # The copy is an ordinary game: it can be played on.
    option = state["decision"]["options"][0]["id"]
    assert authed.post(f"/api/games/{copy['game_id']}/commands", json={"option": option},
                       headers=copy_headers).status_code == 200

    back = authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={"moves": 3}).json()
    earlier = authed.get(f"/api/games/{back['game_id']}/state",
                         headers={"X-Seat-Token": back["seat_tokens"]["0"]}).json()
    assert len(earlier["log"]) < len(state["log"])
    assert authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={"moves": 99}).status_code == 422


def test_resolving_and_deleting_a_report(admin):
    authed = admin
    game_id, headers = solo_game(authed)
    bug_id = report(authed, game_id, headers).json()["id"]
    r = authed.post(f"/api/admin/bugs/{bug_id}/status", json={"status": "resolved"})
    assert r.status_code == 200 and r.json()["status"] == "resolved"
    assert authed.post(f"/api/admin/bugs/{bug_id}/status", json={"status": "fixed"}).status_code == 422
    assert authed.delete(f"/api/admin/bugs/{bug_id}").status_code == 204
    assert authed.get("/api/admin/bugs").json() == []
    assert authed.get(f"/api/admin/bugs/{bug_id}").status_code == 404


def test_a_two_player_report_gives_a_token_for_every_seat(admin):
    authed = admin
    r = authed.post("/api/games", json={"display_name": "Ann", "deck_id": "georgiou", "mode": "two_player"})
    game_id, ann = r.json()["game"]["id"], {"X-Seat-Token": r.json()["seat_token"]}
    assert report(authed, game_id, ann).status_code == 409  # not started
    j = authed.post(f"/api/games/{game_id}/join", json={"display_name": "Bob", "deck_id": "soval"})
    bob = {"X-Seat-Token": j.json()["seat_token"]}
    bug_id = report(authed, game_id, bob, "Seen from the second seat.").json()["id"]
    copy = authed.post(f"/api/admin/bugs/{bug_id}/recreate", json={}).json()
    assert copy["reporter_seat"] == 1 and set(copy["seat_tokens"]) == {"0", "1"}
    view = authed.get(f"/api/games/{copy['game_id']}/state", headers={"X-Seat-Token": copy["seat_tokens"]["1"]}).json()
    assert view["you"] == 1


def test_replay_script_reads_a_downloaded_report(admin, tmp_path):
    authed = admin
    game_id, headers = solo_game(authed)
    play_some(authed, game_id, headers)
    bug_id = report(authed, game_id, headers).json()["id"]
    path = tmp_path / "report.json"
    path.write_text(json.dumps(authed.get(f"/api/admin/bugs/{bug_id}").json()))
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "replay_bug.py"), str(path), "--back", "2",
                          "--state", str(tmp_path / "state.json")], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    assert "Replayed 4 of 6 commands" in out.stdout and "The Glory did not arrive." in out.stdout
    assert "Waiting for seat 0" in out.stdout and json.loads((tmp_path / "state.json").read_text())["seed"]
