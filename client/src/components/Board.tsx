import { useCallback, useEffect, useRef, useState } from "react";
import { CardView, GameStateView, OptionView } from "../api";
import { Card, CardPreview, PlayableContext, Preview, PreviewContext, SelectContext, Selection, TargetContext } from "./Cards";
import { CardPanel } from "./CardPanel";
import { PlayerMat } from "./PlayerMat";
import { CenterMat } from "./CenterMat";

function Confirm({ option, onContinue, onBack }: { option: OptionView; onContinue: () => void; onBack: () => void }) {
  const back = useRef<HTMLButtonElement>(null);
  useEffect(() => back.current?.focus(), []);
  return (
    <div className="modal-backdrop" onKeyDown={(e) => e.key === "Escape" && onBack()}>
      <div className="card modal" role="alertdialog" aria-labelledby="confirm-title">
        <h2 id="confirm-title">This can't be undone</h2>
        <p>{option.reason ?? "This reveals information or ends your turn."}</p>
        <div className="row">
          <button ref={back} className="secondary" onClick={onBack}>Go back</button>
          <button onClick={onContinue}>Continue</button>
        </div>
      </div>
    </div>
  );
}

/** The prompt and answer buttons of a decision. */
function DecisionOptions({ prompt, options, busy, canUndo, onPick, onUndo, hint, cards }: {
  hint?: string;
  cards?: CardView[];
  prompt: string;
  options: OptionView[];
  busy: boolean;
  canUndo: boolean;
  onPick: (o: OptionView) => void;
  onUndo: () => void;
}) {
  return (
    <div className="stack">
      <p><strong>{prompt}</strong></p>
      {cards && cards.length > 0 && (
        <div className="dock-cards">{cards.map((c) => <Card key={c.uid} card={c} />)}</div>
      )}
      {hint && <p className="muted">{hint}</p>}
      <div className="options">
        {options.map((o) => (
          <button key={o.id} disabled={busy} className="option" onClick={() => onPick(o)}>
            {o.irreversible && <span aria-label="Cannot be undone" title="Cannot be undone">🔒 </span>}
            {o.label}
          </button>
        ))}
      </div>
      {canUndo && <button className="secondary" disabled={busy} onClick={onUndo}>Undo</button>}
    </div>
  );
}

/** True while the element is on screen. */
function useOnScreen(ref: React.RefObject<HTMLElement | null>): boolean {
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting));
    observer.observe(el);
    return () => observer.disconnect();
  }, [ref]);
  return visible;
}

