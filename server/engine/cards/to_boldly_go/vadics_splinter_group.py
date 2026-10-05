"""2ALL15 Vadic's Splinter Group (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL15.md"""

from engine.cards import operation, trait_modifier
from engine.ops import A, card, table_cards

from ._util import is_suit


@operation("2ALL15", 0, uses=[A.DUPLICATE, A.PUT, A.TAKE_INCIDENT])
def infiltrate(ctx, actions):
    """PLAY: You may duplicate a play operation of a Person or Cargo you or your opponent has in play (excluding beamed
    cards). Then either: put a Person into your Staging Area (without triggering their play operation) OR take an
    Incident. Ruling: copying "deploy this card" does nothing, since this is neither Ship nor Ongoing (KW-DUP-04)."""
    players = [ctx.me] + ([ctx.opponent] if ctx.opponent else [])
    candidates = [i for p in players for i in ctx.in_play(p, beamed=False)
                  if is_suit(i, "Person", "Cargo") and i is not ctx.this_card]
    if candidates:
        yield from actions.duplicate(candidates, label="a Person or Cargo in play")
    people = [i for i in ctx.me.hand if is_suit(i, "Person")]
    options = ([("put", "Put a Person from your hand into your Staging Area")] if people else []) + \
        [("incident", "Take an Incident")]
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Then choose one.", options))
    if choice == "put":
        person = yield from actions.pick_card("Put which Person into your Staging Area?", people)
        yield from actions.put_into_staging(person)
    else:
        yield from actions.take_incident()


@trait_modifier("2ALL15", staging=True)
def changeling(state, owner, inst, target):
    """SPECIAL: While this card is in your Staging Area and you have a Borg in play, this card is additionally treated
    as Wildcard. Note: the engine has no Wildcard rules yet (REQ-TR-05), so this has no further effect."""
    if target is not inst:
        return set()
    in_play = [*table_cards(owner), *owner.staging]
    return {"Wildcard"} if any("Borg" in card(i).traits for i in in_play) else set()
