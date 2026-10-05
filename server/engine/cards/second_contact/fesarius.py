"""3SHI01 Fesarius (Ship). Spec: resources/scans/second_contact/cards/ships/3SHI01.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import deploy_and_warp_this, has_trait, is_suit, others_in_hand, ships, warp_this_ship

operation("3SHI01", 0, uses=[A.DEPLOY, A.WARP])(deploy_and_warp_this)
operation("3SHI01", 1, uses=[A.WARP])(warp_this_ship)


@operation("3SHI01", 2, uses=[A.BEAM], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(others_in_hand(ctx)))
def beam_aboard(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to beam a card here."""
    card = yield from actions.pick_card("Beam which card to Fesarius?", others_in_hand(ctx))
    yield from actions.beam(card, ctx.this_card)


def _starfleet_aboard(ctx):
    return [b for b in ctx.this_card.beamed if is_suit(b, "Person") and has_trait(b, "Starfleet")]


def _ready(ctx) -> bool:
    return (bool(_starfleet_aboard(ctx)) and any(is_suit(i, "Directive") for i in ctx.me.hand)
            and any(s is not ctx.this_card and not s.exhausted for s in ships(ctx)))


@operation("3SHI01", 3, uses=[A.LOG, A.DISCARD, A.EXHAUST, A.TAKE_ENCOUNTER], requires=_ready)
def first_contact(ctx, actions):
    """ACTIVATION: Log a Person with Starfleet that is beamed here, discard a Directive, and exhaust another Ship to
    take the top Encounter to your Discard pile. Log this card."""
    person = yield from actions.pick_card("Log which Starfleet Person beamed here?", _starfleet_aboard(ctx))
    yield from actions.log(person)
    yield from actions.discard(1, pred=lambda i: is_suit(i, "Directive"), label="a Directive")
    other = yield from actions.pick_card("Exhaust which other Ship?",
                                         [s for s in ships(ctx) if s is not ctx.this_card and not s.exhausted])
    yield from actions.exhaust(other)
    encounter = yield from actions.take_encounter()
    if encounter:
        yield from actions.discard(1, pred=lambda i: i is encounter, label=ctx.name(encounter))
    yield from actions.log(ctx.this_card)
