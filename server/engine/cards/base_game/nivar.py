"""1BUR12 Ni'Var (Location). Spec: resources/scans/base_game/cards/captains/burnham/1BUR12.md"""

from engine.cards import operation, skill_icons
from engine.ops import A

from ._util import ctx_for, has_trait



@operation("1BUR12", 0, uses=[A.TAKE_CONTROL, A.REMOVE_STARDATE_GLORY])
def reunified(ctx, actions):
    """PLAY: Take control of this location. Remove 1 [Glory] from the Stardate card."""
    yield from actions.take_control(ctx.this_card)
    yield from actions.remove_stardate_glory(1)


@operation("1BUR12", 1, uses=[A.FIND, A.SCAN_FOR])
def science_institute(ctx, actions):
    """CONTROL: You may find Inspire OR scan for an Ambassador."""
    choice = yield from actions.choose("Ni'Var:", [("find", "Find Inspire"), ("scan", "Scan for an Ambassador"),
                                                   ("none", "Neither")])
    if choice == "find":
        yield from actions.find(lambda i: ctx.card(i).name == "Inspire", "Inspire")
    elif choice == "scan":
        yield from actions.scan_for(lambda i: has_trait(i, "Ambassador"), "an Ambassador")


@skill_icons("1BUR12")
def many_voices(state, owner, inst):
    """PASSIVE: This card has 1 [Research] for each Vulcan, 1 [Influence] for each Ambassador, and 1 [Military] for
    each Romulan you have in play (including traits on this card)."""
    ctx = ctx_for(state, owner)
    cards = ctx.in_play()
    if not any(i.uid == inst.uid for i in cards):
        cards = [*cards, inst]
    icons = []
    for trait, icon in (("Vulcan", "Research"), ("Ambassador", "Influence"), ("Romulan", "Military")):
        icons += [icon] * sum(1 for i in cards if ctx.has(i, trait))
    return icons
