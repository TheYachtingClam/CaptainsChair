"""2CAR05 EVA Suits (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR05.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


def _people(ctx):
    return [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person")]


@operation("2CAR05", 0, uses=[A.DEPLOY, A.BEAM])
def suit_up(ctx, actions):
    """PLAY: Deploy this card. You may beam a Person from your hand or Discard pile here."""
    yield from actions.deploy(ctx.this_card)
    person = yield from actions.pick_card("Beam a Person from your hand or Discard pile here?", _people(ctx),
                                          optional=True, none_label="No")
    if person:
        yield from actions.beam(person, ctx.this_card)


@operation("2CAR05", 1, uses=[A.BEAM], requires=lambda ctx: bool(_people(ctx)))
def beam_person(ctx, actions):
    """ACTIVATION: Beam a Person from your hand or Discard pile here."""
    person = yield from actions.pick_card("Beam which Person here?", _people(ctx))
    yield from actions.beam(person, ctx.this_card)


@operation("2CAR05", 2, uses=[A.SEND_AWAY_TEAM, A.DISMISS],
           trigger=lambda ctx, ev: ev["kind"] == "warp" and ev["seat"] == ctx.me.seat)
def spacewalk(ctx, actions):
    """REACTION: After warping a Ship, send an [Away Team] to the Location you warped to for each Person beamed here.
    Dismiss this card."""
    loc = next((l for l in ctx.all_locations() if l.uid == ctx.event.get("location")), None)
    people = sum(1 for b in ctx.this_card.beamed if is_suit(b, "Person"))
    if loc is not None and people:
        yield from actions.send_away_team(people, target=loc, same_location=True)
    yield from actions.dismiss(ctx.this_card)
