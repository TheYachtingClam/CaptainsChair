"""Burnham's Crew deck (plans/base-game.md Step 12): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/burnham/ and resources/scans/base_game/boards/cb-burnham-*.md."""

import random

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose, hand_size
from engine.ops import _payable_developments, Ctx
from engine.scoring import score_player
from engine.setup import SeatSetup, new_game
from engine.state import OpRef
from engine.views import game_view
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
DECK = content().crew_deck("burnham")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def burnham(**kw):
    return given(deck="burnham", opponent="soval", **kw)


def discovery(s):
    return card(s, "1BUR03", zone="fleet")


def inert(s):
    return next((i for i in me(s).status if i.card == "1BUR02"), None)


def held(s):
    return inert(s).res.get("dilithium", 0)


def zone_for(cid):
    return {"Person": "duty", "Location": "locations"}.get(CARDS[cid].suit, "fleet")


def can_activate(s, inst, index):
    return f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}


def run(s, inst, index, event=None):
    s.decision = None
    s.op_queue.append(OpRef(mode="trigger" if event else "auto", seat=0, uid=inst.uid, index=index, event=event))
    advance(s, flag_irreversible=False)


def developments(s):
    return [i.card for i in _payable_developments(Ctx(s, OpRef(mode="auto", seat=0)))]


# ------------------------------------------------------------------ the deck as a whole

def test_setup_and_copies():
    s = burnham()
    p = me(s)
    assert p.captain.card == "1BUR01" and [i.card for i in p.status] == ["1BUR02"]
    assert [i.card for i in p.fleet] == ["1BUR03"] and not p.locations
    assert len(p.development) == 8 and len(p.reserve) == 4 and len(p.hand) + len(p.draw) == 10
    assert p.dilithium == 1 and held(s) == 0  # the starting Dilithium is in her supply (REQ-CORE-32)
    assert any(i.card == "1BUR26" for i in s.incident)  # Subspace Phenomenon
    assert registry.OPS[("1BUR16", 0)].fn is registry.OPS[("2ARC15", 0)].fn  # Inspire
    assert hand_size(s, p) == 6
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1BUR01", 0),  # her Clean-up rule
    ("1BUR15", 3),  # needs an attack on a Duty Officer
    ("1BUR13", 1),  # needs an Incident just taken
    ("1BUR22", 2),  # needs a Person just gained
    ("1BUR24", 1),  # dismisses the Discovery
    ("1BUR06", 1),  # replaces a gain
    ("1BUR15", 2),  # needs a card beamed to it
    ("1BUR23", 2),  # needs a Creature in play
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_burnham_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "2SHI01"], "tracks": tracks, "dilithium": 12,
                    "locations": ["2LOC07"]}  # a Ship in hand
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["2SHI01"], "dilithium": 12,  # a Ship
                    "locations": RICH.get("locations", []) + ([] if z == "locations" else ["2LOC07"])}
        if z == "locations":
            position["locations"] = [cid, "2LOC07"]
    for seed in range(2):
        s = burnham(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid
        for loc in me(s).locations:
            loc.away[0] = 1
        refresh(s)
        inst = card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert can_activate(s, inst, index), f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


@pytest.mark.parametrize("seed", range(6))
def test_random_games_with_burnham(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sela", "picard", "sisko", "koloth"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "burnham", "advanced" if seed % 2 else "basic"),
                                      SeatSetup("O", other, "basic")], [], False, box="both")
    advance(s, flag_irreversible=False)
    for n in range(6000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, s.decision.seat, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids),
               flag_irreversible=False)
        if n % 80 == 0:
            game_view(s, 0)
    assert s.step == "over"


def test_cadet_training_with_burnham():
    s = new_game(2, "cadet", [SeatSetup("P", "burnham", "advanced")], [], False, box="core")
    advance(s, flag_irreversible=False)
    rng = random.Random(2)
    for _ in range(4000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
    assert s.step == "over"


# ------------------------------------------------------------------ helpers

def complete(s, mission_id):
    choose(s, 0, f"mission:{mission_id}", flag_irreversible=False)


def offered(s, mission_id):
    return f"mission:{mission_id}" in {o.id for o in s.decision.options}


def drive(s, *prefer):
    """Answer until the Action Step menu: the first preferred option, else the first."""
    while s.decision is not None and s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for p in prefer for o in opts if p in o), opts[0]))


