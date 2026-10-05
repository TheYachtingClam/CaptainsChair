"""Freeman's Crew deck and missions (plans/card-implementation.md Step 16), including the SUPPORT chain acceptance
scenario (requirements/21-expansion-second-contact.md section 8, REQ-AS-29)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose, secured_by
from engine.ops import A, Actions, Ctx, can_afford, pay_resources, start
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
SHARED = {"3FRE06", "3FRE15", "3FRE17", "3FRE18", "3FRE25"}  # PLAYs shared with other decks, tested there
FREEMAN = sorted(k for k in CARDS if k.startswith("3FRE") and k not in SHARED)


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def freeman(**kw):
    kw.setdefault("expansions", ["second_contact"])
    return given(deck="freeman", opponent="soval", **kw)


def ctx(s):
    return Ctx(s, OpRef(mode="auto", seat=0))


def cerritos(s):
    return next(i for i in me(s).fleet if i.card == "3FRE02")


def zone_for(cid):
    suit = CARDS[cid].suit
    return {"Person": "duty", "Location": "locations", "Status": "status"}.get(suit, "fleet")


def resolve_all(s, prefer=("Yes",)):
    while s.decision is not None and s.decision.kind in ("op", "trigger"):
        opts = options(s)
        if s.decision.kind == "trigger":
            answer(s, next(o for o in opts if o.startswith("Do not")))
            continue
        answer(s, next((p for p in prefer for o in opts if p in o), ""))


def run_op(s, cid, index, zone):
    inst = card(s, cid, zone=zone)
    start(s, OpRef(mode="op", seat=0, uid=inst.uid, card=cid, index=index))


NEEDS_OWN_SETUP = {
    ("3FRE23", 2),  # 4 Lower Deckers in play: test_bradward_dismisses_four_lower_deckers
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in FREEMAN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_freeman_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "2SHI01"], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks}
    for seed in range(2):
        s = freeman(**position)
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
    for index in range(4):
        assert registry.OPS[("3FRE11", index)].fn is registry.OPS[("3FRE02", index)].fn
    for index in range(2):
        assert registry.OPS[("3FRE23", index)].fn is registry.OPS[("3RIK14", index)].fn
        assert registry.OPS[("3FRE15", index)].fn is registry.OPS[("2INC05", index)].fn
    assert registry.OPS[("3FRE25", 0)].fn is registry.OPS[("3RIK24", 0)].fn


# ------------------------------------------------------------------ acceptance scenario: the SUPPORT chain

def test_support_chain_kranch_boimler_tendi():
    """K'ranch is promoted; Bradward Boimler's SUPPORT duplicates K'ranch's PLAY, which promotes Boimler ("this card"
    is the duplicating card); that exceeds the Duty Officer limit and triggers D'Vana Tendi's SUPPORT, and her PASSIVE
    keeps her on duty alongside Boimler (REQ-AS-29)."""
    s = freeman(hand=["3PER11", "3FRE23", "3FRE14"])
    glory, research = me(s).glory, me(s).tracks["research"]
    play(s, card(s, "3PER11", zone="hand"), 0)
    answer(s, "Yes")  # log the drawn card for 2 Glory
    answer(s, "Yes")  # promote K'ranch
    assert s.decision.kind == "trigger" and "Bradward Boimler" in " ".join(options(s))
    answer(s, "Bradward Boimler")
    trail = []
    while s.decision.kind in ("op", "trigger"):
        prompt, opts = s.decision.prompt, options(s)
        trail.append(prompt)
        if s.decision.kind == "trigger":
            answer(s, "D'Vana Tendi" if any("D'Vana Tendi" in o for o in opts) else "Do not")
        elif "Gain 2 on which track?" in prompt:
            answer(s, "Research")
        elif "Dismiss one" in prompt:
            answer(s, "K'ranch")
        else:
            answer(s, "Yes" if "Yes" in opts else opts[0])
    assert any("Dismiss one" in p for p in trail)  # step 4: over the Duty Officer limit
    assert me(s).glory == glory + 4  # 2 Glory from K'ranch, 2 more from Boimler duplicating it
    assert me(s).tracks["research"] == research + 2  # step 6
    duty = {i.card for i in me(s).duty}
    assert {"3FRE23", "3FRE14"} <= duty, duty  # Boimler (promoted as "this card") and Tendi stay on duty



# ------------------------------------------------------------------ Freeman and her Ships

def test_freeman_sends_a_team_after_gaining_on_a_track():
    s = freeman(hand=["2PER07", "3FRE12"])
    loc = s.neutral[0]
    cerritos(s).at = loc.uid
    refresh(s)
    play(s, card(s, "3FRE12", zone="hand"), 0)  # T'Ana: gain 1 Research (no Incident to return, so no question)
    assert s.decision.kind == "trigger" and "Carol Freeman" in " ".join(options(s))
    answer(s, "Carol Freeman")
    resolve_all(s, prefer=("Hoshi",))
    assert s.neutral[0].away.get(0, 0) >= 1


def test_freeman_warps_the_cerritos_after_returning_an_incident():
    s = freeman(hand=["2INC05", "2PER07"])
    refresh(s)
    play(s, card(s, "2INC05", zone="hand"), 0)  # Subspace Phenomenon: discard a card to return this card
    answer(s, "Hoshi")
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    assert s.decision.kind == "trigger" and "Carol Freeman" in " ".join(options(s))
    answer(s, "Carol Freeman")
    resolve_all(s)
    assert cerritos(s).at is not None


def test_freeman_endgame_scores_the_log():
    s = freeman(log=["2PER07", "2PER11", "2PER14", "2PER10", "2PER13"])
    assert registry.ENDGAME["3FRE01"](s, me(s)) == 2


def test_cerritos_play_gains_on_the_lowest_track():
    s = freeman(hand=["3FRE11"], tracks={"research": 3, "influence": 1, "military": 1})
    play(s, card(s, "3FRE11", zone="hand"), 0)
    resolve_all(s, prefer=("No", "Yes"))
    carlsbad = card(s, "3FRE11", zone="fleet")
    assert carlsbad.exhausted


def test_fleet_of_30_counts_twice_for_securing():
    s = freeman(fleet=["3FRE03"])
    loc = s.neutral[0]
    card(s, "3FRE03", zone="fleet").at = loc.uid
    loc.away[0] = 1
    assert secured_by(s, loc, 0)  # 2 + 1 = 3 tokens
    assert registry.DUTY_LIMIT["3FRE03"] == 1


def test_fleet_of_30_lets_away_teams_in_past_two_enemy_ships():
    s = freeman(fleet=["3FRE03"], opp={"fleet": ["2SHI01", "2SHI02"]})
    loc = s.neutral[0]
    card(s, "3FRE03", zone="fleet").at = loc.uid
    for ship in opp(s).fleet:
        ship.at = loc.uid
    acts = Actions(ctx(s), [A.SEND_AWAY_TEAM])
    assert loc in acts.away_targets()


# ------------------------------------------------------------------ Tendi's resources

def test_tendi_makes_latinum_and_dilithium_interchangeable():
    s = freeman(duty=["3FRE14"])
    p = me(s)
    p.dilithium, p.latinum, p.glory = 0, 3, 0
    assert can_afford(p, dilithium=2)
    pay_resources(p, dilithium=2)
    assert (p.dilithium, p.latinum, p.glory) == (0, 1, 0)
    s2 = freeman()
    q = me(s2)
    q.dilithium, q.latinum, q.glory = 0, 3, 0
    assert not can_afford(q, dilithium=2)


def test_tendi_extra_starfleet_slot():
    s = freeman(duty=["3FRE14", "2PER07"])
    refresh(s)
    assert s.decision.kind == "action"  # two Duty Officers fit: Tendi's extra Starfleet slot


# ------------------------------------------------------------------ Developments and Reserve cards

def test_apergosians_duplicate_ignores_logging_itself():
    s = freeman(hand=["3FRE04"], draw=["3PER11"])
    play(s, card(s, "3FRE04", zone="hand"), 0)
    answer(s, "K'ranch")  # find K'ranch
    while s.decision.kind in ("op", "trigger"):
        opts = options(s)
        if s.decision.kind == "trigger":
            answer(s, next(o for o in opts if o.startswith("Do not")))
        elif "Duplicate a PLAY of K'ranch again?" in s.decision.prompt:
            answer(s, "No")
        else:
            answer(s, "K'ranch" if any("K'ranch" in o for o in opts) else ("No" if "No" in opts else opts[0]))
    assert any(i.card == "3PER11" for i in me(s).log) and any(i.card == "3FRE04" for i in me(s).log)


def test_shax_returns_from_the_log():
    s = freeman(hand=["3FRE10", "2SHI01"])
    play(s, card(s, "3FRE10", zone="hand"), 0)
    resolve_all(s, prefer=("Stop",))
    shax = card(s, "3FRE10")
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.LOG])
    list(acts.log(shax))
    refresh(s)
    assert shax.uid in uids(me(s).hand)


def test_tana_returns_a_taken_incident():
    s = freeman(duty=["3FRE12"])
    actions = me(s).actions
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.TAKE_INCIDENT])
    list(acts.take_incident())
    refresh(s)
    assert s.decision.kind == "trigger" and "T'Ana" in " ".join(options(s))
    answer(s, "T'Ana")
    resolve_all(s)
    assert me(s).draw[-1].card == "3FRE12" and me(s).actions == actions + 1
    assert not any(CARDS[i.card].suit == "Incident" for i in me(s).hand)


def test_tana_has_research():
    s = freeman(duty=["3FRE12"])
    assert ctx(s).skills(card(s, "3FRE12", zone="duty")) == ["Research"]


def test_rutherford_refreshes_an_exhausted_ship():
    s = freeman(hand=["3FRE13", "2PER07"])
    refresh(s)
    activate(s, cerritos(s), 3)  # promote Hoshi: exhausts the Cerritos
    answer(s, "Hoshi")
    while s.decision.kind == "trigger" and not any("Rutherford" in o for o in options(s)):
        answer(s, next(o for o in options(s) if o.startswith("Do not")))
    assert s.decision.kind == "trigger" and "Samanthan Rutherford" in " ".join(options(s))
    answer(s, "Samanthan Rutherford")
    resolve_all(s, prefer=("No",))
    assert not cerritos(s).exhausted


def test_anomaly_consolidation_day_after_a_support():
    s = freeman(hand=["3FRE13", "2PER07"], staging=["3FRE21"])
    dil = me(s).dilithium
    refresh(s)
    activate(s, cerritos(s), 3)
    answer(s, "Hoshi")
    while s.decision.kind == "trigger" and not any("Rutherford" in o for o in options(s)):
        answer(s, next(o for o in options(s) if o.startswith("Do not")))
    answer(s, "Samanthan Rutherford")
    seen = False
    while s.decision.kind in ("op", "trigger"):
        if "Anomaly Consolidation Day" in s.decision.prompt:
            answer(s, "Gain 2 Dilithium")
            seen = True
        elif s.decision.kind == "trigger":
            answer(s, next(o for o in options(s) if o.startswith("Do not")))
        else:
            answer(s, "No" if "No" in options(s) else options(s)[0])
    assert seen and me(s).dilithium == dil + 2


def test_t88_scans_instead_of_gaining():
    s = freeman(fleet=["3FRE07"])
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.GAIN_CARD])
    gen = acts.gain_card(["Person"], label="a Person")
    ask = next(gen)
    assert any("T88" in label for _, label in ask.options)


def test_tlyn_support_after_logging():
    s = freeman(hand=["3FRE05", "3PER11"])
    play(s, card(s, "3PER11", zone="hand"), 0)
    answer(s, "Yes")  # log the drawn card
    while s.decision.kind == "op":
        answer(s, "No" if "No" in options(s) else options(s)[0])
    assert s.decision.kind == "trigger" and "T'Lyn" in " ".join(options(s))


def test_second_contact_shuffles_the_ally_in():
    s = freeman(hand=["3FRE16"])
    ally = s.new_inst("2ALL01")
    s.junk.append(ally)
    play(s, card(s, "3FRE16", zone="hand"), 0)
    resolve_all(s, prefer=("Abramson", "2ALL01", CARDS["2ALL01"].name))
    assert ally.uid in uids(me(s).draw) or ally.uid in uids(me(s).hand)
    assert any(i.card == "3FRE16" for i in me(s).staging)  # Reserve not empty: Second Contact is not logged


def test_dooplers_shuffle_themselves_in():
    s = freeman(hand=["3FRE20"])
    me(s).latinum = me(s).glory = 0
    play(s, card(s, "3FRE20", zone="hand"), 0)
    resolve_all(s)
    assert any(i.card == "3FRE20" for i in me(s).draw)


def test_kayshon_discards_one_of_each_suit():
    s = freeman(hand=["3FRE09", "2PER07", "2PER11", "2SHI01"])
    glory = me(s).glory
    play(s, card(s, "3FRE09", zone="hand"), 0)
    answer(s, "Hoshi")
    assert not any("Malcolm Reed" in o for o in options(s))  # a Person was already discarded
    answer(s, CARDS["2SHI01"].name)
    answer(s, "None")  # stop
    assert me(s).glory == glory + 2 and card(s, "3FRE09") in me(s).duty


def test_bradward_dismisses_four_lower_deckers():
    s = freeman(duty=["3FRE23"])
    cerritos(s).beamed += [s.new_inst(c) for c in ("3FRE24", "3FRE05", "3FRE13")]
    refresh(s)
    boimler = card(s, "3FRE23", zone="duty")
    assert f"activate:{boimler.uid}:2" in {o.id for o in s.decision.options}
    activate(s, boimler, 2)
    resolve_all(s)
    assert not me(s).duty and not cerritos(s).beamed and any(CARDS[i.card].suit == "Encounter" for i in me(s).hand)


def test_mariner_support_after_an_ally():
    s = freeman(hand=["3FRE24", "3FRE20"])
    cerritos(s).at = s.neutral[0].uid
    refresh(s)
    play(s, card(s, "3FRE20", zone="hand"), 0)
    seen = False
    while s.decision.kind in ("op", "trigger"):
        opts = options(s)
        if s.decision.kind == "trigger" and any("Beckett Mariner" in o for o in opts):
            answer(s, "Beckett Mariner")
            seen = True
        elif s.decision.kind == "trigger":
            answer(s, next(o for o in opts if o.startswith("Do not")))
        else:
            answer(s, opts[0])
    assert seen


# ------------------------------------------------------------------ missions

def _offered(s, mission):
    return f"mission:{mission}" in {o.id for o in s.decision.options}


def test_project_swing_by():
    s = freeman(tracks={"research": 4, "influence": 4})
    cerritos(s).beamed += [s.new_inst(c) for c in ("2ALL01", "2ALL02", "2ALL03", "2ALL04")]
    refresh(s)
    assert _offered(s, "project-swing-by")
    choose(s, 0, "mission:project-swing-by", flag_irreversible=False)
    resolve_all(s, prefer=("No",))
    assert not cerritos(s).beamed  # the beamed Allies that met the goal are dismissed (REQ-MS-06)


def test_beta_shift():
    s = freeman(board="advanced")
    cerritos(s).beamed += [s.new_inst(c) for c in ("3FRE23", "3FRE24", "2PER07", "2PER11")]
    refresh(s)
    assert _offered(s, "beta-shift")
    glory = me(s).glory
    choose(s, 0, "mission:beta-shift", flag_irreversible=False)
    resolve_all(s, prefer=("No",))
    assert me(s).glory == glory + 2


def test_calling_all_your_friends():
    s = freeman(board="advanced")
    loc = s.neutral[0]
    cerritos(s).at = loc.uid
    cerritos(s).beamed += [s.new_inst(c) for c in ("2SHI01", "2SHI02")]
    loc.beamed += [s.new_inst("2SHI03"), s.new_inst("2SHI04")]
    refresh(s)
    assert _offered(s, "calling-all-your-friends")
    choose(s, 0, "mission:calling-all-your-friends", flag_irreversible=False)
    resolve_all(s)
    assert "calling-all-your-friends" in me(s).missions_completed
