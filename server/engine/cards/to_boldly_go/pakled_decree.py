"""2REB16 Pakled Decree (Directive, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB16.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, LogFromHand

from ._util import beam_helmet_here, has_trait, helmets_in_hand

HELMET_HERE = EffectCost(lambda ctx: bool(helmets_in_hand(ctx)), beam_helmet_here, (A.BEAM,), "beam a Helmet here")


@operation("2REB16", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("2REB16", 1, uses=[A.BEAM, A.GAIN_CARD], cost=[HELMET_HERE])
def tribute(ctx, actions):
    """ACTIVATION: Beam a Helmet here to gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")


@operation("2REB16", 2, uses=[A.LOG, A.DRAW, A.DISCARD], requires=lambda ctx: ctx.track("military") >= 15,
           cost=[LogFromHand(lambda ctx, i: has_trait(i, "Weapon"), "a Weapon", ("hand", "discard"))])
def arsenal(ctx, actions):
    """ACTIVATION: If you have 15 [Military], log a Weapon from your hand or Discard pile to draw 3 cards and discard
    one of them."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(3)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")
