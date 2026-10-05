"""2ARC05 Agent Daniels (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC05.md"""

from engine.cards import development_cost, hand_size_modifier, operation
from engine.ops import A, Condition, DiscardFromHand, Spend

from ._util import count_traits, has_trait

development_cost("2ARC05", Spend(dilithium=3), Condition(lambda ctx: count_traits(ctx, "Xindi") >= 2, "2+ Xindi in play"))


@operation("2ARC05", 0, uses=[A.DRAW, A.DRAW_FROM_DISCARD, A.GAIN_SPECIALTY])
def temporal_agent(ctx, actions):
    """PLAY: Draw a card from your deck or Discard pile. For each Anomaly you have in play, gain 1 [Research]. For each
    Ambassador you have in play, gain 1 [Influence]. For each Alien/Xindi you have in play, gain 1 [Military]."""
    source = "deck"
    if ctx.me.discard:
        source = yield from actions.choose("Draw from where?", [("deck", "Your Draw deck"), ("discard", "Your Discard pile")])
    if source == "deck":
        yield from actions.draw(1)
    else:
        yield from actions.draw_from_discard()
    for track, traits in (("research", ("Anomaly",)), ("influence", ("Ambassador",)), ("military", ("Alien", "Xindi"))):
        n = count_traits(ctx, *traits)
        if n:
            yield from actions.gain_specialty(track, n)


@operation("2ARC05", 1, uses=[A.DISCARD, A.RECALL], cost=[DiscardFromHand(1)],
           requires=lambda ctx: any(not has_trait(i, "Time Travel") for i in ctx.me.staging))
def rewrite(ctx, actions):
    """ACTIVATION: Discard a card to recall a non-Time Travel card from your Staging Area."""
    card = yield from actions.pick_card("Recall which card?", [i for i in ctx.me.staging if not has_trait(i, "Time Travel")])
    yield from actions.recall(card)


@hand_size_modifier("2ARC05")
def foresight(state, owner, size):
    """PASSIVE: Increase your hand size by 1 for each of [Research]/[Influence]/[Military] you have at 6+."""
    return size + sum(1 for v in owner.tracks.values() if v >= 6)
