"""1SHI11 U.S.S. Reliant (Ship). Spec: resources/scans/base_game/cards/ships/1SHI11.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import (beam_a_card_here, can_discard_then_beam, deploy_and_warp_this, has_trait, opponent_ships,
                    others_in_hand, virtual, warp_this_ship)

operation("1SHI11", 0, uses=[A.DEPLOY, A.WARP])(deploy_and_warp_this)


def _augment(i):
    return has_trait(i, "Augment")


@operation("1SHI11", 1, uses=[A.DEPLOY, A.SEND_AWAY_TEAM, A.DRAW, A.DISCARD, A.GAIN_RESOURCE],
           requires=lambda ctx: ctx.track("influence") >= 5 and (virtual(ctx) or len(opponent_ships(ctx)) <= 1))
def survey(ctx, actions):
    """PLAY: Requires [Influence] 5. If your opponent has at most 1 Ship deployed, deploy this ship then choose 2 of
    the following: send an [Away Team] to a Location OR draw a card OR discard an Augment to gain 2 [Glory]."""
    yield from actions.deploy(ctx.this_card)
    labels = {"team": "Send an Away Team to a Location", "draw": "Draw a card",
              "augment": "Discard an Augment to gain 2 Glory"}
    for n in (1, 2):
        able = {"team": bool(actions.away_targets()), "draw": True, "augment": bool(others_in_hand(ctx, _augment))}
        choices = [(k, v) for k, v in labels.items() if able[k]]
        if not choices:
            return
        pick = yield from actions.choose(f"Choose option {n} of 2.", choices)
        del labels[pick]
        if pick == "team":
            yield from actions.send_away_team(1)
        elif pick == "draw":
            yield from actions.draw(1)
        else:
            yield from actions.discard(1, pred=_augment, label="an Augment")
            yield from actions.gain_resource("glory", 2)


operation("1SHI11", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SHI11", 3, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
