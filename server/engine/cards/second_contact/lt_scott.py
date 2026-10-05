"""3PIK04 Lt. Scott (Person, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition, DiscardFromHand, DismissFromPlay, Spend

from ._util import is_suit, ships

development_cost("3PIK04", Spend(dilithium=3), Condition(lambda ctx: "3PIK08" in ctx.me.enlisted, "have enlisted Pelia"))


@operation("3PIK04", 0, uses=[A.DISMISS, A.TRIGGER_CONTROL, A.EXHAUST, A.DRAW, A.DISCARD],
           cost=[DismissFromPlay(lambda ctx, i: i in ctx.me.fleet and is_suit(i, "Ship"), "a deployed Ship")])
def miracle_worker(ctx, actions):
    """PLAY: Dismiss a deployed Ship to trigger a controlled Location's control operation. You may exhaust a Ship to
    draw 2 cards and discard one of them."""
    loc = yield from actions.pick_card("Trigger the CONTROL of which Location?", ctx.me.locations)
    if loc:
        yield from actions.trigger_control(loc)
    ready = [s for s in ships(ctx) if not s.exhausted]
    ship = yield from actions.pick_card("Exhaust a Ship to draw 2 and discard 1 of them?", ready, optional=True,
                                        none_label="No")
    if ship:
        yield from actions.exhaust(ship)
        before = {i.uid for i in ctx.me.hand}
        yield from actions.draw(2)
        drawn = {i.uid for i in ctx.me.hand} - before
        if drawn:
            yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")


@operation("3PIK04", 1, uses=[A.GAIN_RESOURCE, A.FIND, A.REFRESH])
def spare_parts(ctx, actions):
    """ACTIVATION: Gain 2 [Dilithium]. Then, either find a Ship OR refresh a Ship."""
    yield from actions.gain_resource("dilithium", 2)
    tired = [s for s in ships(ctx) if s.exhausted]
    choice = "find" if not tired else (
        yield from actions.choose("Then?", [("find", "Find a Ship"), ("refresh", "Refresh a Ship")]))
    if choice == "find":
        yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship")
    else:
        ship = yield from actions.pick_card("Refresh which Ship?", tired)
        yield from actions.refresh(ship)


@operation("3PIK04", 2, uses=[A.DISCARD, A.REFRESH], cost=[DiscardFromHand(1)])
def recalibrate(ctx, actions):
    """ACTIVATION: Discard a card to refresh a Location."""
    loc = yield from actions.pick_card("Refresh which Location?", [i for i in ctx.me.locations if i.exhausted])
    if loc:
        yield from actions.refresh(loc)
