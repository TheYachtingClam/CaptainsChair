"""Your cards against the Bot, plans/solo-mode.md Step 3 (requirements/22-solo-mode.md §8 and §12), plus the
SURPRISE operations and the Ticking Clock challenge (§6.2, §10)."""

from engine import bot as bot_rules
from engine.content import content
from engine.game import advance, choose
from engine.ops import A, Actions, Ctx
from engine.setup import BotSetup, SeatSetup, new_game
from engine.state import OpRef

CARDS = content().cards


def solo(deck="kirk", bot="soval", seed=11, ticking_clock=False):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], ["second_contact"], True,
                 bot=BotSetup(bot, "admiral", ticking_clock))
    advance(s, flag_irreversible=False)
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def options(s):
    return [o.label for o in s.decision.options]


def answer(s, text):
    option = next(o for o in s.decision.options if text in o.label)
    choose(s, s.decision.seat, option.id, flag_irreversible=False)


def give(s, card_id, zone="hand"):
    inst = s.new_inst(card_id)
    getattr(me(s), zone).append(inst)
    s.decision = None
    advance(s, flag_irreversible=False)
    return inst


def play(s, inst, index=0):
    choose(s, 0, f"play:{inst.uid}:{index}", flag_irreversible=False)


def finish(s, prefer=()):
    """Answer the human's questions until their Action Step, preferring options containing a `prefer` text."""
    while s.decision is not None and not (s.decision.kind == "action" and s.decision.seat == 0):
        opts = options(s)
        pick = next((p for p in prefer for o in opts if p in o), None)
        if s.decision.kind == "trigger" and pick is None:
            pick = "Do not"
        answer(s, pick if pick else opts[0])


def bot_officer(s, card_id="2PER11"):
    bot = the_bot(s)
    officer = s.new_inst(card_id)
    bot.duty.append(officer)
    bot.bot.suits_side = "with_duty_officer"
    return officer


def log_text(s):
    return " | ".join(e.text for e in s.log)


# ------------------------------------------------------------------ choices the Bot makes (REQ-SOLO-111, -112)

def test_stone_of_gol_makes_the_bot_dismiss_its_officer():
    """REQ-SOLO-113: the Bot picks the first option, dismisses its Duty Officer, and flips its SUITS card back."""
    s = solo()
    bot_officer(s)
    gol = give(s, "2ENC07")
    play(s, gol, 0)
    finish(s)
    bot = the_bot(s)
    assert not bot.duty and bot.bot.suits_side == "no_duty_officer"
    assert any(i.card == "2PER11" for i in bot.discard)


def test_the_bot_declines_to_return_incidents():
    """REQ-SOLO-111, -187: T'Pau lets both players return an Incident; the Bot never does."""
    s = solo(deck="soval")
    the_bot(s).discard.append(s.new_inst("2INC02"))
    tpau = give(s, "2SOV06")
    play(s, tpau, 0)
    finish(s, prefer=("No", "Do not"))
    assert any(i.card == "2INC02" for i in the_bot(s).discard)


def test_a_forced_ship_choice_takes_the_most_recently_deployed():
    """REQ-SOLO-166: the Clumpship makes the Bot log a Ship; it picks its most recently deployed one."""
    s = solo(deck="rebner")
    bot = the_bot(s)
    first, second = s.new_inst("2SHI01"), s.new_inst("2SHI03")
    bot.fleet += [first, second]
    me(s).draw.insert(0, s.new_inst("2CAR14"))  # a Weapon to draw and log
    clump = give(s, "2REB11")
    play(s, clump, 0)
    finish(s, prefer=("Phaser", CARDS["2CAR14"].name, "Do not"))
    bot = the_bot(s)
    assert [i.card for i in bot.log] == ["2SHI03"] and [i.card for i in bot.fleet] == ["2SHI01"]


# ------------------------------------------------------------------ helping the Bot (REQ-SOLO-186 to -188)

def test_a_draw_for_the_bot_discards_the_top_of_its_deck():
    s = solo()
    bot = the_bot(s)
    top = bot.draw[0]
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.DRAW])
    list(acts.draw(1, player=bot))
    assert not bot.hand and bot.discard[-1].uid == top.uid


def test_lirpa_dismisses_the_officer_and_the_bot_draw_is_a_discard():
    s = solo(deck="soval")
    bot_officer(s)
    top = the_bot(s).draw[0]
    lirpa = give(s, "2CAR11")
    play(s, lirpa, 0)
    finish(s, prefer=("No",))
    bot = the_bot(s)
    assert not bot.duty and not bot.hand and any(i.uid == top.uid for i in bot.discard)


def test_resources_given_to_the_bot_are_gained_normally():
    s = solo()
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.GAIN_RESOURCE])
    list(acts.gain_resource("dilithium", 2, player=the_bot(s)))
    assert the_bot(s).dilithium == 2


# ------------------------------------------------------------------ attacking the Bot (REQ-SOLO-190 to -195)

def test_steals_always_succeed_from_the_supply():
    s = solo()
    bot = the_bot(s)
    assert bot.glory == 0
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.STEAL])
    glory = me(s).glory
    list(acts.steal("glory", 1))
    assert me(s).glory == glory + 1 and bot.glory == 0


