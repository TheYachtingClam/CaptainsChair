"""Rebner's Crew board missions. Specs: resources/scans/to_boldly_go/boards/cb-rebner-basic.md and
cb-rebner-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import has_trait, ships

SMART = ("Engineer", "Scientist", "Communication")


def _smart_cards(ctx):
    """One card per trait (one card may cover several), preferring non-Pakled cards so the Glory bonus can apply."""
    cards = sorted(ctx.in_play(), key=lambda i: has_trait(i, "Pakled"))
    picks = []
    for trait in SMART:
        found = next((c for c in cards if has_trait(c, trait)), None)
        if found is None:
            return None
        if found not in picks:
            picks.append(found)
    return picks


@mission_goal("things-that-make-us-smart")
def smart_goal(ctx):
    """Have an Engineer, a Scientist, and a Communication in play."""
    return _smart_cards(ctx)


@mission_reward("things-that-make-us-smart", uses=[A.ENLIST_DEVELOPMENT, A.GAIN_RESOURCE])
def smart_reward(ctx, actions):
    """Enlist a Development, paying 1 [Dilithium] or 1 [Latinum] less. If none of the cards fulfilling the goal have
    Pakled, gain 2 [Glory]."""
    picks = _smart_cards(ctx) or []
    no_pakled = bool(picks) and not any(has_trait(c, "Pakled") for c in picks)
    yield from actions.enlist_development(discount=True)
    if no_pakled:
        yield from actions.gain_resource("glory", 2)


@mission_goal("things-that-make-us-strong")
def strong_goal(ctx):
    """Have 2 Weapon in play and [Military] 6+."""
    weapons = [i for i in ctx.in_play() if has_trait(i, "Weapon")]
    return weapons[:2] if len(weapons) >= 2 and ctx.track("military") >= 6 else None


@mission_reward("things-that-make-us-strong", uses=[A.SCAN_FOR, A.DRAW])
def strong_reward(ctx, actions):
    """Scan for a card with a [Military] Focus icon. Draw 3 cards."""
    yield from actions.scan_for(lambda i: ctx.card(i).focus == "Military", "a card with a Military Focus icon")
    yield from actions.draw(3)


@mission_goal("things-that-make-us-fast")
def fast_goal(ctx):
    """Have 4 deployed Ships and 8 [Dilithium]."""
    deployed = ships(ctx)
    return deployed[:4] if len(deployed) >= 4 and ctx.me.dilithium >= 8 else None


@mission_reward("things-that-make-us-fast", uses=[A.TAKE_CONTROL])
def fast_reward(ctx, actions):
    """Take control of the top card of the Location deck."""
    if ctx.state.location_deck:
        yield from actions.take_control(ctx.state.location_deck[0])
