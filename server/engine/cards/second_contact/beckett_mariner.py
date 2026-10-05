"""3FRE24 Beckett Mariner (Person). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE24.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import is_suit

TRACKS = ("research", "influence", "military")


@operation("3FRE24", 0, uses=[A.TAKE_INCIDENT, A.GAIN_CARD, A.FREE_PLAY], cost=[TakeIncidentCost(2)])
def borrow_a_ship(ctx, actions):
    """PLAY: Take 2 Incident to gain a Ship and free play the gained card."""
    ship = yield from actions.gain_card(["Ship"], label="a Ship")
    if ship is not None and ship in actions.free_play_candidates(lambda i: i.uid == ship.uid,
                                                                 ("hand", "discard", "draw")):
        yield from actions.free_play(ship)


@operation("3FRE24", 1, uses=[A.GAIN_RESOURCE, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ally"))
def old_friends(ctx, actions):
    """SUPPORT: After putting an Ally into play, gain 1 [Latinum] and send an [Away Team] to a Location where you
    have a Ship."""
    yield from actions.gain_resource("latinum", 1)
    yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))


@operation("3FRE24", 2, uses=[A.GAIN_SPECIALTY, A.DISMISS])
def show_off(ctx, actions):
    """ACTIVATION: Gain on one Specialty track for each matching Skill icon you have in play (excluding beamed cards).
    If you gained 3+, dismiss this card."""
    cards = ctx.in_play(beamed=False)
    counts = {t: sum(1 for c in cards for s in ctx.skills(c) if s in (t.capitalize(), "Any")) for t in TRACKS}
    track = yield from actions.choose("Gain on which track?", [(t, f"{t.capitalize()}: +{n}") for t, n in counts.items()])
    if counts[track]:
        yield from actions.gain_specialty(track, counts[track])
    if counts[track] >= 3:
        yield from actions.dismiss(ctx.this_card)
