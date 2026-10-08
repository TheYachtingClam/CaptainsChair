"""The Khan Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/khan.md

The Khan Bot starts on its KHAN IN EXILE card (`player.bot.exile`), whose rows name traits and suits alike, and moves
to the regular TRAITS and SUITS cards when that card says so (REQ-CD-KHN-11). "Unmarked" in a row is a card or
Location with a trait not yet marked on the Bot's Crew board."""

from engine.bot import (END_OF_TURN, FOCUS_VP, MARK_VP, ON_SUPPLEMENT, SETUP_REMOVES, SUPPLEMENT_BOTTOM, VALUE_BONUS,
                        mark_trait, row, unmarked)
from engine.bot.actions import card_matches
from engine.ops import A, card

CREW = "khan"
REVENGE = "2KHA10"  # Revenge Is a Dish Best Served Cold, named by the Attack row
EXILE_ENDS_AT = 5  # Dilithium

# Solo setup (REQ-CD-KHN-11): no Ceti Alpha V or VI; Genesis Device at the bottom of the Supplement deck.
SETUP_REMOVES[CREW] = ("2KHA02A", "2KHA03")
SUPPLEMENT_BOTTOM[CREW] = ("2KHA11",)
# Special rule: 3 VP for each marked trait; a card with an unmarked trait is worth 3 more; each Focus icon scores, and
# is valued at, 3.
MARK_VP[CREW] = 3
FOCUS_VP[CREW] = 3
VALUE_BONUS[CREW] = lambda state, bot, inst: 3 if unmarked(state, bot, inst) else 0


def _exile_supplement(state, bot):
    """KHAN IN EXILE: Whenever a card is drawn or discarded from the Supplement deck, the bot gains 1 [Dilithium]."""
    if bot.bot.exile:
        bot.dilithium += 1
        state.emit(f"{bot.name} gains 1 Dilithium (Khan in Exile: a card left the Supplement deck).", seat=bot.seat)


def _exile_end_of_turn(state, bot):
    """KHAN IN EXILE: At the end of its turn, the bot gains 1 [Dilithium]. Then, if it has 5+ [Dilithium], it spends
    them all, gains the top Encounter, and replaces this card with the regular Automated Command cards."""
    if not bot.bot.exile:
        return
    bot.dilithium += 1
    state.emit(f"{bot.name} gains 1 Dilithium (Khan in Exile): it has {bot.dilithium}.", seat=bot.seat)
    if bot.dilithium < EXILE_ENDS_AT:
        return
    state.emit(f"{bot.name} spends all {bot.dilithium} Dilithium.", seat=bot.seat)
    bot.dilithium = 0
    if state.encounter:
        encounter = state.encounter.pop(0)
        bot.discard.append(encounter)
        state.emit(f"{bot.name} gains the Encounter {card(encounter).name} to its Discard pile.", seat=bot.seat,
                   irreversible=True, card=encounter.card)
        mark_trait(state, bot, encounter)
    bot.bot.exile = False
    bot.bot.suits_side = "with_duty_officer" if bot.duty else "no_duty_officer"
    state.emit(f"{bot.name} leaves exile: it replaces KHAN IN EXILE with its regular TRAITS and SUITS cards.",
               seat=bot.seat)


ON_SUPPLEMENT[CREW] = _exile_supplement
END_OF_TURN[CREW] = _exile_end_of_turn


def _discard_top_for_glory(ctx, actions):
    """Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your Captain, gain 1
    [Glory]. "Your Captain" is the human's."""
    discarded = yield from actions.discard_top(1)
    human = ctx.opponent
    traits = [t for t in card(human.captain).traits if t != "Human"] if human is not None else []
    if any(card_matches(inst, t) for inst in discarded for t in traits):
        yield from actions.gain_glory(1)


# ------------------------------------------------------------------ KHAN IN EXILE

@row(CREW, "exile_traits", 2, uses=[A.SEND_AWAY_TEAM, A.TAKE_INCIDENT, A.GAIN_CARD])
def exile_augment(ctx, actions):
    """Augment: Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location. Take an Incident to gain a
    Person."""
    yield from actions.send_away_team(prefer="unmarked > Augment / Scientist > Location")
    yield from actions.take_incident()
    yield from actions.gain_card("Person")


