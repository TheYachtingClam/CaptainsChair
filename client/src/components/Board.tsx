import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CardView, GameStateView, OptionView, RowRef } from "../api";
import { BotPlayback, botTurnClosed } from "./BotPlayback";
import { SoloAid } from "./SoloAid";
import {
  Card, CardPreview, CardViewer, Inspect, InspectContext, PlayableContext, Preview, PreviewContext, SelectContext, Selection, TargetContext,
  PlayersContext,
} from "./Cards";
import { CardPanel } from "./CardPanel";
import { Sheet, usePhone } from "./Sheet";
import { PlayerMat } from "./PlayerMat";
import { CenterMat, NeutralZone } from "./CenterMat";

function Confirm({ option, onContinue, onBack, solo }: {
  option: OptionView;
  onContinue: () => void;
  onBack: () => void;
  /** Solo mode: ending your turn starts the Bot's turn (REQ-SOLO-200). */
  solo?: boolean;
}) {
  const back = useRef<HTMLButtonElement>(null);
  useEffect(() => back.current?.focus(), []);
  return (
    <div className="modal-backdrop" onKeyDown={(e) => e.key === "Escape" && onBack()}>
      <div className="card modal" role="alertdialog" aria-labelledby="confirm-title">
        <h2 id="confirm-title">This can't be undone</h2>
        <p>
          {solo && (option.id === "end" || option.id === "done")
            ? "This ends your turn and starts the Bot's turn. Nothing before this point can be undone afterwards."
            : option.reason ?? "This reveals information or ends your turn."}
        </p>
        <div className="row">
          <button ref={back} className="secondary" onClick={onBack}>Go back</button>
          <button onClick={onContinue}>Continue</button>
        </div>
      </div>
    </div>
  );
}

/** The prompt and answer buttons of a decision. */
/** Answers shown together under a title, e.g. the Neutral Zone Locations. */
export interface OptionGroup {
  title: string;
  options: OptionView[];
}

/** A card shown in the decision box, with where it comes from. */
interface DockCard {
  card: CardView;
  option?: string; // the answer this card gives
  source?: "faceup" | "deck" | "junk";
}
const SOURCE_LABEL = { faceup: "Faceup", deck: "From the deck", junk: "From the Junk" } as const;

function DecisionOptions({ prompt, options, busy, canUndo, onPick, onUndo, hint, cards, groupOf }: {
  hint?: string;
  /** Puts an answer in a titled box; answers with no group are listed as usual. */
  groupOf?: (o: OptionView) => string | undefined;
  cards?: DockCard[];
  prompt: string;
  options: OptionView[];
  busy: boolean;
  canUndo: boolean;
  onPick: (o: OptionView) => void;
  onUndo: () => void;
}) {
  const button = (o: OptionView) => (
    <button key={o.id} disabled={busy} className="option" onClick={() => onPick(o)}>
      {o.irreversible && <span aria-label="Cannot be undone" title="Cannot be undone">🔒 </span>}
      {o.label}
    </button>
  );
  // Groups keep the order of their first answer, so they read like the table.
  const groups: OptionGroup[] = [];
  const rest: OptionView[] = [];
  for (const o of options) {
    const title = groupOf?.(o);
    if (!title) {
      rest.push(o);
      continue;
    }
    const g = groups.find((x) => x.title === title);
    if (g) g.options.push(o);
    else groups.push({ title, options: [o] });
  }
  return (
    <div className="stack">
      <p><strong>{prompt}</strong></p>
      {cards && cards.length > 0 && (
        <div className="dock-cards">
          {cards.map(({ card, source }) => (
            <figure key={card.uid} className={`dock-card ${source ? `from-${source}` : ""}`}>
              <Card card={card} />
              {source && <figcaption>{SOURCE_LABEL[source]}</figcaption>}
            </figure>
          ))}
        </div>
      )}
      {hint && <p className="muted">{hint}</p>}
      {groups.map((g) => (
        <fieldset key={g.title} className="option-group">
          <legend>{g.title}</legend>
          <div className="options centered">{g.options.map(button)}</div>
        </fieldset>
      ))}
      {rest.length > 0 && <div className="options">{rest.map(button)}</div>}
      {canUndo && <button className="secondary" disabled={busy} onClick={onUndo}>Undo</button>}
    </div>
  );
}

