"""0INC03 Subspace Rhapsody (Incident, promo). Spec: resources/scans/promo2/cards/incident/0INC03.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


def _directives(ctx):
    return [i for i in ctx.me.hand if is_suit(i, "Directive") and i is not ctx.this_card]


@operation("0INC03", 0, uses=[A.PUT, A.RETURN_INCIDENT, A.REFRESH], requires=lambda ctx: bool(_directives(ctx)))
def musical_number(ctx, actions):
    """PLAY: Put a Directive in your Staging Area (without triggering its play operation) to return this card. You may
    sing the text of its first play operation to refresh either a Duty Officer OR your Captain.
    Ruling: singing cannot be checked online, so the player confirms they sang."""
    directive = yield from actions.pick_card("Put which Directive into your Staging Area?", _directives(ctx))
    yield from actions.put_into_staging(directive)
    yield from actions.return_incident(ctx.this_card)
    first = next((op.text for op in ctx.card(directive).operations if op.kind == "PLAY"), None)
    if first and (yield from actions.may(f'Did you sing "{first}"?')):
        tired = [i for i in [ctx.me.captain, *ctx.me.duty] if i.exhausted]
        card = yield from actions.pick_card("Refresh your Captain or a Duty Officer?", tired)
        if card:
            yield from actions.refresh(card)


@operation("0INC03", 1, uses=[])
def replaces_an_incident(ctx, actions):
    """SPECIAL: During setup, replace a random Incident in the Incident deck with this card. Done by game setup
    (engine/setup.py, REQ-CS-22); nothing happens during play."""
    return
    yield  # pragma: no cover
