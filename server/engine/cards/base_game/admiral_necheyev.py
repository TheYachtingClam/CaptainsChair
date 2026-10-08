"""1PER02 Admiral Necheyev (Person). Spec: resources/scans/base_game/cards/person/1PER02.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, is_suit, others_in_hand, ships


@operation("1PER02", 0, uses=[A.WARP, A.FREE_PLAY, A.BEAM])
def orders(ctx, actions):
    """PLAY: You may warp a Ship. You may free play a Directive from your hand or your Discard pile. Up to 3 times: beam
    a card to a Ship."""
    movable = [s for s in ships(ctx) if actions.can_warp(s)]
    ship = yield from actions.pick_card("Warp a Ship?", movable, optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)
    this = ctx.this_card
    directives = [i for i in actions.free_play_candidates(lambda i: is_suit(i, "Directive"), ("hand", "discard"))
                  if i.uid != this.uid]
    directive = yield from actions.pick_card("Free play a Directive from your hand or Discard pile?", directives,
                                             optional=True, none_label="No")
    if directive:
        yield from actions.free_play(directive)
    for n in (1, 2, 3):
        if not ships(ctx) or not others_in_hand(ctx):
            break
        card = yield from actions.pick_card(f"Beam a card to a Ship ({n} of up to 3)?", others_in_hand(ctx),
                                            optional=True, none_label="Stop")
        if not card:
            break
        target = yield from actions.pick_card(f"Beam {ctx.name(card)} to which Ship?", ships(ctx))
        yield from actions.beam(card, target)


@operation("1PER02", 1, uses=[A.DRAW])
def briefing(ctx, actions):
    """RESUPPLY: Draw a card for each Ops you have in play (max 3)."""
    n = min(3, count_traits(ctx, "Ops"))
    if n:
        yield from actions.draw(n)


@operation("1PER02", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])
def redeploy(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to warp any number of your Ship."""
    moved: set[str] = set()
    while True:
        left = [s for s in ships(ctx) if s.uid not in moved and actions.can_warp(s)]
        ship = yield from actions.pick_card("Warp which Ship?", left, optional=True, none_label="Stop")
        if not ship:
            break
        moved.add(ship.uid)
        yield from actions.warp(ship)
