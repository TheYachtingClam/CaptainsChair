"""1BUR15 Book's Ship (Ship). Spec: resources/scans/base_game/cards/captains/burnham/1BUR15.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, EffectCost

from ._util import beamed_here, warp_this_ship


@operation("1BUR15", 0, uses=[A.DEPLOY, A.SEND_AWAY_TEAM])
def slip_in(ctx, actions):
    """PLAY: Deploy this ship. You may send an [Away Team] to a Location, ignoring any opponent Ship."""
    yield from actions.deploy(ctx.this_card)
    if actions.away_targets(ignore_ships=True) and (
            yield from actions.may("Send an Away Team to a Location, ignoring any opponent Ship?")):
        yield from actions.send_away_team(1, ignore_ships=True)


operation("1BUR15", 1, uses=[A.DISCARD, A.WARP], cost=[DiscardFromHand(1)])(warp_this_ship)


@operation("1BUR15", 2, uses=[A.DISCARD, A.RECALL], cost=[DiscardFromHand(1)], requires=lambda ctx: bool(beamed_here(ctx)))
def unload(ctx, actions):
    """ACTIVATION: Discard a card to recall a card beamed here."""
    card = yield from actions.pick_card("Recall which card?", beamed_here(ctx))
    if card:
        yield from actions.recall(card)


def _dismiss_beamed(ctx, actions):
    card = yield from actions.pick_card("Dismiss which card beamed to Book's Ship (cost)?", beamed_here(ctx))
    yield from actions.dismiss(card)


@operation("1BUR15", 3, uses=[A.DISMISS],
           cost=[EffectCost(lambda ctx: bool(beamed_here(ctx)), _dismiss_beamed, (A.DISMISS,),
                            "dismiss a card beamed here")],
           trigger=lambda ctx, ev: ev["kind"] == "would_dismiss_duty_officer" and ev["seat"] == ctx.me.seat)
def morph(ctx, actions):
    """REACTION: When an attack would dismiss your Duty Officer, dismiss a card beamed here to ignore the effect."""
    actions.emit("Book's Ship: the Duty Officer is not dismissed.")
    return True
    yield  # pragma: no cover
