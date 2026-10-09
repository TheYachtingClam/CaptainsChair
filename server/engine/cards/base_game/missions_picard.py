"""Picard's Crew board missions. Specs: resources/scans/base_game/boards/cb-picard-basic.md and
cb-picard-advanced.md. A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A, SPECIES

from ._util import beamed_to_ships, has_trait, is_suit


def _may_junk(actions):
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@mission_goal("peace-negotiations")
def peace_goal(ctx):
    """Have 3 Ally on the same Ship, and at least two of [Military]/[Influence]/[Research] at 4+."""
    if sum(ctx.track(t) >= 4 for t in ("research", "influence", "military")) < 2:
        return None
    for _, cards in beamed_to_ships(ctx):
        allies = [c for c in cards if is_suit(c, "Ally")]
        if len(allies) >= 3:
            return allies[:3]
    return None


@mission_reward("peace-negotiations", uses=[A.GAIN_RESOURCE, A.DRAW, A.JUNK])
def peace_reward(ctx, actions):
    """Gain 4 [Dilithium] and draw 4 cards. You may junk a card from the Market."""
    yield from actions.gain_resource("dilithium", 4)
    yield from actions.draw(4)
    yield from _may_junk(actions)


@mission_goal("arbiter-of-succession")
def arbiter_goal(ctx):
    """Have 3 Klingon on the same Ship."""
    for _, cards in beamed_to_ships(ctx):
        klingons = [c for c in cards if has_trait(c, "Klingon")]
        if len(klingons) >= 3:
            return klingons[:3]
    return None


@mission_reward("arbiter-of-succession", uses=[A.GAIN_RESOURCE, A.GAIN_SPECIALTY, A.GAIN_ACTION, A.JUNK])
def arbiter_reward(ctx, actions):
    """Gain 1 [Glory], and 1 [Influence]/[Military]. Gain an [Action]. You may junk a card from the Market."""
    yield from actions.gain_resource("glory", 1)
    track = yield from actions.choose("Gain 1 on which track?", [("influence", "Influence"), ("military", "Military")])
    yield from actions.gain_specialty(track, 1)
    yield from actions.gain_action(1)
    yield from _may_junk(actions)


@mission_goal("seek-out-new-life")
def new_life_goal(ctx):
    """Have 6 Different Species (excluding cards with Human/Starfleet) in play. Each Alien and each Transcendent
    counts as a different one."""
    cards = [i for i in ctx.in_play() if not ({"Human", "Starfleet"} & ctx.traits(i))]
    named = SPECIES - {"Alien"}
    seen: dict[str, object] = {}
    extra = []
    for inst in cards:
        traits = ctx.traits(inst)
        if "Alien" in traits or "Transcendent" in traits:
            extra.append(inst)  # each such card is a species of its own
            continue
        for species in sorted(traits & named):
            seen.setdefault(species, inst)
    found = list(seen.values()) + extra
    return found[:6] if len(seen) + len(extra) >= 6 else None


@mission_reward("seek-out-new-life", uses=[A.TAKE_ENCOUNTER])
def new_life_reward(ctx, actions):
    """Take the top Discovery (Encounter)."""
    yield from actions.take_encounter()
