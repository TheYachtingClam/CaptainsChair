"""2ALL05 Kaelon II Science Ministry (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL05.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2ALL05", 0, uses=[A.DEPLOY, A.PLACE_RESOURCES, A.EXHAUST])
def found(ctx, actions):
    """PLAY: Deploy this card. Place 3 [Dilithium] on this card and exhaust this card."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.place_resources(ctx.this_card, "dilithium", 3)
    yield from actions.exhaust(ctx.this_card)


@operation("2ALL05", 1, uses=[A.GAIN_SPECIALTY, A.MOVE_RESOURCES, A.LOG])
def fund(ctx, actions):
    """CLEAN-UP: If this card is exhausted, gain 1 [Research]. Otherwise, move 1 [Dilithium] from this card to a card
    in the Market. If there are no resources here, log this card.
    Ruling: this runs before the Clean-up refresh, so on the turn it is played it is exhausted."""
    ministry = ctx.this_card
    if ministry.exhausted:
        yield from actions.gain_specialty("research", 1)
    else:
        market = [i for i in ctx.state.market.values() if i is not None]
        target = yield from actions.pick_card("Move 1 Dilithium from Kaelon II onto which Market card?", market)
        if target:
            yield from actions.move_resources("dilithium", 1, target, source=ministry)
    if not any(ministry.res.values()):
        yield from actions.log(ministry)


@operation("2ALL05", 2, uses=[A.GAIN_RESOURCE, A.DRAW_FROM_DISCARD],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("by") == ctx.me.seat and ctx.event_card is not None
           and is_suit(ctx.event_card, "Person", "Directive"))
def grant(ctx, actions):
    """REACTION: After logging a Person/Directive, you may gain 1 [Dilithium] from here and you may draw a card from
    your Discard pile."""
    ministry = ctx.this_card
    if ministry.res.get("dilithium") and (yield from actions.may("Gain 1 Dilithium from Kaelon II?")):
        yield from actions.gain_resource("dilithium", 1, source=ministry)
    if ctx.me.discard:
        yield from actions.draw_from_discard(optional=True)
