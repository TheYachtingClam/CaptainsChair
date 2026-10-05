"""3RIK04 Solving Science Mysteries (Directive, Ongoing, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK04.md"""

from engine.cards import development_cost, operation, skill_rewrite
from engine.ops import A, Spend, SpendVariable, TakeIncidentCost

from ._util import has_trait

development_cost("3RIK04", SpendVariable(lambda ctx: {"dilithium": ctx.track("military") // 2}))


@operation("3RIK04", 0, uses=[A.TAKE_INCIDENT, A.DEPLOY], cost=[TakeIncidentCost()])
def commit(ctx, actions):
    """PLAY: Take an Incident to deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("3RIK04", 1, uses=[A.SCAN_FOR, A.DRAW, A.DEPLOY], cost=[Spend(dilithium=4)])
def investigate(ctx, actions):
    """PLAY: Spend 4 [Dilithium] to scan for a Scientist and draw a card. Deploy this card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Scientist"), "a Scientist")
    yield from actions.draw(1)
    yield from actions.deploy(ctx.this_card)


@skill_rewrite("3RIK04")
def science_first(state, owner, source, icons):
    """PASSIVE: All of your [Military] are treated as [Research] instead. Any Skill can still be either."""
    return ["Research" if icon == "Military" else icon for icon in icons]
