import { useEffect, useMemo, useState } from "react";
import { BotStep, BotTurnView, RowRef } from "../api";
import { imageUrl } from "./Cards";

const AUTO_DELAY_MS = 1100;

function watchedKey(gameId: string) {
  return `cc.botwatched.${gameId}`;
}

interface Watched {
  start: number; // the Bot turn, by its log position
  count: number; // the step being shown
  closed?: boolean; // the player closed the panel after the turn
}

/** How far the player has watched the latest Bot turn. */
function loadWatched(gameId: string): Watched {
  try {
    const raw = localStorage.getItem(watchedKey(gameId));
    if (raw) return JSON.parse(raw);
  } catch {
    // private window or blocked storage: start from nothing
  }
  return { start: -1, count: 0 };
}

function saveWatched(gameId: string, watched: Watched) {
  try {
    localStorage.setItem(watchedKey(gameId), JSON.stringify(watched));
  } catch {
    // ignore
  }
}

/** The card and matched row in effect at a step: the latest ones up to and including it. */
function context(steps: BotStep[], index: number): { card?: BotStep["card"]; row?: RowRef } {
  let card: BotStep["card"];
  let row: RowRef | undefined;
  for (let i = 0; i <= index && i < steps.length; i++) {
    if (steps[i].card) {
      if (steps[i].card!.id !== card?.id) row = undefined;
      card = steps[i].card;
    }
    if (steps[i].row) row = steps[i].row;
  }
  return { card, row };
}

/**
 * Watch the Bot's turn one step at a time (REQ-SOLO-56): the card it flipped, the Automated Command row that matched
 * (highlighted on its command card through `onHighlight`), and each thing it did. Previous, Next, Auto-play and Skip.
 * Playback stops on the last step so the player can step back through the turn; Done closes the panel.
 */
export function BotPlayback({ gameId, turn, botName, rowText, onHighlight }: {
  gameId: string;
  turn: BotTurnView | null;
  botName: string;
  rowText: (row: RowRef) => string | undefined;
  onHighlight: (row: RowRef | null) => void;
}) {
  const steps = turn?.steps ?? [];
  const last = Math.max(steps.length - 1, 0);
  const [index, setIndex] = useState(() => {
    const w = loadWatched(gameId);
    return turn && w.start === turn.start ? Math.min(w.count, last) : 0;
  });
  const [closed, setClosed] = useState(() => {
    const w = loadWatched(gameId);
    // Older saves marked a finished turn by counting past its last step.
    return !!turn && w.start === turn.start && (!!w.closed || (turn.finished && w.count >= turn.steps.length));
  });
  const [auto, setAuto] = useState(true);

  // A new Bot turn opens at its first step; more steps of the same turn continue where we were.
  useEffect(() => {
    if (!turn) return;
    const w = loadWatched(gameId);
    if (w.start === turn.start) return;
    setIndex(0);
    setClosed(false);
    setAuto(true);
  }, [gameId, turn?.start]); // eslint-disable-line react-hooks/exhaustive-deps

  const watching = !!turn && steps.length > 0 && !closed;
  const atEnd = index >= last;

  useEffect(() => {
    if (turn) saveWatched(gameId, { start: turn.start, count: index, closed });
  }, [gameId, turn, index, closed]);

  // Auto-play stops on the last step; steps that arrive later (a turn waiting on your answer) carry on.
  useEffect(() => {
    if (!watching || !auto || atEnd) return;
    const timer = setTimeout(() => setIndex((i) => Math.min(i + 1, last)), AUTO_DELAY_MS);
    return () => clearTimeout(timer);
  }, [watching, auto, atEnd, index, last]);

  const shown = useMemo(() => context(steps, index), [steps, index]);
  useEffect(() => {
    onHighlight(watching ? shown.row ?? null : null);
  }, [watching, shown.row?.side, shown.row?.number]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!watching) return null;
  const step = steps[Math.min(index, last)];
  const rowLabel = shown.row ? rowText(shown.row) : undefined;
  return (
    <div className="bot-playback card" role="region" aria-label={`${botName}'s turn`} aria-live="polite">
      <header className="row">
        <strong>{botName}'s turn</strong>
        <span className="muted">
          Step {Math.min(index, last) + 1} of {steps.length}{turn!.finished ? "" : "+"}
          {atEnd && turn!.finished && " · turn over"}
        </span>
      </header>
      <div className="bot-playback-controls">
        <button className="secondary" disabled={index === 0} onClick={() => { setAuto(false); setIndex((i) => Math.max(i - 1, 0)); }}>
          Previous
        </button>
        <button disabled={atEnd} onClick={() => { setAuto(false); setIndex((i) => Math.min(i + 1, last)); }}>Next</button>
        <button className="secondary" disabled={atEnd} onClick={() => setAuto((a) => !a)}>
          {auto ? "Pause" : "Auto-play"}
        </button>
        <button className="secondary" disabled={atEnd} onClick={() => { setAuto(false); setIndex(last); }}>Skip to end</button>
        <button disabled={!turn!.finished} title={turn!.finished ? undefined : "The Bot's turn is not over yet"}
          onClick={() => setClosed(true)}>Done</button>
      </div>
      <div className="bot-playback-body">
        <div className="bot-playback-card-slot">
          {shown.card && <img className="bot-playback-card" src={imageUrl(shown.card.image)} alt={shown.card.name} />}
        </div>
        <div className="stack">
          <p className="bot-step">{step.text}</p>
          {rowLabel && <p className="bot-row"><span className="muted">Matched row:</span> {rowLabel}</p>}
        </div>
      </div>
    </div>
  );
}
