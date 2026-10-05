"""2PER22 Tevrin Krit (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER22.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit, ships


@operation("2PER22", 0, uses=[A.SCAN, A.BEAM, A.GAIN_RESOURCE], cost=[Spend(dilithium=2)])
def recruit(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to scan 3 of Person. You may immediately beam the gained card to a deployed Ship to
    gain 1 [Latinum]."""
    person = yield from actions.scan(3, ["Person"])
    if person and ships(ctx):
        ship = yield from actions.pick_card(f"Beam {ctx.name(person)} to a deployed Ship to gain 1 Latinum?",
                                            ships(ctx), optional=True, none_label="No")
        if ship:
            yield from actions.beam(person, ship)
            yield from actions.gain_resource("latinum", 1)


@operation("2PER22", 1, uses=[A.GAIN_RESOURCE])
def trade(ctx, actions):
    """RESUPPLY: Gain 1 [Latinum] for each Cargo you have in play."""
    n = ctx.count_in_play(lambda i: is_suit(i, "Cargo"))
    if n:
        yield from actions.gain_resource("latinum", n)


