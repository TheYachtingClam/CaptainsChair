"""1KOL13 Rura Penthe (Location). Spec: resources/scans/base_game/cards/captains/koloth/1KOL13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import beamed_here, is_suit, people_in_hand, take_control_of_this

operation("1KOL13", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1KOL13", 1, uses=[A.GAIN_RESOURCE])
def mines(ctx, actions):
    """CONTROL: Gain 2 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 2)


@operation("1KOL13", 2, uses=[A.GAIN_RESOURCE])
def forced_labour(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium] for each Person beamed here."""
    n = sum(1 for b in beamed_here(ctx) if is_suit(b, "Person"))
    if n:
        yield from actions.gain_resource("dilithium", n)


@operation("1KOL13", 3, uses=[A.BEAM], requires=lambda ctx: bool(people_in_hand(ctx)))
def imprison(ctx, actions):
    """ACTIVATION: Beam a Person here."""
    person = yield from actions.pick_card("Beam which Person to Rura Penthe?", people_in_hand(ctx))
    yield from actions.beam(person, ctx.this_card)