def start_op(s, inst, index):
    from engine.ops import start

    start(s, OpRef(mode="op", seat=0, uid=inst.uid, card=inst.card, index=index))


def actions_for(s, *uses):
    from engine.ops import Actions

    return Actions(Ctx(s, OpRef(mode="auto", seat=0)), list(uses))


def opponent_plays(s, card_id, index=0):
    s.active = 1
    s.step = "action"
    refresh(s)
    choose(s, 1, f"play:{card(s, card_id, seat=1, zone='hand').uid}:{index}", flag_irreversible=False)


# ------------------------------------------------------------------ Inert Dilithium and the Captain

def test_core_as_4_gained_dilithium_is_inert_until_recrystallized():
    s = burnham(hand=["1BUR07", "1BUR07"], empty_hand=True)
    assert me(s).dilithium == 1
    play(s, card(s, "1BUR07", zone="hand"), 0)  # Jett Reno: gain 3 Dilithium
    assert me(s).dilithium == 1 and held(s) == 3
    play(s, card(s, "1BUR07", zone="hand"), 1)  # recrystallize 2
    assert me(s).dilithium == 3 and held(s) == 1


def test_core_as_5_dilithium_on_a_gained_market_card_goes_to_the_supply():
    s = burnham(hand=["1BUR17"], empty_hand=True, latinum=1)
    cargo = s.market["Cargo"]
    cargo.res["dilithium"] = 2
    refresh(s)
    play(s, card(s, "1BUR17", zone="hand"), 1)  # Recover: spend 1 Latinum to gain a Cargo
    drive(s, content().cards[cargo.card].name)
    assert me(s).dilithium == 3 and held(s) == 0 and me(s).draw[0].uid == cargo.uid


def finish_turn(s):
    answer(s, "End the Action Step")
    while s.active == 0 and s.step != "over":
        d = s.decision
        choose(s, d.seat, {"discard": "done", "control": "skip"}.get(d.kind, d.options[0].id), flag_irreversible=False)


def test_core_as_6_her_clean_up_places_dilithium_instead_of_glory():
    s = burnham()
    s.stardate_glory = 3
    glory = me(s).glory
    before = sum(i.res.get("glory", 0) for i in s.market.values() if i)
    finish_turn(s)
    cards = [i for i in s.market.values() if i]
    assert s.stardate_glory == 2 and me(s).glory == glory
    assert sorted(i.res.get("dilithium", 0) for i in cards)[-2:] == [0, 2]
    assert sum(i.res.get("glory", 0) for i in cards) == before


def test_cadet_training_places_one_dilithium():
    s = given(deck="burnham", mode="cadet")
    finish_turn_cadet = [i for i in s.market.values() if i]
    assert all(not i.res.get("dilithium") for i in finish_turn_cadet)
    answer(s, "End the Action Step")
    while s.step == "cleanup" or s.decision.kind != "action":
        d = s.decision
        if s.step == "over":
            break
        choose(s, d.seat, {"discard": "done", "control": "skip"}.get(d.kind, d.options[0].id), flag_irreversible=False)
        if s.step == "resupply":
            break
    assert sum(i.res.get("dilithium", 0) for i in s.market.values() if i) + \
        sum(i.res.get("dilithium", 0) for i in s.junk) == 1


def test_glory_cannot_pay_for_dilithium_while_inert_dilithium_is_in_play():
    s = burnham(glory=6)
    me(s).dilithium = 0
    refresh(s)
    assert not can_activate(s, me(s).captain, 1)  # Spend 3 Dilithium
    me(s).status.clear()
    refresh(s)
    assert can_activate(s, me(s).captain, 1)


