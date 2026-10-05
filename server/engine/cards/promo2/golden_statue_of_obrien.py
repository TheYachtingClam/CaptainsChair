"""0CAR03 Golden Statue of O'Brien (Cargo, promo). Spec: resources/scans/promo2/cards/cargo/0CAR03.md
"""

from engine.cards import endgame, operation
from engine.ops import A

from ._util import has_trait


@operation("0CAR03", 0, uses=[A.FIND, A.DEPLOY])
def unveil(ctx, actions):
    """PLAY: You may find an Engineer. Deploy this card."""
    if (yield from actions.may("Find an Engineer?")):
        yield from actions.find(lambda i: has_trait(i, "Engineer"), "an Engineer", optional=True)
    yield from actions.deploy(ctx.this_card)


@endgame("0CAR03")
def engineers_in_log(state, player):
    """ENDGAME: Score 1 [VP] for each Engineer in your Log."""
    return sum(1 for i in player.log if has_trait(i, "Engineer"))


def _beamed(ctx):
    return [b for host in ctx.in_play(beamed=False) for b in host.beamed]


@operation("0CAR03", 1, uses=[A.RECALL],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("by") == ctx.me.seat and ctx.event_card is not None
           and has_trait(ctx.event_card, "Engineer") and bool(_beamed(ctx)))
def tribute(ctx, actions):
    """REACTION: After logging an Engineer recall a beamed card."""
    card = yield from actions.pick_card("Recall which beamed card?", _beamed(ctx))
    if card:
        yield from actions.recall(card)