def test_a_forced_discard_lets_you_decide_and_move_the_top_discard():
    s = solo(deck="rebner")
    bot = the_bot(s)
    moved = s.new_inst("2PER07")
    bot.discard.append(moved)
    rumdar = give(s, "2REB09")
    play(s, rumdar, 0)
    while "has no hand" not in s.decision.prompt:
        answer(s, options(s)[0])
    assert any("move Hoshi Sato" in o for o in options(s)) and "It failed" in options(s)
    answer(s, "move Hoshi Sato")
    finish(s, prefer=("No",))
    assert the_bot(s).draw[0].uid == moved.uid


def test_harry_mudd_success_and_failure():
    """REQ-SOLO-193 example 2: success lets the Bot "draw" (discard its top card); failure gives it an Incident."""
    for outcome in ("It succeeded (nothing else happens)", "It failed"):
        s = solo()
        me(s).tracks["influence"] = 3
        top = the_bot(s).draw[0]
        mudd = give(s, "2PER06")
        play(s, mudd, 0)
        while "has no hand" not in s.decision.prompt:
            answer(s, options(s)[0])
        answer(s, outcome)
        finish(s, prefer=("No",))
        bot = the_bot(s)
        if outcome == "It failed":
            assert CARDS[bot.draw[0].card].suit == "Incident"
        else:
            assert any(i.uid == top.uid for i in bot.discard)


def test_recalling_the_bot_officer_dismisses_it():
    s = solo()
    officer = bot_officer(s)
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.RECALL])
    list(acts.recall(officer))
    bot = the_bot(s)
    assert not bot.hand and any(i.uid == officer.uid for i in bot.discard)


def test_ash_tyler_dismisses_the_officer_and_suits_flip_back():
    s = solo(deck="georgiou")
    bot_officer(s)
    me(s).staging += [s.new_inst("2PER10"), s.new_inst("2PER10")]  # Klingons outnumber Starfleet
    tyler = give(s, "2PER03")
    play(s, tyler, 1)
    finish(s, prefer=("No",))
    bot = the_bot(s)
    assert not bot.duty and bot.bot.suits_side == "no_duty_officer"


def test_incidents_given_to_the_bot_go_on_its_deck():
    s = solo()
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.GIVE])
    incident = s.new_inst("2INC02")
    me(s).hand.append(incident)
    list(acts.give_incident(incident))
    assert the_bot(s).draw[0].uid == incident.uid and not the_bot(s).hand


# ------------------------------------------------------------------ SURPRISE operations (REQ-SOLO-87)

def resolve_as_bot(s, card_id):
    bot = the_bot(s)
    inst = s.new_inst(card_id)
    bot.staging.append(inst)
    s.decision = None
    bot_rules.queue_resolution(s, bot, inst)
    advance(s, flag_irreversible=False)
    return inst


def test_dilithium_shockwave_surprise():
    s = solo()
    top = the_bot(s).draw[0]
    dilithium = me(s).dilithium
    shock = resolve_as_bot(s, "2INC01")
    bot = the_bot(s)
    assert "resolves its SURPRISE operation" in log_text(s)
    assert bot.glory == 1 and any(i.uid == top.uid for i in bot.discard)
    assert me(s).dilithium == dilithium + 2 and s.incident[-1].uid == shock.uid


def test_knowledge_of_a_terrible_fate_surprise():
    s = solo()
    bottom = the_bot(s).reserve[-1]
    resolve_as_bot(s, "3PIK17")
    bot = the_bot(s)
    assert bot.glory == 1 and any(i.uid == bottom.uid for i in bot.discard)
    assert not any(i.card == "3PIK17" for i in bot.staging + bot.discard)  # destroyed


def test_time_is_running_out_surprise():
    s = solo(ticking_clock=True)
    bot = the_bot(s)
    supplement_top = bot.reserve[0]
    incidents = len(s.incident)
    hand = len(me(s).hand)
    resolve_as_bot(s, "2DIR01")
    assert s.decision.seat == 0 and "Discard" in s.decision.prompt  # you draw a card, then discard one
    answer(s, options(s)[0])
    bot = the_bot(s)
    assert bot.glory == 2 and bot.draw[0].uid == supplement_top.uid
    assert len(s.incident) == incidents - 1 and CARDS[s.junk[-1].card].suit == "Incident"
    assert len(me(s).hand) == hand


def test_ticking_clock_puts_time_is_running_out_in_the_supplement():
    s = solo(ticking_clock=True)
    assert any(i.card == "2DIR01" for i in the_bot(s).reserve)
    s = solo()
    assert not any(i.card == "2DIR01" for i in the_bot(s).reserve)


def test_random_games_with_every_market_card_against_the_bot():
    """Random play with the whole Market forced into the human's deck, so their cards meet the Bot."""
    import random

    market = [k for k, c in CARDS.items() if c.is_common and c.suit in ("Person", "Cargo", "Ship", "Ally")]
    for seed in range(3):
        rng = random.Random(seed)
        s = solo(deck=rng.choice(["kirk", "georgiou", "pike"]), seed=seed, ticking_clock=seed == 1)
        me(s).draw = [s.new_inst(k) for k in rng.sample(market, 30)] + me(s).draw
        for _ in range(4000):
            if s.step == "over":
                break
            assert s.decision.seat == 0
            ids = [o.id for o in s.decision.options]
            plays = [i for i in ids if i.startswith(("play:", "activate:"))]
            choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids),
                   flag_irreversible=False)
        assert s.step == "over"
