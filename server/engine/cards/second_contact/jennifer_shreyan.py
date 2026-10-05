"""3PER10 Jennifer Sh'reyan (Person). Spec: resources/scans/second_contact/cards/person/3PER10.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, ships


@operation("3PER10", 0, uses=[A.BEAM, A.GAIN_RESOURCE, A.RECALL, A.WARP], requires=lambda ctx: bool(ships(ctx)))
def pilot(ctx, actions):
    """PLAY: Beam this card to a deployed Ship to gain 2 [Dilithium]. You may recall another card beamed to that
    Ship. You may warp that Ship."""
    ship = yield from actions.pick_card("Beam Jennifer Sh'reyan to which Ship?", ships(ctx))
    yield from actions.beam(ctx.this_card, ship)
    yield from actions.gain_resource("dilithium", 2)
    others = [b for b in ship.beamed if b is not ctx.this_card]
    card = yield from actions.pick_card("Recall another card beamed to that Ship?", others, optional=True, none_label="No")
    if card:
        yield from actions.recall(card)
    if (yield from actions.may(f"Warp {ctx.name(ship)}?")):
        yield from actions.warp(ship)


@operation("3PER10", 2, uses=[A.WARP, A.DRAW, A.DISCARD], requires=lambda ctx: bool(ships(ctx)))
def evasive(ctx, actions):
    """ACTIVATION: Warp a Ship to draw 2 cards and discard one of them."""
    ship = yield from actions.pick_card("Warp which Ship?", ships(ctx))
    yield from actions.warp(ship)
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")


@operation("3PER10", 1, uses=[A.DRAW, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def new_crew(ctx, actions):
    """SUPPORT: After gaining a Person, draw a card and you may send an [Away Team] to a controlled Location."""
    yield from actions.draw(1)
    if ctx.me.locations and (yield from actions.may("Send an Away Team to one of your controlled Locations?")):
        yield from actions.send_away_team(1, where=lambda loc: loc in ctx.me.locations)
