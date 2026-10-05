"""Pike's Crew deck and missions (plans/card-implementation.md Step 14)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose
from engine.ops import A, Actions, Ctx, _payable_developments, start
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
SHARED = {"3PIK14", "3PIK18"}  # copies of Political Crisis and Strange New Worlds, tested with the originals
PIKE = sorted(k for k in CARDS if k.startswith("3PIK") and k not in SHARED)


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def pike(**kw):
    kw.setdefault("expansions", ["second_contact"])
    return given(deck="pike", opponent="soval", **kw)


def ctx(s):
    return Ctx(s, OpRef(mode="auto", seat=0))


def status(s):
    return next(i for i in me(s).status if i.card == "3PIK02")


def zone_for(cid):
    suit = CARDS[cid].suit
    return {"Person": "duty", "Location": "locations", "Status": "status"}.get(suit, "fleet")


def resolve_all(s, prefer=("Yes",)):
    while s.decision is not None and s.decision.kind in ("op", "trigger"):
        opts = options(s)
        if s.decision.kind == "trigger":
            answer(s, next((o for o in opts if "Pass" in o or "No" in o or "Don't" in o), opts[-1]))
            continue
        answer(s, next((p for p in prefer for o in opts if p in o), ""))


def run_op(s, cid, index, zone):
    inst = card(s, cid, zone=zone)
    start(s, OpRef(mode="op", seat=0, uid=inst.uid, card=cid, index=index))


NEEDS_OWN_SETUP = {
    ("3PIK16", 1),  # needs the Enterprise at a controlled Location: test_hit_it_triggers_the_enterprise_location
    ("3PIK20", 2),  # needs a secured neutral Location: test_hemmer_takes_control_of_a_secured_location
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in PIKE for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_pike_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["2ENC08"]}  # an Encounter to log for Knowledge of a Terrible Fate
    for seed in range(2):
        s = pike(**position)
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
    assert ("3PIK14", 0) in registry.OPS and registry.OPS[("3PIK14", 0)].fn is registry.OPS[("2INC03", 0)].fn
    assert registry.OPS[("3PIK18", 0)].fn is registry.OPS[("2GEO17", 0)].fn


# ------------------------------------------------------------------ Pike and his Status card

def test_pike_reaction_logs_an_incident_after_a_time_travel():
    s = pike(hand=["2INC03"], staging=[], tracks={"research": 9})
    glory = me(s).glory
    play(s, card(s, "3PIK17", zone="hand"), 0)  # Knowledge of a Terrible Fate: Time Travel
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    assert s.decision.kind == "trigger" and "Christopher Pike" in " ".join(options(s))
    answer(s, "Christopher Pike")
    resolve_all(s)
    assert me(s).glory == glory + 1 and any(i.card == "2INC03" for i in me(s).log)


def test_pike_passive_lets_incidents_come_from_the_log():
    s = pike()
    incident = s.new_inst("2INC03")
    me(s).log.append(incident)
    assert incident in ctx(s).hand_incidents()
    acts = Actions(ctx(s), [A.FIND, A.FREE_PLAY])
    assert incident in acts.free_play_candidates(lambda i: CARDS[i.card].suit == "Incident")
    gen = acts.find(lambda i: CARDS[i.card].suit == "Incident", "an Incident")
    ask = next(gen)
    assert any(o[0] == f"log:{incident.uid}" for o in ask.options)


def test_without_pike_the_log_is_not_searched():
    s = given(deck="kirk", opponent="soval")
    me(s).log.append(s.new_inst("2INC03"))
    assert not ctx(s).hand_incidents()


def test_status_reaction_gains_on_a_matching_track():
    s = pike()
    research = me(s).tracks["research"]
    hemmer = card(s, "3PIK20", zone="hand")
    me(s).dilithium = 5
    refresh(s)
    play(s, hemmer, 0)
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    assert s.decision.kind == "trigger" and "Improbable" in " ".join(options(s))
    answer(s, "Improbable")
    resolve_all(s)
    assert me(s).tracks["research"] == research + 1 and status(s).exhausted


def test_status_ignores_beamed_cards():
    s = pike(fleet=["3PIK19"])
    ship = me(s).fleet[0]
    acts = Actions(ctx(s), [A.BEAM])
    list(acts.beam(card(s, "3PIK20", zone="hand"), ship))
    assert s.pending_events[-1]["beamed"] is True


def test_status_clean_up_influence_or_glory():
    s = pike()
    influence = me(s).tracks["influence"]
    run_op(s, "3PIK02", 0, "status")
    assert me(s).tracks["influence"] == influence + 1
    s = pike(glory=2)
    shady = next(k for k, c in CARDS.items() if "Shady" in c.traits and c.suit == "Person")
    me(s).staging.append(s.new_inst(shady))
    glory = me(s).glory
    run_op(s, "3PIK02", 0, "status")
    assert me(s).glory == glory - 1


def test_uhura_reacts_to_the_status_exhausting():
    s = pike(duty=["3PIK24"], hand=["3PIK21"])
    spock = card(s, "3PIK21", zone="hand")
    play(s, spock, 0)  # Lt. Spock: Research icon, so the Status card reacts
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    answer(s, "Improbable")  # Spock has a single Research icon, so no track choice
    assert s.decision.kind == "trigger" and "Cadet Uhura" in " ".join(options(s))


def test_batel_refreshes_the_status():
    s = pike(duty=["3PIK10"])
    status(s).exhausted = True
    refresh(s)
    activate(s, card(s, "3PIK10", zone="duty"), 2)
    assert not status(s).exhausted


# ------------------------------------------------------------------ passives and development conditions

def test_laan_treats_military_as_any_with_a_weapon():
    s = pike(duty=["3PIK22"])
    laan = card(s, "3PIK22", zone="duty")
    assert ctx(s).skills(laan) == ["Military"]
    me(s).duty.append(s.new_inst("3PIK23"))  # M'Benga: Weapon
    assert ctx(s).skills(laan) == ["Any"]


def test_pelia_is_wildcard_with_another_engineer():
    from engine.ops import traits_of

    s = pike(duty=["3PIK08"])
    pelia = card(s, "3PIK08", zone="duty")
    assert "Wildcard" not in traits_of(s, pelia)
    me(s).staging.append(s.new_inst("3PIK20"))  # Hemmer: Engineer
    assert "Wildcard" in traits_of(s, pelia)


def test_scott_needs_pelia_enlisted_and_pelia_is_free_with_hemmer_logged():
    s = pike(dilithium=9, latinum=0)
    payable = {i.card for i in _payable_developments(ctx(s))}
    assert "3PIK04" not in payable and "3PIK08" not in payable
    me(s).log.append(s.new_inst("3PIK20"))
    assert "3PIK08" in {i.card for i in _payable_developments(ctx(s))}
    me(s).enlisted.append("3PIK08")
    assert "3PIK04" in {i.card for i in _payable_developments(ctx(s))}


def test_enlisting_records_the_development():
    s = pike(hand=["2ARC22"], dilithium=9, latinum=9)
    play(s, card(s, "2ARC22", zone="hand"), 1)
    answer(s, "Development")
    answer(s, "Marie Batel")
    resolve_all(s, prefer=("No",))
    assert "3PIK10" in me(s).enlisted


def test_chapel_cannot_be_promoted():
    assert "3PIK12" in registry.CANNOT_PROMOTE


def test_batel_allows_an_extra_duty_officer():
    assert registry.DUTY_LIMIT["3PIK10"] == 1


# ------------------------------------------------------------------ duplicates

def test_una_duplicates_a_resupply_from_the_discard_pile():
    s = pike(duty=["3PIK13"], fleet=["3PIK19"])
    dil = me(s).dilithium
    run_op(s, "3PIK13", 1, "duty")
    assert "Erica Ortegas" in " ".join(options(s))  # Ortegas starts in the Discard pile
    answer(s, "Erica Ortegas")
    answer(s, "U.S.S. Enterprise")
    answer(s, s.decision.options[0].label)
    resolve_all(s)
    assert me(s).dilithium == dil + 1


def test_time_crystal_duplicates_a_development_play():
    s = pike(hand=["3PIK15"])
    play(s, card(s, "3PIK15", zone="hand"), 1)
    assert any("Talosians" in o or "Batel" in o or "Pelia" in o for o in options(s))


# ------------------------------------------------------------------ Ongoing, Ships and Locations

def test_knowledge_of_a_terrible_fate():
    s = pike(fleet=["3PIK17"])
    devs = len(me(s).development)
    run_op(s, "3PIK17", 1, "fleet")
    resolve_all(s)
    assert len(me(s).development) == devs - 1 and s.junk[-1].card.startswith("3PIK")
    hand = len(me(s).hand)
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.TAKE_INCIDENT])
    list(acts.take_incident())
    refresh(s)
    assert s.decision.kind == "trigger" and "Knowledge" in " ".join(options(s))
    answer(s, "Knowledge")
    resolve_all(s)
    assert len(me(s).hand) == hand + 3


def test_hit_it_triggers_the_enterprise_location():
    s = pike(fleet=["3PIK19"], hand=["3PIK16"])
    me(s).fleet[0].at = me(s).locations[0].uid  # at Starbase One
    refresh(s)
    actions = me(s).actions
    assert can_play(s, card(s, "3PIK16", zone="hand"), 1)
    play(s, card(s, "3PIK16", zone="hand"), 1)
    resolve_all(s)
    assert me(s).actions == actions + 1  # Starbase One's CONTROL: gain an Action (Hit It costs none)


def test_hemmer_takes_control_of_a_secured_location():
    s = pike(duty=["3PIK20"], fleet=["3PIK19"])
    loc = s.neutral[0]
    me(s).fleet[0].at = loc.uid
    loc.away[0] = 2  # with the Ship, 3 tokens: secured (REQ-CT-01)
    loc.away.pop(1, None)
    for ship in opp(s).fleet:
        ship.at = None
    refresh(s)
    assert ctx(s).secured_by(loc)
    activate(s, card(s, "3PIK20", zone="duty"), 2)
    resolve_all(s, prefer=("No",))
    assert loc.uid in uids(me(s).locations) and any(i.card == "3PIK20" for i in me(s).log)


def test_starbase_one_draws_per_two_ships():
    s = pike(fleet=["3PIK19", "2SHI01", "2SHI02", "2SHI03"])
    hand = len(me(s).hand)
    run_op(s, "3PIK03", 1, "locations")
    resolve_all(s)
    assert len(me(s).hand) == hand + 2


def test_rigel_vii_logs_beamed_cards_for_glory():
    s = pike(locations=["3PIK07"])
    rigel = card(s, "3PIK07", zone="locations")
    rigel.beamed += [s.new_inst("2PER07"), s.new_inst("2PER11")]
    glory = me(s).glory
    run_op(s, "3PIK07", 3, "locations")
    resolve_all(s)
    assert me(s).glory == glory + 1 and not card(s, "3PIK07", zone="locations").beamed


def test_mbenga_reaction_returns_an_incident():
    s = pike(duty=["3PIK23"], hand=["2INC03", "2INC05"], empty_hand=True)
    me(s).hand.append(s.new_inst("3PIK22"))  # La'an: Military icon
    refresh(s)
    play(s, card(s, "2INC03", zone="hand"), 0)  # Political Crisis: discard a card to return this card
    answer(s, "La'an")
    assert s.decision.kind == "trigger" and "Joseph M'Benga" in " ".join(options(s))
    answer(s, "Joseph M'Benga")
    resolve_all(s)
    assert not any(i.card == "2INC05" for i in me(s).hand)




# ------------------------------------------------------------------ missions

def _offered(s, mission):
    return f"mission:{mission}" in {o.id for o in s.decision.options}


def test_weight_of_the_future():
    tt = [k for k, c in CARDS.items() if "Time Travel" in c.traits and c.suit in ("Person", "Ally", "Cargo")][:4]
    s = pike(staging=tt, fleet=["3PIK17", "2CAR14"])
    me(s).discard.append(s.new_inst("2INC03"))
    me(s).log.append(s.new_inst("2INC05"))
    refresh(s)
    assert _offered(s, "weight-of-the-future")
    choose(s, 0, "mission:weight-of-the-future", flag_irreversible=False)
    answer(s, "Political Crisis")
    answer(s, options(s)[0] if "Stop" not in options(s)[0] else options(s)[1])
    resolve_all(s)
    assert not any(i.card in ("2INC03", "2INC05") for i in me(s).discard + me(s).log)


def test_boy_scout():
    people = ["2PER07", "2PER11", "2PER14", "3PIK20", "3PIK21", "3PIK22", "3PIK23"]
    s = pike(board="advanced", staging=people, tracks={"influence": 7})
    refresh(s)
    assert _offered(s, "boy-scout")
    choose(s, 0, "mission:boy-scout", flag_irreversible=False)
    resolve_all(s)
    assert "boy-scout" in me(s).missions_completed


def test_to_explore():
    s = pike(board="advanced", fleet=["3PIK19"], staging=["2ENC08", "2ENC04"])
    loc = s.neutral[0]
    ship = me(s).fleet[0]
    ship.at = loc.uid
    alien = next(k for k, c in CARDS.items() if "Alien" in c.traits and c.suit == "Person")
    ship.beamed += [s.new_inst("3PIK20"), s.new_inst("3PIK21"), s.new_inst(alien)]
    refresh(s)
    assert _offered(s, "to-explore")
    glory = s.stardate_glory
    choose(s, 0, "mission:to-explore", flag_irreversible=False)
    resolve_all(s)
    assert loc.uid in uids(me(s).locations) and s.stardate_glory == glory - 1
