"""2CAR02 Borg Spatial Trajector (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, ships


@operation("2CAR02", 0, uses=[A.BEAM, A.PUT, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("research") >= 4)
def transport(ctx, actions):
    """PLAY: Requires [Research] 4. Select up to 3 Person from your hand or Discard pile. For each either: beam it to
    a Ship OR put it on the top of your deck to send an [Away Team] to a Location."""
    for n in (1, 2, 3):
        people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person")]
        person = yield from actions.pick_card(f"Select a Person ({n} of up to 3) from your hand or Discard pile.",
                                              people, optional=True, none_label="Stop")
        if not person:
            break
        options = ([("beam", "Beam it to a Ship")] if ships(ctx) else []) + \
            [("top", "Put it on top of your deck to send an Away Team")]
        choice = yield from actions.choose(f"{ctx.name(person)}: beam it, or top-deck it to send an Away Team?", options)
        if choice == "beam":
            ship = yield from actions.pick_card("Beam it to which Ship?", ships(ctx))
            yield from actions.beam(person, ship)
        else:
            yield from actions.put_on_deck(person)
            yield from actions.send_away_team(1)


@operation("2CAR02", 1, uses=[], requires=lambda ctx: False)
def regenerate(ctx, actions):
    """PLAY: Requires [Borg] 6. Regenerate 1 [Drone] and you may send a [Drone] to any Location.
    Ruling: Borg Collective rules are not in these boxes (KW-DRONE-01), so this can never be played."""
    return
    yield  # pragma: no cover
