import { useState } from "react";
import { CardView, PlayerView } from "../api";
import { Card, CardBack, PileViewer, Slot, imageUrl, usePreviewHandlers } from "./Cards";

// Crew board track geometry, as fractions of the board image (measured from the scans).
const TRACK_X0 = 0.073; // centre of space 0
const TRACK_STEP = 0.0553; // distance between spaces
const TRACK_Y: Record<string, number> = { research: 0.51, influence: 0.71, military: 0.9 };
const TRACK_COLOUR: Record<string, string> = { research: "#2f7de1", influence: "#e0b400", military: "#d93636" };

function CrewBoard({ p }: { p: PlayerView }) {
  const hasTracks = p.deck !== "khan"; // Khan marks traits instead (REQ-CD-KHN-04)
  const preview = usePreviewHandlers(p.board, true);
  return (
    <div className="crew-board" {...preview} title={`${p.name}'s Crew board`}>
      <img src={imageUrl(p.board)} alt={`${p.name}'s Crew board`} />
      {hasTracks && Object.entries(p.tracks).map(([track, value]) => (
        <span
          key={track}
          className="track-marker"
          title={`${track}: ${value}`}
          style={{ left: `${(TRACK_X0 + Math.min(value, 15) * TRACK_STEP) * 100}%`, top: `${TRACK_Y[track] * 100}%`, background: TRACK_COLOUR[track] }}
        />
      ))}
      <span className="mission-tokens" title="Mission Completion tokens">
        Missions {p.missions_completed.length}/{p.mission_tokens}
      </span>
    </div>
  );
}

function Tokens({ p }: { p: PlayerView }) {
  return (
    <div className="tokens" aria-label="Resources and actions">
      <span className="token action" title="Available actions">{p.actions} Action{p.actions === 1 ? "" : "s"}</span>
      <span className="token glory" title="Glory">{p.resources.glory} Glory</span>
      <span className="token dilithium" title="Dilithium">{p.resources.dilithium} Dilithium</span>
      <span className="token latinum" title="Latinum">{p.resources.latinum} Latinum</span>
    </div>
  );
}

/** A table area outlined in thin blue, with its name in the corner. */
function Section({ label, cards, place }: { label: string; cards: CardView[]; place?: (c: CardView) => string | undefined }) {
  return (
    <div className="section" aria-label={label}>
      <span className="section-label">{label}</span>
      <div className="lane">
        {cards.map((c) => (
          <Card key={c.uid} card={c} badges={place?.(c) ? <span className="badge bottom-left">at {place(c)}</span> : null} />
        ))}
      </div>
    </div>
  );
}

export function PlayerMat({ p, you, active, locationNames }: {
  p: PlayerView;
  you: boolean;
  active: boolean;
  locationNames: Record<string, string>;
}) {
  const [viewing, setViewing] = useState<null | "discard" | "development" | "log">(null);
  const piles = { discard: ["Discard pile", p.discard], development: ["Development pile", p.development], log: ["Captain's Log", p.log] } as const;
  const topDiscard = p.discard[p.discard.length - 1];

  return (
    <section className={`mat ${active ? "active" : ""}`} aria-label={`${p.name}'s play area`}>
      <header className="mat-header">
        <h2>{p.name}{you && " (you)"}</h2>
        {active && <span className="pill">Active player</span>}
      </header>

      <div className="mat-grid">
        {/* Left column: Reserve, Status, Development, tokens, Crew board (items 7, 4, 6, 12, 1) */}
        <div className="mat-left">
          <div className="row top">
            <CardBack label="Reserve" count={p.reserve_count} />
            {p.status.map((c) => <Card key={c.uid} card={c} />)}
          </div>
          <button type="button" className="dev-pile" onClick={() => setViewing("development")} disabled={!p.development.length}>
            <span>Development</span>
            <span className="count">{p.development.length}</span>
          </button>
          <Tokens p={p} />
          <CrewBoard p={p} />
        </div>

        {/* Duty Officer and Location Area (items 8) */}
        <div className="cell duty"><Section label="Duty Officer" cards={p.duty} /></div>
        <div className="cell locations"><Section label="Location Area" cards={p.locations} /></div>

        {/* Captain and Fleet Area (items 3, 13, 9) */}
        <div className="cell captain">
          <Card
            card={p.captain}
            badges={
              <>
                <span className="badge away" title="Away Teams on the Captain">{p.away_pool} Away</span>
                <button type="button" className="badge log-badge" onClick={() => setViewing("log")} title="View the Captain's Log">
                  Log {p.log.length}
                </button>
              </>
            }
          />
        </div>
        <div className="cell fleet">
          <Section label="Fleet Area" cards={p.fleet} place={(c) => (c.at ? locationNames[c.at] : undefined)} />
        </div>

        {/* Draw deck, Staging Area, Discard pile (items 5, 10) */}
        <div className="cell draw">
          <CardBack label="Draw deck" count={p.draw_count} />
        </div>
        <div className="cell staging">
          {p.staging.length ? <div className="lane">{p.staging.map((c) => <Card key={c.uid} card={c} />)}</div> : <span className="staging-label">Staging Area</span>}
        </div>
        <div className="cell discard">
          {topDiscard ? (
            <button type="button" className="discard-pile" onClick={() => setViewing("discard")} aria-label={`Discard pile: ${p.discard.length} card(s)`}>
              <img src={imageUrl(topDiscard.image)} alt="" />
              <span className="badge">{p.discard.length}</span>
            </button>
          ) : <Slot label="Discard pile" tone="discard" />}
        </div>
      </div>

      {/* Hand (item 14) */}
      <div className="hand" aria-label={you ? "Your hand" : `${p.name}'s hand`}>
        {p.hand
          ? p.hand.map((c, i) => {
              const mid = (p.hand!.length - 1) / 2;
              return <Card key={c.uid} card={c} style={{ transform: `rotate(${(i - mid) * 4}deg) translateY(${Math.abs(i - mid) * 4}px)` }} />;
            })
          : Array.from({ length: p.hand_count }, (_, i) => <div key={i} className="card-back small" aria-hidden />)}
        <span className="muted hand-size">Hand {p.hand_count} / {p.hand_size}</span>
      </div>

      {viewing && <PileViewer title={piles[viewing][0]} cards={[...piles[viewing][1]]} onClose={() => setViewing(null)} />}
    </section>
  );
}
