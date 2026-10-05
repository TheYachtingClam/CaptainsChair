"""2PER08 Jackabog (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER08.md"""

from engine.cards import operation
from engine.ops import A, DismissFromPlay, Spend

from ._util import has_trait, is_suit, others_in_hand, ships


@operation("2PER08", 0, uses=[A.GAIN_CARD, A.BEAM], cost=[Spend(dilithium=1, latinum=1)])
def salvage(ctx, actions):
    """PLAY: Spend 1 [Dilithium] and 1 [Latinum] to gain a Ship from the Junk. You may beam the gained card to a
    Ship. Ruling: the gained Ship may be beamed from wherever it was placed."""
    ship = yield from actions.gain_card(["Ship"], label="a Ship from the Junk", only_junk=True)
    if ship and ships(ctx):
        host = yield from actions.pick_card(f"Beam {ctx.name(ship)} to a Ship?", ships(ctx), optional=True, none_label="No")
        if host:
            yield from actions.beam(ship, host)


@operation("2PER08", 1, uses=[A.TAKE_ENCOUNTER, A.LOG], requires=lambda ctx: ctx.track("military") >= 5,
           cost=[DismissFromPlay(lambda ctx, i: i in ships(ctx) and sum(is_suit(b, "Ship") for b in i.beamed) >= 2,
                                 "a Ship with 2+ Ship beamed to it")])
def clumpship(ctx, actions):
    """PLAY: Requires [Military] 5. Dismiss a Ship with 2+ Ship beamed to it to take the top Encounter. Log this card."""
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)


@operation("2PER08", 2, uses=[A.GAIN_SPECIALTY, A.DRAW])
def helmet_drill(ctx, actions):
    """RESUPPLY: Gain 1 [Military]. If Jackabog is wearing a Helmet, draw 2 cards."""
    yield from actions.gain_specialty("military", 1)
    if any(has_trait(b, "Helmet") for b in ctx.this_card.beamed):
        yield from actions.draw(2)


@operation("2PER08", 3, uses=[A.BEAM], cost=[Spend(dilithium=1)],
           requires=lambda ctx: bool(others_in_hand(ctx, lambda i: has_trait(i, "Helmet"))))
def put_on_helmet(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to beam a Helmet here."""
    helmet = yield from actions.pick_card("Beam which Helmet to Jackabog?",
                                          others_in_hand(ctx, lambda i: has_trait(i, "Helmet")))
    yield from actions.beam(helmet, ctx.this_card)