def test_burnham_gains_an_ally_and_a_glory():
    s = burnham(dilithium=2)
    glory = me(s).glory
    activate(s, me(s).captain, 1)
    drive(s)
    assert me(s).dilithium == 0 and me(s).glory == glory + 1
    assert content().cards[me(s).draw[0].card].suit == "Ally"


def test_discovery_keeps_her_dilithium_from_being_stolen():
    s = burnham(dilithium=2, opp={"hand": ["1SHI08"]})  # Son'a Battlecruiser steals 1 Dilithium
    opponent_plays(s, "1SHI08")
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert me(s).dilithium == 3
    s = burnham(dilithium=2, opp={"hand": ["1SHI08"]})
    me(s).fleet.clear()
    opponent_plays(s, "1SHI08")
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert me(s).dilithium == 2


def test_discovery_refreshes_after_its_warp():
    s = burnham()
    activate(s, discovery(s), 1)
    drive(s)
    assert discovery(s).at is not None and not discovery(s).exhausted


# ------------------------------------------------------------------ Developments

def test_theta_zeta_ends_the_inert_dilithium():
    s = burnham(hand=["1BUR10", "1BUR23"], empty_hand=True)
    inert(s).res["dilithium"] = 4
    glory = me(s).glory
    play(s, card(s, "1BUR10", zone="hand"), 0)
    drive(s)
    assert me(s).dilithium == 5 and not me(s).status and me(s).glory == glory + 4
    assert any(i.card == "1BUR02" for i in me(s).log) and hand_size(s, me(s)) == 5
    play(s, card(s, "1BUR23", zone="hand"), 0)  # Cleveland Booker: gain 1 Dilithium and 1 Latinum
    assert me(s).dilithium == 6
    assert registry.ENDGAME["1BUR10"](s, me(s)) == 3
    theta = card(s, "1BUR10", zone="locations")
    assert not any(t.uid == theta.uid for t in actions_for(s, "SEND_AWAY_TEAM").away_targets())


def test_development_costs():
    s = burnham()
    me(s).dilithium = 0
    assert "1BUR07" in developments(s)  # Jett Reno: dismiss a deployed Ship
    assert not {"1BUR04", "1BUR05", "1BUR08", "1BUR09", "1BUR10", "1BUR06"} & set(developments(s))
    s = burnham(duty=["1BUR05"], discard=["2ENC01"], tracks={"research": 12, "influence": 5})
    me(s).dilithium = 0
    assert {"1BUR04", "1BUR08", "1BUR09", "1BUR10"} <= set(developments(s))  # Vance on duty; an Encounter to log
    assert "1BUR06" not in developments(s)  # Adira Tal also costs 2 Dilithium
    me(s).dilithium = 2
    assert "1BUR06" in developments(s)


def test_uss_federation_scores_focus_icons():
    s = burnham()
    wanted = sum(1 for i in [*me(s).hand, *me(s).draw, *me(s).discard, *me(s).fleet, *me(s).status, me(s).captain]
                 if content().cards[i.card].focus in ("Influence", "Military"))
    assert registry.ENDGAME["1BUR04"](s, me(s)) == wanted


def test_adira_tal_replaces_a_gain_and_gives_a_science_slot():
    from engine.ops import duty_fits

    s = burnham(duty=["1BUR06"], hand=["1BUR17", "1BUR22", "1BUR23"], empty_hand=True, latinum=1)
    adira, tilly, booker = (card(s, c) for c in ("1BUR06", "1BUR22", "1BUR23"))
    assert duty_fits(s, me(s), [adira, tilly]) and not duty_fits(s, me(s), [adira, booker])
    glory = me(s).glory
    play(s, card(s, "1BUR17", zone="hand"), 1)  # Recover: gain a Cargo
    seen = False
    while s.decision.kind != "action":
        opts = options(s)
        seen = seen or any("Adira Tal" in o for o in opts)
        answer(s, next((o for o in opts if "Adira Tal" in o), opts[0]))
    assert seen and me(s).glory == glory + 1


