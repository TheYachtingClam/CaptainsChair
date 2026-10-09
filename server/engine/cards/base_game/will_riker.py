"""1PIC24 Will Riker (Person). Spec: resources/scans/base_game/cards/captains/picard/1PIC24.md
Not the Captain William T. Riker (3RIK01)."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("1PIC24", 0, uses=[A.DRAW_FROM_DISCARD, A.SPEND, A.SEND_AWAY_TEAM, A.TRIGGER_CONTROL])
def number_one(ctx, actions):
    """PLAY: Draw 2 cards from your Discard pile. You may spend 1 [Dilithium] to send an [Away Team] to a Location. If
    you targeted a controlled Location, trigger that card's control operation."""
    for _ in range(2):
        if ctx.me.discard:
            yield from actions.draw_from_discard()
    if actions.can_spend(dilithium=1) and actions.away_targets() and (
            yield from actions.may("Spend 1 Dilithium to send an Away Team to a Location?")):
        yield from actions.spend(dilithium=1)
        loc = yield from actions.send_away_team(1)
        if loc is not None and any(c.uid == loc.uid for c in ctx.controlled_locations()):
            yield from actions.trigger_control(loc)


@operation("1PIC24", 1, uses=[A.DISCARD, A.GAIN_RESOURCE])
def poker_night(ctx, actions):
    """RESUPPLY: Discard the top card of your deck and gain 1 [Latinum]."""
    yield from actions.discard_from_deck()
    yield from actions.gain_resource("latinum", 1)


def _starfleet_ship(i):
    return is_suit(i, "Ship") and has_trait(i, "Starfleet")


@operation("1PIC24", 2, uses=[A.FREE_PLAY], requires=lambda ctx: any(_starfleet_ship(i) for i in ctx.me.hand))
def take_command(ctx, actions):
    """ACTIVATION: Free play a Ship with Starfleet."""
    ship = yield from actions.pick_card("Free play which Starfleet Ship?", actions.free_play_candidates(_starfleet_ship))
    if ship:
        yield from actions.free_play(ship)


@operation("1PIC24", 3, uses=[A.DRAW_FROM_DISCARD], requires=lambda ctx: any(is_suit(i, "Ship") for i in ctx.me.discard))
def salvage(ctx, actions):
    """ACTIVATION: Draw a Ship from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Ship"), "a Ship")
