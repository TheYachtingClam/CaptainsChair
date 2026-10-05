import { useEffect, useMemo, useState } from "react";
import { BotStep, BotTurnView, RowRef } from "../api";
import { imageUrl } from "./Cards";

const AUTO_DELAY_MS = 1100;

function watchedKey(gameId: string) {
  return `cc.botwatched.${gameId}`;
}

/** How far the player has watched: the Bot turn (its log position) and how many of its steps. */
function loadWatched(gameId: string): { start: number; count: number } {
  try {
    const raw = localStorage.getItem(watchedKey(gameId));
    if (raw) return JSON.parse(raw);
  } catch {
    // private window or blocked storage: start from nothing
  }
  return { start: -1, count: 0 };
}

function saveWatched(gameId: string, start: number, count: number) {
  try {
    localStorage.setItem(watchedKey(gameId), JSON.stringify({ start, count }));
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
 * (highlighted on its command card through `onHighlight`), and each thing it did. Next, Auto-play and Skip.
 */
export function BotPlayback({ gameId, turn, botName, rowText, onHighlight }: {
  gameId: string;
  turn: BotTurnView | null;
  botName: string;
  rowText: (row: RowRef) => string | undefined;
  onHighlight: (row: RowRef | null) => void;
}) {
  const [index, setIndex] = useState(() => {
    if (!turn) return 0;
    const w = loadWatched(gameId);
    return w.start === turn.start ? w.count : 0;
  });
  const [auto, setAuto] = useState(true);
  const steps = turn?.steps ?? [];

  // A new Bot turn starts from its first step; more steps of the same turn continue where we were.
  useEffect(() => {
    if (!turn) return;
    const w = loadWatched(gameId);
    setIndex(w.start === turn.start ? Math.min(w.count, turn.steps.length) : 0);
  }, [gameId, turn?.start]); // eslint-disable-line react-hooks/exhaustive-deps

  const watching = !!turn && index < steps.length;

  useEffect(() => {
    if (turn) saveWatched(gameId, turn.start, index);
  }, [gameId, turn, index]);

  useEffect(() => {
    if (!watching || !auto) return;
    const timer = setTimeout(() => setIndex((i) => i + 1), AUTO_DELAY_MS);
    return () => clearTimeout(timer);
  }, [watching, auto, index]);

  const shown = useMemo(() => context(steps, index), [steps, index]);
  useEffect(() => {
    onHighlight(watching ? shown.row ?? null : null);
  }, [watching, shown.row?.side, shown.row?.number]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!watching) return null;
  const step = steps[index];
  const rowLabel = shown.row ? rowText(shown.row) : undefined;
  return (
    <div className="bot-playback card" role="region" aria-label={`${botName}'s turn`} aria-live="polite">
      <header className="row">
        <strong>{botName}'s turn</strong>
        <span className="muted">Step {index + 1} of {steps.length}{turn!.finished ? "" : "+"}</span>
      </header>
      <div className="bot-playback-body">
        {shown.card && (
          <img className="bot-playback-card" src={imageUrl(shown.card.image)} alt={shown.card.name} />
        )}
        <div className="stack">
          <p className="bot-step">{step.text}</p>
          {rowLabel && <p className="bot-row"><span className="muted">Matched row:</span> {rowLabel}</p>}
        </div>
      </div>
      <div className="row">
        <button onClick={() => { setAuto(false); setIndex((i) => i + 1); }}>Next</button>
        <button className="secondary" onClick={() => setAuto((a) => !a)}>{auto ? "Pause" : "Auto-play"}</button>
        <button className="secondary" onClick={() => setIndex(steps.length)}>Skip to the end</button>
      </div>
    </div>
  );
}
