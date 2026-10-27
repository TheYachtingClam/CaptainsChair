"""Tutorials (requirements/24-tutorials.md): the stacked setup, the rails, Next and Let me play, undo, and the Picard
script played through the API to the end of its guided turns."""

from engine.setup import SeatSetup, new_game


def start(client, tutorial_id="picard-basics"):
    r = client.post(f"/api/tutorials/{tutorial_id}")
    assert r.status_code == 201, r.text
    return r.json()["game"]["id"]


def state(client, game_id):
    return client.get(f"/api/games/{game_id}/state").json()


def follow(client, game_id, view):
    """One step as the coach asks: Next past an explanation, or the one move the step allows."""
    step = view["tutorial"]["step"]
    if step["next"]:
        return client.post(f"/api/games/{game_id}/tutorial/next")
    allowed = [o for o in view["decision"]["options"] if not o.get("disabled")]
    assert allowed, f"step {step['id']} allows no answer"
    return client.post(f"/api/games/{game_id}/commands", json={"option": allowed[0]["id"]})


def test_tutorials_are_listed(authed):
    listed = authed.get("/api/tutorials").json()
    assert {"id": "picard-basics", "title": "Learn to play with Picard",
            "summary": listed[0]["summary"]} in listed


def test_the_picard_script_plays_through_its_guided_turns(authed):
    """REQ-TUT-61: turns 1 to 3 on rails, every step reachable with the stacked decks, ending in free play."""
    game_id = start(authed)
    view = state(authed, game_id)
    assert view["mode"] == "cadet" and view["tutorial"]["index"] == 0 and view["tutorial"]["total"] == 63
    assert [c["id"] for c in view["players"][0]["hand"]] == ["1PIC19", "1PIC22", "1PIC17", "1PIC24", "1PIC16"]
    seen = []
    for _ in range(200):
        if view["tutorial"]["free"]:
            break
        seen.append(view["tutorial"]["step"]["id"])
        r = follow(authed, game_id, view)
        assert r.status_code == 200, (seen[-1], r.text)
        view = r.json()
    assert view["tutorial"]["free"] and len(seen) == 63
    me = view["players"][0]
    assert view["turn"] == 4 and view["decision"]["kind"] == "action"  # free play starts on turn 4
    assert {l["name"] for l in me["locations"]} == {"Verex III", "Farpoint Station"}
    assert [d["name"] for d in me["duty"]] == ["Will Riker"]
    enterprise = next(s for s in me["fleet"] if s["id"] == "1PIC02")
    assert [b["name"] for b in enterprise["beamed"]] == ["Tholians", "Halkan Council", "Bolians"]
    assert not any(o.get("disabled") for o in view["decision"]["options"])  # free play: everything allowed


def test_the_rails_refuse_other_moves(authed):
    """REQ-TUT-23: other answers are shown disabled and refused; Next only passes an explanation."""
    game_id = start(authed)
    view = state(authed, game_id)
    assert view["tutorial"]["step"]["next"] and all(o.get("disabled") for o in view["decision"]["options"])
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 409
    for _ in range(8):  # the welcome explanations
        view = authed.post(f"/api/games/{game_id}/tutorial/next").json()
    step = view["tutorial"]["step"]
    assert step["id"] == "utilize" and not step["next"]
    allowed = [o["id"] for o in view["decision"]["options"] if not o.get("disabled")]
    assert len(allowed) == 1 and allowed[0].startswith("play:") and allowed[0].endswith(":0")
    assert authed.post(f"/api/games/{game_id}/tutorial/next").status_code == 409  # this step waits for a move
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 409
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": allowed[0]}).status_code == 200


def test_undo_steps_the_coach_back(authed):
    """REQ-TUT-24: Next is stored as a move, so Back is an ordinary undo."""
    game_id = start(authed)
    view = authed.post(f"/api/games/{game_id}/tutorial/next").json()
    assert view["tutorial"]["index"] == 1 and view["can_undo"]
    view = authed.post(f"/api/games/{game_id}/undo").json()
    assert view["tutorial"]["index"] == 0


def test_let_me_play_ends_the_rails(authed):
    """REQ-TUT-25."""
    game_id = start(authed)
    view = authed.post(f"/api/games/{game_id}/tutorial/free").json()
    assert view["tutorial"]["free"] and view["tutorial"]["step"] is None
    assert not any(o.get("disabled") for o in view["decision"]["options"])
    assert authed.post(f"/api/games/{game_id}/commands", json={"option": "end"}).status_code == 200


def test_ordinary_games_have_no_coach(authed):
    r = authed.post("/api/games", json={"deck_id": "picard", "mode": "cadet", "box": "core"})
    view = state(authed, r.json()["game"]["id"])
    assert "tutorial" not in view and not any(o.get("disabled") for o in view["decision"]["options"])


def test_stacking_orders_the_decks_and_uses_no_randomness():
    """REQ-TUT-10, -11: stacking fixes the named cards and leaves the seed's later shuffles alone."""
    seats = [SeatSetup("You", "picard", "basic")]
    stack = {"hand": ["1PIC19", "1PIC22"], "draw": ["1PIC15"], "market": {"Ally": "1ALL13"},
             "market_decks": {"Ally": ["1ALL02"]}, "neutral": ["1LOC19", "1LOC12", "1LOC20"]}
    plain, stacked = new_game(7, "cadet", seats, box="core"), new_game(7, "cadet", seats, box="core", stack=stack)
    me = stacked.players[0]
    assert [i.card for i in me.hand][:2] == ["1PIC19", "1PIC22"] and len(me.hand) == 5 and me.draw[0].card == "1PIC15"
    assert sorted(i.card for i in me.hand + me.draw) == sorted(i.card for i in plain.players[0].hand + plain.players[0].draw)
    assert stacked.market["Ally"].card == "1ALL13" and stacked.market_decks["Ally"][0].card == "1ALL02"
    assert [i.card for i in stacked.neutral] == ["1LOC19", "1LOC12", "1LOC20"]
    assert stacked.rng_calls == plain.rng_calls
