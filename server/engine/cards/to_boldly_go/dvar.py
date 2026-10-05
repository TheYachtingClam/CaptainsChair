"""2SHI04 D'Var (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI04.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship


@operation("2SHI04", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this ship."""
    yield from actions.deploy(ctx.this_card)


operation("2SHI04", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI04", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("2SHI04", 3, uses=[A.GAIN_SPECIALTY, A.DISMISS], cost=[Spend(latinum=1)],
           requires=lambda ctx: ctx.track("influence") >= 4)
def research(ctx, actions):
    """ACTIVATION: Requires [Influence] 4. Spend 1 [Latinum] to gain 1 [Research] for each [Research] you have in
    play (excluding beamed cards). If you gained 3+ [Research], dismiss this card.
    Ruling: Any Skill icons may count as Research, at the owner's choice."""
    cards = ctx.in_play(beamed=False)
    research = sum(ctx.skills(c).count("Research") for c in cards)
    anys = sum(ctx.skills(c).count("Any") for c in cards)
    count = research
    if anys:
        answer = yield from actions.choose(
            f"You have {research} Research and {anys} Any Skill icon(s). Count how many Any icons as Research?",
            [(str(n), f"{n} (gain {research + n})") for n in range(anys + 1)])
        count += int(answer)
    yield from actions.gain_specialty("research", count)
    if count >= 3:
        yield from actions.dismiss(ctx.this_card)
