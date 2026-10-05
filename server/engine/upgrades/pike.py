"""Pike's Five-Year Mission upgrades. Spec: resources/scans/second_contact/command/pike.md"""

from engine.ops import A, TakeIncidentCost
from engine.upgrades import boost, own, reinforce
from engine.upgrades._shared import ICON_SKILLS

CREW = "pike"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.ENLIST_DEVELOPMENT], cost=[TakeIncidentCost()])
def enlist_a_development(ctx, actions):
    """BOOST: Before drawing the starting hand, take an Incident to enlist a Development."""
    yield from actions.enlist_development()


@boost(CREW, "win", 1, uses=[A.GAIN_SPECIALTY])
def one_of_each(ctx, actions):
    """BOOST: Gain 1 [Research], 1 [Influence], and 1 [Military]."""
    for track in ("research", "influence", "military"):
        yield from actions.gain_specialty(track, 1)


@reinforce(CREW, "loss", 0)
def a_skill_card(cards):
    """REINFORCE: A card with [Research]/[Influence]/[Military] from your Available cards or Reserve deck."""
    return [own(cards, "Available", "Reserve", pred=lambda c: bool(ICON_SKILLS & set(c.skills)))]


@boost(CREW, "loss", 1, moment="after_hand", uses=[A.FREE_PLAY, A.RECALL])
def free_play_then_recall(ctx, actions):
    """BOOST: After drawing the starting hand, free play a non-Time Travel card, then recall it."""
    cards = actions.free_play_candidates(lambda i: not ctx.has(i, "Time Travel"))
    if not cards:
        ctx.state.emit("No non-Time Travel card can be free played.")
        return
    inst = yield from actions.pick_card("Free play which card? It is recalled afterwards.", cards)
    uid = inst.uid
    yield from actions.free_play(inst)
    played = next((i for i in ctx.in_play() if i.uid == uid), None)
    if played is not None:
        yield from actions.recall(played)
