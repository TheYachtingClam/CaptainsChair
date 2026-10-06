"""Crew board missions (requirements/10-missions-and-specialties.md §4, REQ-AS-30, -31)."""

from engine.content import content
from engine.game import advance
from engine.scoring import score_player
from tests.scenario import answer, card, given, options

CARDS = content().cards


def me(s):
    return s.players[0]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def mission_options(s):
    return [o for o in s.decision.options if o.id.startswith("mission:")]


def complete(s, mission_id):
    from engine.game import choose

    choose(s, 0, f"mission:{mission_id}", flag_irreversible=False)


def beam(s, host_id, *card_ids, zone="fleet"):
    host = card(s, host_id, zone=zone)
    for cid in card_ids:
        host.beamed.append(s.new_inst(cid))
    return host


# --------------------------------------------------------------------------- Georgiou


def test_call_in_the_reinforcements_as_15():
    """AS-15 (p. 20): the reward resolves, the Klingon clause fails because Ash Tyler is beamed, and the beamed
    Hostile Contact is dismissed; Burnham and the Shenzhou stay."""
    s = given(duty=["2GEO13"], tracks={"military": 6})
    shenzhou = beam(s, "2GEO02", "2GEO23", "2PER03")  # Hostile Contact, Ash Tyler (Klingon, beamed)
    refresh(s)
    assert [o.label for o in mission_options(s)] == ["Complete mission: Call in the Reinforcements"]
    dil = me(s).dilithium
    complete(s, "call-in-the-reinforcements")
    answer(s, "")  # scan 1 of Ship: take the one looked at
    answer(s, "Discard pile")
    while s.decision.kind == "op":
        answer(s, "")  # free play the Ship: deploy/warp choices
    assert me(s).dilithium >= dil + 3 - 2  # Ship PLAY costs may spend some; the reward gives 3
    assert "call-in-the-reinforcements" in me(s).missions_completed
    hc = next(i for i in me(s).discard if i.card == "2GEO23")
    assert hc and card(s, "2GEO13").uid in uids(me(s).duty)
    # The log says why the beamed card left the Ship.
    assert any(e.text == "Hostile Contact is dismissed: it was beamed to U.S.S. Shenzhou and used for the mission "
               "Call in the Reinforcements." for e in s.log)
    assert [b.card for b in card(s, "2GEO02", zone="fleet").beamed] == ["2PER03"]
    refresh(s)
    assert not mission_options(s)  # completed once only (REQ-MS-07), and Basic has 1 token
    _ = shenzhou


def test_reinforcements_needs_military_6():
    s = given(duty=["2GEO13"], tracks={"military": 5})
    beam(s, "2GEO02", "2GEO23")
    refresh(s)
    assert not mission_options(s)


def test_hardly_a_negotiation_dismisses_the_beamed_persons():
    s = given(board="advanced", tracks={"research": 1, "influence": 1, "military": 1})
    beam(s, "2GEO02", "2PER10", "2PER08", "2PER22")  # Lursa, Jackabog, Tevrin Krit: no Starfleet
    refresh(s)
    assert any("Hardly a Negotiation" in o.label for o in mission_options(s))
    complete(s, "hardly-a-negotiation")
    answer(s, "No")  # no Development
    assert not card(s, "2GEO02", zone="fleet").beamed
    assert {"2PER10", "2PER08", "2PER22"} <= {i.card for i in me(s).discard}


def test_gazing_at_the_stars_enlists_kaminar_free():
    s = given(board="advanced", staging=["2SHI07", "2CAR08"], tracks={"research": 7})  # two Aliens
    dil, lat = me(s).dilithium, me(s).latinum
    refresh(s)
    complete(s, "gazing-at-the-stars")
    assert me(s).draw[0].card == "2GEO03" or any(i.card == "2GEO03" for i in me(s).hand)
    assert (me(s).dilithium, me(s).latinum) == (dil, lat)  # no development cost paid


def test_advanced_missions_score_their_vp():
    s = given(board="advanced", staging=["2SHI07", "2CAR08"], tracks={"research": 7})
    refresh(s)
    before = score_player(s, me(s))["parts"]["missions"]
    complete(s, "gazing-at-the-stars")
    assert score_player(s, me(s))["parts"]["missions"] == before + 3


# --------------------------------------------------------------------------- Soval


def test_my_mind_to_your_mind_counts_non_beamed_research_or_any():
    # Soval's starting cards plus Research/Any cards: Petra (Research), Sarina (Any), Universal Translator (Research)...
    s = given(deck="soval", opponent="georgiou", staging=["2PER13", "2PER18", "2CAR18", "2SHI07", "2PER19"])
    from engine.ops import Ctx
    from engine.state import OpRef

    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    research = [i for i in ctx.in_play(beamed=False) if {"Research", "Any"} & set(ctx.skills(i))]
    assert len(research) >= 5
    refresh(s)
    assert any("My Mind to Your Mind" in o.label for o in mission_options(s))


def test_my_mind_to_your_mind_ignores_beamed_cards():
    s = given(deck="soval", opponent="georgiou", fleet=["2SHI03"])
    from engine.ops import Ctx
    from engine.state import OpRef

    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    have = [i for i in ctx.in_play(beamed=False) if {"Research", "Any"} & set(ctx.skills(i))]
    extra = ["2PER13", "2PER18", "2CAR18", "2SHI07"][: max(0, 4 - len(have))]
    for cid in extra:
        me(s).staging.append(s.new_inst(cid))
    beam(s, "2SHI03", "2PER19")  # one more Research card, but beamed
    refresh(s)
    assert not any("My Mind" in o.label for o in mission_options(s))


def test_cooperation_with_starfleet_dismisses_beamed_starfleet():
    s = given(deck="soval", opponent="georgiou", board="advanced", fleet=["2SHI03", "2SHI07", "2SHI08"],
              staging=["2ENC01"])
    beam(s, "2SHI03", "2PER11", "2PER07", "2PER24")  # three Starfleet
    refresh(s)
    assert any("Cooperation with Starfleet" in o.label for o in mission_options(s))
    complete(s, "cooperation-with-starfleet")
    answer(s, "Human")
    while s.decision.kind == "op":
        answer(s, "No" if "No" in options(s) else "")
    assert not card(s, "2SHI03", zone="fleet").beamed
