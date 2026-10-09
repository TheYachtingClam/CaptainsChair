"""Koloth's Crew board missions. Specs: resources/scans/base_game/boards/cb-koloth-basic.md and
cb-koloth-advanced.md. A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import count_traits, distinct_traits, has_trait, ships, species_of


@mission_goal("expanding-the-empire")
def empire_goal(ctx):
    """Have a total of 6 deployed Ship / controlled Location in play, at least one of each."""
    fleet, locations = ships(ctx), ctx.controlled_locations()
    return [*fleet, *locations][:6] if fleet and locations and len(fleet) + len(locations) >= 6 else None


@mission_reward("expanding-the-empire", uses=[A.ENLIST_RESERVE, A.ENLIST_DEVELOPMENT, A.DISMISS])
def empire_reward(ctx, actions):
    """Enlist two Reserves OR Enlist a Development. Dismiss a deployed Ship."""
    choice = yield from actions.choose("Expanding the Empire:", [("reserves", "Enlist two Reserves"),
                                                                 ("development", "Enlist a Development")])
    if choice == "reserves":
        yield from actions.enlist_reserve()
        yield from actions.enlist_reserve()
    else:
        yield from actions.enlist_development()
    ship = yield from actions.pick_card("Dismiss which deployed Ship?", ships(ctx))
    if ship:
        yield from actions.dismiss(ship)


@mission_goal("romulan-weapons-trade-agreement")
def trade_goal(ctx):
    """Have 1 or more Romulan on a Ship that has Klingon."""
    for ship in ships(ctx):
        romulan = next((b for b in ship.beamed if has_trait(b, "Romulan")), None)
        if romulan is not None and has_trait(ship, "Klingon"):
            return [ship, romulan]
    return None


@mission_reward("romulan-weapons-trade-agreement", uses=[A.GAIN_SPECIALTY, A.ENLIST_DEVELOPMENT, A.JUNK])
def trade_reward(ctx, actions):
    """Gain 1 [Military] for each Romulan in play. Enlist Prototype Cloak for free. You may junk a card from the
    Market. If Prototype Cloak already left the Development pile, that step does nothing."""
    romulans = count_traits(ctx, "Romulan")
    if romulans:
        yield from actions.gain_specialty("military", romulans)
    if any(i.card == "1KOL03" for i in ctx.me.development):
        yield from actions.enlist_development(free=True, pred=lambda i: i.card == "1KOL03")
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@mission_goal("sabotage")
def sabotage_goal(ctx):
    """Have 2 Different Species (excluding cards with Klingon), 2 Weapon (excluding your Captain), and 1 Scientist in
    play."""
    cards = ctx.in_play()
    outsiders = [i for i in cards if not has_trait(i, "Klingon") and species_of(i)]
    weapons = [i for i in cards if i is not ctx.me.captain and has_trait(i, "Weapon")]
    scientist = next((i for i in cards if has_trait(i, "Scientist")), None)
    if scientist is None or len(weapons) < 2:
        return None
    from engine.ops import SPECIES

    if distinct_traits(outsiders, SPECIES) < 2:
        return None
    return [*outsiders[:2], *weapons[:2], scientist]


@mission_reward("sabotage", uses=[A.ENLIST_RESERVE, A.ATTACK, A.TAKE_INCIDENT])
def sabotage_reward(ctx, actions):
    """ATTACK REWARD: Enlist a Reserve. You may force your opponent to take 2 Incident."""
    yield from actions.enlist_reserve()
    if (yield from actions.may("Force your opponent to take 2 Incidents?")) and (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
        yield from actions.take_incident(opponent=True)
