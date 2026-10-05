"""Five-Year Mission, the core campaign (plans/solo-mode.md Step 7; requirements/22-solo-mode.md §14)."""

from engine import campaign as rules
from engine.content import content
from engine.game import advance, choose
from engine.setup import BotSetup, SeatSetup, new_game

CARDS = content().cards


# ------------------------------------------------------------------ the rules (engine/campaign.py)

def test_difficulty_table():
    assert rules.difficulty("ensign", "set_phasers_to_stun") == "ensign"
    assert rules.difficulty("ensign", "kobayashi_maru") == "admiral"
    assert rules.difficulty("commander", "gates_of_sto_vo_kor") == "admiral"
    assert rules.difficulty("commodore", "set_phasers_to_stun") == "captain"
    assert rules.difficulty("captain", "yellow_alert") == "captain"


def test_ranks_and_the_end():
    assert rules.promoted("ensign") == "lieutenant" and rules.promoted("commodore") == "admiral"
    assert rules.finished("admiral", 5) and rules.finished("captain", 10) and not rules.finished("captain", 9)
    assert rules.evaluation("admiral", 5) == "The Legends: Archer, Kirk, Picard, you…"
    assert rules.evaluation("admiral", 8) == "Section 31 will be in touch…"
    assert rules.evaluation("admiral", 10) == "Welcome to Starfleet Command!"
    assert rules.evaluation("ensign", 10) == "You are like an eternal Harry Kim."


def test_upgrade_restrictions():
    assert rules.restriction("soval", True) == "Telepath / [Research]"
    assert rules.matches_restriction("2PER16", "Telepath / [Research]")  # Riva: Telepath
    assert not rules.matches_restriction("2PER07", "Telepath / [Research]")  # Hoshi Sato
    helmet_cargo = next(k for k, c in CARDS.items() if c.is_common and c.suit == "Cargo" and "Helmet" in c.traits)
    other_cargo = next(k for k, c in CARDS.items() if c.is_common and c.suit == "Cargo" and "Helmet" not in c.traits)
    assert rules.matches_restriction(other_cargo, "Cargo (except Helmet)")
    assert not rules.matches_restriction(helmet_cargo, "Cargo (except Helmet)")


def test_only_market_cards_can_be_reinforced():
    """REQ-CAMP-24: never an Encounter, an Incident, or a common Location."""
    assert rules.can_be_reinforced("2PER16")
    assert not rules.can_be_reinforced("2INC02") and not rules.can_be_reinforced("2ENC08")
    assert not rules.can_be_reinforced("2LOC05") and not rules.can_be_reinforced("2SOV06")  # a Crew card


def test_option_a_lists_matching_cards_you_had():
    s = new_game(1, "solo", [SeatSetup("Me", "kirk", "basic")], [], False, bot=BotSetup("soval"))
    human = s.players[0]
    human.discard += [s.new_inst("2PER16"), s.new_inst("2PER16"), s.new_inst("2PER07")]
    assert rules.option_a_cards(s, human, "soval", True) == ["2PER16"]


# ------------------------------------------------------------------ the Reinforcement pile and Reinforce

def campaign_game(reinforcement=("2PER16", "2PER07"), seed=2):
    s = new_game(seed, "solo", [SeatSetup("Me", "kirk", "basic", tuple(reinforcement))], [], False,
                 bot=BotSetup("soval"))
    advance(s, flag_irreversible=False)
    return s


def test_reinforce_is_shuffled_in_when_the_pile_has_cards():
    s = campaign_game()
    human = s.players[0]
    assert [i.card for i in human.reinforcement] == ["2PER16", "2PER07"]
    assert any(i.card == "2DIR02" for i in human.draw + human.hand)
    s2 = campaign_game(reinforcement=())
    assert not any(i.card == "2DIR02" for i in s2.players[0].draw + s2.players[0].hand)


def test_reinforcement_cards_do_not_score_until_taken():
    from engine.scoring import owned_cards

    s = campaign_game()
    assert not any(i.card == "2PER16" for i in owned_cards(s.players[0]))


def test_reinforce_takes_a_card_from_the_pile():
    s = campaign_game()
    human = s.players[0]
    reinforce = next(i for i in human.draw + human.hand if i.card == "2DIR02")
    if reinforce in human.draw:
        human.draw.remove(reinforce)
        human.hand.append(reinforce)
    s.decision = None
    advance(s, flag_irreversible=False)
    choose(s, 0, f"play:{reinforce.uid}:0", flag_irreversible=False)
    option = next(o for o in s.decision.options if "Riva" in o.label)
    choose(s, 0, option.id, flag_irreversible=False)
    human = s.players[0]
    assert any(i.card == "2PER16" for i in human.hand) and [i.card for i in human.reinforcement] == ["2PER07"]
    assert f"play:{reinforce.uid}:1" not in {o.id for o in s.decision.options}  # the pile is not empty


def test_reinforce_with_an_empty_pile_draws_and_logs_itself():
    s = campaign_game(reinforcement=("2PER16",))
    human = s.players[0]
    human.reinforcement.clear()
    reinforce = next(i for i in human.draw + human.hand if i.card == "2DIR02")
    if reinforce in human.draw:
        human.draw.remove(reinforce)
        human.hand.append(reinforce)
    s.decision = None
    advance(s, flag_irreversible=False)
    assert f"play:{reinforce.uid}:0" not in {o.id for o in s.decision.options}
    hand = len(human.hand)
    choose(s, 0, f"play:{reinforce.uid}:1", flag_irreversible=False)
    human = s.players[0]
    assert len(human.hand) == hand and any(i.card == "2DIR02" for i in human.log)


