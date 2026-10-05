"""2PER14 Phlox (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER14.md
"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit, others_in_hand, ships


def _incidents(cards):
    return [i for i in cards if is_suit(i, "Incident")]


@operation("2PER14", 0, uses=[A.RETURN_INCIDENT], requires=lambda ctx: bool(_incidents(others_in_hand(ctx))))
def treat(ctx, actions):
    """PLAY: Return an Incident from your hand."""
    card = yield from actions.pick_card("Return which Incident?", _incidents(others_in_hand(ctx)))
    yield from actions.return_incident(card)


@operation("2PER14", 1, uses=[A.RETURN_INCIDENT, A.BEAM], requires=lambda ctx: ctx.track("research") >= 6)
def sickbay(ctx, actions):
    """PLAY: Requires [Research] 6. Return any number of Incident from your hand. You may return an Incident from
    your Discard pile. Beam this card to a deployed Ship, if able."""
    while _incidents(ctx.me.hand):
        card = yield from actions.pick_card("Return an Incident from your hand?", _incidents(ctx.me.hand),
                                            optional=True, none_label="Stop")
        if not card:
            break
        yield from actions.return_incident(card)
    card = yield from actions.pick_card("Return an Incident from your Discard pile?", _incidents(ctx.me.discard),
                                        optional=True, none_label="No")
    if card:
        yield from actions.return_incident(card)
    if ships(ctx):
        ship = yield from actions.pick_card("Beam Phlox to which Ship?", ships(ctx))
        yield from actions.beam(ctx.this_card, ship)


@operation("2PER14", 2, uses=[A.GAIN_SPECIALTY], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "send_away_team" and ev["seat"] == ctx.me.seat and ev.get("neutral"))
def field_medicine(ctx, actions):
    """REACTION: After sending an [Away Team] to a neutral Location, spend 1 [Dilithium] to gain 1 [Research]."""
    yield from actions.gain_specialty("research", 1)
