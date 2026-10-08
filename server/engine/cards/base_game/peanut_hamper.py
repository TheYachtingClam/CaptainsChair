"""1PER17 Peanut Hamper (Person). Spec: resources/scans/base_game/cards/person/1PER17.md"""

from engine.cards import operation
from engine.ops import A, Spend


@operation("1PER17", 0, uses=[A.SCAN], cost=[Spend(dilithium=2)])
def replicate(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to scan 1 of Cargo."""
    yield from actions.scan(1, ["Cargo"])


@operation("1PER17", 1, uses=[A.GAIN_RESOURCE, A.RECALL, A.PROMOTE])
def reassign(ctx, actions):
    """PLAY: Gain 3 [Dilithium]. You may recall your Duty Officer. Promote this card to Duty Officer."""
    yield from actions.gain_resource("dilithium", 3)
    officer = yield from actions.pick_card("Recall a Duty Officer?", list(ctx.me.duty), optional=True, none_label="No")
    if officer:
        yield from actions.recall(officer)
    yield from actions.promote(ctx.this_card)


@operation("1PER17", 2, uses=[A.GAIN_RESOURCE])
def exocomp(ctx, actions):
    """RESUPPLY: Gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)


@operation("1PER17", 3, uses=[A.PUT], trigger=lambda ctx, ev: ev["kind"] == "attacked" and ev["seat"] == ctx.me.seat)
def flee(ctx, actions):
    """PASSIVE: After you are attacked, put this card on the top of your deck."""
    yield from actions.put_on_deck(ctx.this_card)


@operation("1PER17", 4, uses=[A.PUT, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.has(ctx.event_card, "Shady"))
def defect(ctx, actions):
    """REACTION: After putting a Shady into play, put this card on the top of your deck and gain 1 [Latinum]."""
    yield from actions.put_on_deck(ctx.this_card)
    yield from actions.gain_resource("latinum", 1)
