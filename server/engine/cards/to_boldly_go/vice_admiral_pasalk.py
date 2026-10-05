"""2PER26 Vice Admiral Pasalk (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER26.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import has_trait, opponent_has, others_in_hand


@operation("2PER26", 1, uses=[A.DISCARD, A.DRAW])
def refit(ctx, actions):
    """RESUPPLY: You may discard a card to draw a card. Repeat this for each Ongoing you have in play.
    Rulebook example: with 1 Ongoing in play it may happen up to 2 times."""
    times = 1 + ctx.count_in_play(lambda i: has_trait(i, "Ongoing"))
    for n in range(1, times + 1):
        if not others_in_hand(ctx) or not (yield from actions.may(f"Discard a card to draw a card ({n} of {times})?")):
            break
        yield from actions.discard(1)
        yield from actions.draw(1)


@operation("2PER26", 0, uses=[A.REFRESH, A.ATTACK, A.FORCE, A.DISCARD, A.GAIN_RESOURCE])
def inspection(ctx, actions):
    """ATTACK PLAY: Refresh a Starfleet and force your opponent to discard a card. If your opponent has an Augment in
    play, repeat this and gain 1 [Glory]."""
    times = 2 if opponent_has(ctx, lambda i: "Augment" in ctx.traits(i)) else 1
    for _ in range(times):
        tired = [i for i in ctx.in_play(beamed=False) if i.exhausted and has_trait(i, "Starfleet")]
        card = yield from actions.pick_card("Refresh which Starfleet?", tired)
        if card:
            yield from actions.refresh(card)
        if (yield from actions.attack()) and ctx.opponent is not None:
            yield from actions.discard(1, player=ctx.opponent)
    if times == 2:
        yield from actions.gain_resource("glory", 1)


registry.NO_OPPONENT_REACTIONS.add("2PER26")  # SPECIAL: no opponent Reactions on your turn while Pasalk is in play
