"""3PIK19 U.S.S. Enterprise (Ship). Spec: resources/scans/second_contact/cards/captains/pike/3PIK19.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, others_in_hand, status_of, warp_this_ship


@operation("3PIK19", 0, uses=[A.DEPLOY, A.WARP, A.BEAM])
def launch(ctx, actions):
    """PLAY: Deploy this ship. Warp this ship OR beam a card here."""
    yield from actions.deploy(ctx.this_card)
    options = [("warp", "Warp this Ship")] + ([("beam", "Beam a card here")] if others_in_hand(ctx) else [])
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Then?", options))
    if choice == "warp":
        yield from actions.warp(ctx.this_card)
    else:
        yield from beam_a_card_here(ctx, actions)


operation("3PIK19", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("3PIK19", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("3PIK19", 3, uses=[A.PROMOTE, A.REFRESH], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))
def bridge_crew(ctx, actions):
    """ACTIVATION: Promote a Person from your hand to Duty Officer to refresh Improbable, Unstoppable, Sensational."""
    person = yield from actions.pick_card("Promote which Person?", [i for i in ctx.me.hand if is_suit(i, "Person")])
    yield from actions.promote(person)
    status = status_of(ctx.me, "3PIK02")
    if status is not None and person in ctx.me.duty:
        yield from actions.refresh(status)
