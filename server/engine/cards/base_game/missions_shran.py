"""Shran's Crew board missions. Specs: resources/scans/base_game/boards/cb-shran-basic.md and cb-shran-advanced.md.
A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from itertools import permutations

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import beamed_to_ships, has_trait, is_suit

FEDERATION = ("Vulcan", "Tellarite", "Andorian", "Alien", "Ambassador", "Communication")


@mission_goal("securing-andorias-borders")
def borders_goal(ctx):
    """Have 3 controlled Location in play, and 4 Weapon in play."""
    weapons = [i for i in ctx.in_play() if has_trait(i, "Weapon")]
    locations = ctx.controlled_locations()
    return [*locations[:3], *weapons[:4]] if len(locations) >= 3 and len(weapons) >= 4 else None


@mission_reward("securing-andorias-borders", uses=[A.SCAN, A.DRAW, A.GAIN_ACTION])
def borders_reward(ctx, actions):
    """Scan 1 of Ship, draw a card, gain an [Action]."""
    yield from actions.scan(1, ["Ship"])
    yield from actions.draw(1)
    yield from actions.gain_action(1)


def _delegates(cards):
    """A Human and three other cards showing three different traits of the six, or None. One card, one trait."""
    for human in [c for c in cards if has_trait(c, "Human")]:
        others = [c for c in cards if c is not human]
        for trio in permutations(FEDERATION, 3):
            picked, pool = [], list(others)
            for trait in trio:
                card = next((c for c in pool if has_trait(c, trait)), None)
                if card is None:
                    break
                picked.append(card)
                pool.remove(card)
            else:
                return [human, *picked]
    return None


@mission_goal("founding-the-federation")
def federation_goal(ctx):
    """Have 1 Human and 3 different of Vulcan / Tellarite / Andorian / Alien / Ambassador / Communication on the same
    Ship. Ruling: four different cards."""
    for _, cards in beamed_to_ships(ctx):
        found = _delegates(cards)
        if found:
            return found
    return None


@mission_reward("founding-the-federation", uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def federation_reward(ctx, actions):
    """Gain 2 [Research], 2 [Influence], and 2 [Military]. You may send an [Away Team] to a Location with Starbase."""
    for track in ("research", "influence", "military"):
        yield from actions.gain_specialty(track, 2)
    starbase = lambda loc: has_trait(loc, "Starbase")  # noqa: E731
    if actions.away_targets(starbase) and (yield from actions.may("Send an Away Team to a Starbase Location?")):
        yield from actions.send_away_team(1, starbase)


@mission_goal("andorian-mining-consortium")
def consortium_goal(ctx):
    """Have 3 Business in play."""
    business = [i for i in ctx.in_play() if has_trait(i, "Business")]
    return business[:3] if len(business) >= 3 else None


@mission_reward("andorian-mining-consortium", uses=[A.SCAN, A.GAIN_RESOURCE, A.FREE_PLAY])
def consortium_reward(ctx, actions):
    """Scan 1 of Cargo, gain 2 [Latinum] and 1 [Glory]. You may free play an Incident to gain 1 [Glory]."""
    yield from actions.scan(1, ["Cargo"])
    yield from actions.gain_resource("latinum", 2)
    yield from actions.gain_resource("glory", 1)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    incident = yield from actions.pick_card("Free play an Incident to gain 1 Glory?", incidents, optional=True,
                                            none_label="No")
    if incident:
        yield from actions.free_play(incident)
        yield from actions.gain_resource("glory", 1)