def test_doctor_kovich_hand_size_and_tracks():
    s = burnham(duty=["1BUR08"], tracks={"research": 5, "influence": 5, "military": 4})
    assert hand_size(s, me(s)) == 8  # 5, Inert Dilithium, and two tracks at 5+
    s = burnham(hand=["1BUR08"], empty_hand=True)
    play(s, card(s, "1BUR08", zone="hand"), 0)
    drive(s)
    assert me(s).tracks["research"] == 1 and len(me(s).hand) == 1  # the Discovery is an Anomaly


def test_trance_worm_logs_what_it_gains():
    s = burnham(hand=["1BUR11"], empty_hand=True, latinum=1)
    logged = len(me(s).log)
    play(s, card(s, "1BUR11", zone="hand"), 0)
    drive(s)
    assert len(me(s).log) == logged + 1 and me(s).latinum == 1
    poor = burnham(hand=["1BUR11"], empty_hand=True)
    me(poor).latinum = me(poor).glory = 0
    refresh(poor)
    play(poor, card(poor, "1BUR11", zone="hand"), 0)
    drive(poor)
    assert len(me(poor).log) == logged  # no Latinum, no gain


# ------------------------------------------------------------------ the rest of the deck

def test_books_ship_saves_a_duty_officer():
    s = burnham(duty=["1BUR13"], fleet=["1BUR15"], opp={"hand": ["1SIS09"]})  # Garak dismisses a Duty Officer
    ship = card(s, "1BUR15", zone="fleet")
    ship.beamed.append(s.new_inst("2CAR07"))
    opponent_plays(s, "1SIS09")
    answer(s, "Dismiss an opponent")
    assert any("Book's Ship" in o for o in options(s))
    answer(s, "Use Book's Ship")
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert [i.card for i in me(s).duty] == ["1BUR13"] and not card(s, "1BUR15", zone="fleet").beamed
    assert any(i.card == "2CAR07" for i in me(s).discard)


def test_books_ship_recalls_a_beamed_card():
    s = burnham(fleet=["1BUR15"], hand=["2CAR07"], empty_hand=True)
    ship = card(s, "1BUR15", zone="fleet")
    assert not can_activate(s, ship, 2)
    ship.beamed.append(s.new_inst("2PER16"))
    refresh(s)
    activate(s, card(s, "1BUR15", zone="fleet"), 2)
    drive(s)
    assert [i.card for i in me(s).hand] == ["2PER16"]


def test_grudge_boards_books_ship():
    s = burnham(fleet=["1BUR15"], hand=["1BUR14", "2CAR07"], empty_hand=True)
    play(s, card(s, "1BUR14", zone="hand"), 0)
    drive(s, "Yes")
    assert sorted(i.card for i in card(s, "1BUR15", zone="fleet").beamed) == ["1BUR14", "2CAR07"]


def test_cleveland_booker_counts_creatures():
    s = burnham(duty=["1BUR23"])
    assert not can_activate(s, card(s, "1BUR23", zone="duty"), 2)
    s = burnham(duty=["1BUR23"], staging=["1BUR14", "1BUR11"], empty_hand=True)  # Grudge and the Trance Worm
    glory = me(s).glory
    activate(s, card(s, "1BUR23", zone="duty"), 2)
    answer(s, "Draw a card")
    answer(s, "Gain 1 Glory")
    assert len(me(s).hand) == 1 and me(s).glory == glory + 1


def test_skill_icons_of_nivar_and_keyla_detmer():
    s = burnham(locations=["1BUR12"], duty=["1BUR20"])
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    assert sorted(ctx.skills(card(s, "1BUR12", zone="locations"))) == ["Military", "Research"]  # Vulcan and Romulan
    assert ctx.skills(card(s, "1BUR20", zone="duty")) == ["Any", "Any"]


def test_nivar_removes_a_glory_from_the_stardate():
    s = burnham(hand=["1BUR12"], empty_hand=True, discard=["1BUR16"])
    s.stardate_glory = 5
    play(s, card(s, "1BUR12", zone="hand"), 0)
    drive(s, "Find Inspire")
    assert s.stardate_glory == 4 and any(i.card == "1BUR16" for i in me(s).hand)


