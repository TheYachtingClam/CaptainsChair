"""2PER04 Commander Tysess (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER04.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit, ships


@operation("2PER04", 1, uses=[A.TRIGGER_CONTROL], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "send_away_team" and ev["seat"] == ctx.me.seat and ev.get("controlled"))
def andorian_command(ctx, actions):
    """REACTION: After sending an [Away Team] to a controlled Location, spend 1 [Dilithium] to trigger that card's
    control operation."""
    loc = next((l for l in ctx.me.locations if l.uid == ctx.event.get("location")), None)
    if loc is not None:
        yield from actions.trigger_control(loc)


@operation("2PER04", 0, uses=[A.FIND, A.PROMOTE, A.DUPLICATE, A.SPEND, A.BEAM])
def recruit_officer(ctx, actions):
    """PLAY: Find a Person, except in your Reserve deck, and promote them to Duty Officer. You may spend an [Action] to
    duplicate a play operation of the promoted card. You may spend 1 [Dilithium] to beam this card to a deployed Ship.
    Ruling: spending the action is an explicit cost; it uses an available Action token (KW-ACT-03)."""
    person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person", exclude_reserve=True)
    if person:
        yield from actions.promote(person)
        has_play = any(op.kind == "PLAY" for op in ctx.card(person).operations)
        if has_play and actions.can_spend(actions=1) and (
                yield from actions.may(f"Spend an Action to duplicate a PLAY operation of {ctx.name(person)}?")):
            yield from actions.spend(actions=1)
            yield from actions.duplicate([person], label=ctx.name(person), optional=False)
    if ships(ctx) and actions.can_spend(dilithium=1) and ctx.this_card in ctx.me.staging and (
            yield from actions.may("Spend 1 Dilithium to beam Commander Tysess to a deployed Ship?")):
        ship = yield from actions.pick_card("Beam Tysess to which Ship?", ships(ctx))
        yield from actions.spend(dilithium=1)
        yield from actions.beam(ctx.this_card, ship)
