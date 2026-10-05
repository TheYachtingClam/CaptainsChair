"""Helpers shared by the bonus modules. Registers nothing."""

from engine.ops import card

SKILLS = ("research", "influence", "military")
ICON_SKILLS = {"Research", "Influence", "Military", "Any"}  # [Any Skill] counts as each of them


def is_suit(inst, *suits) -> bool:
    from engine.ops import suits_of

    return bool(suits_of(inst) & set(suits))


def gain_track_choice(ctx, actions, n: int, tracks=SKILLS):
    """Gain n on one Specialty track of the human's choice ("gain 2 [Research]/[Influence]/[Military]")."""
    track = yield from actions.choose(f"Gain {n} on which Specialty track?", [(t, t.capitalize()) for t in tracks])
    yield from actions.gain_specialty(track, n)


def find_and_promote_person(ctx, actions):
    """Find a Person, except in your Reserve deck, and promote them to Duty Officer."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person", exclude_reserve=True)
    if found is not None:
        yield from actions.promote(found)
