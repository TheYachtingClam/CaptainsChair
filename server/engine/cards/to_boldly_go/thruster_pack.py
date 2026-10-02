"""2GEO08 Thruster Pack (Cargo, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO08.md"""

from engine.cards import development_cost, operation, state_check
from engine.ops import A, Spend, can_afford

from ._util import is_suit

development_cost("2GEO08", Spend(dilithium=2))


@operation("2GEO08", 0, uses=[A.DEPLOY, A.FIND, A.BEAM, A.GAIN_ACTION])
def deploy_and_beam(ctx, actions):
    """PLAY: Deploy this card. You may find up to 3 Person and beam them here. If you beamed at least 2,
    gain an Action."""
    pack = ctx.this_card
    yield from actions.deploy(pack)
    beamed = 0
    while beamed < 3 and (yield from actions.may(f"Find a Person and beam it to {ctx.name(pack)}? ({beamed} so far)")):
        person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person", optional=True)
        if not person:
            break
        yield from actions.beam(person, pack)
        beamed += 1
    if beamed >= 2:
        yield from actions.gain_action(1)


@operation("2GEO08", 1, uses=[A.RECALL], requires=lambda ctx: any(is_suit(b, "Person") for b in ctx.this_card.beamed))
def recall_person(ctx, actions):
    """ACTIVATION: Recall a Person beamed here."""
    person = yield from actions.pick_card("Recall which Person?", [b for b in ctx.this_card.beamed if is_suit(b, "Person")])
    yield from actions.recall(person)


@operation("2GEO08", 2, uses=[A.BEAM, A.SPEND, A.REFRESH], cost=[Spend(dilithium=1)],
           requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand + ctx.me.discard))
def beam_person(ctx, actions):
    """ACTIVATION: Spend 1 Dilithium to beam a Person here from your hand or Discard pile. You may spend
    1 Dilithium to refresh this card."""
    person = yield from actions.pick_card("Beam which Person here?",
                                          [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person")])
    yield from actions.beam(person, ctx.this_card)
    if can_afford(ctx.me, dilithium=1) and (yield from actions.may("Spend 1 Dilithium to refresh Thruster Pack?")):
        yield from actions.spend(dilithium=1)
        yield from actions.refresh(ctx.this_card)


@state_check("2GEO08")
def empty(state, owner, inst):
    """PASSIVE: If no cards are beamed here, dismiss this card."""
    return not inst.beamed
