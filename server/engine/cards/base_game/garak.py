"""1SIS09 Garak (Person, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS09.md"""

from engine.cards import development_cost, hand_size_modifier, operation
from engine.ops import A, Spend

development_cost("1SIS09", Spend(latinum=2))


@operation("1SIS09", 0, uses=[A.ATTACK, A.DISMISS, A.DRAW, A.GAIN_SPECIALTY, A.SPEND, A.SCAN])
def plain_simple_tailor(ctx, actions):
    """ATTACK PLAY: Choose 2 of the following: Dismiss (one of) your opponent's Duty Officer(s) and you draw a card OR
    gain 1 [Influence] OR spend 1 [Latinum] to scan 2 of Person. Only the first option is the attack."""
    labels = {"dismiss": "Dismiss an opponent Duty Officer and draw a card", "influence": "Gain 1 Influence",
              "scan": "Spend 1 Latinum to scan 2 of Person"}
    opp = ctx.opponent
    for n in (1, 2):
        able = {"dismiss": True, "influence": True, "scan": actions.can_spend(latinum=1)}
        choices = [(k, v) for k, v in labels.items() if able[k]]
        if not choices:
            return
        pick = yield from actions.choose(f"Choose option {n} of 2.", choices)
        del labels[pick]
        if pick == "dismiss":
            if (yield from actions.attack()) and opp is not None and opp.duty:
                officer = yield from actions.pick_card("Dismiss which opponent Duty Officer?", list(opp.duty))
                yield from actions.dismiss(officer)
            yield from actions.draw(1)
        elif pick == "influence":
            yield from actions.gain_specialty("influence", 1)
        else:
            yield from actions.spend(latinum=1)
            yield from actions.scan(2, ["Person"])


@hand_size_modifier("1SIS09")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 2."""
    return size + 2
