"""2CAR08 Horta (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR08.md
"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


@operation("2CAR08", 0, uses=[A.JUNK, A.LOG, A.ENLIST_DEVELOPMENT, A.DEPLOY])
def tunnel(ctx, actions):
    """PLAY: Junk a card from the Market. You may log an Attack to enlist a Development. Deploy this card."""
    yield from actions.junk()
    attacks = others_in_hand(ctx, lambda i: has_trait(i, "Attack"))
    card = yield from actions.pick_card("Log an Attack from your hand to enlist a Development?", attacks,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)
        yield from actions.enlist_development()
    yield from actions.deploy(ctx.this_card)


@operation("2CAR08", 1, uses=[A.GAIN_RESOURCE], requires=lambda ctx: ctx.track("research") >= 4,
           trigger=lambda ctx, ev: ev["kind"] == "gain_resource" and ev["seat"] == ctx.me.seat
           and ev.get("resource") == "dilithium" and ctx.track("research") >= 4)
def mine(ctx, actions):
    """REACTION: Requires [Research] 4. After gaining [Dilithium], gain 2 additional [Dilithium].
    Ruling: its own gain cannot re-trigger it, because Horta is exhausted."""
    yield from actions.gain_resource("dilithium", 2)
