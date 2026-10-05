"""0SHI02 U.S.S. Cabot (Ship, promo). Spec: resources/scans/promo2/cards/ships/0SHI02.md
Tribbles is not in these sets."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, count_traits, has_trait, warp_this_ship


@operation("0SHI02", 0, uses=[A.DEPLOY, A.TAKE_INCIDENT, A.SCAN_FOR])
def survey(ctx, actions):
    """PLAY: Deploy this ship. You may take an Incident to scan for Creature."""
    yield from actions.deploy(ctx.this_card)
    if ctx.state.incident and (yield from actions.may("Take an Incident to scan for a Creature?")):
        yield from actions.take_incident()
        yield from actions.scan_for(lambda i: has_trait(i, "Creature"), "a Creature")


@operation("0SHI02", 1, uses=[A.DRAW, A.GAIN_RESOURCE, A.LOG])
def xenobiology(ctx, actions):
    """RESUPPLY: Draw a card for each Creature in play. If you drew 3 or more, gain 1 [Glory] and log this card.
    Ruling: only your own Creatures count, beamed ones included."""
    n = count_traits(ctx, "Creature")
    drawn = (yield from actions.draw(n)) if n else 0
    if drawn >= 3:
        yield from actions.gain_resource("glory", 1)
        yield from actions.log(ctx.this_card)


operation("0SHI02", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("0SHI02", 3, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("0SHI02", 4, uses=[A.FREE_PLAY, A.DRAW_FROM_DISCARD],
           trigger=lambda ctx, ev: ev["kind"] == "exhaust" and ev["uid"] == ctx.ref.uid)
def tribble_trouble(ctx, actions):
    """PASSIVE: After exhausting this card either: free play Tribbles OR draw Tribbles from your Discard pile.
    Tribbles is not in these sets, so this usually does nothing."""
    playable = actions.free_play_candidates(lambda i: ctx.name(i) == "Tribbles")
    in_discard = [i for i in ctx.me.discard if ctx.name(i) == "Tribbles"]
    options = ([("play", "Free play Tribbles")] if playable else []) + ([("draw", "Take Tribbles from your Discard pile")]
                                                                       if in_discard else [])
    if not options:
        return
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("U.S.S. Cabot: choose one.", options))
    if choice == "play":
        yield from actions.free_play(playable[0])
    else:
        yield from actions.draw_from_discard(lambda i: ctx.name(i) == "Tribbles", "Tribbles")