def test_joann_owosekun_does_both_for_a_glory():
    s = burnham(hand=["1BUR21", "2CAR07"], empty_hand=True)
    discovery(s).at = s.neutral[0].uid
    refresh(s)
    glory = me(s).glory
    play(s, card(s, "1BUR21", zone="hand"), 0)
    answer(s, "Yes")
    answer(s, content().cards["2CAR07"].name)
    assert me(s).glory == glory + 1 and s.neutral[0].away.get(0, 0) == 1 and len(discovery(s).beamed) == 1


def test_joann_owosekun_resupply_and_activation():
    s = burnham(duty=["1BUR21"], locations=["2LOC07"])
    latinum, pile = me(s).latinum, len(me(s).discard)
    start_op(s, card(s, "1BUR21", zone="duty"), 1)
    assert me(s).latinum == latinum + 1 and len(me(s).discard) == pile + 1
    loc = card(s, "2LOC07", zone="locations")
    loc.exhausted = True
    discovery(s).at = loc.uid
    refresh(s)
    activate(s, card(s, "1BUR21", zone="duty"), 2)
    drive(s)
    assert discovery(s).exhausted and not card(s, "2LOC07", zone="locations").exhausted


def test_keyla_detmer_warps_and_lands_a_team():
    s = burnham(hand=["1BUR20", "2CAR07"], empty_hand=True)
    pile = len(me(s).discard)
    play(s, card(s, "1BUR20", zone="hand"), 0)
    drive(s, "Yes")
    loc = next(l for l in [*s.neutral, *me(s).locations] if l.uid == discovery(s).at)
    assert loc.away.get(0, 0) == 1 and len(me(s).discard) == pile + 2


def test_sylvia_tilly():
    s = burnham(hand=["1BUR22"], empty_hand=True)
    me(s).captain.exhausted = True
    refresh(s)
    play(s, card(s, "1BUR22", zone="hand"), 0)  # she is the one Scientist besides the Captain, and one Engineer
    drive(s)
    assert len(me(s).hand) == 1 and not me(s).captain.exhausted
    s = burnham(hand=["1BUR22"], empty_hand=True, discard=["2CAR07"])
    inert(s).res["dilithium"] = 2
    play(s, card(s, "1BUR22", zone="hand"), 1)
    drive(s)
    assert me(s).dilithium == 2 and held(s) == 1 and me(s).log
    s = burnham(duty=["1BUR22"], hand=["1INC01"], empty_hand=True, discard=["1BUR13"])
    pool = me(s).away_pool
    run(s, card(s, "1BUR22", zone="duty"), 2, {"kind": "gain", "seat": 0, "uid": card(s, "1BUR13", zone="discard").uid})
    drive(s)
    assert me(s).away_pool == pool - 1 and not me(s).hand


def test_hugh_culber_returns_a_taken_incident():
    s = burnham(duty=["1BUR13"], hand=["1INC01", "1BUR17"], empty_hand=True)
    deck = len(s.incident)
    run(s, card(s, "1BUR13", zone="duty"), 1,
        {"kind": "take_incident", "seat": 0, "uid": card(s, "1INC01", zone="hand").uid})
    drive(s)
    assert len(s.incident) == deck + 1 and me(s).tracks["research"] == 1 and not me(s).hand


def test_paul_stamets():
    s = burnham(hand=["1BUR24"], empty_hand=True, fleet=["2SHI01"])
    inert(s).res["dilithium"] = 3
    play(s, card(s, "1BUR24", zone="hand"), 0)
    drive(s, "No")
    assert me(s).dilithium == 3 and held(s) == 1  # two deployed Ships
    s = burnham(duty=["1BUR24"], dilithium=2, empty_hand=True)
    activate(s, card(s, "1BUR24", zone="duty"), 1)
    drive(s)
    assert not me(s).fleet and not me(s).duty and me(s).dilithium == 0
    assert any(content().cards[i.card].suit == "Encounter" for i in me(s).hand)
    without = burnham(duty=["1BUR24"], dilithium=2)
    me(without).fleet.clear()
    refresh(without)
    assert not can_activate(without, card(without, "1BUR24", zone="duty"), 1)


