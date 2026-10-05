"""2ARC19 "Trip" Tucker III (Person). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC19.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import earth_of, is_suit


@operation("2ARC19", 0, uses=[A.GAIN_CARD, A.LOG, A.GAIN_RESOURCE, A.PUT, A.PLACE_RESOURCES])
def chief_engineer(ctx, actions):
    """PLAY: Gain a Cargo from the top of the deck and either: log it and gain 1 [Dilithium] OR put it on top of your
    Reserve deck and place 1 [Dilithium] on Earth."""
    cargo = yield from actions.gain_card(["Cargo"], label="the top Cargo", deck_only=True)
    if not cargo:
        return
    options = [("log", "Log it and gain 1 Dilithium")]
    if earth_of(ctx.me) is not None:
        options.append(("reserve", "Put it on top of your Reserve deck and place 1 Dilithium on Earth"))
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose(f"{ctx.name(cargo)}: choose one.", options))
    if choice == "log":
        yield from actions.log(cargo)
        yield from actions.gain_resource("dilithium", 1)
    else:
        yield from actions.put_on_reserve(cargo)
        yield from actions.place_resources(earth_of(ctx.me), "dilithium", 1)


@operation("2ARC19", 1, uses=[A.REFRESH])
def maintenance(ctx, actions):
    """ACTIVATION: Refresh a Ship/Cargo."""
    tired = [i for i in [*ctx.me.fleet, *ctx.me.staging] if i.exhausted and is_suit(i, "Ship", "Cargo")]
    card = yield from actions.pick_card("Refresh which Ship or Cargo?", tired)
    if card:
        yield from actions.refresh(card)


@operation("2ARC19", 2, uses=[A.DISCARD, A.DRAW_FROM_DISCARD],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Directive"), "a Directive")],
           trigger=lambda ctx, ev: ev["kind"] == "dismiss" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship") and ctx.event_card in ctx.me.discard)
def salvage(ctx, actions):
    """REACTION: After dismissing a Ship, discard a Directive to draw it from your Discard pile."""
    ship = ctx.event_card
    yield from actions.draw_from_discard(lambda i: i.uid == ship.uid, ctx.name(ship))


