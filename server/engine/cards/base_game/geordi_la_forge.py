"""1PIC09 Geordi La Forge (Person, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit, ships

development_cost("1PIC09", Spend(dilithium=2))


@operation("1PIC09", 0, uses=[A.FIND, A.REFRESH])
def engineering(ctx, actions):
    """PLAY: You may find a Ship. You may refresh a Ship."""
    if (yield from actions.may("Find a Ship?")):
        yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship")
    tired = [s for s in ships(ctx) if s.exhausted]
    ship = yield from actions.pick_card("Refresh a Ship?", tired, optional=True, none_label="No")
    if ship:
        yield from actions.refresh(ship)


@operation("1PIC09", 1, uses=[A.GAIN_RESOURCE, A.FREE_PLAY],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship"))
def shakedown(ctx, actions):
    """REACTION: After gaining a Ship, gain 1 [Glory] and you may immediately free play it."""
    yield from actions.gain_resource("glory", 1)
    ship = ctx.event_card
    if ship is not None and actions.free_play_candidates(lambda i: i.uid == ship.uid, cards=[ship]) and (
            yield from actions.may(f"Free play {ctx.name(ship)}?")):
        yield from actions.free_play(ship)
