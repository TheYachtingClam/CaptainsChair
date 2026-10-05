"""The Rebner Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/rebner.md

Special rule: Research and Influence multipliers are always 0 for the Rebner Bot (REQ-CD-REB-02). His board data
already has no multipliers on those tracks, so the Bot's scoring and value function need nothing more."""

from engine.bot import row
from engine.ops import A, card

CREW = "rebner"
ANY_MARKET_CARD = "Person / Cargo / Ship / Ally"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.TAKE_ENCOUNTER, A.LOG, A.GAIN_CARD, A.DISCARD])
def helmet(ctx, actions):
    """Helmet: If this card is Big Enough Helmet, take top Encounter and log this card. Otherwise, gain the most
    valuable card in the Market and discard the top 2 cards of the Bot deck."""
    if actions.this.card == "2REB03":
        yield from actions.take_encounter()
        yield from actions.log()
    else:
        yield from actions.gain_card(ANY_MARKET_CARD, label="Market card")
        yield from actions.discard_top(2)


@row(CREW, "traits", 3, uses=[A.LOG, A.ATTACK, A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def weapon(ctx, actions):
    """Weapon: If Bot has 6+ [Military], log this card and you take an Incident. Otherwise, gain 1 [Military] and send
    an [Away Team] to a neutral Location."""
    if actions.track("military") >= 6:
        yield from actions.log()
        if (yield from actions.attack()):
            yield from actions.human_takes_incident()
    else:
        yield from actions.gain_specialty("military", 1)
        yield from actions.send_away_team()


@row(CREW, "traits", 4, uses=[A.LOG, A.ATTACK, A.DISCARD, A.DEPLOY, A.ENGAGE, A.PROMOTE])
def attack(ctx, actions):
    """Attack: If able to do both, log a Weapon from Bot Discard pile, and you log a Ship either from your hand,
    Discard pile, or in play. Otherwise, you discard a card. If this card is a Ship, deploy it; it engages. If this
    card is a Person, promote it to Duty Officer."""
    if actions.in_discard("Weapon") and actions.human_ships():
        yield from actions.log_from_discard(lambda i: "Weapon" in card(i).traits)
        if (yield from actions.attack()):
            yield from actions.human_logs_ship()
    elif (yield from actions.attack()):
        yield from actions.human_discards()
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.engage()
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 5, uses=[A.JUNK, A.DISCARD, A.GAIN_SPECIALTY, A.PROMOTE])
def engineer(ctx, actions):
    """Engineer: Junk the most valuable card in the Market (ignoring any with tokens). Discard the top card of the
    Supplement deck. Gain 1 [Military]. If this card is a Person, promote it to Duty Officer."""
    yield from actions.junk()
    yield from actions.discard_supplement_top()
    yield from actions.gain_specialty("military", 1)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 6, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE, A.LOG, A.GAIN_RESOURCE, A.GAIN_CARD])
def scientist_communication(ctx, actions):
    """Scientist / Communication: Gain 1 [Military]. If this card is a Ship, deploy this Ship; it explores. Otherwise,
    log the top card of the Bot deck, gain 1 [Glory], and if able, gain a [Military Focus] > Cargo, including from the
    Junk."""
    yield from actions.gain_specialty("military", 1)
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.explore()
    else:
        yield from actions.log_top(1)
        yield from actions.gain_glory(1)
        yield from actions.gain_card("[Military Focus] > Cargo", including_junk=True)


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.JUNK, A.GAIN_CARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Junk the most valuable card in the Market (ignoring any with tokens). If able, gain a [Military
    Focus]. Otherwise, gain 2 [Military]. Return this card."""
    yield from actions.junk()
    if (yield from actions.gain_card("[Military Focus]")) is None:
        yield from actions.gain_specialty("military", 2)
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.GAIN_CARD, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If a Helmet is in Bot Discard pile: If able, gain a Helmet / Cargo /
    [Military Focus] from the Junk. Otherwise, send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.explore()
    gained = None
    if actions.in_discard("Helmet"):
        gained = yield from actions.gain_card("Helmet / Cargo / [Military Focus]", from_junk=True)
    if gained is None:
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD, A.ATTACK, A.TAKE_INCIDENT, A.LOG])
def ally(ctx, actions):
    """Ally: Discard the top card of the Supplement deck. Gain 2 [Military]. If able, gain a [Military Focus] from the
    Junk. You take an Incident. Log this card."""
    yield from actions.discard_supplement_top()
    yield from actions.gain_specialty("military", 2)
    yield from actions.gain_card("[Military Focus]", from_junk=True)
    if (yield from actions.attack()):
        yield from actions.human_takes_incident()
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.TAKE_INCIDENT, A.GAIN_CARD, A.DISCARD])
def cargo(ctx, actions):
    """Cargo: If a Helmet is in Bot Discard pile, take an Incident and gain a Ship / Ally. Otherwise, discard the top 2
    cards of the Bot deck, then if able, gain a [Military Focus] > Person > Cargo from the Junk."""
    if actions.in_discard("Helmet"):
        yield from actions.take_incident()
        yield from actions.gain_card("Ship / Ally")
    else:
        yield from actions.discard_top(2)
        yield from actions.gain_card("[Military Focus] > Person > Cargo", from_junk=True)


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_CARD, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain a Weapon > Ship. Promote this card to Duty Officer."""
    yield from actions.gain_card("Weapon > Ship")
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.JUNK, A.DISCARD, A.PROMOTE, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 3 cards of the
    Bot deck. If able, promote a Person from Bot Discard pile to Duty Officer. Otherwise, send an [Away Team] to a
    neutral Location."""
    yield from actions.junk()
    yield from actions.discard_top(3)
    if (yield from actions.promote_from_discard()) is None:
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_RESOURCE, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the top 2 cards of the Bot deck. Gain a [Military Focus] > Attack > Weapon > Ship. Gain 1
    [Glory]. Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("[Military Focus] > Attack > Weapon > Ship")
    yield from actions.gain_glory(1)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.GAIN_CARD])
def location(ctx, actions):
    """Location: If able, gain an Engineer / Communication / Scientist. Otherwise, gain a Weapon / Attack > Person from
    the Junk."""
    if (yield from actions.gain_card("Engineer / Communication / Scientist")) is None:
        yield from actions.gain_card("Weapon / Attack > Person", from_junk=True)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Gain 1 [Military]. Send an [Away Team] to a neutral Location. Return this card."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.send_away_team()
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM, A.DISCARD])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it engages. If a Helmet is in Bot Discard pile, send an [Away Team] to a neutral
    Location. Otherwise, discard the top 2 cards of the Bot deck."""
    yield from actions.deploy()
    yield from actions.engage()
    if actions.in_discard("Helmet"):
        yield from actions.send_away_team()
    else:
        yield from actions.discard_top(2)