export function Board({ view, onChoose, onUndo, busy }: {
  view: GameStateView;
  onChoose: (option: string) => void;
  onUndo: () => void;
  busy: boolean;
}) {
  const [pending, setPending] = useState<OptionView | null>(null);
  const [preview, setPreview] = useState<Preview>(null);
  const [selection, setSelection] = useState<Selection>(null);
  const decisionBox = useRef<HTMLElement>(null);
  const decisionBoxVisible = useOnScreen(decisionBox);
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
  const d = view.decision;
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
  const visibleUids = new Set(
    [...view.neutral_zone, ...Object.values(view.market).filter((c): c is NonNullable<typeof c> => !!c),
     ...view.players.flatMap((p) => [p.captain, ...p.status, ...p.fleet, ...p.locations, ...p.duty, ...p.staging,
       ...(p.hand ?? []), ...p.fleet.flatMap((s) => s.beamed ?? [])])].map((c) => c.uid),
  );
  // Cards the question is about that are not on the board, e.g. a card just gained or looked at from a deck.
  const shownCards = midOperation ? (d!.cards ?? []).filter((c) => !visibleUids.has(c.uid)) : [];
  const optionFor = (uid: string) => d?.options?.find((o) => o.id === uid || o.id.endsWith(`:${uid}`));
  const targets = new Map<string, OptionView>();
  if (midOperation) {
    for (const uid of [...visibleUids, ...shownCards.map((c) => c.uid)]) {
      const o = optionFor(uid);
      if (o) targets.set(uid, o);
    }
  }
  const targetKey = [...targets.keys()].join(",");
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
  }, [targetKey]);
  const showDock = !!d?.options && d.kind !== "action" && !view.result && !selection && !pending
    && (midOperation || !decisionBoxVisible);

  return (
    <PreviewContext.Provider value={setPreview}>
    <PlayableContext.Provider value={playable}>
    <SelectContext.Provider value={{ selected: selectedUid, toggle }}>
    <TargetContext.Provider value={{ targets, answer: pick }}>
    <div className="stack">
      <section className="card" ref={decisionBox}>
        <div className="row between">
          <strong>
            Turn {view.turn} · {view.players[view.active]?.name}'s turn · {view.step}
            {view.resolution && ` · Resolution: game ends after turn ${view.last_turn}`}
          </strong>
          <span className="muted">
            Stardate: {view.stardate.glory} Glory, {view.stardate.remaining} card(s) left · Incidents {view.incident_count} ·
            Encounters {view.encounter_count}
          </span>
        </div>
        {view.result ? (
          <div>
            <h2>Game over ({view.result.reason})</h2>
            {view.mode === "cadet" && view.result.reason === "burn" && <p>The Burn ends Cadet Training: you lose.</p>}
            {view.result.scores?.map((s) => (
              <p key={s.seat}>
                {s.name}: {s.total} VP {view.mode !== "cadet" && view.result!.winners.includes(s.seat) && "— winner"}
              </p>
            ))}
            {view.result.rating && <p><strong>{view.result.rating}</strong></p>}
          </div>
        ) : d && d.options && midOperation ? (
          <p><strong>{d.prompt}</strong> <span className="muted">Answer in the box at the bottom of the screen.</span></p>
        ) : d && d.options ? (
          <DecisionOptions prompt={d.prompt} options={d.options} busy={busy} canUndo={view.can_undo}
            onPick={pick} onUndo={onUndo} />
        ) : (
          <p className="muted">Waiting for {d ? view.players[d.seat]?.name : "…"}: {d?.prompt}</p>
        )}
      </section>

      {others.map((p) => <PlayerMat key={p.seat} p={p} you={false} active={view.active === p.seat} locationNames={locationNames} />)}

      <CenterMat view={view} />

      {mine && (
        <PlayerMat p={mine} you active={view.active === mine.seat} locationNames={locationNames}
          onEndTurn={endOption && !busy ? () => pick(endOption) : null}
          missions={d?.kind === "action" && d.seat === view.you ? (d.options ?? []).filter((o) => o.id.startsWith("mission:")) : []}
          onMission={busy ? undefined : pick} />
      )}

      <section className="card">
        <h2>Log</h2>
        <ul className="list plain mono">{[...view.log].reverse().map((line, i) => <li key={i}>{line}</li>)}</ul>
      </section>

      {pending && (
        <Confirm option={pending} onBack={() => setPending(null)} onContinue={() => { onChoose(pending.id); setPending(null); }} />
      )}
      {/* A question asked mid-operation (e.g. where to warp) stays in sight while the top box is scrolled away.
          The Action Step menu is left out: its choices are made from the cards and the End Turn button. */}
      {showDock && (
        <div className="decision-dock card" role="dialog" aria-label="Your decision">
          <DecisionOptions prompt={d!.prompt} options={d!.options!} busy={busy} canUndo={view.can_undo}
            onPick={pick} onUndo={onUndo} cards={shownCards}
            hint={targets.size ? "Or click a highlighted card." : undefined} />
        </div>
      )}
      <CardPreview preview={preview} />
      {selection && (
        <CardPanel selection={selection} view={view} onClose={deselect}
          onChoose={(o) => { setSelection(null); pick(o); }} />
      )}
    </div>
    </TargetContext.Provider>
    </SelectContext.Provider>
    </PlayableContext.Provider>
    </PreviewContext.Provider>
  );
}
