"""Cadet Training (requirements/16-solo-and-cadet-training.md)."""

import random

from engine import ops
from engine.content import content
from engine.game import HANDLERS, _advance_untracked, advance, choose, gain_glory, secured_by
from engine.setup import SeatSetup, new_game
from engine.state import OpRef


def cadet(seed=1, deck="georgiou"):
    state = new_game(seed, "cadet", [SeatSetup("Cadet", deck, "basic")])
    advance(state)
    return state


def test_setup_uses_the_cadet_stardates():
    s = cadet()
    assert [i.card for i in s.stardates] == ["SD06", "SD07"]
    assert s.stardate_glory == 5 and len(s.players) == 1


def test_gained_glory_comes_from_the_supply():
    s = cadet()
    p = s.players[0]
    gain_glory(s, p, 3)
    assert p.glory == 4 and s.stardate_glory == 5  # REQ-CTM-10


def test_virtual_opponent_holds_neutral_locations():
    s = cadet()
    loc = s.neutral[0]
    loc.away[0] = 2
    assert not secured_by(s, loc, 0)
    loc.away[0] = 3
    assert secured_by(s, loc, 0)  # 3 tokens against the virtual opponent's 1 (REQ-CTM-12)


def test_virtual_opponent_skips_incidents():
    s = cadet()
    ctx = ops.Ctx(s, OpRef(mode="auto", seat=0))
    assert ctx.opponent is None and ctx.virtual_opponent
    incidents, glory = len(s.incident), s.players[0].glory
    gen = ops.Actions(ctx, [ops.A.TAKE_INCIDENT]).take_incident(opponent=True)
    for _ in gen:
        pass
    assert len(s.incident) == incidents and s.players[0].glory == glory + 1  # REQ-CTM-13


def end_actions(s):
    choose(s, 0, "end")


def test_cleanup_wipes_one_market_card_then_places_glory():
    s = cadet()
    end_actions(s)
    assert s.decision.kind == "wipe"
    suit = s.decision.options[0].id.split(":")[1]
    wiped = s.market[suit].uid
    choose(s, 0, f"wipe:{suit}")
    assert s.junk[-1].uid == wiped and s.market[suit].uid != wiped
    assert s.decision.kind == "glory"
    choose(s, 0, s.decision.options[0].id)
    assert s.stardate_glory == 4


def play_out(s, rng, *, plays=0.8, stop=None):
    while s.step != "over":
        if stop and stop(s):
            return
        d = s.decision
        ids = [o.id for o in d.options]
        options = [i for i in ids if i.startswith(("play:", "activate:"))]
        option = rng.choice(options) if options and rng.random() < plays else rng.choice(ids)
        s.decision = None
        HANDLERS[d.kind](s, s.player(d.seat), option)
        _advance_untracked(s)


def test_stardates_run_the_eleven_turn_game():
    s = cadet(seed=2)
    rng = random.Random(2)
    staged_at = []
    seen = set()

    def watch(state):
        p = state.players[0]
        for sd in p.received_stardates:
            if sd.uid not in seen:
                seen.add(sd.uid)
                staged_at.append(state.turn)
        return False

    play_out(s, rng, plays=0.0, stop=watch)  # no card plays: Glory leaves the Stardate only in Clean-up
    assert staged_at == [4]  # turn 5 (0-based 4) empties the first Stardate (REQ-CTM-22)
    assert not s.players[0].received_stardates  # resolved in turn 6
    assert s.result["reason"] == "resolution"
    assert s.turn == 10  # the game ends after turn 11 (REQ-CTM-23)
    assert "rating" in s.result


def test_resolution_wipes_happen_on_turn_six():
    s = cadet(seed=3)
    rng = random.Random(3)
    play_out(s, rng, plays=0.0, stop=lambda st: st.turn == 5 and st.step == "cleanup" and st.substep == "wipe")
    lines = [e.text for e in s.log]
    assert "The Market is wiped." in lines


def test_burn_is_a_loss():
    s = cadet()
    from engine.game import burn

    burn(s)
    assert s.result["winners"] == [] and s.step == "over"  # REQ-CTM-14


def test_random_cadet_games_finish():
    for seed in range(20):
        s = cadet(seed=seed, deck=["georgiou", "soval"][seed % 2])
        play_out(s, random.Random(seed))
        assert s.step == "over"
        assert s.result["reason"] in ("resolution", "burn")
