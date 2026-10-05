"""Five-Year Mission bonuses and challenges (plans/solo-mode.md Step 8; requirements/22-solo-mode.md §14.3, §14.4)."""

import inspect

import pytest

from engine import campaign as rules
from engine import upgrades
from engine.content import content
from engine.game import advance, choose, dismiss
from engine.ops import A, Actions, Ctx, OpRef, _state_checks
from engine.setup import BotSetup, CampaignSetup, SeatSetup, new_game

upgrades.load()
CARDS = content().cards


def game(deck="kirk", seed=3, reinforcement=(), **camp):
    return new_game(seed, "solo", [SeatSetup("Me", deck, "basic", tuple(reinforcement), CampaignSetup(**camp))], [],
                    False, bot=BotSetup("soval"))


def run_to_action(s, pick=lambda d: d.options[0].id):
    """Advance through setup, answering every question with `pick`, until the human's first Action Step."""
    advance(s, flag_irreversible=False)
    for _ in range(80):
        if s.step == "action" and s.decision and s.decision.kind == "action":
            return s
        if s.decision is None or s.step == "over":
            return s
        choose(s, s.decision.seat, pick(s.decision), flag_irreversible=False)
    raise AssertionError("setup did not finish")


# ------------------------------------------------------------------ the registry

def test_every_bonus_has_code_except_khans():
    for crew, data in content().command.items():
        for side, section in (("win", data.upgrades.win), ("loss", data.upgrades.loss)):
            for i, printed in enumerate(section.bonuses):
                key = upgrades.key(crew, side, i)
                if crew == "khan":
                    continue  # on hold with Khan's deck
                if printed.startswith("REINFORCE"):
                    assert key in upgrades.REINFORCES, key
                else:
                    assert key in upgrades.BOOSTS, key
                    impl = upgrades.BOOSTS[key]
                    assert impl.uses <= {v for k, v in vars(A).items() if k.isupper()}, key
                    doc = " ".join(inspect.getdoc(impl.fn).split())
                    assert doc == printed, (key, doc, printed)


def test_moments_follow_the_printed_text():
    for key, impl in upgrades.BOOSTS.items():
        printed = upgrades.text(key)
        expected = "before_hand" if "Before drawing" in printed else "after_hand" if "After drawing" in printed \
            else "start"
        assert impl.moment == expected, key


# ------------------------------------------------------------------ Boosts in a game

@pytest.mark.parametrize("key", sorted(upgrades.BOOSTS))
def test_every_boost_runs_to_the_first_turn(key):
    s = run_to_action(game(boosts=(key,)))
    assert s.step == "action" and s.turn == 0
    assert any("Boost" in e.text for e in s.log), key


def test_without_boosts_there_is_no_setup_step():
    s = game()
    assert s.step == "start" and len(s.players[0].hand) == 5


def test_boosts_run_around_the_starting_hand():
    s = game(boosts=("soval:win:1",))  # before the hand: find a Person and promote them
    assert s.step == "setup" and s.players[0].hand == []
    s = run_to_action(s)
    human = s.players[0]
    assert len(human.duty) == 1 and len(human.hand) == 5  # the hand is drawn after the Boost


def test_gain_one_of_each():
    human = run_to_action(game(boosts=("pike:win:1",))).players[0]
    assert (human.tracks["research"], human.tracks["influence"], human.tracks["military"]) == (1, 1, 1)


def test_gain_an_action_lasts_into_the_first_turn():
    from engine.content import content as c

    s = run_to_action(game(boosts=("georgiou:loss:1",)))
    human = s.players[0]
    assert human.actions == c().boards[human.board].actions + 1


def test_kirk_win_discards_the_top_card_then_gains_two():
    s = run_to_action(game(boosts=("kirk:win:0",)), pick=lambda d: next(
        (o.id for o in d.options if o.id == "military"), d.options[0].id))
    human = s.players[0]
    assert human.tracks["military"] == 2 and len(human.discard) == 1


def test_a_boost_with_a_cost_may_be_declined():
    s = run_to_action(game(boosts=("pike:win:0",)), pick=lambda d: next(
        (o.id for o in d.options if o.id == "no"), d.options[0].id))
    assert len(s.incident) == len(game().incident) and not s.players[0].enlisted


def test_a_boost_with_a_cost_takes_the_incident_then_enlists():
    s = run_to_action(game(boosts=("pike:win:0",)))
    assert len(s.incident) == len(game().incident) - 1 and s.players[0].enlisted


def test_a_boost_whose_cost_cannot_be_paid_is_skipped():
    s = game(boosts=("archer:win:1",), no_dilithium=True)
    s.players[0].glory = 0  # Glory would pay for the Dilithium (KW-SPEND-02)
    s = run_to_action(s)
    assert any("Boost skipped" in e.text for e in s.log)


def _incidents(p):
    return sum(CARDS[i.card].suit == "Incident" for i in p.hand + p.draw + p.discard)


