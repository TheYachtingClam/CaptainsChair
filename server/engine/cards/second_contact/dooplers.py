"""3FRE20 Dooplers (Ally). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE20.md"""

from engine.cards import operation
from engine.ops import A


@operation("3FRE20", 0, uses=[A.TAKE_INCIDENT, A.GAIN_CARD, A.GAIN_SPECIALTY, A.SPEND, A.SHUFFLE_INTO])
def multiply(ctx, actions):
    """PLAY: Take an Incident to your Discard pile. Gain an Ally. Gain 1 [Influence]. Then either: spend 1 [Latinum]
    OR shuffle this card into your deck."""
    yield from actions.take_incident(to="discard")
    yield from actions.gain_card(["Ally"], label="an Ally")
    yield from actions.gain_specialty("influence", 1)
    options = ([("spend", "Spend 1 Latinum")] if actions.can_spend(latinum=1) else []) + \
        [("shuffle", "Shuffle Dooplers into your deck")]
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Then?", options))
    if choice == "spend":
        yield from actions.spend(latinum=1)
    elif ctx.this_card in ctx.me.staging:
        yield from actions.shuffle_into(ctx.this_card)
