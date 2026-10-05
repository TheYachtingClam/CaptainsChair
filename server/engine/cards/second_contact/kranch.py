"""3PER11 K'ranch (Person). Spec: resources/scans/second_contact/cards/person/3PER11.md"""

from engine.cards import operation
from engine.ops import A


@operation("3PER11", 0, uses=[A.GAIN_SPECIALTY, A.DRAW, A.LOG, A.GAIN_RESOURCE, A.PROMOTE])
def collector(ctx, actions):
    """PLAY: Gain 1 [Military]. Draw a card. You may log the drawn card to gain 2 [Glory]. If you do, you may promote
    this card to Duty Officer."""
    yield from actions.gain_specialty("military", 1)
    before = list(ctx.me.hand)
    yield from actions.draw(1)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn and (yield from actions.may(f"Log {ctx.name(drawn[0])} to gain 2 Glory?")):
        yield from actions.log(drawn[0])
        yield from actions.gain_resource("glory", 2)
        if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote K'ranch to Duty Officer?")):
            yield from actions.promote(ctx.this_card)


@operation("3PER11", 1, uses=[A.LOG, A.GAIN_RESOURCE, A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat and ctx.event_card is not None)
def trophy(ctx, actions):
    """REACTION: After gaining a card, log the gained card to gain 1 [Dilithium] and draw a card."""
    gained = ctx.event_card
    if gained is None:
        return
    yield from actions.log(gained)
    yield from actions.gain_resource("dilithium", 1)
    yield from actions.draw(1)
