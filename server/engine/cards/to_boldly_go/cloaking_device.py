"""2CAR03 Cloaking Device (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR03.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, others_in_hand, ships


@operation("2CAR03", 0, uses=[A.REFRESH, A.DRAW, A.JUNK, A.DEPLOY])
def cloak(ctx, actions):
    """PLAY: Refresh up to 3 of your Ship. Draw 2 cards. Junk a card from the Market. Deploy this card."""
    for n in (1, 2, 3):
        tired = [s for s in ships(ctx) if s.exhausted]
        ship = yield from actions.pick_card(f"Refresh a Ship ({n} of up to 3)?", tired, optional=True, none_label="Stop")
        if not ship:
            break
        yield from actions.refresh(ship)
    yield from actions.draw(2)
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)


@operation("2CAR03", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship") and not has_trait(ctx.event_card, "Cloak"))
def cloak_ship(ctx, actions):
    """REACTION: After deploying a Ship without Cloak, that Ship is additionally treated as Cloak for the remainder of
    your turn, and you may discard a card to send an [Away Team] to a Location, ignoring any opponent Ship.
    Ruling: nothing in these sets reads Cloak afterwards, so the "treated as Cloak" part has no effect."""
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to send an Away Team, ignoring opponent Ships?")):
        yield from actions.discard(1)
        yield from actions.send_away_team(1, ignore_ships=True)
