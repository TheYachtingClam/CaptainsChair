"""Freeman's Crew board missions. Specs: resources/scans/second_contact/boards/cb-freeman-basic.md and
cb-freeman-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import has_trait, is_suit, ships

TRACKS = ("research", "influence", "military")


def _ship_with(ctx, pred, n):
    """A deployed Ship whose card plus its beamed cards include n matching cards: (ship, those cards)."""
    for ship in ships(ctx):
        cards = [c for c in [ship, *ship.beamed] if pred(c)]
        if len(cards) >= n:
            return ship, cards
    return None, []


@mission_goal("project-swing-by")
def swing_by_goal(ctx):
    """Have a deployed Ship with 4 Ally (including its beamed cards), and 2 of your tracks at 4+."""
    _, allies = _ship_with(ctx, lambda c: is_suit(c, "Ally"), 4)
    high = sum(1 for t in TRACKS if ctx.track(t) >= 4)
    return allies[:4] if allies and high >= 2 else None


@mission_reward("project-swing-by", uses=[A.GAIN_RESOURCE, A.DRAW, A.JUNK])
def swing_by_reward(ctx, actions):
    """Gain 4 [Dilithium]. Draw 4 cards. You may junk a card from the Market."""
    yield from actions.gain_resource("dilithium", 4)
    yield from actions.draw(4)
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@mission_goal("beta-shift")
def beta_shift_goal(ctx):
    """Have a deployed Ship with 4 Person (including its beamed cards), 2 of which are Lower Decker."""
    for ship in ships(ctx):
        people = [c for c in [ship, *ship.beamed] if is_suit(c, "Person")]
        deckers = [c for c in people if has_trait(c, "Lower Decker")]
        if len(people) >= 4 and len(deckers) >= 2:
            return deckers[:2] + [c for c in people if c not in deckers[:2]][:2]
    return None


@mission_reward("beta-shift", uses=[A.SCAN_FOR, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def beta_shift_reward(ctx, actions):
    """You may scan for an Anomaly. You may send an [Away Team] to a Location. Gain 2 [Glory]."""
    if (yield from actions.may("Scan for an Anomaly?")):
        yield from actions.scan_for(lambda i: has_trait(i, "Anomaly"), "an Anomaly")
    if (yield from actions.may("Send an Away Team to a Location?")):
        yield from actions.send_away_team(1)
    yield from actions.gain_resource("glory", 2)


def _ships_at_neutral(ctx):
    """For each neutral Location: your deployed Ships there, and Ships beamed to them or to the Location."""
    out = {}
    for loc in ctx.state.neutral:
        cards = []
        for ship in ctx.ships_at(loc):
            cards += [ship, *[b for b in ship.beamed if is_suit(b, "Ship")]]
        cards += [b for b in loc.beamed if is_suit(b, "Ship")]
        out[loc.uid] = cards
    return out


@mission_goal("calling-all-your-friends")
def friends_goal(ctx):
    """Have 5 Ships at the same neutral Location. Each Ship token counts once here: the California-class fleet's
    double weight is only for securing."""
    for cards in _ships_at_neutral(ctx).values():
        if len(cards) >= 5:
            return cards
    return None


@mission_reward("calling-all-your-friends", uses=[A.GAIN_SPECIALTY, A.SCAN_FOR])
def friends_reward(ctx, actions):
    """Twice: gain 1 [Research]/[Influence]/[Military], whichever is the lowest. Scan for a card with a [Research]/
    [Influence]/[Military] Focus icon."""
    for _ in (1, 2):
        lowest = min(TRACKS, key=lambda t: ctx.track(t))  # ties go Research, Influence, Military
        yield from actions.gain_specialty(lowest, 1)
    yield from actions.scan_for(lambda i: ctx.card(i).focus in ("Research", "Influence", "Military"),
                                "a card with a Focus icon")
