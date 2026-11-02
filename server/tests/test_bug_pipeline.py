"""Fetching bug reports with the bug token (REQ-BUG-10), and scripts/bugs.py (plans/bug-pipeline.md)."""

import importlib.util
import io
import json
from pathlib import Path

import pytest

from app.config import get_settings
from tests.conftest import another_browser
from tests.test_bugs import play_some, report, solo_game

ROOT = Path(__file__).resolve().parents[2]
TOKEN = "a-long-random-bug-token-for-tests"
spec = importlib.util.spec_from_file_location("bugs_cli", ROOT / "scripts" / "bugs.py")
bugs_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bugs_cli)


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setattr(get_settings(), "bug_api_token", TOKEN)
    return TOKEN


def bearer(value):
    return {"Authorization": f"Bearer {value}"}


@pytest.fixture
def filed(admin):
    """An admin's solo game with a bug report; returns (admin browser, report id)."""
    game_id = solo_game(admin)
    play_some(admin, game_id)
    return admin, report(admin, game_id, "Nick's Glory did not arrive.").json()["id"]


def test_the_token_lists_downloads_and_resolves(filed, token):
    admin, bug_id = filed
    robot = another_browser(admin)  # no cookies
    listed = robot.get("/api/admin/bugs", headers=bearer(token))
    assert listed.status_code == 200 and [b["id"] for b in listed.json()] == [bug_id]
    assert robot.get(f"/api/admin/bugs/{bug_id}", headers=bearer(token)).json()["bundle"]["commands"]
    download = robot.get(f"/api/admin/bugs/{bug_id}/download", headers=bearer(token))
    assert download.status_code == 200 and json.loads(download.content)["id"] == bug_id
    r = robot.post(f"/api/admin/bugs/{bug_id}/status", json={"status": "resolved"}, headers=bearer(token))
    assert r.status_code == 200 and r.json()["status"] == "resolved"


def test_a_wrong_or_missing_token_is_refused(filed, token):
    admin, bug_id = filed
    robot = another_browser(admin)
    assert robot.get("/api/admin/bugs").status_code == 401
    assert robot.get("/api/admin/bugs", headers=bearer("not-the-token")).status_code == 401
    assert robot.get(f"/api/admin/bugs/{bug_id}/download", headers={"Authorization": "Basic x"}).status_code == 401


def test_no_token_configured_turns_the_route_off(filed, monkeypatch):
    admin, _ = filed
    monkeypatch.setattr(get_settings(), "bug_api_token", "")
    robot = another_browser(admin)
    assert robot.get("/api/admin/bugs", headers=bearer("")).status_code == 401
    assert robot.get("/api/admin/bugs", headers=bearer("anything")).status_code == 401


def test_the_admin_session_still_works(filed, token):
    admin, bug_id = filed
    assert admin.get("/api/admin/bugs").status_code == 200
    assert admin.get(f"/api/admin/bugs/{bug_id}/download").status_code == 200


def test_the_token_opens_nothing_else(filed, token):
    """Every other admin endpoint, and the player endpoints, refuse the token."""
    admin, bug_id = filed
    robot = another_browser(admin)
    h = bearer(token)
    game_id = admin.get("/api/admin/games").json()[0]["id"]
    refused = [
        robot.delete(f"/api/admin/bugs/{bug_id}", headers=h),
        robot.post(f"/api/admin/bugs/{bug_id}/recreate", json={}, headers=h),
        robot.get("/api/admin/games", headers=h),
        robot.get("/api/admin/users", headers=h),
        robot.get("/api/admin/invites", headers=h),
        robot.get("/api/admin/campaigns", headers=h),
        robot.get(f"/api/admin/games/{game_id}/observe", headers=h),
        robot.get("/api/admin/status", headers=h),
        robot.get(f"/api/games/{game_id}/state", headers=h),
        robot.get("/api/me/games", headers=h),
    ]
    assert all(r.status_code in (401, 403) for r in refused), [(r.url, r.status_code) for r in refused]
    assert admin.get("/api/admin/bugs").json()[0]["status"] == "open"


