"""2GEO05 Red Angel (Encounter, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO05.md"""

from engine import cards as registry
from engine.cards import development_cost, endgame, operation
from engine.ops import A, Spend, TakeIncidentCost
from engine.scoring import owned_cards

from ._util import has_trait, is_suit

development_cost("2GEO05", Spend(dilithium=3), TakeIncidentCost())
registry.SCANS_INCLUDE_JUNK.add("2GEO05")  # PASSIVE: Whenever scanning, include cards in the Junk too.


@operation("2GEO05", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("2GEO05", 2, uses=[A.GAIN_ACTION, A.RECALL], cost=[TakeIncidentCost()])
def action_and_recall(ctx, actions):
    """ACTIVATION: Take an Incident to gain an Action. You may recall a non-Time Travel, non-Encounter card
    from your Staging Area."""
    yield from actions.gain_action(1)
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel") and not is_suit(i, "Encounter")]
    card = yield from actions.pick_card("Recall a card from your Staging Area?", cards, optional=True, none_label="No")
    if card:
        yield from actions.recall(card)


@endgame("2GEO05")
def anomalies(state, player):
    """ENDGAME: Score 1 VP for each of your Anomaly cards."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Anomaly"))
