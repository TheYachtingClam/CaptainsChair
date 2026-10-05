"""Georgiou's Crew board missions. Specs: resources/scans/to_boldly_go/boards/cb-georgiou-basic.md and
cb-georgiou-advanced.md. A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import count_traits, has_trait, is_suit, ships


def _beamed_to(ship):
    return list(ship.beamed)


@mission_goal("call-in-the-reinforcements")
def reinforcements_goal(ctx):
    """Have [Military] at 6+. Have Cmdr. Burnham on duty, and an Incident beamed to the U.S.S. Shenzhou."""
    if ctx.track("military") < 6:
        return None
    burnham = next((i for i in ctx.me.duty if i.card == "2GEO13"), None)
    for shenzhou in [s for s in ctx.me.fleet if s.card == "2GEO02"]:
        incident = next((b for b in _beamed_to(shenzhou) if is_suit(b, "Incident")), None)
        if burnham and incident:
            return [burnham, shenzhou, incident]
    return None


@mission_reward("call-in-the-reinforcements", uses=[A.SCAN, A.FREE_PLAY, A.GAIN_RESOURCE, A.DISMISS])
def reinforcements_reward(ctx, actions):
    """Scan 1 of Ship and free play the gained card. Gain 3 [Dilithium]. If you have 1+ Klingon in play (excluding
    beamed cards), dismiss Cmdr. Burnham and gain 2 [Glory].
    Ruling: the Ship is free played from wherever it was gained to."""
    ship = yield from actions.scan(1, ["Ship"])
    if ship and actions.free_play_candidates(lambda i: i is ship, cards=[ship]):
        yield from actions.free_play(ship)
    yield from actions.gain_resource("dilithium", 3)
    if count_traits(ctx, "Klingon", beamed=False):
        burnham = next((i for i in ctx.me.duty if i.card == "2GEO13"), None)
        if burnham:
            yield from actions.dismiss(burnham)
        yield from actions.gain_resource("glory", 2)


@mission_goal("hardly-a-negotiation")
def negotiation_goal(ctx):
    """Have 3 Person (excluding cards with Starfleet) on the same Ship, and have [Research], [Influence], and
    [Military] all at 1+."""
    if min(ctx.track(t) for t in ("research", "influence", "military")) < 1:
        return None
    for ship in ships(ctx):
        people = [c for c in [ship, *ship.beamed] if is_suit(c, "Person") and not has_trait(c, "Starfleet")]
        if len(people) >= 3:
            return people[:3]
    return None


@mission_reward("hardly-a-negotiation", uses=[A.ENLIST_DEVELOPMENT, A.DRAW, A.GAIN_ACTION])
def negotiation_reward(ctx, actions):
    """You may enlist a Development. If you have 2+ Vulcan in play, either draw a card OR gain an [Action]."""
    if (yield from actions.may("Enlist a Development?")):
        yield from actions.enlist_development()
    if count_traits(ctx, "Vulcan") >= 2:
        choice = yield from actions.choose("Draw a card or gain an Action?", [("draw", "Draw a card"),
                                                                              ("action", "Gain an Action")])
        if choice == "draw":
            yield from actions.draw(1)
        else:
            yield from actions.gain_action(1)


@mission_goal("gazing-at-the-stars")
def stars_goal(ctx):
    """Have [Research] at 7+, and 2 Alien in play."""
    aliens = [i for i in ctx.in_play() if "Alien" in ctx.traits(i)]
    return aliens[:2] if ctx.track("research") >= 7 and len(aliens) >= 2 else None


@mission_reward("gazing-at-the-stars", uses=[A.ENLIST_DEVELOPMENT, A.DRAW])
def stars_reward(ctx, actions):
    """Enlist Kaminar for free. Draw a card for each Scientist you have in play.
    Ruling: if Kaminar already left the Development pile, the first step does nothing."""
    if any(i.card == "2GEO03" for i in ctx.me.development):
        yield from actions.enlist_development(free=True, pred=lambda i: i.card == "2GEO03")
    scientists = count_traits(ctx, "Scientist")
    if scientists:
        yield from actions.draw(scientists)
