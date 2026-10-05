"""2ALL10 Red Squadron (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL10.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, opponent_ships, ships


@operation("2ALL10", 0, uses=[A.DRAW, A.DISCARD, A.BEAM, A.WARP])
def scramble(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. You may beam a card from your Staging Area to a Ship
    (can be this card). You may warp a Ship."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")
    your_ships = ships(ctx)
    if your_ships and ctx.me.staging:
        card = yield from actions.pick_card("Beam a card from your Staging Area to a Ship?", list(ctx.me.staging),
                                            optional=True, none_label="No")
        if card:
            ship = yield from actions.pick_card(f"Beam {ctx.name(card)} to which Ship?", your_ships)
            yield from actions.beam(card, ship)
    if your_ships:
        ship = yield from actions.pick_card("Warp a Ship?", ships(ctx), optional=True, none_label="No")
        if ship:
            yield from actions.warp(ship)


@operation("2ALL10", 1, uses=[A.FIND, A.DRAW, A.ATTACK, A.FORCE, A.DISMISS, A.LOG],
           requires=lambda ctx: ctx.track("influence") >= 3)
def strike_wing(ctx, actions):
    """ATTACK PLAY: Requires [Influence] 3. Find a Starfleet/Dominion. Draw 2 cards. Force your opponent to dismiss a
    deployed Ship. Log this card."""
    yield from actions.find(lambda i: has_trait(i, "Starfleet", "Dominion"), "a Starfleet or Dominion")
    yield from actions.draw(2)
    if (yield from actions.attack()) and opponent_ships(ctx):
        ship = yield from actions.pick_card("Red Squadron: dismiss one of your deployed Ships.", opponent_ships(ctx),
                                            seat=ctx.opponent.seat)
        yield from actions.dismiss(ship)
    yield from actions.log(ctx.this_card)