def test_saru_resupply_needs_two_people():
    s = burnham(duty=["1BUR25"], hand=["1BUR13", "1BUR22"], empty_hand=True, tracks={"influence": 2})
    actions = me(s).actions
    start_op(s, card(s, "1BUR25", zone="duty"), 1)
    assert me(s).actions == actions + 1
    s = burnham(duty=["1BUR25"], hand=["1BUR13"], empty_hand=True, tracks={"influence": 2})
    start_op(s, card(s, "1BUR25", zone="duty"), 1)
    assert me(s).actions == actions


def test_admiral_vance_trades_an_incident_for_an_action():
    s = burnham(duty=["1BUR05"], hand=["1INC01"], empty_hand=True, locations=["2LOC07"])
    card(s, "2LOC07", zone="locations").away[0] = 3
    refresh(s)
    actions = me(s).actions
    activate(s, card(s, "1BUR05", zone="duty"), 1)
    drive(s, "Energy Drain")
    assert me(s).actions == actions + 1 and len(me(s).hand) == 2


# ------------------------------------------------------------------ missions

def test_investigate_the_burn():
    s = burnham(tracks={"research": 5})
    assert not offered(s, "investigate-the-burn")
    discovery(s).beamed.extend(s.new_inst(c) for c in ("1INC01", "1INC02", "1BUR25", "1BUR22"))  # Saru and Tilly
    inert(s).res["dilithium"] = 3
    refresh(s)
    complete(s, "investigate-the-burn")
    drive(s)
    assert content().cards[me(s).draw[0].card].suit == "Encounter" and me(s).dilithium == 3 and held(s) == 1
    assert not discovery(s).beamed  # the contributors are dismissed (REQ-MS-06)


def test_reunite_the_federation():
    s = burnham(board="advanced", log=["1CAR16"], staging=["1BUR22", "1BUR24", "1BUR13"])  # Unstable Wormhole
    assert not offered(s, "reunite-the-federation")
    discovery(s).beamed.extend(s.new_inst(c) for c in ("1ALL09", "2ALL09", "1ALL05"))  # Kelpien, Orion, Alien
    refresh(s)
    species = {t for i in discovery(s).beamed for t in content().cards[i.card].traits}
    if not offered(s, "reunite-the-federation"):
        pytest.fail(f"not offered with {sorted(species)}")
    locations = len(me(s).locations)
    complete(s, "reunite-the-federation")
    drive(s)
    assert len(me(s).locations) == locations + 1


def test_dealing_with_the_emerald_chain():
    s = burnham(board="advanced", staging=["1BUR23", "1ALL06"], log=["1ALL10", "1PER03"], hand=["1INC03", "2CAR07"],
                empty_hand=True, dilithium=3, latinum=3)
    glory, latinum = me(s).glory, me(s).latinum
    complete(s, "dealing-with-the-emerald-chain")
    drive(s, "Political Crisis")
    assert me(s).latinum >= latinum + 2 - 3 and held(s) == 2 and me(s).glory >= glory + 2
    assert score_player(s, me(s))["parts"]["missions"] == 6


def test_jett_reno_discards_what_she_gains():
    s = burnham(duty=["1BUR07"], empty_hand=True)
    top = me(s).draw[0].uid
    activate(s, card(s, "1BUR07", zone="duty"), 2)
    drive(s)
    assert me(s).draw[0].uid == top and content().cards[me(s).discard[-1].card].suit in ("Cargo", "Ship")
    assert any(content().cards[i.card].suit == "Incident" for i in me(s).hand)


def test_stolen_dilithium_comes_off_inert_dilithium_first():
    """Rulebook p. 35, Rules for Burnham."""
    s = burnham(opp={"hand": ["1SHI08"]})  # Son'a Battlecruiser steals 1 Dilithium
    me(s).fleet.clear()  # without the Discovery-A
    inert(s).res["dilithium"] = 2
    theirs = opp(s).dilithium
    opponent_plays(s, "1SHI08")
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert held(s) == 1 and me(s).dilithium == 1 and opp(s).dilithium == theirs + 1
