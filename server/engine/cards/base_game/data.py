"""1PIC12 Data (Person). Spec: resources/scans/base_game/cards/captains/picard/1PIC12.md"""

from engine.cards import operation
from engine.ops import A

from ._util import others_in_hand

TRACKS = [("research", "Research"), ("influence", "Influence"), ("military", "Military")]


@operation("1PIC12", 0, uses=[A.GAIN_SPECIALTY])
def learn(ctx, actions):
    """PLAY: Gain 1 [Research]/[Influence]/[Military]."""
    track = yield from actions.choose("Gain 1 on which track?", TRACKS)
    yield from actions.gain_specialty(track, 1)


@operation("1PIC12", 1, uses=[A.LOG, A.GAIN_SPECIALTY], requires=lambda ctx: bool(others_in_hand(ctx)))
def memory(ctx, actions):
    """ACTIVATION: Log a card from your hand. If you do, gain 1 [Research]/[Influence]/[Military] for every 5 cards in
    your Log (rounded down). Each point may go on a track of your choice."""
    card = yield from actions.pick_card("Log which card from your hand?", others_in_hand(ctx))
    if not card:
        return
    yield from actions.log(card)
    for n in range(len(ctx.me.log) // 5):
        track = yield from actions.choose(f"Gain 1 on which track ({n + 1} of {len(ctx.me.log) // 5})?", TRACKS)
        yield from actions.gain_specialty(track, 1)