def test_return_an_incident_after_the_hand():
    s = run_to_action(game(boosts=("freeman:win:1",), extra_incident=True))
    assert _incidents(s.players[0]) == _incidents(game(extra_incident=True).players[0]) - 1
    assert any("returns" in e.text for e in s.log)


def test_free_play_then_recall():
    s = run_to_action(game(boosts=("pike:loss:1",)))
    human = s.players[0]
    assert any("recalls" in e.text for e in s.log) or any("No non-Time Travel" in e.text for e in s.log)
    assert len(human.hand) >= 5 - 1


# ------------------------------------------------------------------ REINFORCE bonuses

def test_reinforce_pools():
    pools = rules.reinforce_pools("georgiou:win:0", "kirk")
    assert len(pools) == 2 and pools[0] and pools[1]
    assert all(CARDS[c].suit == "Person" and CARDS[c].position == "Available" for c in pools[0])
    assert all(CARDS[c].position == "Reserve" for c in pools[1])
    archer = rules.reinforce_pools("archer:loss:1", "kirk")[0]
    assert archer and all(CARDS[c].position == "Reserve" and CARDS[c].suit != "Incident" for c in archer)
    already = rules.reinforce_pools("freeman:loss:0", "kirk", reinforcement=pools[0][:1])[0]
    assert pools[0][0] not in already


def test_an_own_card_in_the_pile_leaves_the_deck():
    person = rules.reinforce_pools("freeman:loss:0", "kirk")[0][0]
    s = game(reinforcement=(person,))
    human = s.players[0]
    assert [i.card for i in human.reinforcement] == [person]
    assert not any(i.card == person for i in human.draw + human.hand + human.reserve)


# ------------------------------------------------------------------ challenges

def test_available_challenges():
    assert "only_ship" not in rules.available_challenges("soval")  # no starting deployed Ship
    assert "only_ship" in rules.available_challenges("kirk")
    assert "arrive_on_tuesday" in rules.available_challenges("pike")


def test_challenge_setup_follows_the_streak():
    all_on = list(rules.CHALLENGES)
    first = rules.game_setup("ensign", [], all_on, ())
    assert not first.no_dilithium and not first.mixed_reserve and not first.reinforce_in_reserve
    assert not first.extra_incident and first.only_ship and first.teams_aside == 1
    one = rules.game_setup("lieutenant", ["win"], all_on, (), "latinum")
    assert one.no_latinum and not one.no_dilithium and one.mixed_reserve and one.reinforce_in_reserve
    assert one.teams_aside == 2 and not one.extra_incident
    two = rules.game_setup("commander", ["loss", "win", "win"], all_on, ())
    assert two.no_dilithium and two.no_latinum and two.extra_incident
    reset = rules.game_setup("commander", ["win", "win", "loss"], all_on, ())
    assert not reset.no_dilithium and not reset.extra_incident and reset.teams_aside == 1
    assert rules.needs_resource_choice(["win"], all_on) and not rules.needs_resource_choice(["win", "win"], all_on)


def test_rules_of_acquisition_removes_option_b_after_a_success():
    assert rules.option_b("soval", True, ["rules_of_acquisition"]) == []
    assert rules.option_b("soval", False, ["rules_of_acquisition"]) == ["soval:loss:0", "soval:loss:1"]
    assert rules.option_b("khan", True) == []  # Khan waits


def test_live_long_and_prosper():
    human = game(no_dilithium=True, no_latinum=True).players[0]
    assert human.dilithium == 0 and human.latinum == 0 and human.glory == 1


def test_not_a_weakness():
    plain, mixed = game(seed=5).players[0], game(seed=5, mixed_reserve=True).players[0]
    assert len(mixed.reserve) == len(plain.reserve)
    every = lambda p: sorted(i.card for i in p.reserve + p.draw + p.hand)  # noqa: E731
    assert every(mixed) == every(plain)


def test_two_weeks_to_the_closest_outpost():
    human = game(reinforcement=("2PER16",), reinforce_in_reserve=True).players[0]
    assert any(i.card == "2DIR02" for i in human.reserve)
    assert not any(i.card == "2DIR02" for i in human.draw + human.hand)


def test_running_like_a_baby_gazelle():
    plain, gazelle = game(), game(extra_incident=True)
    assert len(gazelle.incident) == len(plain.incident) - 1
    assert _incidents(gazelle.players[0]) == _incidents(plain.players[0]) + 1


def _actions(s, seat=0, uses=(A.DISMISS, A.RECALL)):
    return Actions(Ctx(s, OpRef(mode="auto", seat=seat)), uses)


def test_only_ship_in_the_quadrant_dismissed():
    s = run_to_action(game(only_ship=True))
    human = s.players[0]
    ship = next(i for i in human.fleet if i.uid == human.only_ship)
    dismiss(s, human, ship)
    assert s.step == "over" and s.result["reason"] == "only_ship" and s.result["winners"] == [1]


