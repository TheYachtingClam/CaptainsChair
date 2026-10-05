"""2PER03 Ash Tyler (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER03.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import count_traits


@operation("2PER03", 0, uses=[A.FIND],
           requires=lambda ctx: count_traits(ctx, "Starfleet", exclude=ctx.this_card)
           >= count_traits(ctx, "Klingon", exclude=ctx.this_card))
def starfleet_officer(ctx, actions):
    """PLAY: Requires Starfleet >= Klingon in play: Find a card with [Military]/[Military Focus].
    Ruling: Tyler counts himself for both traits, so he cancels out of the comparison."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "military"), "a card with Military")


@hand_size_modifier("2PER03")
def glory_hand_size(state, owner, size):
    """PASSIVE: If you have 8+ [Glory], increase your hand size by 2."""
    return size + 2 if owner.glory >= 8 else size


@operation("2PER03", 1, uses=[A.ATTACK, A.DISMISS, A.GAIN_RESOURCE, A.PROMOTE],
           requires=lambda ctx: count_traits(ctx, "Klingon", exclude=ctx.this_card)
           >= count_traits(ctx, "Starfleet", exclude=ctx.this_card))
def klingon_agent(ctx, actions):
    """ATTACK PLAY: Requires Klingon >= Starfleet in play: Dismiss an opponent Duty Officer to gain 2 [Glory]. You may
    promote this card to Duty Officer."""
    if (yield from actions.attack()):
        opp = ctx.opponent
        if opp is None:
            yield from actions.gain_resource("glory", 2)  # the virtual opponent's Duty Officer
        else:
            officer = yield from actions.pick_card("Dismiss which opponent Duty Officer?", list(opp.duty))
            if officer:
                yield from actions.dismiss(officer)
                yield from actions.gain_resource("glory", 2)
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Ash Tyler to Duty Officer?")):
        yield from actions.promote(ctx.this_card)