@row(CREW, "exile_traits", 3, uses=[A.DISCARD, A.GAIN_RESOURCE, A.RETURN_INCIDENT])
def exile_incident(ctx, actions):
    """Incident: Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your
    Captain, gain 1 [Glory]. Return this card."""
    yield from _discard_top_for_glory(ctx, actions)
    yield from actions.return_incident()


@row(CREW, "exile_traits", 4, uses=[A.JUNK, A.SEND_AWAY_TEAM])
def exile_ship(ctx, actions):
    """Ship: Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral
    unmarked > Location."""
    yield from actions.junk()
    yield from actions.send_away_team(prefer="unmarked > Location")


@row(CREW, "exile_traits", 5, uses=[A.JUNK, A.GAIN_CARD])
def exile_directive(ctx, actions):
    """Directive: Junk the most valuable card in the Market (ignoring any with tokens). Gain an unmarked > Person /
    Cargo / Ship / Ally from the Junk."""
    yield from actions.junk()
    yield from actions.gain_card("unmarked > Person / Cargo / Ship / Ally", from_junk=True)


@row(CREW, "exile_traits", 6, uses=[A.DISCARD, A.TAKE_INCIDENT, A.SPEND, A.GAIN_RESOURCE])
def exile_other(ctx, actions):
    """Person / Cargo / Ally / Location: Discard the top card of the Bot deck. If this card is a Location taken during
    the Control Step, gain an Incident, and spend 1 [Dilithium], if able. If this card is a Person, gain 1 [Glory]
    from the supply."""
    yield from actions.discard_top(1)
    if actions.is_("Location") and actions.controlled:
        yield from actions.gain_incident()
        yield from actions.spend(1)
    if actions.is_("Person"):
        yield from actions.gain_glory(1, supply=True)


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.ATTACK, A.DISMISS, A.GAIN_RESOURCE, A.CONTINUE_RESOLUTION])
def mind_control(ctx, actions):
    """Mind Control: You dismiss a Duty Officer, if able, otherwise gain 2 [Glory]. Continue resolution."""
    dismissed = False
    if (yield from actions.attack()):
        dismissed = yield from actions.human_dismisses_duty_officer()
    if not dismissed:
        yield from actions.gain_glory(2)
    yield from actions.continue_resolution()


@row(CREW, "traits", 3, uses=[A.SEND_AWAY_TEAM, A.TAKE_INCIDENT, A.GAIN_CARD, A.DISCARD])
def augment_ops(ctx, actions):
    """Augment / Ops: Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location. If this card is a
    Person, take an Incident and take a Person; otherwise discard the top card of the Supplement deck."""
    yield from actions.send_away_team(prefer="unmarked > Augment / Scientist > Location")
    if actions.is_("Person"):
        yield from actions.take_incident()
        yield from actions.gain_card("Person", take=True)
    else:
        yield from actions.discard_supplement_top()


@row(CREW, "traits", 4, uses=[A.RETURN_INCIDENT, A.SEND_AWAY_TEAM, A.LOG])
def creature_scientist(ctx, actions):
    """Creature / Scientist: Return an Incident from Bot Discard pile, if able. Send 2 [Away Team] to a neutral
    Location, ignoring any opponent Ship. Log this card."""
    yield from actions.return_incident_from_discard()
    loc = yield from actions.send_away_team(ignore_ships=True)
    if loc is not None:
        yield from actions.send_away_team(target=loc, ignore_ships=True)
    yield from actions.log()


