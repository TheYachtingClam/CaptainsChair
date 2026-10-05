"""Archer's Crew deck and missions (plans/card-implementation.md Step 13)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose
from engine.ops import A, Ctx, _payable_developments
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
SHARED = {"2ARC13", "2ARC14", "2ARC20", "2ARC21"}  # copies of other decks' cards, tested there
ARCHER = sorted(k for k in CARDS if k.startswith("2ARC") and k not in SHARED)


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def archer(**kw):
    return given(deck="archer", opponent="soval", **kw)


def earth(s):
    return next(i for i in me(s).status if i.card == "2ARC02")


def zone_for(cid):
    suit = CARDS[cid].suit
    return {"Person": "duty", "Location": "locations", "Status": "status"}.get(suit, "fleet")


def resolve_all(s, prefer=("Yes",)):
    while s.decision is not None and s.decision.kind == "op":
        opts = options(s)
        pick = next((p for p in prefer for o in opts if p in o), "")
        answer(s, pick)


NEEDS_OWN_SETUP = {
    ("2ARC10", 2),  # needs a Ship at the Repair Station: test_repair_station_draws_with_a_ship_there
    ("2ARC09", 1),  # tested in test_xindi_council_attack
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in ARCHER for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_archer_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks}
    for seed in range(2):
        s = archer(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid
        refresh(s)
        inst = card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}, f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


def test_shared_operations():
    assert registry.OPS[("2ARC03", 3)].fn is registry.OPS[("2GEO02", 3)].fn  # promote, as on the Shenzhou
    assert registry.OPS[("2ARC12", 1)].fn is registry.OPS[("2SOV21", 1)].fn


def test_archer_endgame_counts_unique_traits():
    s = archer()
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    traits = set()
    for i in ctx.in_play():
        traits |= set(CARDS[i.card].traits)
    assert registry.ENDGAME["2ARC01"](s, me(s)) == len(traits) // 3


def test_archer_resupply_takes_three_from_earth():
    s = archer()
    e = earth(s)
    e.res = {"dilithium": 2, "latinum": 2}
    ship = me(s).fleet[0]
    ship.at = s.neutral[0].uid
    dil, lat = me(s).dilithium, me(s).latinum
    from engine.ops import start

    start(s, OpRef(mode="op", seat=0, uid=me(s).captain.uid, card="2ARC01", index=0))
    resolve_all(s, prefer=("Yes", "Dilithium"))
    assert me(s).captain.exhausted
    assert me(s).dilithium + me(s).latinum == dil + lat + 3 and sum(earth(s).res.values()) == 1


def test_ships_can_warp_to_earth():
    s = archer(hand=["2ARC16"])
    play(s, card(s, "2ARC16", zone="hand"), 0)
    answer(s, "Warp a Ship")
    while s.decision.kind == "op" and "Earth" not in " ".join(options(s)):
        answer(s, options(s)[0])
    answer(s, "Earth")
    ship = next(i for i in me(s).fleet if i.at == earth(s).uid)
    assert ship is not None


def test_cards_beamed_to_earth_cannot_be_recalled_or_dismissed():
    from engine.ops import Actions

    s = archer()
    person = s.new_inst("2PER07")
    earth(s).beamed.append(person)
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.RECALL, A.DISMISS])
    list(acts.recall(person))
    list(acts.dismiss(person))
    assert person.uid in uids(earth(s).beamed)


def test_earth_clean_up_beams_a_card_with_no_shared_trait():
    s = archer(hand=["2PER10"])  # Lursa: Klingon, nothing in common with Archer
    from engine.ops import start

    glory = earth(s).res.get("glory", 0)
    influence = me(s).tracks["influence"]
    start(s, OpRef(mode="op", seat=0, uid=earth(s).uid, card="2ARC02", index=0))
    answer(s, CARDS["2PER10"].name)
    resolve_all(s)
    assert any(b.card == "2PER10" for b in earth(s).beamed)
    assert earth(s).res.get("glory", 0) == glory + 1 and me(s).tracks["influence"] == influence + 1


def test_earth_clean_up_shared_trait_gives_nothing():
    s = archer(hand=["2CAR14"])  # Starfleet, like Archer
    from engine.ops import start

    start(s, OpRef(mode="op", seat=0, uid=earth(s).uid, card="2ARC02", index=0))
    answer(s, CARDS["2CAR14"].name)
    resolve_all(s)
    assert any(b.card == "2CAR14" for b in earth(s).beamed) and not earth(s).res.get("glory")


def test_earth_reaction_after_discarding_a_directive():
    s = archer(duty=["2ARC08"], hand=["2ARC15"])
    refresh(s)
    activate(s, card(s, "2ARC08", zone="duty"), 1)
    answer(s, "Inspire")
    assert s.decision.kind == "trigger" and "Earth" in " ".join(options(s))
    answer(s, "Earth")
    answer(s, "Latinum")
    resolve_all(s)
    assert earth(s).res.get("latinum", 0) == 1 and earth(s).res.get("glory", 0) == 1


def test_shran_enlist_adds_away_teams():
    s = archer(dilithium=5, latinum=5, hand=["2ARC22"])
    me(s).development.insert(0, s.new_inst("2ARC06"))
    pool, aside = me(s).away_pool, me(s).away_aside
    assert "2ARC06" in [i.card for i in _payable_developments(Ctx(s, OpRef(mode="auto", seat=0)))]
    play(s, card(s, "2ARC22", zone="hand"), 1)
    answer(s, "Development")
    while s.decision.kind in ("op", "trigger"):
        opts = options(s)
        answer(s, next((o for o in opts if "Shran" in o), "No" if "No" in opts else ""))
    assert me(s).away_aside == aside - 2 and me(s).away_pool == pool + 2


def test_faith_of_the_heart_reorders_reserve():
    s = archer(hand=["2ARC23"])
    me(s).reserve[:0] = [s.new_inst(c) for c in ("2PER07", "2PER11", "2PER14")]
    top = [i.card for i in me(s).reserve[:2]]
    play(s, card(s, "2ARC23", zone="hand"), 1)
    resolve_all(s, prefer=("bottom", "Bottom", "No"))
    assert [i.card for i in me(s).reserve[:1]] == ["2PER14"]  # both looked-at cards went to the bottom
    assert sorted(i.card for i in me(s).reserve[-2:]) == sorted(top)


def test_faith_of_the_heart_needs_a_ready_captain():
    s = archer(hand=["2ARC23"])
    me(s).captain.exhausted = True
    refresh(s)
    assert not can_play(s, card(s, "2ARC23", zone="hand"), 0)


def test_repair_station_draws_with_a_ship_there():
    s = archer(locations=["2ARC10"])
    station = card(s, "2ARC10", zone="locations")
    me(s).fleet[0].at = station.uid
    refresh(s)
    hand = len(me(s).hand)
    activate(s, station, 2)
    resolve_all(s)
    assert len(me(s).hand) == hand + 1


def test_xindi_council_attack():
    s = archer(hand=["2ARC09"], tracks={"influence": 6}, opp={"duty": ["2ARC05"]})
    opp_loc = opp(s).locations[0]
    play(s, card(s, "2ARC09", zone="hand"), 1)
    while s.decision.kind != "action":
        answer(s, options(s)[0])
    assert card(s, "2ARC09").uid in uids(me(s).log)
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand)
    assert opp(s).locations[0].exhausted or opp_loc.uid not in uids(opp(s).locations)


def test_xindi_council_needs_influence_6():
    s = archer(hand=["2ARC09"], tracks={"influence": 5})
    assert not can_play(s, card(s, "2ARC09", zone="hand"), 1)


def test_agent_daniels_hand_size():
    s = archer(duty=["2ARC05"], tracks={"research": 6, "military": 7})
    assert registry.HAND_SIZE["2ARC05"](s, me(s), 5) == 7


def test_trip_tucker_takes_back_a_dismissed_ship():
    from engine.game import dismiss

    s = archer(duty=["2ARC19"], hand=["2ARC15"])
    ship = me(s).fleet[0]
    dismiss(s, me(s), ship)
    refresh(s)
    assert s.decision.kind == "trigger" and "Tucker" in " ".join(options(s))
    answer(s, "Tucker")
    resolve_all(s)
    assert ship.uid in uids(me(s).hand)


def _goal(s, mission):
    return [o.id for o in s.decision.options if o.id == f"mission:{mission}"]


def test_history_with_every_light_year():
    s = archer(dilithium=8)
    nx = next(i for i in me(s).fleet if i.card == "2ARC03")
    loc = s.neutral[0]
    nx.at = loc.uid
    loc.away[0] = 2
    nx.beamed.append(s.new_inst("2PER07"))
    refresh(s)
    assert _goal(s, "history-with-every-light-year")
    choose(s, 0, "mission:history-with-every-light-year", flag_irreversible=False)
    resolve_all(s)
    assert loc.uid in uids(me(s).locations) or any(i.uid == loc.uid for i in me(s).locations)


def test_coalition_of_planets():
    s = archer(board="advanced", duty=["2PER07"])  # Hoshi: Communication
    loc = s.neutral[0]
    s.neutral.remove(loc)
    me(s).locations.append(loc)
    loc.beamed += [s.new_inst(c) for c in ("2ARC06", "2ARC07")]  # Shran (Andorian), Soval (Vulcan)
    tellarite = next(k for k, c in CARDS.items() if "Tellarite" in c.traits)
    loc.beamed.append(s.new_inst(tellarite))
    refresh(s)
    assert _goal(s, "coalition-of-planets")
    hand = len(me(s).hand)
    choose(s, 0, "mission:coalition-of-planets", flag_irreversible=False)
    resolve_all(s, prefer=("Scan 2 of Person", "No"))
    assert len(me(s).hand) >= hand + 1 and "coalition-of-planets" in me(s).missions_completed


def test_temporal_cold_war():
    species = ["2PER10", "2ARC06", "2ARC07"]  # Klingon, Andorian, Vulcan
    extra = [k for k, c in CARDS.items() if CARDS[k].suit == "Person" and
             any(t in c.traits for t in ("Ferengi", "Romulan", "Xindi", "Denobulan", "Cardassian"))]
    tt = [k for k, c in CARDS.items() if "Time Travel" in c.traits and c.suit in ("Person", "Ally")][:2]
    s = archer(board="advanced", duty=[], staging=species + extra[:4] + tt + ["2INC01"])
    refresh(s)
    if not _goal(s, "temporal-cold-war"):
        pytest.skip("content lacks the species mix for this setup")
    actions = s.decision.options
    choose(s, 0, "mission:temporal-cold-war", flag_irreversible=False)
    resolve_all(s, prefer=("No",))
    assert "temporal-cold-war" in me(s).missions_completed and actions
