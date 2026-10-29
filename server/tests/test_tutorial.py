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


def test_tutorials_are_listed_with_progress(authed):
    """REQ-TUT-42, -50: each tutorial, whether it is finished, and the game in progress."""
    listed = authed.get("/api/tutorials").json()
    assert [t["id"] for t in listed][:2] == ["picard-basics", "bot-basics"]  # the first tutorial first
    first = next(t for t in listed if t["id"] == "picard-basics")
    assert first["title"] == "Learn to play with Picard" and not first["finished"] and first["game_id"] is None
    game_id = start(authed)
    first = next(t for t in authed.get("/api/tutorials").json() if t["id"] == "picard-basics")
    assert first["game_id"] == game_id and not first["finished"]


def test_the_picard_script_plays_through_its_guided_turns(authed):
    """REQ-TUT-61: turns 1 to 3 on rails, every step reachable with the stacked decks, ending in free play."""
    game_id = start(authed)
    view = state(authed, game_id)
    assert view["mode"] == "cadet" and view["tutorial"]["index"] == 0 and view["tutorial"]["total"] == 65
    assert [c["id"] for c in view["players"][0]["hand"]] == ["1PIC19", "1PIC22", "1PIC17", "1PIC24", "1PIC16"]
    seen = []
    for _ in range(200):
        if view["tutorial"]["free"]:
            break
        seen.append(view["tutorial"]["step"]["id"])
        r = follow(authed, game_id, view)
        assert r.status_code == 200, (seen[-1], r.text)
        view = r.json()
    assert view["tutorial"]["free"] and len(seen) == 65
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


def play_rails(client, game_id):
    view = state(client, game_id)
    while not view["tutorial"]["free"]:
        view = follow(client, game_id, view).json()
    return view


def test_tips_appear_after_the_rails_one_at_a_time(authed):
    """REQ-TUT-31, -32: free play begins with Strange New Worlds in hand (a playable tip) and an Incident in hand."""
    game_id = start(authed)
    view = play_rails(authed, game_id)
    assert view["tutorial"]["tip"]["id"] == "strange-new-worlds" and view["tutorial"]["tip"]["show"] == "card:1PIC18"
    view = authed.post(f"/api/games/{game_id}/tutorial/tip").json()
    assert view["tutorial"]["tip"]["id"] == "incident-in-hand"
    view = authed.post(f"/api/games/{game_id}/undo").json()  # Got it is a move: undo brings the tip back
    assert view["tutorial"]["tip"]["id"] == "strange-new-worlds"
    authed.post(f"/api/games/{game_id}/tutorial/tip")
    view = authed.post(f"/api/games/{game_id}/tutorial/tip").json()
    assert view["tutorial"]["tip"] is None
    assert authed.post(f"/api/games/{game_id}/tutorial/tip").status_code == 409


def test_no_tips_while_on_the_rails(authed):
    game_id = start(authed)
    assert state(authed, game_id)["tutorial"]["tip"] is None


def test_the_end_of_game_moments():
    """REQ-TUT-32: the moments read the game's end flags."""
    from types import SimpleNamespace

    from app.tutorial import _triggered

    me = SimpleNamespace(tracks={"research": 4, "influence": 0, "military": 0}, hand=[])
    game = SimpleNamespace(players=[me], decision=None, stardates=[1, 2], result=None, last_turn=None, turn=3,
                           mode="cadet")
    assert _triggered({"track_at_least": 4}, game) and not _triggered({"moment": "stardate-empties"}, game)
    game.stardates = [1]
    assert _triggered({"moment": "stardate-empties"}, game) and not _triggered({"moment": "last-turn"}, game)
    game.last_turn, game.turn = 10, 10
    assert _triggered({"moment": "last-turn"}, game) and not _triggered({"moment": "game-over"}, game)
    game.result = {"reason": "resolution"}
    assert _triggered({"moment": "game-over"}, game) and _triggered({"moment": "final-scoring"}, game)
    assert not _triggered({"moment": "last-turn"}, game) and not _triggered({"moment": "stardate-empties"}, game)


def test_more_and_the_how_cards_work_sheet(authed):
    """REQ-TUT-20, -43: a step's optional detail, and the reference sheet behind the coach's "?"."""
    game_id = start(authed)
    view = state(authed, game_id)
    assert view["tutorial"]["step"]["id"] == "welcome" and "How cards work" in view["tutorial"]["step"]["more"]
    view = authed.post(f"/api/games/{game_id}/tutorial/next").json()
    view = authed.post(f"/api/games/{game_id}/tutorial/next").json()
    assert view["tutorial"]["step"]["id"] == "resources" and "2 Dilithium" in view["tutorial"]["step"]["more"]
    guide = authed.get("/api/tutorials/guides/how-cards-work").json()
    assert guide["title"] == "How cards work"
    assert all(r["term"] and r["means"] for s in guide["sections"] for r in s["rows"])
    assert authed.get("/api/tutorials/guides/nothing").status_code == 404
    assert authed.get("/api/tutorials/guides/..%2Fsecrets").status_code == 404


def test_the_bot_script_plays_through_its_guided_turns(authed):
    """plans/tutorial-bot.md: three guided turns against an Ensign Koloth Bot, its turns fixed by the stacked deck."""
    game_id = start(authed, "bot-basics")
    view = state(authed, game_id)
    assert view["mode"] == "solo" and view["players"][1]["bot"]
    seen = []
    for _ in range(200):
        if view["tutorial"]["free"]:
            break
        seen.append(view["tutorial"]["step"]["id"])
        r = follow(authed, game_id, view)
        assert r.status_code == 200, (seen[-1], r.text)
        view = r.json()
    assert view["tutorial"]["free"] and len(seen) == view["tutorial"]["total"]
    me, bot = view["players"]
    assert {l["name"] for l in me["locations"]} == {"Amargosa Observatory", "Farpoint Station"}
    assert [d["name"] for d in me["duty"]] == ["Will Riker"]
    archer = next(l for l in view["neutral_zone"] if l["name"] == "Archer IV")
    assert archer["away_teams"] == {"0": 3, "1": 1} and archer["secured_by"] == [0]  # the Bot's turn 3 gave it up
    assert not bot["duty"] and not bot["fleet"]
    assert "Phasers" not in [c["name"] for c in me["fleet"]]  # used up against the Disruptors attack


def test_the_khan_script_plays_through_its_guided_turns(authed):
    """plans/tutorial-khan.md: three guided turns of Khan in Cadet Training, against Archer's traits."""
    game_id = start(authed, "khan-basics")
    view = state(authed, game_id)
    seen = []
    for _ in range(200):
        if view["tutorial"]["free"]:
            break
        seen.append(view["tutorial"]["step"]["id"])
        r = follow(authed, game_id, view)
        assert r.status_code == 200, (seen[-1], r.text)
        view = r.json()
    assert view["tutorial"]["free"] and len(seen) == view["tutorial"]["total"]
    me = view["players"][0]
    assert [t["trait"] for t in me["traits"] if t["marked"]] == ["Ambassador", "Creature", "NX-01"]
    assert {l["name"] for l in me["locations"]} >= {"Ceti Alpha V", "Ceti Alpha VI", "Mutara Nebula", "Babel One"}