@row(CREW, "with_duty_officer", 3, uses=[A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Take an Incident. Gain 1 [Military]. If able, gain a [Military Focus]. Otherwise, gain a Cargo and log
    Duty Officer. Log this card."""
    yield from actions.take_incident()
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.gain_card("[Military Focus]")) is None:
        yield from actions.gain_card("Cargo")
        yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.ATTACK, A.REMOVE_AWAY_TEAM,
                                        A.SEND_AWAY_TEAM, A.DISMISS])
def cargo_officer(ctx, actions):
    """Cargo: Gain a [Military Focus] > Person. Gain 1 [Military] and you remove an [Away Team] from a neutral Location
    where the Bot has 1+ token. Send an [Away Team] to a neutral Location. Dismiss Duty Officer."""
    from engine.game import tokens_at

    yield from actions.gain_card("[Military Focus] > Person")
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.attack(removes_away_teams=True)):
        yield from actions.human_removes_away_team(
            lambda loc: loc in ctx.state.neutral and tokens_at(ctx.state, loc, ctx.me.seat) >= 1)
    yield from actions.send_away_team()
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.PEEK, A.DISCARD, A.SEND_AWAY_TEAM, A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD])
def person_officer(ctx, actions):
    """Person: If the top card of the Bot deck is a Helmet, discard it and send an [Away Team] to a neutral Location.
    Otherwise, log it, gain 1 [Military], and gain an Communication > Scientist > Ally / Ship, including from the
    Junk."""
    top = yield from actions.peek_top()
    if top is not None and "Helmet" in card(top).traits:
        yield from actions.discard_top(1)
        yield from actions.send_away_team()
    else:
        if top is not None:
            yield from actions.log_top(1)
        yield from actions.gain_specialty("military", 1)
        yield from actions.gain_card("Communication > Scientist > Ally / Ship", including_junk=True)


@row(CREW, "with_duty_officer", 6, uses=[A.JUNK, A.DISCARD, A.GAIN_CARD, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def directive_officer(ctx, actions):
    """Directive: Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 2 cards of the
    Bot deck. If a Helmet is in Bot Discard pile, gain a Cargo / Ship. Otherwise, send an [Away Team] to a neutral
    Location and gain 1 [Military]."""
    yield from actions.junk()
    yield from actions.discard_top(2)
    if actions.in_discard("Helmet"):
        yield from actions.gain_card("Cargo / Ship")
    else:
        yield from actions.send_away_team()
        yield from actions.gain_specialty("military", 1)


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_RESOURCE, A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Glory]. Gain an Engineer / Communication / Scientist > Person, including from the Junk. Log
    this card."""
    yield from actions.gain_glory(1)
    yield from actions.gain_card("Engineer / Communication / Scientist > Person", including_junk=True)
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.DISMISS, A.RESOLVE_CARD])
def location_officer(ctx, actions):
    """Location: If a Helmet is in Bot Discard pile, gain 1 [Military] and discard the top card of the Supplement deck.
    Otherwise, dismiss Duty Officer, then resolve the top card of the Bot deck."""
    if actions.in_discard("Helmet"):
        yield from actions.gain_specialty("military", 1)
        yield from actions.discard_supplement_top()
    else:
        yield from actions.dismiss_duty_officer()
        yield from actions.resolve_top()