@row(CREW, "traits", 5, uses=[A.MARK_TRAIT, A.ATTACK, A.TAKE_INCIDENT, A.FIND, A.LOG])
def attack(ctx, actions):
    """Attack: Mark a trait. You take an Incident from Bot Discard pile, if able. Otherwise, you find any card, and
    log the found card. If this card is Revenge is a dish best served cold, you log this card; otherwise the bot logs
    this card."""
    yield from actions.mark_trait()
    revenge = actions.this.card == REVENGE
    if (yield from actions.attack()):
        if not (yield from actions.human_takes_incident_from_discard()):
            yield from actions.human_finds_and_logs()
        if revenge:
            yield from actions.human_logs()
    if not revenge:
        yield from actions.log()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.DISCARD, A.GAIN_RESOURCE, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your
    Captain, gain 1 [Glory]. Return this card."""
    yield from _discard_top_for_glory(ctx, actions)
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE])
def ship(ctx, actions):
    """Ship: Deploy this ship; it engages."""
    yield from actions.deploy()
    yield from actions.engage()


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally(ctx, actions):
    """Ally: Take a Spy / Cloak / Synthetic if able; otherwise gain a Person / Ship. Log this card."""
    if (yield from actions.gain_card("Spy / Cloak / Synthetic", take=True)) is None:
        yield from actions.gain_card("Person / Ship")
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_CARD])
def cargo(ctx, actions):
    """Cargo: Gain a Person from the top of the deck."""
    yield from actions.gain_top_of_deck("Person")


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_RESOURCE, A.TAKE_INCIDENT, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain 1 [Glory]. Gain an Incident. Promote this card to Duty Officer."""
    yield from actions.gain_glory(1)
    yield from actions.gain_incident()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.JUNK, A.GAIN_CARD])
def directive(ctx, actions):
    """Directive: Junk the most valuable card in the Market (ignoring any with tokens). Gain an Ally > Ship from the
    Junk."""
    yield from actions.junk()
    yield from actions.gain_card("Ally > Ship", from_junk=True)


@row(CREW, "no_duty_officer", 7, uses=[A.RESOLVE_CARD])
def encounter(ctx, actions):
    """Encounter: Resolve the top card of the Supplement deck."""
    yield from actions.resolve_supplement_top()


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.GAIN_CARD])
def location(ctx, actions):
    """Location: Discard the top 2 cards of the Bot deck. Gain a Ship."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Ship")


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.DISCARD, A.GAIN_RESOURCE, A.ATTACK, A.GIVE])
def incident_officer(ctx, actions):
    """Incident: Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your
    Captain, gain 1 [Glory]. You take this card."""
    yield from _discard_top_for_glory(ctx, actions)
    if (yield from actions.attack()):
        yield from actions.human_takes()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Deploy this ship; it engages. Send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain a Cargo > Ally > Person. Log Duty Officer. Log this card."""
    yield from actions.gain_card("Cargo > Ally > Person")
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.GAIN_CARD, A.LOG])
def cargo_officer(ctx, actions):
    """Cargo: Gain a Ally > Person / Ship. Log Duty Officer."""
    yield from actions.gain_card("Ally > Person / Ship")
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.PUT, A.DISMISS])
def person_officer(ctx, actions):
    """Person: Put an Augment from Bot Discard pile on top of the Bot deck, if able. Dismiss Duty Officer."""
    augment = actions.topmost_in_discard("Augment")
    if augment is not None:
        yield from actions.put_on_top(augment)
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 6, uses=[A.JUNK, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: Junk the most valuable card in the Market (ignoring any with tokens). Gain a Person / Cargo / Ally,
    including from the Junk."""
    yield from actions.junk()
    yield from actions.gain_card("Person / Cargo / Ally", including_junk=True)


@row(CREW, "with_duty_officer", 7, uses=[A.TAKE_ENCOUNTER, A.DESTROY, A.LOG, A.RESOLVE_CARD])
def encounter_officer(ctx, actions):
    """Encounter: If 8 or more traits are marked, gain the highest value card of the top 3 Encounter and destroy the
    other two, then log the gained card and this card. Otherwise, resolve the top card of the Supplement deck."""
    if actions.traits_marked >= 8:
        gained = yield from actions.gain_best_encounter(3)
        if gained is not None:
            yield from actions.log(gained)
        yield from actions.log()
    else:
        yield from actions.resolve_supplement_top()


@row(CREW, "with_duty_officer", 8, uses=[A.DISCARD, A.LOG])
def location_officer(ctx, actions):
    """Location: Discard the top card of the Supplement deck. Log Duty Officer."""
    yield from actions.discard_supplement_top()
    yield from actions.log_duty_officer()
