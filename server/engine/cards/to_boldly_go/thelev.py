"""2PER23 Thelev (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER23.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import count_traits


@operation("2PER23", 0, uses=[A.GAIN_RESOURCE, A.DRAW, A.REFRESH])
def infiltrate(ctx, actions):
    """PLAY: Gain 1 [Latinum] for each Ambassador you have in play. Draw a card for each Ambassador your opponent has
    in play. If you have 6+ [Military], you may refresh a Duty Officer."""
    mine = count_traits(ctx, "Ambassador")
    if mine:
        yield from actions.gain_resource("latinum", mine)
    theirs = count_traits(ctx, "Ambassador", player=ctx.opponent) if ctx.opponent else 0
    if theirs:
        yield from actions.draw(theirs)
    if ctx.track("military") >= 6:
        tired = [i for i in ctx.me.duty if i.exhausted]
        officer = yield from actions.pick_card("Refresh a Duty Officer?", tired, optional=True, none_label="No")
        if officer:
            yield from actions.refresh(officer)


@hand_size_modifier("2PER23")
def larger_hand(state, owner, size):
    """PASSIVE: Requires [Influence] 6. Increase your hand size by 2."""
    return size + 2 if owner.tracks["influence"] >= 6 else size
