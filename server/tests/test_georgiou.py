"""Georgiou's deck and the operation runtime (engine/ops.py)."""

import random
import re
from pathlib import Path

import pytest

from engine import cards as registry
from engine import ops
from engine.content import content
from engine.game import advance, choose, table_cards
from engine.setup import SeatSetup, new_game
from engine.state import OpRef

SEATS = [SeatSetup("Geo", "georgiou", "basic"), SeatSetup("Sov", "soval", "basic")]


def at_action(seed=1, seats=SEATS):
    """A game where seat 0 is in its Action Step with no decision of its own pending."""
    state = new_game(seed, "two_player", seats)
    state.active = state.first_seat = 0
    advance(state)
    while not (state.decision.kind == "action" and state.decision.seat == 0):
        d = state.decision
        choose(state, d.seat, {"action": "end", "discard": "done", "control": "skip"}.get(d.kind, d.options[0].id))
    return state


def give(state, card_id, zone="hand", seat=0):
    inst = state.new_inst(card_id)
    getattr(state.player(seat), zone).append(inst)
    refresh(state)
    return inst


def refresh(state):
    """Rebuild the Action Step options after a test changed the state."""
    state.decision = None
    advance(state)


def act(state, option_id):
    choose(state, state.decision.seat, option_id)


def pick(state, text):
    """Answer the current decision with the option whose label contains `text`."""
    d = state.decision
    match = [o for o in d.options if text in o.label]
    assert match, f"no option {text!r} in {[o.label for o in d.options]} ({d.prompt})"
    choose(state, d.seat, match[0].id)


def play(state, inst, index):
    act(state, f"play:{inst.uid}:{index}")


def me(state):
    return state.player(0)


# --------------------------------------------------------------------------- registry


def test_every_registered_operation_matches_the_card():
    data = content().cards
    claude = (Path(__file__).parents[2] / "CLAUDE.md").read_text()
    for (cid, index), impl in registry.OPS.items():
        ops_ = data[cid].operations
        assert index < len(ops_), f"{cid} has no operation {index}"
        assert ops_[index].kind != "ENDGAME"
        for use in impl.uses:
            assert f"`{use}`" in claude or f"`A.{use}`" in claude, f"{cid}: {use} is not in the CLAUDE.md action list"
        if ops_[index].kind in ("REACTION",):
            assert impl.trigger is not None, f"{cid} {index}: a REACTION needs a trigger"


def test_shared_copies_have_the_same_text():
    data = content().cards
    by_fn = {}
    for (cid, index), impl in registry.OPS.items():
        by_fn.setdefault((impl.fn, index), []).append(cid)
    for (fn, index), ids in by_fn.items():
        texts = set()
        for cid in ids:
            text = data[cid].operations[index].text or ""
            texts.add(re.sub(re.escape(data[cid].name), "THIS", text).replace("Ambassador THIS", "THIS"))
        texts = {t.replace("Sarek", "THIS") for t in texts}
        assert len(texts) == 1, (ids, texts)


def test_every_georgiou_operation_is_implemented():
    data = content().cards
    for cid, c in data.items():
        if not cid.startswith("2GEO"):
            continue
        for index, op in enumerate(c.operations):
            if op.kind in ("PLAY", "ACTIVATION", "REACTION", "CONTROL", "RESUPPLY", "CLEAN-UP"):
                assert (cid, index) in registry.OPS, f"{cid} {index} {op.kind}"


def test_undeclared_action_raises():
    state = at_action()
    ctx = ops.Ctx(state, OpRef(mode="auto", seat=0))
    with pytest.raises(ops.UndeclaredActionError):
        next(ops.Actions(ctx, [ops.A.GAIN_RESOURCE]).draw(1))


# --------------------------------------------------------------------------- Directives


def uids(cards):
    return [i.uid for i in cards]


def test_analyze_dilithium_is_free_and_ship_costs_an_action():
    s = at_action()
    analyze = give(s, "2GEO15")
    before, actions = me(s).dilithium, me(s).actions
    play(s, analyze, 2)  # printed without the action icon
    assert me(s).dilithium == before + 2 and me(s).actions == actions
    assert analyze.uid in uids(me(s).staging)
    play(s, give(s, "2GEO15"), 0)
    pick(s, "Ship")
    pick(s, "Discard pile")
    assert me(s).actions == actions - 1


def test_analyze_take_incident_to_gain_a_ship():
    s = at_action()
    analyze = give(s, "2GEO15")
    incidents = len(s.incident)
    play(s, analyze, 0)
    pick(s, "Ship")
    pick(s, "Discard pile")
    assert len(s.incident) == incidents - 1
    assert any(content().cards[i.card].suit == "Incident" for i in me(s).hand)
    assert any(content().cards[i.card].suit == "Ship" for i in me(s).discard)


def test_recruit_puts_a_card_on_the_deck():
    s = at_action()
    recruit = give(s, "2GEO16")
    top = me(s).hand[0]
    play(s, recruit, 0)
    pick(s, content().cards[top.card].name)
    pick(s, "Person")
    pick(s, "Discard pile")
    assert me(s).draw[0].uid == top.uid
    assert any(content().cards[i.card].suit == "Person" for i in me(s).discard)


def test_utilize_dilithium_per_location():
    s = at_action()
    me(s).locations.append(s.new_inst("2GEO19"))
    utilize = give(s, "2GEO18")
    before = me(s).dilithium
    play(s, utilize, 0)
    assert me(s).dilithium == before + 3


