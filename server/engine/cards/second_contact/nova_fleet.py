"""3ALL03 Nova Fleet (Ally). Spec: resources/scans/second_contact/cards/ally/3ALL03.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, opponent_has


@operation("3ALL03", 0, uses=[A.GAIN_CARD, A.LOG])
def salvage(ctx, actions):
    """PLAY: Gain an Ally/Cargo from the Junk. Log this card."""
    yield from actions.gain_card(["Ally", "Cargo"], label="an Ally or Cargo from the Junk", only_junk=True)
    yield from actions.log(ctx.this_card)


@operation("3ALL03", 1, uses=[A.GAIN_CARD, A.TAKE_INCIDENT],
           trigger=lambda ctx, ev: ev["kind"] == "would_junk" and ev["seat"] == ctx.me.seat)
def salvage_rights(ctx, actions):
    """SUPPORT: When you junk a card from the Market, gain it to your hand instead. If your opponent has a Lower
    Decker in play, take an Incident. Ruling: a card with tokens cannot be junked, so it cannot be gained this way."""
    target = ctx.event_card
    if target is None:
        return False
    yield from actions.gain_card(None, lambda i: i.uid == target.uid, ctx.name(target), to_hand=True)
    if opponent_has(ctx, lambda i: has_trait(i, "Lower Decker")):
        yield from actions.take_incident()
    return True
