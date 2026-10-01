import copy

import pytest

from engine.content import content
from engine.game import IllegalCommand, advance, choose, gain_glory, secured_by, take_incident
from engine.scoring import incidents_owned
from engine.setup import SeatSetup, SetupError, new_game
from engine.views import game_view

SEATS = [SeatSetup("Ann", "soval", "basic"), SeatSetup("Ben", "georgiou", "basic")]


def game(seed=7, seats=SEATS, **kw):
    state = new_game(seed, "two_player", seats, **kw)
    advance(state)
    return state


def pass_turn(state):
    """End the active player's turn with no plays: end actions, place Glory, draw up."""
    seat = state.active
    while state.active == seat and state.step != "over":
        d = state.decision
        option = {"action": "end", "discard": "done", "control": "skip"}.get(d.kind) or d.options[0].id
        choose(state, d.seat, option)


# --------------------------------------------------------------------------- setup


def test_central_setup():
    s = game()
    assert all(s.market[suit] is not None for suit in ("Person", "Cargo", "Ship", "Ally"))
    assert len(s.neutral) == 3
    assert len(s.stardates) == 5 and s.stardate_glory == content().cards[s.stardates[0].card].starting_glory
    assert len(s.incident) == 6 and len(s.encounter) == 8
    assert s.junk == [] and s.rewards == []


def test_player_setup_soval():
    p = game().players[0]
    assert p.captain.card == "2SOV01"
    assert [i.card for i in p.status] == ["2SOV02"]
    assert [i.card for i in p.locations] == ["2SOV03"]
    assert len(p.hand) == 5
    assert (p.dilithium, p.latinum, p.glory) == (1, 1, 1)
    assert p.away_pool == 4 and p.actions == 3 and p.mission_tokens == 1
    total = len(p.hand) + len(p.draw) + len(p.reserve) + len(p.development) + len(p.discard) + len(p.fleet) + len(p.locations) + len(p.status) + 1
    assert total == 24


def test_special_setups():
    s = new_game(3, "two_player", [SeatSetup("R", "rebner", "basic"), SeatSetup("K", "khan", "advanced")])
    rebner, khan = s.players
    assert len(rebner.hand) == 3  # REQ-CD-REB-01
    assert len(khan.hand) == 6  # Ceti Alpha V (REQ-CD-KHN-02)
    assert all(not i.card.endswith("B") for i in khan.draw + khan.development + khan.locations)
    s = new_game(3, "two_player", [SeatSetup("A", "archer", "basic"), SeatSetup("P", "pike", "basic")], expansions=["second_contact"])
    archer, pike = s.players
    assert archer.away_pool == 2 and archer.away_aside == 4
    starbase = next(i for i in pike.locations if i.card == "3PIK03")
    assert starbase.away == {1: 1}
    assert len(s.junk) == 4 and len(s.rewards) == 8  # REQ-EXP-12, REQ-EXP-14


def test_promos_and_rhapsody():
    s = new_game(5, "two_player", SEATS, promos=True)
    ids = [i.card for i in s.incident]
    assert "0INC03" in ids and len(ids) == 6  # replaces a random Incident (REQ-CS-22)


def test_setup_is_deterministic():
    a, b = game(seed=11), game(seed=11)
    assert a.model_dump() == b.model_dump()
    assert game(seed=12).model_dump() != a.model_dump()


def test_unsupported_mode():
    with pytest.raises(SetupError):
        new_game(1, "solo", SEATS[:1])


# --------------------------------------------------------------------------- turn flow


def test_turn_passes_and_hand_refills():
    s = game()
    first = s.active
    assert s.decision.kind == "action" and s.decision.seat == first
    pass_turn(s)
    assert s.active != first and s.turn == 1
    assert len(s.player(first).hand) == 5
    assert s.step == "action"


def test_wrong_seat_and_unknown_option_are_rejected():
    s = game()
    with pytest.raises(IllegalCommand):
        choose(s, 1 - s.active, "end")
    with pytest.raises(IllegalCommand):
        choose(s, s.active, "nope")