def test_utilize_counts_detmer_any_skill_only_on_duty():
    def labels(on_duty):
        s = at_action()
        if on_duty:
            me(s).duty.append(s.new_inst("2GEO21"))
        me(s).hand.append(s.new_inst("2GEO21"))  # not in play: never counts
        play(s, give(s, "2GEO18"), 1)
        return {o.id: int(o.label.split("+")[1]) for o in s.decision.options}

    without, with_ = labels(False), labels(True)
    assert all(with_[t] == without[t] + 1 for t in without)


def test_strange_new_worlds_requires_a_location_and_logs_it():
    s = at_action()
    snw = give(s, "2GEO17")
    assert f"play:{snw.uid}:0" not in {o.id for o in s.decision.options}
    vsa = s.new_inst("2GEO19")
    me(s).locations.append(vsa)
    vsa.away[0] = 1
    me(s).fleet[0].at = vsa.uid
    refresh(s)
    encounters = len(s.encounter)
    play(s, snw, 0)
    if s.decision.kind == "op" and "Location" in s.decision.prompt:
        pick(s, "Vulcan Science Academy")
    pick(s, "")  # take one of the two Encounters
    assert len(s.encounter) == encounters - 1
    assert vsa.uid in uids(me(s).log) and me(s).tracks["research"] == 1


def test_hostile_contact_returns_itself():
    s = at_action()
    hc = give(s, "2GEO23")
    play(s, hc, 0)
    pick(s, "")
    assert hc.uid not in uids(me(s).staging) and s.incident[-1].uid == hc.uid
    assert not any(e.get("uid") == hc.uid and e["kind"] == "put_into_play" for e in s.pending_events)


# --------------------------------------------------------------------------- Persons and triggers


def test_detmer_reaction_draws_after_warp():
    s = at_action()
    me(s).duty.append(s.new_inst("2GEO21"))
    detmer = give(s, "2GEO21")
    hand = len(me(s).hand)
    play(s, detmer, 0)
    pick(s, "Yes")
    pick(s, "")  # discard a card
    if s.decision.kind == "op" and "Warp which" in s.decision.prompt:
        pick(s, "")
    pick(s, "")  # destination
    while s.decision.kind == "op":
        pick(s, "")
    assert s.decision.kind == "trigger"
    pick(s, "Use")
    # Detmer played, one discarded, one drawn by the Reaction.
    assert len(me(s).hand) == hand - 2 + 1
    assert any(loc.away.get(0) for loc in s.neutral)


def test_burnham_attack_lets_opponent_choose():
    s = at_action()
    me(s).tracks["military"] = 2
    opp = s.player(1)
    officer = s.new_inst("2SOV05")
    opp.duty.append(officer)
    burnham = give(s, "2GEO13")
    play(s, burnham, 0)
    assert s.decision.seat == 1
    pick(s, "Dismiss")
    pick(s, "")
    assert officer.uid in uids(s.player(1).discard)
    assert me(s).glory == 4


def test_danby_logs_himself_with_three_starfleet():
    s = at_action()
    for cid in ("2GEO12", "2GEO21"):
        me(s).duty.append(s.new_inst(cid))
    danby = give(s, "2GEO20")
    play(s, danby, 0)
    assert me(s).tracks["military"] == 3
    assert danby.uid in uids(me(s).log) and danby.uid not in uids(me(s).staging)


def test_answers_replay_deterministically():
    a, b = at_action(seed=4), at_action(seed=4)
    for s in (a, b):
        play(s, give(s, "2GEO15"), 0)
        pick(s, "Ship")
    assert a.model_dump() == b.model_dump()


# --------------------------------------------------------------------------- smoke


@pytest.mark.parametrize("seed", range(12))
def test_random_games_do_not_crash(seed):
    """Play random legal options for many decisions; every card that comes up gets exercised."""
    rng = random.Random(seed)
    decks = ["georgiou", "georgiou"] if seed % 2 else ["georgiou", "soval"]
    s = new_game(seed, "two_player", [SeatSetup("A", decks[0], "basic"), SeatSetup("B", decks[1], "basic")])
    advance(s, flag_irreversible=False)
    for _ in range(600):
        if s.step == "over":
            break
        d = s.decision
        ids = [o.id for o in d.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:"))]
        option = rng.choice(plays) if plays and rng.random() < 0.8 else rng.choice(ids)
        s.decision = None
        from engine.game import HANDLERS, _advance_untracked

        HANDLERS[d.kind](s, s.player(d.seat), option)
        _advance_untracked(s)
    for p in s.players:
        uids = [i.uid for z in ("hand", "draw", "discard", "reserve", "development", "staging", "fleet", "locations", "duty", "log")
                for i in getattr(p, z)]
        assert len(uids) == len(set(uids)), "a card is in two places"


def test_gained_card_is_shown_with_the_where_question():
    from engine.views import game_view

    s = at_action()
    play(s, give(s, "2GEO15"), 0)
    ship = s.market["Ship"].uid
    pick(s, "faceup")
    view = game_view(s, 0)
    assert view["decision"]["prompt"].endswith("where?")
    assert [c["uid"] for c in view["decision"]["cards"]] == [ship]
    assert "cards" not in game_view(s, 1)["decision"]  # only the deciding player sees them