# ------------------------------------------------------------------ the API (app/routes/campaigns.py)

def create(client, **overrides):
    body = {"display_name": "Nick", "deck_id": "kirk", "mode": "set_phasers_to_stun", **overrides}
    return client.post("/api/campaigns", json=body)


def test_a_campaign_needs_its_link(authed):
    r = create(authed)
    assert r.status_code == 201
    cid = r.json()["campaign"]["id"]
    assert authed.get(f"/api/campaigns/{cid}").status_code == 403
    assert authed.get(f"/api/campaigns/{cid}", headers={"X-Campaign-Token": "nope"}).status_code == 403
    view = authed.get(f"/api/campaigns/{cid}", headers={"X-Campaign-Token": r.json()["token"]}).json()
    assert view["rank"] == "ensign" and view["phase"] == "start" and view["assignments_left"] == 10
    assert "khan" not in {o["deck_id"] for o in view["opponents"]}


def test_unknown_mode_is_rejected(authed):
    assert create(authed, mode="easy").status_code == 422


def _finish_game(monkeypatch, won: bool, extra_cards=()):
    """Make the next build of a campaign game report it over."""
    from app import play

    real = play.build

    def fake(game):
        state = real(game)
        human = state.players[0]
        human.discard += [state.new_inst(c) for c in extra_cards]
        state.step = "over"
        state.result = {"reason": "resolution", "winners": [0 if won else 1],
                        "scores": [{"seat": 0, "name": "Nick", "total": 50}, {"seat": 1, "name": "Bot", "total": 40}]}
        return state

    monkeypatch.setattr("app.routes.campaigns.play.build", fake)


def test_assignment_flow(authed, monkeypatch):
    grant = create(authed).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}

    r = authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "soval"}, headers=h)
    assert r.status_code == 201
    started = r.json()
    assert started["campaign"]["phase"] == "playing" and started["seat_token"]
    game = authed.get(f"/api/games/{started['game_id']}").json()
    assert game["mode"] == "solo" and game["bot"]["difficulty"] == "ensign" and game["campaign_id"] == cid
    # Only one assignment at a time.
    assert authed.post(f"/api/campaigns/{cid}/assignments", json={}, headers=h).status_code == 409

    _finish_game(monkeypatch, won=True, extra_cards=("2PER16",))
    view = authed.get(f"/api/campaigns/{cid}", headers=h).json()
    assert view["rank"] == "lieutenant" and view["phase"] == "upgrade"
    assert view["upgrade"]["won"] and [c["id"] for c in view["upgrade"]["options"]] == ["2PER16"]
    assert authed.post(f"/api/campaigns/{cid}/upgrade", json={"card_id": "2PER07"}, headers=h).status_code == 422
    view = authed.post(f"/api/campaigns/{cid}/upgrade", json={"card_id": "2PER16"}, headers=h).json()
    assert [c["id"] for c in view["reinforcement"]] == ["2PER16"] and view["phase"] == "start"
    # A Bot you have beaten cannot be faced again (REQ-CAMP-05).
    assert "soval" not in {o["deck_id"] for o in view["opponents"]}
    assert authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "soval"}, headers=h).status_code == 422

    # The next game is at the new rank's difficulty and brings the Reinforcement pile.
    monkeypatch.undo()
    r = authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "kirk"}, headers=h).json()
    game = authed.get(f"/api/games/{r['game_id']}").json()
    assert game["bot"]["difficulty"] == "lieutenant"
    state = authed.get(f"/api/games/{r['game_id']}/state", headers={"X-Seat-Token": r["seat_token"]}).json()
    assert [c["id"] for c in state["players"][0]["reinforcement"]] == ["2PER16"]


def test_a_loss_keeps_the_rank_and_with_no_card_option_b_is_required(authed, monkeypatch):
    grant = create(authed).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}
    authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "soval"}, headers=h)
    _finish_game(monkeypatch, won=False)
    view = authed.get(f"/api/campaigns/{cid}", headers=h).json()
    assert view["rank"] == "ensign" and view["phase"] == "upgrade" and not view["upgrade"]["won"]
    assert view["upgrade"]["options"] == []
    assert [b["key"] for b in view["upgrade"]["bonuses"]] == ["soval:loss:0", "soval:loss:1"]
    assert authed.post(f"/api/campaigns/{cid}/upgrade", json={}, headers=h).status_code == 422  # must pick B
    view = authed.post(f"/api/campaigns/{cid}/upgrade", json={"bonus": "soval:loss:0"}, headers=h).json()
    assert view["boosts"] == ["BOOST: Gain 1 [Research]/[Military]."] and view["phase"] == "start"


def test_reaching_admiral_ends_the_campaign(authed, monkeypatch):
    from app.db import get_db
    from app.models import Campaign

    grant = create(authed).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}
    db = next(authed.app.dependency_overrides.get(get_db, get_db)())
    camp = db.get(Campaign, cid)
    camp.rank = "commodore"
    db.commit()
    authed.post(f"/api/campaigns/{cid}/assignments", json={}, headers=h)
    _finish_game(monkeypatch, won=True)
    view = authed.get(f"/api/campaigns/{cid}", headers=h).json()
    assert view["rank"] == "admiral" and view["phase"] == "finished"
    assert view["evaluation"] == "The Legends: Archer, Kirk, Picard, you…"

