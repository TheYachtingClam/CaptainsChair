"""Acceptance scenarios from the rulebook examples (requirements/18-acceptance-scenarios.md, AS-01 to AS-19).

AS-12 is in test_wildcard.py, AS-15 in test_missions.py and AS-19 in test_market_cards.py; the Second Contact SUPPORT
chain (requirements/21-expansion-second-contact.md section 8) is in test_freeman.py. The solo-mode scenarios
(requirements/22-solo-mode.md section 13) wait for the Bot."""

from engine.content import content
from engine.game import advance, choose, hand_size
from engine.ops import A, Actions, Ctx, start
from engine.scoring import score_player
from engine.state import OpRef
from tests.scenario import activate, answer, card, given, name, options, play

CARDS = content().cards


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def run(s, inst, index, seat=0):
    start(s, OpRef(mode="op", seat=seat, uid=inst.uid, card=inst.card, index=index))


def skip_triggers(s):
    while s.decision.kind == "trigger":
        answer(s, next(o for o in options(s) if o.startswith("Do not")))


def test_as01_resupply_counts_anomalies_and_repeats_per_ongoing():
    """Xindi-Reptillian Battleship draws 1 for 2 Anomalies (one beamed); Pasalk may discard-to-draw up to 2 times with
    1 Ongoing in play, seeing each draw before the next choice."""
    s = given(fleet=["2SHI13"], staging=["2CAR06"], duty=["2PER26"])  # Forced Singularity: Anomaly, Ongoing
    shenzhou = card(s, "2GEO02", zone="fleet")
    shenzhou.beamed.append(s.new_inst("2ALL08"))  # Organians
    hand = len(me(s).hand)
    run(s, card(s, "2SHI13", zone="fleet"), 2)
    assert len(me(s).hand) == hand + 1
    run(s, card(s, "2PER26", zone="duty"), 1)
    assert "1 of 2" in s.decision.prompt
    answer(s, "Yes")
    answer(s, options(s)[0])  # discard a card; then the draw happens before the next question
    after_first = len(me(s).hand)
    assert "2 of 2" in s.decision.prompt and after_first == hand + 1
    answer(s, "Yes")
    answer(s, options(s)[0])
    assert len(me(s).hand) == hand + 1 and s.decision.kind != "op"


def test_as02_taking_control():
    s = given()
    archer_iv = next(loc for loc in s.neutral if loc.card == "2LOC02")
    shenzhou = card(s, "2GEO02", zone="fleet")
    shenzhou.at = archer_iv.uid
    archer_iv.away = {0: 2, 1: 1}
    me(s).away_pool -= 2
    opp(s).away_pool -= 1
    pool, opp_pool, opp_glory = me(s).away_pool, opp(s).away_pool, opp(s).glory
    neutral = len(s.neutral)
    from engine.game import take_control

    take_control(s, me(s), archer_iv)
    advance(s, flag_irreversible=False)
    assert shenzhou.uid in uids(me(s).discard)
    assert me(s).away_pool == pool + 2 and opp(s).away_pool == opp_pool + 1
    assert opp(s).glory == opp_glory + 1
    assert archer_iv.uid in uids(me(s).locations) and len(s.neutral) == neutral


def test_as03_play_without_an_action():
    s = given(hand=["2GEO10"])
    actions = me(s).actions
    play(s, card(s, "2GEO10", zone="hand"), 1)
    while s.decision.kind == "op":
        answer(s, options(s)[-1] if "Stop" in options(s)[-1] or "None" in options(s)[-1] else options(s)[0])
    assert me(s).actions == actions and any(i.card == "2GEO10" for i in me(s).staging)


