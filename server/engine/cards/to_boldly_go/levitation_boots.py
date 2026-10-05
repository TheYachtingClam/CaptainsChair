"""2KIRK17 Levitation Boots (Cargo, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK17.md"""

from engine.cards import operation, state_check
from engine.ops import A, Spend

from ._util import is_suit


def _people(ctx):
    return [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person")]


@operation("2KIRK17", 0, uses=[A.DEPLOY, A.BEAM])
def strap_in(ctx, actions):
    """PLAY: Deploy this card. You may beam up to 3 Person from your hand or Discard pile here.
    Ruling: with nothing beamed here afterwards, its PASSIVE dismisses it at once."""
    yield from actions.deploy(ctx.this_card)
    for n in (1, 2, 3):
        person = yield from actions.pick_card(f"Beam a Person here ({n} of up to 3)?", _people(ctx), optional=True,
                                              none_label="Stop")
        if not person:
            break
        yield from actions.beam(person, ctx.this_card)


@operation("2KIRK17", 1, uses=[A.RECALL], requires=lambda ctx: any(is_suit(b, "Person") for b in ctx.this_card.beamed))
def step_off(ctx, actions):
    """ACTIVATION: Recall a Person beamed here."""
    person = yield from actions.pick_card("Recall which Person?", [b for b in ctx.this_card.beamed if is_suit(b, "Person")])
    yield from actions.recall(person)


@operation("2KIRK17", 2, uses=[A.BEAM], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(_people(ctx)))
def step_on(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to beam a Person here from your hand or Discard pile."""
    person = yield from actions.pick_card("Beam which Person here?", _people(ctx))
    yield from actions.beam(person, ctx.this_card)


@state_check("2KIRK17")
def empty_boots(state, owner, inst):
    """PASSIVE: If no cards are beamed here, dismiss this card."""
    return inst in owner.fleet and not inst.beamed
