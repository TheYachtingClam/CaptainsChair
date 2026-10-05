"""3FRE05 T'Lyn (Person, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait

development_cost("3FRE05", Spend(dilithium=2))


@operation("3FRE05", 0, uses=[A.GAIN_RESOURCE, A.DRAW_FROM_DISCARD, A.FREE_PLAY, A.PROMOTE],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("by") == ctx.me.seat)
def logical(ctx, actions):
    """SUPPORT: After logging a card, either gain 2 [Dilithium] OR draw a card from your Discard pile. Then, you may
    either free play a Lower Decker OR promote a Lower Decker to Duty Officer from your hand or the Staging Area (can be
    this card)."""
    options = [("dilithium", "Gain 2 Dilithium")] + ([("discard", "Draw a card from your Discard pile")]
                                                     if ctx.me.discard else [])
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("T'Lyn: choose one.", options))
    if choice == "dilithium":
        yield from actions.gain_resource("dilithium", 2)
    else:
        yield from actions.draw_from_discard()
    plays = actions.free_play_candidates(lambda i: has_trait(i, "Lower Decker"))
    people = [i for i in ctx.me.hand + ctx.me.staging if has_trait(i, "Lower Decker") and ctx.card(i).suit == "Person"]
    options = ([("play", "Free play a Lower Decker")] if plays else []) + \
        ([("promote", "Promote a Lower Decker")] if people else [])
    if not options:
        return
    choice = yield from actions.choose("Then?", options + [("none", "Neither")])
    if choice == "play":
        card = yield from actions.pick_card("Free play which Lower Decker?", plays)
        yield from actions.free_play(card)
    elif choice == "promote":
        card = yield from actions.pick_card("Promote which Lower Decker?", people)
        yield from actions.promote(card)


@operation("3FRE05", 1, uses=[A.GAIN_SPECIALTY, A.SPEND, A.FREE_PLAY],
           trigger=lambda ctx, ev: ev["kind"] == "gain" and ev["seat"] == ctx.me.seat and ctx.state.step != "resupply")
def science_officer(ctx, actions):
    """REACTION: After gaining a card, except during your Resupply Step, gain 1 [Research] and you may spend 1
    [Dilithium] to free play the gained card."""
    yield from actions.gain_specialty("research", 1)
    gained = ctx.event_card
    if gained is None or not actions.can_spend(dilithium=1):
        return
    if gained in actions.free_play_candidates(lambda i: i.uid == gained.uid, ("hand", "discard", "draw")) and (
            yield from actions.may(f"Spend 1 Dilithium to free play {ctx.name(gained)}?")):
        yield from actions.spend(dilithium=1)
        yield from actions.free_play(gained)
