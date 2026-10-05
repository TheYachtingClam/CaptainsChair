"""2KIRK24 Captain Spock (Person). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK24.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand, Spend

from ._util import is_suit

TRACKS = ("research", "influence", "military")


@operation("2KIRK24", 0, uses=[A.LOG, A.GAIN_RESOURCE, A.GAIN_SPECIALTY],
           cost=[LogFromHand(zones=("hand", "discard"))])
def mind_meld(ctx, actions):
    """PLAY: Log a card from your hand or Discard pile to gain 3 [Dilithium]. If the logged card has 1+ Skill or Focus
    icons, gain 1 on the matching Specialty track (choose one if multiple, or if it has Any Skill/Best Focus)."""
    yield from actions.gain_resource("dilithium", 3)
    logged = ctx.card(actions.paid[0])
    icons = {s.lower() for s in logged.skills if s.lower() in TRACKS}
    if logged.focus and logged.focus.lower() in TRACKS:
        icons.add(logged.focus.lower())
    if "Any" in logged.skills or logged.focus == "Best":
        icons = set(TRACKS)
    if icons:
        track = next(iter(icons)) if len(icons) == 1 else (
            yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in TRACKS if t in icons]))
        yield from actions.gain_specialty(track, 1)


@operation("2KIRK24", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Person"))
def science_officer(ctx, actions):
    """REACTION: After gaining a Person, spend 1 [Dilithium] to send an [Away Team] to a Location where you have a
    Ship. If you do, gain 1 [Glory]."""
    loc = yield from actions.send_away_team(1, where=lambda l: bool(ctx.ships_at(l)))
    if loc is not None:
        yield from actions.gain_resource("glory", 1)