def test_only_ship_in_the_quadrant_recalled():
    s = run_to_action(game(only_ship=True))
    human = s.players[0]
    ship = next(i for i in human.fleet if i.uid == human.only_ship)
    list(_actions(s).recall(ship))
    assert s.step == "over" and s.result["winners"] == [1]


def test_without_the_challenge_losing_the_ship_is_fine():
    s = run_to_action(game())
    human = s.players[0]
    dismiss(s, human, human.fleet[0])
    assert s.step != "over"


def test_they_will_arrive_on_tuesday():
    plain = game().players[0]
    s = game(teams_aside=2)
    human = s.players[0]
    assert human.away_pool == plain.away_pool - 2 and human.teams_until_reserve_empty == 2
    human.reserve.clear()
    _state_checks(s)
    assert human.away_pool == plain.away_pool and human.teams_until_reserve_empty == 0


# ------------------------------------------------------------------ the API

def create(client, **overrides):
    body = {"display_name": "Nick", "deck_id": "kirk", "mode": "set_phasers_to_stun", **overrides}
    return client.post("/api/campaigns", json=body)


def test_challenges_are_checked_against_the_crew(authed):
    assert create(authed, deck_id="soval", challenges=["only_ship"]).status_code == 422
    ids = [c["id"] for c in authed.get("/api/campaigns/challenges/soval").json()]
    assert "only_ship" not in ids and "baby_gazelle" in ids
    view = create(authed, challenges=["only_ship", "live_long_and_prosper"]).json()["campaign"]
    assert [c["id"] for c in view["challenges"]] == ["live_long_and_prosper", "only_ship"]
    assert "Losing your starting Ship fails the assignment." in view["next_notes"]


def _finish(monkeypatch, won):
    from app import play

    real = play.build

    def fake(game):
        state = real(game)
        state.step = "over"
        state.result = {"reason": "resolution", "winners": [0 if won else 1], "scores": []}
        return state

    monkeypatch.setattr("app.routes.campaigns.play.build", fake)


def test_a_boost_applies_in_the_next_game(authed, monkeypatch):
    grant = create(authed, expansions=["second_contact"]).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}
    authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "pike"}, headers=h)
    _finish(monkeypatch, won=True)
    view = authed.get(f"/api/campaigns/{cid}", headers=h).json()
    assert [b["key"] for b in view["upgrade"]["bonuses"]] == ["pike:win:0", "pike:win:1"]
    view = authed.post(f"/api/campaigns/{cid}/upgrade", json={"bonus": "pike:win:1"}, headers=h).json()
    assert view["assignments"][0]["upgrade"]["option"] == "B"
    monkeypatch.undo()
    r = authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "kirk"}, headers=h).json()
    state = authed.get(f"/api/games/{r['game_id']}/state", headers={"X-Seat-Token": r["seat_token"]}).json()
    me = state["players"][0]
    assert me["boosts"] == ["BOOST: Gain 1 [Research], 1 [Influence], and 1 [Military]."]
    assert (me["tracks"]["research"], me["tracks"]["influence"], me["tracks"]["military"]) == (1, 1, 1)


def test_a_reinforce_bonus_moves_own_cards(authed, monkeypatch):
    grant = create(authed).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}
    authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "georgiou"}, headers=h)
    _finish(monkeypatch, won=True)
    view = authed.get(f"/api/campaigns/{cid}", headers=h).json()
    bonus = next(b for b in view["upgrade"]["bonuses"] if b["key"] == "georgiou:win:0")
    assert bonus["kind"] == "reinforce" and bonus["each"] and len(bonus["pools"]) == 2
    a, b = bonus["pools"][0][0]["id"], bonus["pools"][1][0]["id"]
    second = bonus["pools"][0][1]["id"]
    assert authed.post(f"/api/campaigns/{cid}/upgrade", json={"bonus": "georgiou:win:0", "cards": [a, second]},
                       headers=h).status_code == 422  # one from each pool at most
    view = authed.post(f"/api/campaigns/{cid}/upgrade", json={"bonus": "georgiou:win:0", "cards": [a, b]},
                       headers=h).json()
    assert [c["id"] for c in view["reinforcement"]] == [a, b]


def test_live_long_asks_which_resource(authed, monkeypatch):
    grant = create(authed, challenges=["live_long_and_prosper"]).json()
    cid, h = grant["campaign"]["id"], {"X-Campaign-Token": grant["token"]}
    authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "soval"}, headers=h)
    _finish(monkeypatch, won=True)
    view = authed.post(f"/api/campaigns/{cid}/upgrade", json={"bonus": "soval:win:0"}, headers=h).json()
    assert view["choose_resource"]
    monkeypatch.undo()
    r = authed.post(f"/api/campaigns/{cid}/assignments", json={"bot_deck_id": "kirk", "drop": "latinum"},
                    headers=h).json()
    me = authed.get(f"/api/games/{r['game_id']}/state", headers={"X-Seat-Token": r["seat_token"]}).json()["players"][0]
    assert me["resources"]["latinum"] == 0 and me["resources"]["dilithium"] == 1
