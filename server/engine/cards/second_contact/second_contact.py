"""3FRE16 Second Contact (Directive). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE16.md"""

from engine.cards import operation
from engine.ops import A


@operation("3FRE16", 0, uses=[A.DRAW, A.GAIN_CARD, A.LOG, A.SHUFFLE_INTO])
def second_contact(ctx, actions):
    """PLAY: Draw a card. You may gain an Ally from the Junk. If your Reserve deck is empty, log this card; otherwise
    shuffle the gained card into your deck."""
    yield from actions.draw(1)
    gained = yield from actions.gain_card(["Ally"], label="an Ally from the Junk", only_junk=True, optional=True)
    if not ctx.me.reserve:
        yield from actions.log(ctx.this_card)
    elif gained is not None:
        yield from actions.shuffle_into(gained)
