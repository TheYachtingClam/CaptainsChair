"""Burnham's Crew board missions. Specs: resources/scans/base_game/boards/cb-burnham-basic.md and
cb-burnham-advanced.md. A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import beamed_to_ships, has_trait, is_suit, species_of


@mission_goal("investigate-the-burn")
def burn_goal(ctx):
    """Have 2 Incident, a Scientist, and a Kelpien on the same Ship, and [Research] at 5+."""
    if ctx.track("research") < 5:
        return None
    for _ship, cards in beamed_to_ships(ctx):
        incidents = [i for i in cards if is_suit(i, "Incident")]
        scientist = next((i for i in cards if has_trait(i, "Scientist")), None)
        kelpien = next((i for i in cards if has_trait(i, "Kelpien")), None)
        if len(incidents) >= 2 and scientist is not None and kelpien is not None:
            found = [*incidents[:2], scientist]
            return found if any(i.uid == kelpien.uid for i in found) else [*found, kelpien]
    return None


@mission_reward("investigate-the-burn", uses=[A.TAKE_ENCOUNTER, A.MOVE_RESOURCES])
def burn_reward(ctx, actions):
    """Take the top Discovery and put it on the top of your deck. Recrystallize up to 2 [Dilithium]."""
    yield from actions.take_encounter(to="top")
    yield from actions.recrystallize(2)


@mission_goal("reunite-the-federation")
def federation_goal(ctx):
    """Have an Anomaly logged. Have 3 Starfleet in play (excluding your Captain). Have 3 Different Species (excluding
    cards with Starfleet) on the same Ship."""
    anomaly = next((i for i in ctx.me.log if has_trait(i, "Anomaly")), None)
    starfleet = [i for i in ctx.in_play() if i is not ctx.me.captain and has_trait(i, "Starfleet")]
    if anomaly is None or len(starfleet) < 3:
        return None
    for _ship, cards in beamed_to_ships(ctx):
        seen, used = set(), []
        for inst in cards:
            fresh = species_of(inst) - seen
            if fresh and not has_trait(inst, "Starfleet"):
                seen |= fresh
                used.append(inst)
        if len(seen) >= 3:
            return [*starfleet[:3], *used]
    return None


@mission_reward("reunite-the-federation", uses=[A.TAKE_CONTROL])
def federation_reward(ctx, actions):
    """Draw the top Location and take control of it."""
    if ctx.state.location_deck:
        yield from actions.take_control(ctx.state.location_deck[0])


@mission_goal("dealing-with-the-emerald-chain")
def chain_goal(ctx):
    """Have 2 Business/Orion in play. Have 2 Shady logged."""
    traders = [i for i in ctx.in_play() if has_trait(i, "Business", "Orion")]
    shady = [i for i in ctx.me.log if has_trait(i, "Shady")]
    return traders[:2] if len(traders) >= 2 and len(shady) >= 2 else None


@mission_reward("dealing-with-the-emerald-chain", uses=[A.FREE_PLAY, A.GAIN_RESOURCE])
def chain_reward(ctx, actions):
    """You may free play an Incident to gain 2 [Glory], 2 [Dilithium], and 2 [Latinum]."""
    incident = yield from actions.pick_card("Free play an Incident to gain 2 Glory, 2 Dilithium and 2 Latinum?",
                                            actions.free_play_candidates(lambda i: is_suit(i, "Incident")),
                                            optional=True, none_label="No")
    if incident:
        yield from actions.free_play(incident)
        for kind in ("glory", "dilithium", "latinum"):
            yield from actions.gain_resource(kind, 2)
