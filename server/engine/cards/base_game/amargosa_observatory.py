"""1LOC01 Amargosa Observatory (Location). Spec: resources/scans/base_game/cards/location/1LOC01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, ships


@operation("1LOC01", 0, uses=[A.GAIN_CARD, A.GAIN_RESOURCE])
def staff(ctx, actions):
    """CONTROL: You may gain a Person. If it is Scientist/Engineer gain 1 [Glory]."""
    person = yield from actions.gain_card(["Person"], label="a Person", optional=True)
    if person is not None and has_trait(person, "Scientist", "Engineer"):
        yield from actions.gain_resource("glory", 1)


@operation("1LOC01", 1, uses=[A.GAIN_RESOURCE, A.LOG],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Encounter"))
def observation(ctx, actions):
    """REACTION: After putting a Encounter into play, gain 1 [Glory] and you may log a card from your hand or Discard
    pile."""
    yield from actions.gain_resource("glory", 1)
    card = yield from actions.pick_card("Log a card from your hand or Discard pile?", ctx.me.hand + ctx.me.discard,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)


@operation("1LOC01", 2, uses=[A.WARP, A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("uid") == ctx.ref.uid)
def evacuate(ctx, actions):
    """SPECIAL: When you log this card, warp all your deployed Ship to one other Location, then draw 2 cards."""
    movable = [s for s in ships(ctx) if actions.can_warp(s)]
    places = [loc for loc in [*ctx.me.locations, *ctx.state.neutral]]
    if movable and places:
        dest = yield from actions.pick_card("Warp all your Ships to which Location?", places)
        for ship in movable:
            if ship.at != dest.uid:
                yield from actions.warp(ship, destinations=[dest])
    yield from actions.draw(2)
