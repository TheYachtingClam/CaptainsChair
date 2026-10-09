"""1BUR06 Adira Tal (Person, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR06.md"""

from engine.cards import development_cost, duty_slots, operation
from engine.ops import A, Condition, LogFromHand, Spend

development_cost("1BUR06", Spend(dilithium=2), Condition(lambda ctx: ctx.track("research") >= 7, "have 7+ Research"))


@operation("1BUR06", 0, uses=[A.LOG, A.FIND], cost=[LogFromHand(zones=("hand", "discard"))])
def memories(ctx, actions):
    """PLAY: Log a card from your hand or Discard pile to find any card."""
    yield from actions.find(lambda i: True, "any card")


@operation("1BUR06", 1, uses=[A.SCAN, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "would_gain_market" and ev["seat"] == ctx.me.seat
           and len(ev.get("suits") or []) == 1)
def curiosity(ctx, actions):
    """REACTION: When you would gain a card, scan 2 of the same suit instead and gain 1 [Glory]. Only when the gain
    is of one suit (REQ-CORE-42)."""
    yield from actions.scan(2, list(ctx.event["suits"]))
    yield from actions.gain_resource("glory", 1)
    return True


@duty_slots("1BUR06")
def science_officer(state, owner, inst):
    """PASSIVE: You may have an additional Person with Scientist/Engineer on duty."""
    return [("Scientist", "Engineer")]