def test_play_spends_action_and_moves_to_staging():
    s = game()
    p = s.player(s.active)
    play = next(o for o in s.decision.options if o.id.startswith("play:") and "(action)" in o.label)
    uid = play.id.split(":")[1]
    choose(s, p.seat, play.id)
    assert p.actions == 2
    assert uid in [i.uid for i in p.staging]
    choose(s, p.seat, "end")
    while s.decision.kind != "discard":
        choose(s, p.seat, s.decision.options[0].id)
    assert p.staging == [] and uid in [i.uid for i in p.discard]


def test_glory_placement_comes_from_stardate():
    s = game()
    before = s.stardate_glory
    choose(s, s.active, "end")
    assert s.decision.kind == "glory"
    choose(s, s.active, s.decision.options[0].id)
    assert s.stardate_glory == before - 1


def test_emptied_stardate_goes_to_inactive_player_and_wipes_market():
    s = game()
    active = s.player(s.active)
    other = s.opponent(active.seat)
    gain_glory(s, active, s.stardate_glory)  # empties Stardate 1
    assert len(s.stardates) == 4
    assert [i.card for i in other.received_stardates] == ["SD01"]
    market_before = {k: v.uid for k, v in s.market.items()}
    pass_turn(s)  # active ends turn; other's turn starts
    pass_turn(s)  # other's Clean-up resolves SD01: Market wiped
    assert other.received_stardates == []
    assert all(s.market[k] is None or s.market[k].uid != uid for k, uid in market_before.items())


def test_resolution_ends_game_after_final_turns():
    s = game()
    for p in s.players:
        p.glory = 0
    while len(s.stardates) > 1:
        gain_glory(s, s.player(s.active), max(1, s.stardate_glory))
    gain_glory(s, s.player(s.active), s.stardate_glory)
    assert s.resolution
    first_player_turn = s.active == s.first_seat
    assert s.last_turn == s.turn + (1 if first_player_turn else 0) + 2
    while s.step != "over":
        pass_turn(s)
    assert s.result["reason"] == "resolution" and s.result["winners"]


def test_burn_ends_game_immediately():
    s = game()
    p = s.player(s.active)
    before = incidents_owned(p)  # Georgiou's deck has its own Hostile Contact
    while s.step != "over":
        take_incident(s, p)
    assert s.result["reason"] == "burn"
    assert s.result["winners"] == [s.opponent(p.seat).seat]
    assert incidents_owned(p) == before + 6


def test_control_step_offers_secured_location():
    s = game()
    p = s.player(s.active)
    loc = s.neutral[0]
    pool = p.away_pool
    loc.away[p.seat] = 3
    p.away_pool -= 3
    assert secured_by(s, loc, p.seat)
    pass_turn(s)
    pass_turn(s)  # back to p: the Control Step asks
    assert s.decision.kind == "control"
    choose(s, p.seat, f"take:{loc.uid}")
    assert loc in p.locations and p.away_pool == pool
    assert len(s.neutral) == 3
    assert s.decision.kind == "action"


def test_irreversible_flags():
    s = game()
    end = next(o for o in s.decision.options if o.id == "end")
    assert end.irreversible is False  # leads to Glory placement, nothing hidden yet
    choose(s, s.active, "end")
    choose(s, s.active, s.decision.options[0].id)
    done = next(o for o in s.decision.options if o.id == "done")
    assert done.irreversible is True and done.reason


# --------------------------------------------------------------------------- views


def test_views_hide_secrets():
    s = game()
    me, other = 0, 1
    view = game_view(s, me)
    assert view["players"][me]["hand"] is not None
    assert view["players"][other]["hand"] is None and view["players"][other]["hand_count"] == 5
    text = str(view)
    for inst in s.players[other].hand + s.players[me].draw + s.players[other].reserve:
        assert inst.uid not in text
    assert "seed" not in view
    if s.decision.seat != me:
        assert "options" not in view["decision"]


def test_replay_is_exact():
    s = game(seed=99)
    commands = []
    for _ in range(6):
        d = s.decision
        option = {"action": "end", "discard": "done"}.get(d.kind) or d.options[0].id
        commands.append((d.seat, option))
        choose(s, d.seat, option)
    replay = game(seed=99)
    for seat, option in commands:
        choose(replay, seat, option)
    assert replay.model_dump() == s.model_dump()
