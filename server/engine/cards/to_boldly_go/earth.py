"""2ARC02 Earth (Status). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC02.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import is_suit

registry.WARP_DESTINATIONS.add("2ARC02")  # PASSIVE: Ship can warp here.
registry.PROTECTED_BEAMED.add("2ARC02")  # PASSIVE: Cards beamed here cannot be recalled or dismissed, even by missions.


@operation("2ARC02", 0, uses=[A.BEAM, A.GAIN_SPECIALTY, A.PLACE_RESOURCES])
def homeworld(ctx, actions):
    """CLEAN-UP: You may beam a non-Directive card here from your hand or Staging Area. If it shares no traits with
    your Captain, gain 1 [Influence] and place 1 [Glory] here."""
    cards = [i for i in ctx.me.hand + ctx.me.staging if not is_suit(i, "Directive")]
    card = yield from actions.pick_card("Beam a card to Earth?", cards, optional=True, none_label="No")
    if not card:
        return
    yield from actions.beam(card, ctx.this_card)
    if not (ctx.traits(card) & ctx.traits(ctx.me.captain)):
        yield from actions.gain_specialty("influence", 1)
        yield from actions.place_resources(ctx.this_card, "glory", 1)


@operation("2ARC02", 1, uses=[A.PLACE_RESOURCES],
           trigger=lambda ctx, ev: ev["kind"] == "discard" and ev["seat"] == ctx.me.seat and ev.get("step") == "action"
           and ctx.event_card is not None and is_suit(ctx.event_card, "Directive"))
def funding(ctx, actions):
    """REACTION: After discarding a Directive during your Action Step, place 1 [Dilithium]/[Latinum] here."""
    kind = yield from actions.choose("Place which resource on Earth?", [("dilithium", "Dilithium"), ("latinum", "Latinum")])
    yield from actions.place_resources(ctx.this_card, kind, 1)
