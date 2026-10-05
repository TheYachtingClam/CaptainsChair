"""Wildcard (REQ-TR-05 to -07, AS-12, REQ-FS-11). 2ENC04 is an Encounter with the printed Wildcard trait."""

from engine.ops import Ctx, acting, trait_matches
from engine.state import OpRef
from tests.scenario import answer, card, given, options, play

WILDCARD = "2ENC04"


def me(s):
    return s.players[0]


def test_wildcard_counts_as_any_trait_for_its_owner_only():
    s = given(hand=[WILDCARD], opp={"hand": [WILDCARD]})
    mine, theirs = card(s, WILDCARD, zone="hand"), card(s, WILDCARD, seat=1, zone="hand")
    with acting(s, 0):
        assert trait_matches(mine, ("Engineer",)) and not trait_matches(theirs, ("Engineer",))
    with acting(s, 1):
        assert trait_matches(theirs, ("Cardassian",)) and not trait_matches(mine, ("Cardassian",))
    assert not trait_matches(mine, ("Engineer",), state=s)  # nobody acting, e.g. final scoring (REQ-FS-11)


def test_three_different_species_with_a_wildcard():
    """AS-12: Bajoran + Klingon + Wildcard satisfies "3 Different Species"."""
    from engine.cards.to_boldly_go._util import distinct_traits

    s = given(staging=["2CAR13", "2PER10", WILDCARD])  # Orb of Time is Bajoran; Lursa is Klingon
    cards = list(me(s).staging)
    with acting(s, 0):
        assert distinct_traits(cards, ("Bajoran", "Klingon", "Vulcan", "Human")) == 3
    with acting(s, 1):
        assert distinct_traits(cards, ("Bajoran", "Klingon", "Vulcan", "Human")) == 2


def test_a_wildcard_may_be_discarded_as_an_engineer():
    """AS-12: Forced Singularity's Activation discards an Engineer; a Wildcard card qualifies."""
    s = given(hand=[WILDCARD], fleet=["2CAR06"], empty_hand=True)
    me(s).hand[:] = [i for i in me(s).hand if i.card == WILDCARD]
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    singularity = card(s, "2CAR06", zone="fleet")
    assert f"activate:{singularity.uid}:2" in {o.id for o in s.decision.options}


def test_an_attack_cannot_force_a_wildcard():
    """AS-12: an attack demanding a trait (Gral: dismiss an opponent Vulcan or Andorian) cannot pick a Wildcard."""
    s = given(hand=["2PER02"], opp={"staging": [WILDCARD], "fleet": ["2CAR08"]})
    s.players[1].fleet[-1] = s.new_inst(WILDCARD)  # a Wildcard card in the opponent's table
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    glory = me(s).glory
    play(s, card(s, "2PER02", zone="hand"), 1)
    while s.decision.kind == "op":
        assert "Encounter" not in " ".join(options(s))
        answer(s, "No" if "No" in options(s) else "")
    assert me(s).glory == glory  # nothing to dismiss: no Glory


def test_vadics_splinter_group_is_wildcard_with_a_borg():
    s = given(staging=["2ALL15", "2SHI01"])  # Borg Probe is Borg
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    vadic = card(s, "2ALL15", zone="staging")
    assert "Wildcard" in ctx.traits(vadic)
    with acting(s, 0):
        assert ctx.has(vadic, "Vulcan")