def test_as04_play_with_an_action():
    s = given(hand=["2GEO14"])
    card(s, "2GEO02", zone="fleet").at = s.neutral[0].uid
    refresh(s)
    actions = me(s).actions
    play(s, card(s, "2GEO14", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "No" if "No" in options(s) else options(s)[0])
    assert me(s).actions == actions - 1


def test_as05_activation_finds_a_ship_outside_the_reserve():
    s = given(locations=["2LOC06"], discard=["2SHI05"], latinum=1)
    depot = card(s, "2LOC06", zone="locations")
    refresh(s)
    latinum = me(s).latinum
    activate(s, depot, 2)
    answer(s, options(s)[0])  # the discard
    assert all("Reserve" not in o for o in options(s))
    answer(s, name("2SHI05"))
    assert card(s, "2LOC06", zone="locations").exhausted and me(s).latinum == latinum - 1
    assert any(i.card == "2SHI05" for i in me(s).hand)


def test_as06_clean_up_logs_a_staging_card_possibly_itself():
    s = given(hand=["2ALL11"], staging=["2CAR18"])
    play(s, card(s, "2ALL11", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    choose(s, 0, "end", flag_irreversible=False)
    assert s.decision.kind == "op" and "Salt Vampires" in s.decision.prompt
    assert set(options(s)) == {name(i.card) for i in me(s).staging}  # only cards still in the Staging Area
    answer(s, "Salt Vampires")
    assert me(s).log[-1].card == "2ALL11"


def test_as07_stardate_resolution_wipes_the_market_and_empty_locations():
    from engine.game import wipe_market, wipe_neutral_zone

    s = given()
    argus = s.neutral[0]
    ship = s.new_inst("2SHI01")
    opp(s).fleet.append(ship)
    ship.at = argus.uid  # an opponent's Ship keeps this Location in the Neutral Zone
    market = {suit: inst.uid for suit, inst in s.market.items() if inst is not None}
    some = next(iter(s.market.values()))
    some.res["glory"] = 2
    empty = [loc.uid for loc in s.neutral if loc is not argus]
    wipe_market(s)
    wipe_neutral_zone(s)
    assert all(inst is None or inst.uid not in market.values() for inst in s.market.values())
    assert all(inst is not None for inst in s.market.values())  # refilled
    assert argus in s.neutral and not any(loc.uid in empty for loc in s.neutral)
    assert len(s.neutral) == 3  # refilled before Glory Placement
    assert not some.res


def test_as08_glory_placement_and_discarding():
    s = given(hand=["2GEO16"], staging=["2CAR18"], duty=["2PER07"], locations=["2LOC06"])
    stardate = s.stardate_glory
    choose(s, 0, "end", flag_irreversible=False)
    while s.decision.kind != "glory":
        d = s.decision
        choose(s, 0, d.options[0].id, flag_irreversible=False)
    suit = next(sl for sl, inst in s.market.items() if inst is not None)
    choose(s, 0, f"glory:{suit}", flag_irreversible=False)
    assert s.stardate_glory == stardate - 1 and s.market[suit].res.get("glory") == 1
    recruit = card(s, "2GEO16", zone="hand")
    for inst in [i for i in me(s).hand if i is not recruit]:
        choose(s, 0, f"discard:{inst.uid}", flag_irreversible=False)
    assert not me(s).staging  # Staging Area cards went to the Discard pile
    choose(s, 0, "done", flag_irreversible=False)
    assert recruit.uid in uids(me(s).hand) and any(i.card == "2CAR18" for i in me(s).discard)
    assert any(i.card == "2PER07" for i in me(s).duty) and any(i.card == "2LOC06" for i in me(s).locations)


def test_as09_enlisting_a_reserve_mid_draw():
    s = given()
    me(s).draw = me(s).draw[:2]
    me(s).discard = [s.new_inst("2PER07") for _ in range(3)]
    me(s).reserve.insert(0, s.new_inst("2GEO12"))  # Lt. Saru on top of the Reserve
    saru = me(s).reserve[0]
    first_two = list(me(s).draw)
    me(s).hand.clear()
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.DRAW])
    list(acts.draw(4))
    hand = me(s).hand
    assert hand[:2] == first_two and hand[2] is saru and len(hand) == 4


def test_as10_enlisting_a_development_that_costs_an_incident():
    s = given(dilithium=3, empty_hand=True)
    me(s).draw.clear()
    me(s).reserve.clear()
    me(s).discard.clear()
    me(s).hand = [s.new_inst("2PER07") for _ in range(4)]
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.ENLIST_DEVELOPMENT])
    gen = acts.enlist_development(pred=lambda i: i.card == "2GEO05")
    try:
        next(gen)
    except StopIteration:
        pass
    assert me(s).draw and me(s).draw[0].card == "2GEO05"
    assert len(me(s).hand) == 5 and any(CARDS[i.card].suit == "Incident" for i in me(s).hand)
    assert len(me(s).hand) >= hand_size(s, me(s))  # the hand is full: Red Angel stays on top, undrawn


def test_as11_scan_for_a_trait_searches_decks_and_reshuffles():
    s = given(deck="archer")
    s.market["Ship"] = None
    s.market_decks["Ship"] = [s.new_inst("2SHI01"), s.new_inst("2SHI05"), s.new_inst("2SHI03")]
    s.market_decks["Person"] = [s.new_inst("2ARC06")] + s.market_decks["Person"]  # an Andorian, not a Weapon
    for suit, inst in list(s.market.items()):
        if inst is not None and "Weapon" in CARDS[inst.card].traits:
            s.market[suit] = None
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.SCAN_FOR])
    gen = acts.scan_for(lambda i: "Weapon" in CARDS[i.card].traits, "a Weapon")
    ask = next(gen)
    while True:
        choice = "Ship" if any(o[0] == "Ship" for o in ask.options) else ask.options[0][0]
        try:
            ask = gen.send(choice)
        except StopIteration as stop:
            gained = stop.value
            break
    assert gained is not None and gained.card == "2SHI05"  # Holographic Drone Ship
    assert {i.card for i in s.market_decks["Ship"]} == {"2SHI01", "2SHI03"}


