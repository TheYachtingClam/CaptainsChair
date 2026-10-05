"""Soval's Crew board missions. Specs: resources/scans/to_boldly_go/boards/cb-soval-basic.md and
cb-soval-advanced.md. A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import count_traits, has_trait, is_suit, ships



@mission_goal("my-mind-to-your-mind")
def mind_meld_goal(ctx):
    """Have 5 cards with [Research]/[Any Skill] in play (excluding beamed cards). A card counts once."""
    cards = [i for i in ctx.in_play(beamed=False) if {"Research", "Any"} & set(ctx.skills(i))]
    return cards[:5] if len(cards) >= 5 else None


@mission_reward("my-mind-to-your-mind", uses=[A.DRAW, A.GAIN_RESOURCE, A.RETURN_INCIDENT])
def mind_meld_reward(ctx, actions):
    """For each Telepath you have in play, either: draw a card OR gain 1 [Latinum] and you may return an Incident."""
    telepaths = count_traits(ctx, "Telepath")
    for n in range(1, telepaths + 1):
        choice = yield from actions.choose(f"Telepath {n} of {telepaths}: choose one.",
                                           [("draw", "Draw a card"),
                                            ("latinum", "Gain 1 Latinum, and you may return an Incident")])
        if choice == "draw":
            yield from actions.draw(1)
        else:
            yield from actions.gain_resource("latinum", 1)
            incidents = [i for i in ctx.me.hand if is_suit(i, "Incident")]
            card = yield from actions.pick_card("Return an Incident?", incidents, optional=True, none_label="No")
            if card:
                yield from actions.return_incident(card)


@mission_goal("cooperation-with-starfleet")
def cooperation_goal(ctx):
    """Have 3 Ship deployed, 3 Starfleet beamed, and 1 Encounter in play."""
    deployed = ships(ctx)
    beamed = [b for host in ctx.in_play(beamed=False) for b in host.beamed if has_trait(b, "Starfleet")]
    encounters = [i for i in ctx.in_play() if is_suit(i, "Encounter")]
    if len(deployed) >= 3 and len(beamed) >= 3 and encounters:
        return [*deployed[:3], *beamed[:3], encounters[0]]
    return None


@mission_reward("cooperation-with-starfleet", uses=[A.SCAN_FOR, A.SEND_AWAY_TEAM])
def cooperation_reward(ctx, actions):
    """Scan for either Human or Starfleet. You may send 1 [Away Team] each to up to 3 different Location."""
    trait = yield from actions.choose("Scan for which trait?", [("Human", "Human"), ("Starfleet", "Starfleet")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")
    used: list[str] = []
    for n in range(1, 4):
        if not (yield from actions.may(f"Send an Away Team to a different Location ({n} of up to 3)?")):
            break
        loc = yield from actions.send_away_team(1, where=lambda l: l.uid not in used)
        if loc is None:
            break
        used.append(loc.uid)


@mission_goal("the-needs-of-the-many")
def needs_goal(ctx):
    """Have 5 Person and 2 Ally in play. Have [Influence] at 5+."""
    people = [i for i in ctx.in_play() if is_suit(i, "Person")]
    allies = [i for i in ctx.in_play() if is_suit(i, "Ally")]
    if ctx.track("influence") >= 5 and len(people) >= 5 and len(allies) >= 2:
        return [*people[:5], *allies[:2]]
    return None


@mission_reward("the-needs-of-the-many", uses=[A.GAIN_ACTION, A.RECALL, A.LOG, A.ENLIST_DEVELOPMENT])
def needs_reward(ctx, actions):
    """Gain an [Action]. You may recall up to 2 beamed cards. You may log a Duty Officer to enlist a Development.
    Ruling: beamed contributors recalled here are not dismissed afterwards (REQ-MS-06)."""
    yield from actions.gain_action(1)
    for n in (1, 2):
        beamed = [b for host in ctx.in_play(beamed=False) for b in host.beamed]
        card = yield from actions.pick_card(f"Recall a beamed card ({n} of up to 2)?", beamed, optional=True,
                                            none_label="Stop")
        if not card:
            break
        yield from actions.recall(card)
    officer = yield from actions.pick_card("Log a Duty Officer to enlist a Development?", list(ctx.me.duty),
                                           optional=True, none_label="No")
    if officer:
        yield from actions.log(officer)
        yield from actions.enlist_development()