def test_wrong_tokens_are_rate_limited(filed, token):
    admin, _ = filed
    robot = another_browser(admin)
    codes = [robot.get("/api/admin/bugs", headers=bearer(f"guess-{i}")).status_code for i in range(8)]
    assert codes[0] == 401 and codes[-1] == 429


# ------------------------------------------------------------------ scripts/bugs.py

def transport_for(client, token=TOKEN):
    """scripts/bugs.py's transport, sending through the test client in place of the network."""
    def send(method, path, body):
        r = client.request(method, path, json=body, headers=bearer(token))
        return r.status_code, r.content
    return send


def run(client, *argv, tmp_path, token=TOKEN):
    out = io.StringIO()
    code = bugs_cli.run(list(argv), transport_for(client, token), out=out,
                        downloads=tmp_path / "bugs", fixtures=tmp_path / "fixtures")
    return code, out.getvalue()


def test_the_script_lists_gets_and_resolves(filed, token, tmp_path):
    admin, bug_id = filed
    robot = another_browser(admin)
    code, out = run(robot, "list", tmp_path=tmp_path)
    assert code == 0 and bug_id[:8] in out and "Glory did not arrive" in out

    code, out = run(robot, "get", bug_id[:5], tmp_path=tmp_path)
    saved = tmp_path / "bugs" / f"bug-{bug_id}.json"
    assert code == 0 and saved.exists() and json.loads(saved.read_text())["bundle"]["commands"]
    assert saved.read_bytes() == admin.get(f"/api/admin/bugs/{bug_id}/download").content  # the Admin page's file

    assert run(robot, "resolve", bug_id[:6], tmp_path=tmp_path)[0] == 0
    assert "No open reports." in run(robot, "list", tmp_path=tmp_path)[1]
    assert bug_id[:8] in run(robot, "list", "--all", tmp_path=tmp_path)[1]
    assert run(robot, "reopen", bug_id[:6], tmp_path=tmp_path)[0] == 0
    assert bug_id[:8] in run(robot, "list", tmp_path=tmp_path)[1]


def test_newest_is_the_newest_open_bug_not_a_suggestion(filed, token, tmp_path):
    admin, bug_id = filed
    game_id = admin.get("/api/admin/games").json()[0]["id"]
    admin.post(f"/api/games/{game_id}/bugs", json={"description": "A wish", "kind": "feature"})
    code, _ = run(another_browser(admin), "get", "newest", tmp_path=tmp_path)
    assert code == 0 and (tmp_path / "bugs" / f"bug-{bug_id}.json").exists()


def test_the_fixture_is_trimmed_and_replays(filed, token, tmp_path):
    from app import bugs

    admin, bug_id = filed
    code, _ = run(another_browser(admin), "fixture", bug_id, tmp_path=tmp_path)
    path = tmp_path / "fixtures" / f"{bug_id[:8]}.json"
    assert code == 0
    text = path.read_text()
    assert "Admin" not in text and "admin@example.com" not in text  # the players' names are gone
    fixture = json.loads(text)
    bundle = fixture["bundle"]
    assert {"view", "recent_log", "decision"}.isdisjoint(bundle)
    assert fixture["description"] == "Nick's Glory did not arrive."
    full = admin.get(f"/api/admin/bugs/{bug_id}").json()["bundle"]
    assert bundle["game"]["seed"] == full["game"]["seed"] and bundle["commands"] == full["commands"]
    state = bugs.rebuild(bundle)
    assert (state.turn, state.step) == (full["turn"], full["step"])


def test_the_script_explains_failures(filed, tmp_path, monkeypatch, capsys):
    admin, _ = filed
    monkeypatch.setattr(get_settings(), "bug_api_token", TOKEN)
    robot = another_browser(admin)
    assert run(robot, "list", tmp_path=tmp_path, token="wrong")[0] == 1
    assert "refused the token" in capsys.readouterr().err
    assert run(robot, "get", "zzzz", tmp_path=tmp_path)[0] == 1
    assert "No report id starts with" in capsys.readouterr().err
    monkeypatch.delenv("CC_URL", raising=False)
    assert bugs_cli.run(["list"]) == 2
