"""2REB10 Ambassador Grubdin (Person). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB10.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_helmet, wearing


@operation("2REB10", 0, uses=[A.SEND_AWAY_TEAM, A.DISCARD])
def envoy(ctx, actions):
    """PLAY: Send an [Away Team] to a Location. You may discard a Business/Shady to send an (additional) [Away Team]
    to a Location."""
    yield from actions.send_away_team(1)
    if (yield from actions.discard(1, pred=lambda i: has_trait(i, "Business", "Shady"),
                                   label="a Business or Shady to send another Away Team", optional=True)):
        yield from actions.send_away_team(1)


@operation("2REB10", 1, uses=[A.SPEND, A.GAIN_SPECIALTY, A.GAIN_RESOURCE])
def negotiate(ctx, actions):
    """ACTIVATION: You may spend an [Action] to gain 1 [Military] for each Helmet you have in play. If Ambassador
    Grubdin is wearing a Helmet, gain 1 [Latinum] and 1 [Glory]."""
    helmets = ctx.count_in_play(is_helmet)
    if helmets and ctx.me.actions > 0 and (yield from actions.may(f"Spend an Action to gain {helmets} Military?")):
        yield from actions.spend(actions=1)
        yield from actions.gain_specialty("military", helmets)
    if wearing(ctx.this_card):
        yield from actions.gain_resource("latinum", 1)
        yield from actions.gain_resource("glory", 1)
