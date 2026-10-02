import { useEffect, useRef, useState } from "react";
import { CardView, GameStateView, OptionView } from "../api";
import { Card, CardPreview, Preview, PreviewContext } from "./Cards";
import { PlayerMat } from "./PlayerMat";

function Row({ label, cards, empty = "—" }: { label: string; cards: CardView[]; empty?: string }) {
  return (
    <div className="zone">
      <div className="zone-label">{label}</div>
      <div className="cards">{cards.length ? cards.map((c) => <Card key={c.uid} card={c} />) : <span className="muted">{empty}</span>}</div>
    </div>
  );
}

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

export function Board({ view, onChoose, onUndo, busy }: {
  view: GameStateView;
  onChoose: (option: string) => void;
  onUndo: () => void;
  busy: boolean;
}) {
  const [pending, setPending] = useState<OptionView | null>(null);
  const [preview, setPreview] = useState<Preview>(null);
  const me = view.you;
  const others = view.players.filter((p) => p.seat !== me);
  const mine = view.players.find((p) => p.seat === me);
  const d = view.decision;
  const locationNames: Record<string, string> = Object.fromEntries(
    [...view.neutral_zone, ...view.players.flatMap((p) => p.locations)].map((l) => [l.uid, l.name]),
  );

  function pick(o: OptionView) {
    if (o.irreversible) setPending(o);
    else onChoose(o.id);
  }

  return (
    <PreviewContext.Provider value={setPreview}>
    <div className="stack">
      <section className="card">
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
            {view.result.scores?.map((s) => (
              <p key={s.seat}>{s.name}: {s.total} VP {view.result!.winners.includes(s.seat) && "— winner"}</p>
            ))}
          </div>
        ) : d && d.options ? (
          <div className="stack">
            <p><strong>{d.prompt}</strong></p>
            <div className="options">
              {d.options.map((o) => (
                <button key={o.id} disabled={busy} className="option" onClick={() => pick(o)}>
                  {o.irreversible && <span aria-label="Cannot be undone" title="Cannot be undone">🔒 </span>}
                  {o.label}
                </button>
              ))}
            </div>
            {view.can_undo && <button className="secondary" disabled={busy} onClick={onUndo}>Undo</button>}
          </div>
        ) : (
          <p className="muted">Waiting for {d ? view.players[d.seat]?.name : "…"}: {d?.prompt}</p>
        )}
      </section>

      {others.map((p) => <PlayerMat key={p.seat} p={p} you={false} active={view.active === p.seat} locationNames={locationNames} />)}

      <section className="card">
        <Row label="Neutral Zone" cards={view.neutral_zone} />
        <Row label="Market" cards={Object.values(view.market).filter((c): c is CardView => !!c)} />
        <Row label="Junk" cards={view.junk} />
      </section>

      {mine && <PlayerMat p={mine} you active={view.active === mine.seat} locationNames={locationNames} />}

      <section className="card">
        <h2>Log</h2>
        <ul className="list plain mono">{[...view.log].reverse().map((line, i) => <li key={i}>{line}</li>)}</ul>
      </section>

      {pending && (
        <Confirm option={pending} onBack={() => setPending(null)} onContinue={() => { onChoose(pending.id); setPending(null); }} />
      )}
      <CardPreview preview={preview} />
    </div>
    </PreviewContext.Provider>
  );
}
