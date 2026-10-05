"""2PER06 Harry Mudd (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER06.md
The attack PLAY arrives in Step 4."""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


def _recallable(ctx):
    return [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]


@operation("2PER06", 1, uses=[A.DISMISS, A.RECALL], requires=lambda ctx: bool(_recallable(ctx)))
def skip_town(ctx, actions):
    """ACTIVATION: Dismiss this card to recall a non-Time Travel card from your Staging Area."""
    yield from actions.dismiss(ctx.this_card)
    card = yield from actions.pick_card("Recall which card from your Staging Area?", _recallable(ctx))
    yield from actions.recall(card)
