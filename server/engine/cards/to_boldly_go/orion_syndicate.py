"""2ALL09 Orion Syndicate (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL09.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, has_trait, opponent_ships, ships


@operation("2ALL09", 1, uses=[A.GAIN_ACTION, A.DRAW, A.LOG],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Shady"), "a Shady")])
def syndicate_favour(ctx, actions):
    """PLAY: Discard a Shady to gain an [Action]. If you have another Orion in play, draw 2 cards. Log this card."""
    yield from actions.gain_action(1)
    if count_traits(ctx, "Orion", exclude=ctx.this_card):
        yield from actions.draw(2)
    yield from actions.log(ctx.this_card)


@operation("2ALL09", 0, uses=[A.GAIN_RESOURCE, A.ATTACK, A.STEAL, A.FIND])
def racket(ctx, actions):
    """ATTACK PLAY: If you have 3+ Ship deployed, gain 2 [Latinum]. If your opponent has 3+ Ship deployed, steal 2
    [Dilithium]. If you have 8+ [Glory], find a Shady. Ruling: "8+" is your Glory pool."""
    if len(ships(ctx)) >= 3:
        yield from actions.gain_resource("latinum", 2)
    if len(opponent_ships(ctx)) >= 3 and (yield from actions.attack()):
        yield from actions.steal("dilithium", 2)
    if ctx.me.glory >= 8:
        yield from actions.find(lambda i: has_trait(i, "Shady"), "a Shady")