const SCORE_PART: Record<string, string> = {
  glory: "Glory",
  neutral_tokens: "Tokens in the Neutral Zone",
  endgame: "ENDGAME",
  printed_vp: "Printed VP",
  focus_research: "Research Focus",
  focus_influence: "Influence Focus",
  focus_military: "Military Focus",
  focus_best: "Best Focus",
  missions: "Missions",
  resources: "Dilithium and Latinum (1 per 2)",
  traits: "Marked traits (3 each)",
};

export function Board({ gameId, view, onChoose, onUndo, busy, system }: {
  gameId: string;
  view: GameStateView;
  onChoose: (option: string) => void;
  onUndo: () => void;
  busy: boolean;
  /** Exit game, Report a bug, Suggest a feature, the game's details and its players: on a phone they are on the System
   *  tab, above the log. */
  system?: React.ReactNode;
}) {
  const [pending, setPending] = useState<OptionView | null>(null);
  const [preview, setPreview] = useState<Preview>(null);
  const [inspected, setInspected] = useState<Inspect>(null);
  const [holdHint, setHoldHint] = useState(showHoldHint);
  const [tab, setTab] = useState<Area>(() => (view.you != null ? "you" : "centre"));
  // On a phone the table leaves room at the bottom for the sheet, so nothing is hidden behind it (REQ-CLI-34).
  const phone = usePhone();
  const sheetRef = useRef<HTMLDivElement>(null);
  const [sheetHeight, setSheetHeight] = useState(0);
  useEffect(() => {
    const el = sheetRef.current;
    if (!el || !phone) return;
    const observer = new ResizeObserver(() => setSheetHeight(el.getBoundingClientRect().height));
    observer.observe(el);
    return () => observer.disconnect();
  }, [phone]);
  // Android opens its image menu through a contextmenu event; on a touch screen there is no other use for one on the
  // table or the card viewer (REQ-CLI-31). A mouse's right-click is left alone.
  useEffect(() => {
    const touch = window.matchMedia("(hover: none)");
    const block = (e: Event) => {
      const el = e.target as Element | null;
      if (touch.matches && el?.closest?.(".board-root, .card-viewer, .modal-backdrop")) e.preventDefault();
    };
    document.addEventListener("contextmenu", block);
    return () => document.removeEventListener("contextmenu", block);
  }, []);
  const inspect = useCallback((i: Inspect) => {
    setInspected(i);
    if (i) {
      setHoldHint(false);
      rememberHoldHint();
    }
  }, []);
  const [selection, setSelection] = useState<Selection>(null);
  const [botRow, setBotRow] = useState<RowRef | null>(null);
  const [aid, setAid] = useState(false);
  const toggle = useCallback(
    (s: Selection) => setSelection((cur) => (cur && s && cur.card.uid === s.card.uid ? null : s)),
    [],
  );
  const deselect = useCallback(() => {
    setSelection(null);
    setPreview(null);
    // Drop keyboard focus from the card too, so nothing still looks selected.
    const active = document.activeElement;
    if (active instanceof HTMLElement && active.classList.contains("gcard")) active.blur();
  }, []);
  // A selected card that has left the table (e.g. it was played) stays shown until deselected; refresh it if it moved.
  const selectedUid = selection?.card.uid ?? null;
  const me = view.you;
  const others = view.players.filter((p) => p.seat !== me);
  const mine = view.players.find((p) => p.seat === me);
  const bot = view.players.find((p) => p.bot);
  const rowText = (row: RowRef) => {
    const side = bot?.bot?.command.find((s) => s.side === row.side);
    const r = side?.rows.find((x) => x.number === row.number);
    return r ? `${r.matches.join(" / ")}: ${r.text}` : undefined;
  };
  // After the Bot's turn the player must press Done on its playback before their own turn begins: until then the
  // next question (such as which secured Location to control) is held back (REQ-SOLO-56). Questions asked during
  // the Bot's turn are not held: the turn cannot go on without them.
  const botTurn = bot ? view.bot_turn : null;
  const [botDone, setBotDone] = useState<number | null>(() =>
    botTurn && botTurnClosed(gameId, botTurn) ? botTurn.start : null);
  const botHold = !!botTurn && botTurn.finished && botTurn.steps.length > 0 && botDone !== botTurn.start && !view.result;
  const d = botHold ? null : view.decision;
  const endOption = d?.kind === "action" ? d.options?.find((o) => o.id === "end") : undefined;
  // Cards named by a "play" or "activate" option the viewer can choose right now.
  const playable = new Set(
    (d?.options ?? []).filter((o) => /^(play|activate):/.test(o.id)).map((o) => o.id.split(":")[1]),
  );
  const locationNames: Record<string, string> = Object.fromEntries(
    [...view.neutral_zone, ...view.players.flatMap((p) => p.locations)].map((l) => [l.uid, l.name]),
  );

  function pick(o: OptionView) {
    if (o.irreversible) setPending(o);
    else onChoose(o.id);
  }

  // Questions asked while a card resolves (where to warp, what to discard...) go in the floating box,
  // and the cards that answer them are highlighted and clickable.
  const midOperation = !!d?.options && (d.kind === "op" || d.kind === "trigger") && !view.result;
  // Cards beamed to a card on the table are shown under it, so they are on the board too.
  const withBeamed = (cards: typeof view.neutral_zone): typeof view.neutral_zone =>
    cards.flatMap((c) => [c, ...withBeamed(c.beamed ?? [])]);
  const visibleCards = withBeamed([...view.neutral_zone, ...Object.values(view.market).filter((c): c is NonNullable<typeof c> => !!c),
    ...view.players.flatMap((p) => [p.captain, ...p.status, ...p.fleet, ...p.locations, ...p.duty, ...p.staging,
      ...(p.hand ?? [])])]);
  const visibleUids = new Set(visibleCards.map((c) => c.uid));
  // Cards the question is about that are not on the board, e.g. a card just gained or looked at from a deck.
  const shownCards = midOperation ? (d!.cards ?? []).filter((c) => !visibleUids.has(c.uid)) : [];
  const optionFor = (uid: string) => d?.options?.find((o) => o.id === uid || o.id.endsWith(`:${uid}`));
  const targets = new Map<string, OptionView>();
  if (midOperation) {
    for (const uid of [...visibleUids, ...shownCards.map((c) => c.uid)]) {
      const o = optionFor(uid);
      if (o) targets.set(uid, o);
    }
    // "market:<suit>" answers name the faceup Market card by its slot.
    for (const o of d!.options!) {
      const faceup = o.id.startsWith("market:") ? view.market[o.id.slice("market:".length)] : null;
      if (faceup) targets.set(faceup.uid, o);
    }
  }
  // When the question shows cards from off the board (scanning, gaining from a deck or the Junk), the box shows every
  // card that answers it, each marked by where it comes from, so all the choices are side by side.
  const dockCards: DockCard[] = (() => {
    if (!shownCards.length) return [];
    const out: DockCard[] = [];
    for (const o of d!.options!) {
      const [prefix, key] = [o.id.split(":")[0], o.id.split(":").slice(1).join(":")];
      const card = prefix === "market" ? view.market[key] ?? undefined
        : (d!.cards ?? []).find((c) => c.uid === key) ?? visibleCards.find((c) => c.uid === key);
      if (!card || out.some((x) => x.card.uid === card.uid)) continue;
      const source = prefix === "market" ? "faceup" : prefix === "junk" ? "junk"
        : prefix === "look" || prefix === "deck" ? "deck" : undefined;
      out.push({ card, source, option: o.id });
    }
    for (const c of shownCards) if (!out.some((x) => x.card.uid === c.uid)) out.push({ card: c });
    return out;
  })();
  const targetKey = [...targets.keys()].join(",");

  // On a phone the table shows one area at a time (REQ-CLI-32). A tab is marked when its area changed since it was
  // last shown, and a question that asks for cards shows the area that holds them.
  const areaCards = (p: typeof mine) =>
    new Set(p ? withBeamed([p.captain, ...p.status, ...p.fleet, ...p.locations, ...p.duty, ...p.staging, ...(p.hand ?? [])]).map((c) => c.uid) : []);
  const areaOf = (uid: string): Area | null =>
    areaCards(mine).has(uid) ? "you" : others.some((p) => areaCards(p).has(uid)) ? "opponent" : visibleUids.has(uid) ? "centre" : null;
  const areas: { id: Area; label: string; signature: string }[] = [
    ...(mine ? [{ id: "you" as Area, label: "You", signature: JSON.stringify(mine) }] : []),
    { id: "centre", label: "Centre", signature: JSON.stringify([view.market, view.neutral_zone, view.junk.length, view.stardate,
      view.market_deck_counts, view.location_deck_count, view.encounter_count, view.incident_count]) },
    ...(others.length ? [{ id: "opponent" as Area, label: others[0].bot ? "Bot" : "Opponent", signature: JSON.stringify(others) }] : []),
    { id: "log", label: "System", signature: String(view.log.length) },
  ];
  const seen = useRef<Partial<Record<Area, string>>>({});
  for (const a of areas) if (a.id === tab || !phone || seen.current[a.id] === undefined) seen.current[a.id] = a.signature;
  const shownTab: Area = areas.some((a) => a.id === tab) ? tab : areas[0].id;
  // A question's answers name the cards they are about: a Market slot by its suit ("market:Ship", "glory:Ship"), any
  // other card by its uid at the end.
  // The Action Step is left alone: its answers are the cards in your hand and play area.
  const questionKey = d?.options && d.seat === me && d.kind !== "action" ? `${d.prompt}|${d.options.map((o) => o.id).join(",")}` : "";
  // When a question moved you to another tab, answering it brings you back, unless you chose a tab in between.
  const returnTo = useRef<Area | null>(null);
  useEffect(() => {
    if (!phone) return;
    if (!questionKey) {
      if (returnTo.current) setTab(returnTo.current);
      returnTo.current = null;
      return;
    }
    const held = d!.options!
      .map((o) => {
        const tail = o.id.split(":").pop() ?? "";
        return o.id.includes(":") && tail in view.market ? "centre" : areaOf(tail);
      })
      .filter((a): a is Area => !!a);
    if (held.length && !held.includes(shownTab)) {
      returnTo.current ??= shownTab;
      setTab(held[0]);
    }
  }, [questionKey, phone]); // eslint-disable-line react-hooks/exhaustive-deps
  // A new tab starts at the top of the table, below the game's title and buttons.
  const boardRef = useRef<HTMLDivElement>(null);
  const chooseTab = (a: Area) => {
    returnTo.current = null;
    setTab(a);
    const top = boardRef.current ? boardRef.current.getBoundingClientRect().top + window.scrollY - 8 : 0;
    window.scrollTo({ top });
  };
  const showArea = (a: Area) => !phone || shownTab === a;

  useEffect(() => {
    if (!targetKey) return;
    // Bring the highlighted cards into view unless one is fully visible above the floating box.
    const els = [...document.querySelectorAll<HTMLElement>(".gcard.target")];
    const limit = document.querySelector(".decision-dock")?.getBoundingClientRect().top ?? window.innerHeight;
    const onScreen = els.some((el) => {
      const r = el.getBoundingClientRect();
      return r.top >= 0 && r.bottom <= limit;
    });
    if (!onScreen && els[0]) {
      const r = els[0].getBoundingClientRect();
      // Centre the card in the space above the floating box.
      window.scrollBy({ top: r.top + r.height / 2 - limit / 2, behavior: "smooth" });
    }
  }, [targetKey, shownTab]);
  // List the answers in the order their cards sit on screen (top to bottom, then left to right), so the menu reads
  // like the table. Answers without a card on the board, e.g. "None", keep their place after them. It is measured
  // after layout, before the screen is painted, because the cards must be on the page first.
  const [screenOrder, setScreenOrder] = useState<string[] | null>(null);
  const optionsKey = `${d?.prompt}|${(d?.options ?? []).map((o) => o.id).join(",")}|${targetKey}`;
  useLayoutEffect(() => {
    const options = d?.options ?? [];
    const uidOf = new Map<string, string>();
    for (const [uid, o] of targets) uidOf.set(o.id, uid);
    const placed = options.map((o, i) => {
      const uid = uidOf.get(o.id);
      const el = uid ? [...document.querySelectorAll<HTMLElement>(`.gcard[data-uid="${uid}"]`)]
        .find((x) => !x.closest(".decision-dock")) : undefined;
      return { id: o.id, i, r: el?.getBoundingClientRect() };
    });
    const onBoard = placed.filter((p) => p.r).sort((a, b) => {
      const dy = a.r!.top - b.r!.top;
      return Math.abs(dy) > 30 ? dy : a.r!.left - b.r!.left || a.i - b.i;
    });
    setScreenOrder([...onBoard, ...placed.filter((p) => !p.r)].map((p) => p.id));
  }, [optionsKey]); // eslint-disable-line react-hooks/exhaustive-deps
  const dockOptions = (d?.options ?? []).slice().sort((a, b) => {
    const rank = (o: OptionView) => screenOrder?.indexOf(o.id) ?? -1;
    return rank(a) - rank(b);
  });
  // Location answers are boxed by where the Location is: the Neutral Zone or a player's controlled Locations.
  const locationGroup = (o: OptionView): string | undefined => {
    const uid = [...targets].find(([, t]) => t.id === o.id)?.[0];
    if (!uid) return undefined;
    if (view.neutral_zone.some((l) => l.uid === uid)) return "Neutral Zone";
    const owner = view.players.find((p) => p.locations.some((l) => l.uid === uid));
    if (!owner) return undefined;
    return owner.seat === view.you ? "Your controlled Locations" : `${owner.name}'s controlled Locations`;
  };
  // The cards in the box follow the order of the answer buttons.
  const rank = (c: DockCard) => (c.option ? dockOptions.findIndex((o) => o.id === c.option) : dockOptions.length);
  const showDock = !!d?.options && d.kind !== "action" && !view.result && !selection && !pending;
  // Someone else's decision (the other player in a two-player game): a quiet note in the same place.
  const waiting = !view.result && d && !d.options ? `Waiting for ${view.players[d.seat]?.name ?? "…"}: ${d.prompt}` : null;

  return (
    <PreviewContext.Provider value={setPreview}>
    <InspectContext.Provider value={inspect}>
    <PlayersContext.Provider value={view.players}>
    <PlayableContext.Provider value={playable}>
    <SelectContext.Provider value={{ selected: selectedUid, toggle }}>
    <TargetContext.Provider value={{ targets, answer: pick }}>
    <div ref={boardRef} className="stack board-root" style={phone ? { paddingBottom: sheetHeight + 16 } : undefined}>
      {holdHint && (
        <p className="hold-hint" role="note">
          <span>Press and hold any card to see it full size, with the cards beamed to it.</span>
          <button className="link" onClick={() => { setHoldHint(false); rememberHoldHint(); }}>Got it</button>
        </p>
      )}
      {/* The game's state is shown on the mats and its choices on the cards, the End Turn button and the floating
          box, so there is no separate status box; only the result appears up here, once the game is over. */}
      {view.result && (
        <section className="card">
          <div>
            <h2>Game over ({view.result.reason})</h2>
            {view.mode === "cadet" && view.result.reason === "burn" && <p>The Burn ends Cadet Training: you lose.</p>}
            {view.mode === "solo" && (
              <p><strong>
                {view.result.winners.includes(view.you ?? -1) ? "You beat the Bot!"
                  : view.result.reason === "burn" ? "The Burn: the Bot wins."
                  : view.result.reason === "only_ship" ? "Your only Ship left play: the assignment fails."
                  : "The Bot wins. (A tie counts as a loss.)"}
              </strong></p>
            )}
            {view.result.scores?.map((s) => (
              <details key={s.seat}>
                <summary>
                  {s.name}: {s.total} VP {view.mode !== "cadet" && view.result!.winners.includes(s.seat) && "— winner"}
                </summary>
                <ul className="score-parts">
                  {Object.entries(s.parts).filter(([, v]) => v !== 0).map(([k, v]) => (
                    <li key={k}>{SCORE_PART[k] ?? k}: {v}</li>
                  ))}
                </ul>
              </details>
            ))}
            {view.result.rating && <p><strong>{view.result.rating}</strong></p>}
          </div>
        </section>
      )}

      {showArea("opponent") && others.map((p) => (
        <PlayerMat key={p.seat} p={p} you={false} active={view.active === p.seat} locationNames={locationNames}
          highlight={p.bot ? botRow : undefined} onSoloRules={p.bot ? () => setAid(true) : undefined} />
      ))}

      {showArea("centre") && <CenterMat view={view} />}

      {/* The Neutral Zone is on the You tab too, for planning your turn. */}
      {phone && shownTab === "you" && view.neutral_zone.length > 0 && (
        <section className="mat nz-mat" aria-label="Neutral Zone">
          <NeutralZone view={view} compact />
        </section>
      )}
      {mine && showArea("you") && (
        <PlayerMat p={mine} you active={view.active === mine.seat} locationNames={locationNames}
          onEndTurn={endOption && !busy ? () => pick(endOption) : null}
          onUndo={view.can_undo && !busy && !showDock ? onUndo : null}
          missions={d?.kind === "action" && d.seat === view.you ? (d.options ?? []).filter((o) => o.id.startsWith("mission:")) : []}
          onMission={busy ? undefined : pick} />
      )}

      {phone && shownTab === "log" && system && <div className="stack system-actions">{system}</div>}
      {showArea("log") && <section className="card">
        <h2>Log</h2>
        <ul className="list plain mono">{[...view.log].reverse().map((line, i) => <li key={i}>{line}</li>)}</ul>
      </section>}

      {pending && (
        <Confirm option={pending} solo={view.mode === "solo"} onBack={() => setPending(null)} onContinue={() => { onChoose(pending.id); setPending(null); }} />
      )}
      {/* The floating panels. On a laptop each floats on its own; on a phone they share one sheet at the bottom of
          the screen (REQ-CLI-34), and the table leaves room for it. */}
      <div className="sheet-stack" ref={sheetRef}>
      {bot && (
        <BotPlayback gameId={gameId} turn={view.bot_turn} botName={bot.name} rowText={rowText} onHighlight={setBotRow}
          onDone={setBotDone} />
      )}
      {/* Two-player games: step through the other player's turn the same way (REQ-CLI-19). */}
      {!bot && view.opponent_turn && others[0] && (
        <BotPlayback gameId={gameId} turn={view.opponent_turn} botName={others[0].name} rowText={() => undefined}
          onHighlight={() => {}} onDone={() => {}} holdsTurn={false} />
      )}
      {/* A question asked mid-operation (e.g. where to warp) stays in sight while the top box is scrolled away.
          The Action Step menu is left out: its choices are made from the cards and the End Turn button. */}
      {showDock && (
        <Sheet className="decision-dock card" role="dialog" label="Your decision" summary={d!.prompt}>
          <DecisionOptions prompt={d!.prompt} options={dockOptions} busy={busy} canUndo={view.can_undo}
            onPick={pick} onUndo={onUndo} groupOf={locationGroup}
            cards={dockCards.slice().sort((a, b) => rank(a) - rank(b))}
            hint={targets.size ? "Or click a highlighted card." : undefined} />
        </Sheet>
      )}
      {waiting && <div className="decision-dock waiting-note card" role="status">{waiting}</div>}
      {botHold && (
        <div className="decision-dock waiting-note card" role="status">
          The Bot's turn is over. Press <strong>Done</strong> on its turn panel to start your turn.
        </div>
      )}
      {selection && (
        <CardPanel selection={selection} view={botHold ? { ...view, decision: null } : view} onClose={deselect}
          onChoose={(o) => { setSelection(null); pick(o); }} />
      )}
      {phone && (
        <nav className="area-tabs" aria-label="Table areas" style={{ gridTemplateColumns: `repeat(${areas.length}, 1fr)` }}>
          {areas.map((a) => {
            const changed = a.id !== shownTab && seen.current[a.id] !== a.signature;
            return (
              <button key={a.id} type="button" className={a.id === shownTab ? "active" : ""} aria-current={a.id === shownTab}
                onClick={() => chooseTab(a.id)}>
                {a.label}{changed && <span className="tab-mark" aria-label="(changed)" />}
              </button>
            );
          })}
        </nav>
      )}
      </div>
      {aid && <SoloAid onClose={() => setAid(false)} />}
      <CardPreview preview={preview} />
      <CardViewer shown={inspected} onShow={inspect} />
    </div>
    </TargetContext.Provider>
    </SelectContext.Provider>
    </PlayableContext.Provider>
    </PlayersContext.Provider>
    </InspectContext.Provider>
    </PreviewContext.Provider>
  );
}

/** The areas of the table a phone shows one at a time (REQ-CLI-32). */
type Area = "you" | "centre" | "opponent" | "log";

const HOLD_HINT_KEY = "cc.hint.hold";

/** The press-and-hold hint is shown once, on a touch screen, until the player opens a card or dismisses it. */
function showHoldHint(): boolean {
  try {
    return window.matchMedia("(hover: none)").matches && !localStorage.getItem(HOLD_HINT_KEY);
  } catch {
    return false;
  }
}

function rememberHoldHint() {
  try {
    localStorage.setItem(HOLD_HINT_KEY, "1");
  } catch {
    /* storage unavailable: the hint comes back next time */
  }
}
