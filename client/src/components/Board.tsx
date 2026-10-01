import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CardView, GameStateView, OptionView, PlayerView } from "../api";

type Preview = { card: CardView; x: number; y: number } | null;
const PreviewContext = createContext<(p: Preview) => void>(() => {});

const GAP = 18; // distance between the cursor and the preview
const MARGIN = 8; // keep this far from the window edges

/** Large version of the hovered or focused card, placed next to the cursor and kept on screen. */
function CardPreview({ preview }: { preview: Preview }) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!preview || !el) return;
    const { width, height } = el.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    // Prefer the right of the cursor; flip to the left if it would run off screen.
    let left = preview.x + GAP;
    if (left + width > vw - MARGIN) left = preview.x - GAP - width;
    left = Math.max(MARGIN, Math.min(left, vw - width - MARGIN));
    const top = Math.max(MARGIN, Math.min(preview.y - height / 2, vh - height - MARGIN));
    setPos({ left, top });
  }, [preview]);

  if (!preview) return null;
  const { card } = preview;
  return (
    <div
      ref={ref}
      className="card-preview"
      aria-hidden
      style={pos ? { left: pos.left, top: pos.top } : { left: -9999, top: 0 }}
    >
      <img src={`/api/content/images/${card.image}`} alt="" />
      {card.beamed && card.beamed.length > 0 && (
        <div className="preview-beamed">
          <span className="muted">Beamed here:</span>
          {card.beamed.map((b) => <img key={b.uid} src={`/api/content/images/${b.image}`} alt="" />)}
        </div>
      )}
    </div>
  );
}

function Card({ card }: { card: CardView }) {
  const setPreview = useContext(PreviewContext);
  const glory = card.resources?.glory;
  const show = (x: number, y: number) => setPreview({ card, x, y });
  return (
    <div
      className={`gcard ${card.exhausted ? "exhausted" : ""}`}
      title={card.name}
      tabIndex={0}
      onMouseEnter={(e) => show(e.clientX, e.clientY)}
      onMouseMove={(e) => show(e.clientX, e.clientY)}
      onMouseLeave={() => setPreview(null)}
      onFocus={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        show(r.right, r.top + r.height / 2);
      }}
      onBlur={() => setPreview(null)}
    >
      <img src={`/api/content/images/${card.image}`} alt={card.name} loading="lazy" />
      {glory ? <span className="badge">{glory} Glory</span> : null}
      {card.away_teams && Object.keys(card.away_teams).length > 0 && (
        <span className="badge left">
          {Object.entries(card.away_teams).map(([seat, n]) => `P${Number(seat) + 1}:${n}`).join(" ")}
        </span>
      )}
      {card.beamed && card.beamed.length > 0 && <span className="badge left">+{card.beamed.length} beamed</span>}
    </div>
  );
}

function Row({ label, cards, empty = "—" }: { label: string; cards: CardView[]; empty?: string }) {
  return (
    <div className="zone">
      <div className="zone-label">{label}</div>
      <div className="cards">{cards.length ? cards.map((c) => <Card key={c.uid} card={c} />) : <span className="muted">{empty}</span>}</div>
    </div>
  );
}

function PlayerArea({ p, you }: { p: PlayerView; you: boolean }) {
  return (
    <section className="card">
      <div className="row between">
        <h2>{p.name}{you && " (you)"}</h2>
        <span className="muted">
          Dilithium {p.resources.dilithium} · Latinum {p.resources.latinum} · Glory {p.resources.glory} · Actions {p.actions} ·
          Away Teams {p.away_pool}
        </span>
      </div>
      <p className="muted">
        Research {p.tracks.research} · Influence {p.tracks.influence} · Military {p.tracks.military} · Deck {p.draw_count} ·
        Reserve {p.reserve_count} · Discard {p.discard.length} · Development {p.development.length} · Log {p.log.length} ·
        Hand {p.hand_count}/{p.hand_size}
      </p>
      <Row label="Captain, Status, Duty" cards={[p.captain, ...p.status, ...p.duty]} />
      <Row label="Locations" cards={p.locations} />
      <Row label="Fleet" cards={p.fleet} />
      <Row label="Staging Area" cards={p.staging} />
      {p.hand && <Row label="Hand" cards={p.hand} empty="Empty" />}
    </section>
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

      {others.map((p) => <PlayerArea key={p.seat} p={p} you={false} />)}

      <section className="card">
        <Row label="Neutral Zone" cards={view.neutral_zone} />
        <Row label="Market" cards={Object.values(view.market).filter((c): c is CardView => !!c)} />
        <Row label="Junk" cards={view.junk} />
      </section>

      {mine && <PlayerArea p={mine} you />}

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
