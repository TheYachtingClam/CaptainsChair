"""2PER01 Admiral Jarok (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER01.md
The PASSIVE (restriction and extra Duty Officer) arrives in Step 5."""

from engine.cards import operation
from engine.ops import A


@operation("2PER01", 0, uses=[A.DRAW, A.ENLIST_DEVELOPMENT], requires=lambda ctx: ctx.track("military") >= 3)
def defect(ctx, actions):
    """PLAY: Requires [Military] 3. Your opponent may draw a card. Enlist a Development."""
    opp = ctx.opponent
    if opp is not None and (yield from actions.may("Admiral Jarok: do you want to draw a card?", seat=opp.seat)):
        yield from actions.draw(1, player=opp)
    yield from actions.enlist_development()


@operation("2PER01", 1, uses=[A.GAIN_RESOURCE, A.LOG],
           trigger=lambda ctx, ev: ev["kind"] == "attacked" and ev["seat"] == ctx.me.seat)
def counsel(ctx, actions):
    """REACTION: After you are attacked, gain 1 [Glory]. Then, you may log a card from your hand or Discard pile."""
    yield from actions.gain_resource("glory", 1)
    card = yield from actions.pick_card("Log a card from your hand or Discard pile?", ctx.me.hand + ctx.me.discard,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)
