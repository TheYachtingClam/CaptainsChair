"""1SHR11 You Owe Me One (Directive). Spec: resources/scans/base_game/cards/captains/shran/1SHR11.md"""

from engine.cards import operation
from engine.ops import A


@operation("1SHR11", 0, uses=[A.DEPLOY, A.GAIN_RESOURCE])
def debt(ctx, actions):
    """PLAY: Deploy this card. Gain 1 [Glory]."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.gain_resource("glory", 1)


@operation("1SHR11", 1, uses=[A.DRAW, A.GAIN_RESOURCE, A.FORCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev.get("played")
           and ctx.event_card is not None and ctx.name(ctx.event_card) == "Utilize")
def collect(ctx, actions):
    """REACTION: After you or your opponent plays Utilize, choose: draw a card and your opponent gains 2 [Dilithium] OR
    gain 2 [Dilithium] and your opponent may draw a card."""
    opp = ctx.opponent
    choice = yield from actions.choose("You Owe Me One:", [("draw", "Draw a card; your opponent gains 2 Dilithium"),
                                                          ("dilithium", "Gain 2 Dilithium; your opponent may draw a card")])
    if choice == "draw":
        yield from actions.draw(1)
        if opp is not None:
            yield from actions.gain_resource("dilithium", 2, player=opp)
    else:
        yield from actions.gain_resource("dilithium", 2)
        if opp is not None and (yield from actions.may("Draw a card?", seat=opp.seat)):
            yield from actions.draw(1, player=opp)