def test_as13_deploy_and_warp():
    s = given(hand=["2SHI02"], opp={"latinum": 2})
    latinum = me(s).latinum
    play(s, card(s, "2SHI02", zone="hand"), 0)
    skip_triggers(s)
    assert card(s, "2SHI02", zone="fleet") and me(s).latinum == latinum + 1
    marauder = card(s, "2SHI02", zone="fleet")
    refresh(s)
    activate(s, marauder, 1)
    assert set(options(s)) >= {name(loc.card) for loc in s.neutral}
    answer(s, name(s.neutral[0].card))
    marauder = card(s, "2SHI02", zone="fleet")
    assert marauder.exhausted and marauder.at == s.neutral[0].uid


def test_as14_away_team_placement_legality():
    s = given(opp={"fleet": ["2SOV10"]})
    tahal = s.new_inst("2LOC10")
    s.neutral[0] = tahal
    seleya = card(s, "2SOV10", seat=1, zone="fleet")
    seleya.at = tahal.uid
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.SEND_AWAY_TEAM])
    assert tahal not in acts.away_targets() and s.neutral[1] in acts.away_targets()
    card(s, "2GEO02", zone="fleet").at = tahal.uid  # tie the Ship counts
    assert tahal in acts.away_targets()


def test_as16_self_logging_still_triggers_reactions():
    s = given(deck="soval", hand=["2ALL03"], duty=["2SOV12"])
    play(s, card(s, "2ALL03", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, options(s)[0])
    assert any(i.card == "2ALL03" for i in me(s).log)
    assert s.decision.kind == "trigger" and "V'Lar" in " ".join(options(s))
    from engine.ops import trait_matches

    engineers = Ctx(s, OpRef(mode="auto", seat=0)).count_in_play(
        lambda i: trait_matches(i, ("Engineer",), state=s))
    assert not any(i.card == "2ALL03" for i in me(s).staging)
    assert engineers == 0  # the logged Bynars no longer count as an Engineer in play (Energy Drain)


def test_as18_final_scoring_example():
    s = given(deck="soval", tracks={"influence": 10})
    p = me(s)
    p.hand, p.draw, p.reserve, p.discard, p.development, p.log = [], [], [], [], [], []
    p.duty = [s.new_inst(c) for c in ("2SOV06", "2PER14", "2PER26", "2PER16", "2SOV07")]
    p.fleet = [s.new_inst("2SHI05")]
    p.locations = [s.new_inst("2LOC14")]
    p.status = []
    p.glory = 0
    p.missions_completed = ["call-of-duty"]
    board = content().boards[p.board]
    assert board.multiplier("influence", p.highest["influence"]) == 4
    assert score_player(s, p)["total"] == 24


def _act(s, label):
    """Choose the Action Step option whose label contains `label`."""
    option = next(o for o in s.decision.options if label in o.label)
    choose(s, 0, option.id, flag_irreversible=False)


def _answer_until_action(s, *script):
    """Answer questions until the Action Step, each with the first script entry found in its options."""
    script = list(script)
    while s.decision.kind != "action":
        opts = options(s)
        pick = next((x for x in script if any(x in o for o in opts)), None)
        if pick is None:
            raise AssertionError(f"no scripted answer for {s.decision.prompt!r}: {opts}")
        answer(s, pick)


def test_as17_entire_action_step():
    """The rulebook's full Soval turn (pp. 22-23), step by step."""
    s = given(deck="soval", tracks={"research": 5})
    p = me(s)
    vulcan = card(s, "2SOV03", zone="locations")
    khitomer = s.new_inst("2LOC14")
    p.locations.append(khitomer)
    seleya = s.new_inst("2SOV10")
    p.fleet = [seleya]
    seleya.at = s.neutral[0].uid
    p.hand = [s.new_inst(c) for c in ("2SOV16", "2SOV20", "2SOV22", "2PER02", "2SOV15", "2SOV19")]
    p.discard = [s.new_inst("2SOV24")] + [s.new_inst("2ALL08") for _ in range(3)]  # Ti'Mur and fillers
    p.draw = []
    p.reserve = [s.new_inst("2SOV11"), s.new_inst("2SOV12")]  # Paan Mokar on top, V'Lar below
    p.duty = []
    p.staging = [s.new_inst("2CAR18")]  # Universal Translator: the third Research icon in the rulebook's position
    vulcan.away[0] = 2
    khitomer.away[0] = 1
    p.dilithium, p.latinum, p.actions = 3, 2, 3
    s.market["Ally"] = s.new_inst("2ALL05")  # Kaelon II Science Ministry
    s.encounter.insert(0, s.new_inst("2ENC02"))  # Gomtuu among the top 2 Encounters
    refresh(s)

    # 1. Seleya promotes Muroc; Vulcan's PASSIVE allows a 2nd Duty Officer because one is Vulcan.
    _act(s, "Activate Seleya (D'Kyr): Promote")
    _answer_until_action(s, "Muroc")
    assert [i.card for i in me(s).duty] == ["2SOV16"]
    # 2. Muroc draws Ti'Mur from the Discard pile.
    _act(s, "Activate Muroc: Draw a Ship")
    _answer_until_action(s, "Ti'Mur")
    assert any(i.card == "2SOV24" for i in me(s).hand)
    # 3-4. Advisory (no action): spend 1 Dilithium, gain 1 Influence, draw; the deck reshuffles and enlists Paan
    # Mokar, which is drawn. Then beam United Earth to the exhausted Seleya.
    actions, influence = me(s).actions, me(s).tracks["influence"]
    _act(s, "Play Advisory: Spend 1")
    _answer_until_action(s, "United Earth", "Seleya", "Yes")
    assert me(s).actions == actions and me(s).tracks["influence"] == influence + 1
    assert any(i.card == "2SOV11" for i in me(s).hand)
    assert any(b.card == "2SOV22" for b in card(s, "2SOV10", zone="fleet").beamed)
    # 5. Action 1: Paan Mokar takes control; its CONTROL free plays Ti'Mur's second PLAY (Research 5): deploy, warp,
    # send an Away Team.
    _act(s, "Play Paan Mokar")
    _answer_until_action(s, "Ti'Mur", "Requires", "Paan Mokar", "Yes", "Do not")
    timur = card(s, "2SOV24", zone="fleet")
    assert card(s, "2SOV11", zone="locations") and timur.at is not None and me(s).actions == 2
    # 6. Ambassador Gral finds V'Lar in the Reserve deck.
    _act(s, "Play Ambassador Gral: Find")
    _answer_until_action(s, "V'Lar")
    assert any(i.card == "2SOV12" for i in me(s).hand)
    # 7. Action 2: V'Lar spends 1 Latinum to gain an Ally into hand.
    _act(s, "Play V'Lar (action): Spend 1")
    _answer_until_action(s, "Kaelon II", "Do not")
    assert any(i.card == "2ALL05" for i in me(s).hand) and me(s).actions == 1
    # 8. Vulcan draws 2: an Away Team there, and 3+ Away Teams on controlled Locations.
    hand = len(me(s).hand)
    _act(s, "Activate Vulcan")
    assert len(me(s).hand) == hand + 2
    # 9. Ti'Mur discards Stel to beam Kaelon II Science Ministry; the Vulcan Science Directorate reacts: 1 Glory.
    glory = me(s).glory
    _act(s, "Activate Ti'Mur: Discard a card to beam")
    _answer_until_action(s, "Stel", "Kaelon II", "Vulcan Science Directorate", "1 [Glory]", "Glory")
    assert me(s).glory == glory + 1 and any(b.card == "2ALL05" for b in card(s, "2SOV24", zone="fleet").beamed)
    # 10. Action 3: Infinite Diversity removes an Away Team, logs Gral, dismisses Ti'Mur (and its beamed card), and
    # puts Gomtuu on the deck. Khitomer's REACTION on logging an Attack card gains an action.
    _act(s, "Play Infinite Diversity")
    _answer_until_action(s, "Yes", "Khitomer", "Ambassador Gral", "Ti'Mur", "Gomtuu", "Do not")
    assert any(i.card == "2PER02" for i in me(s).log) and any(i.card == "2SOV24" for i in me(s).discard)
    assert me(s).draw[0].card == "2ENC02" and me(s).actions == 1
    # 11. Soval dismisses United Earth, a Human, to draw 2 including Gomtuu.
    _act(s, "Activate Soval")
    _answer_until_action(s, "United Earth")
    assert any(i.card == "2ENC02" for i in me(s).hand)
    # 12. Deploy Gomtuu; the last action gains 1 Military per Research icon in play, excluding beamed cards.
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    military = me(s).tracks["military"]
    _act(s, "Play Gomtuu")
    research = sum(ctx.skills(i).count("Research") for i in ctx.in_play(beamed=False))
    _answer_until_action(s, "Yes", "Do not")
    assert me(s).tracks["military"] == military + research and research == 3 and me(s).actions == 0
    # 13. Clean-up resets to 3 actions; discard, then draw up to 5.
    choose(s, 0, "end", flag_irreversible=False)
    while not (s.decision.kind == "action" and s.decision.seat == 1):
        d = s.decision
        choose(s, d.seat, {"discard": "done"}.get(d.kind, d.options[0].id), flag_irreversible=False)
    assert me(s).actions == 3 and len(me(s).hand) == 5
