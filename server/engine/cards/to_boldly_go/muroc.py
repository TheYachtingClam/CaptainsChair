"""2SOV16 Muroc (Person). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("2SOV16", 0, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.LOG])
def orders(ctx, actions):
    """PLAY: Choose 2 of the following: gain 1 [Influence] OR gain 1 [Military] OR send an [Away Team] to a Location
    where you have a Ship. If you have 6+ [Influence] you may choose all 3 instead. If you do, log this card."""
    remaining = [("influence", "Gain 1 Influence"), ("military", "Gain 1 Military"),
                 ("send", "Send an Away Team to a Location where you have a Ship")]
    allowed = 3 if ctx.track("influence") >= 6 else 2
    chosen = 0
    for n in range(1, allowed + 1):
        options = remaining + ([("stop", "Stop at two")] if n == 3 else [])
        choice = yield from actions.choose(f"Muroc: choose an option ({n} of {allowed}).", options)
        if choice == "stop":
            break
        remaining = [o for o in remaining if o[0] != choice]
        chosen += 1
        if choice == "send":
            yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))
        else:
            yield from actions.gain_specialty(choice, 1)
    if chosen == 3:
        yield from actions.log(ctx.this_card)


@operation("2SOV16", 1, uses=[A.FREE_PLAY])
def vulcan_ship(ctx, actions):
    """ACTIVATION: Free play a Ship with Vulcan."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Ship") and has_trait(i, "Vulcan"))
    card = yield from actions.pick_card("Free play which Vulcan Ship?", cards)
    if card:
        yield from actions.free_play(card)


@operation("2SOV16", 2, uses=[A.DRAW_FROM_DISCARD])
def salvage(ctx, actions):
    """ACTIVATION: Draw a Ship from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Ship"), "a Ship")
