"""1SEL12 T'Pel (Person). Spec: resources/scans/base_game/cards/captains/sela/1SEL12.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A, Spend


@operation("1SEL12", 0, uses=[A.TRIGGER_CONTROL, A.DRAW], cost=[Spend(latinum=1)],
           requires=lambda ctx: ctx.track("influence") >= 4 and bool(ctx.controlled_locations()))
def impostor(ctx, actions):
    """PLAY: Requires [Influence] 4. Spend 1 [Latinum] to trigger the control operation of one of your controlled
    Location. Draw a card."""
    loc = yield from actions.pick_card("Trigger the CONTROL of which Location?", ctx.controlled_locations())
    if loc:
        yield from actions.trigger_control(loc)
    yield from actions.draw(1)


@hand_size_modifier("1SEL12")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1
