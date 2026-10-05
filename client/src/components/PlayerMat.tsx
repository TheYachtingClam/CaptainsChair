import { useState } from "react";
import { BotView, CardView, OptionView, PlayerView, RowRef } from "../api";
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
      {!p.bot && (
        <span className="mission-tokens" title="Mission Completion tokens">
          Missions {p.missions_completed.length}/{p.mission_tokens}
        </span>
      )}
    </div>
  );
}

function Tokens({ p }: { p: PlayerView }) {
  return (
    <div className="tokens" aria-label="Resources and actions">
      {!p.bot && <span className="token action" title="Available actions">{p.actions} Action{p.actions === 1 ? "" : "s"}</span>}
      <span className="token glory" title="Glory">{p.resources.glory} Glory</span>
      <span className="token dilithium" title="Dilithium">{p.resources.dilithium} Dilithium</span>
      <span className="token latinum" title="Latinum">{p.resources.latinum} Latinum</span>
    </div>
  );
}

const SIDE_LABEL: Record<string, string> = {
  traits: "Traits",
  exile_traits: "Khan in Exile traits",
  no_duty_officer: "Suits with no Duty Officer",
  with_duty_officer: "Suits with Duty Officer",
};

/** One side of an Automated Command card: hover to enlarge; the rows are also listed for reading. */
function CommandSide({ side, highlight }: { side: BotView["command"][number]; highlight?: number }) {
  const preview = usePreviewHandlers(side.image ?? "", false);
  return (
    <figure className={`command-side ${highlight ? "matched-side" : ""}`}>
      {side.image && <img src={imageUrl(side.image)} alt={SIDE_LABEL[side.side]} {...preview} />}
      <figcaption>{SIDE_LABEL[side.side]}{!side.up && " (while resolving)"}</figcaption>
      <details open={!!highlight || undefined}>
        <summary>Rows</summary>
        <ol>
          {side.rows.map((r) => (
            <li key={r.number} className={[r.attack ? "attack-row" : "", r.number === highlight ? "matched-row" : ""].join(" ")}>
              <strong>{r.matches.join(" / ")}</strong>: {r.text}
            </li>
          ))}
        </ol>
      </details>
    </figure>
  );
}

/** The Bot's two Automated Command cards: TRAITS, and whichever SUITS side is up (REQ-SOLO-32, -91). While watching a
 * Bot turn, the side holding the matched row is shown with that row highlighted, even if the card has flipped since. */
function CommandCards({ bot, highlight }: { bot: BotView; highlight?: RowRef | null }) {
  const suits = bot.command.find((s) => s.side !== "traits" && (highlight ? s.side === highlight.side : s.up))
    ?? bot.command.find((s) => s.side !== "traits" && s.up);
  const shown = [bot.command.find((s) => s.side === "traits"), suits].filter((s): s is NonNullable<typeof s> => !!s);
  return (
    <div className="command-cards" aria-label="Automated Command cards">
      {shown.map((side) => (
        <CommandSide key={side.side} side={side} highlight={highlight?.side === side.side ? highlight.number : undefined} />
      ))}
      {bot.special_rule && <p className="muted special-rule"><strong>Special rule:</strong> {bot.special_rule}</p>}
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

export function PlayerMat({ p, you, active, locationNames, onEndTurn, missions, onMission, highlight }: {
  /** The Bot: the Automated Command row to highlight while watching its turn. */
  highlight?: RowRef | null;
  /** Missions you can complete now (REQ-MS-09: shown, never auto-completed). */
  missions?: OptionView[];
  onMission?: (o: OptionView) => void;
  p: PlayerView;
  you: boolean;
  active: boolean;
  locationNames: Record<string, string>;
  /** Shown on your own mat. Undefined while ending the turn is not possible. */
  onEndTurn?: (() => void) | null;
}) {
  const [viewing, setViewing] = useState<null | "discard" | "development" | "log" | "draw">(null);
  const piles = {
    discard: ["Discard pile", p.discard],
    development: ["Development pile", p.development],
    log: ["Captain's Log", p.log],
    draw: ["Draw deck (face-up, top first)", p.draw ?? []],
  } as const;
  const topDiscard = p.discard[p.discard.length - 1];

  return (
    <section className={`mat ${active ? "active" : ""}`} aria-label={`${p.name}'s play area`}>
      <header className="mat-header">
        <h2>{p.name}{you && " (you)"}</h2>
        {p.bot && <span className="pill bot-pill">Bot · {p.bot.difficulty[0].toUpperCase() + p.bot.difficulty.slice(1)}</span>}
        {p.bot?.ticking_clock && <span className="pill">Ticking Clock</span>}
        {active && <span className="pill">Active player</span>}
        {p.reinforcement && p.reinforcement.length > 0 && (
          <span className="pill" title={p.reinforcement.map((c) => c.name).join(", ")}>Reinforcement pile: {p.reinforcement.length}</span>
        )}
        {(p.boosts?.length ?? 0) > 0 && <span className="pill" title={p.boosts!.join("\n")}>Boosts: {p.boosts!.length}</span>}
        {(p.teams_aside ?? 0) > 0 && (
          <span className="pill" title="They Will Arrive on Tuesday: they return when your Reserve deck empties">
            {p.teams_aside} Away Team(s) set aside
          </span>
        )}
        {p.only_ship && <span className="pill" title="Only Ship in the Quadrant">Only Ship</span>}
      </header>

      <div className="mat-grid">
        {/* Left column: Reserve, Status, Development, tokens, Crew board (items 7, 4, 6, 12, 1) */}
        <div className="mat-left">
          <div className="row top">
            <CardBack label={p.bot ? "Supplement" : "Reserve"} count={p.reserve_count} />
            {p.status.map((c) => <Card key={c.uid} card={c} />)}
          </div>
          {p.bot ? <CommandCards bot={p.bot} highlight={highlight} /> : (
            <button type="button" className="dev-pile" onClick={() => setViewing("development")} disabled={!p.development.length}>
              <span>Development</span>
              <span className="count">{p.development.length}</span>
            </button>
          )}
          <Tokens p={p} />
          <CrewBoard p={p} />
          {missions && missions.length > 0 && onMission && (
            <div className="mission-actions">
              {missions.map((o) => (
                <button key={o.id} className="mission-button" onClick={() => onMission(o)}>
                  {o.irreversible && <span title="Cannot be undone">🔒 </span>}{o.label}
                </button>
              ))}
            </div>
          )}
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
                <button type="button" className="badge log-badge" onClick={(e) => { e.stopPropagation(); setViewing("log"); }} title="View the Captain's Log">
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
          {p.draw && p.draw.length ? (
            <button type="button" className="discard-pile" onClick={() => setViewing("draw")}
              aria-label={`Face-up Draw deck: ${p.draw.length} card(s)`} title="The Draw deck is face-up (Gluonic Distortion)">
              <img src={imageUrl(p.draw[0].image)} alt="" />
              <span className="badge">{p.draw.length}</span>
            </button>
          ) : <CardBack label={p.bot ? "Bot deck" : "Draw deck"} count={p.draw_count} />}
        </div>
        <div className="cell staging">
          {p.staging.length ? (
            <div className="lane">
              {p.staging.map((c) => (c.facedown
                ? <div key={c.uid} className="card-back" aria-label="A facedown Bot card" title="Not resolved yet" />
                : <Card key={c.uid} card={c} />))}
            </div>
          ) : <span className="staging-label">Staging Area</span>}
        </div>
        <div className="cell discard">
          {topDiscard ? (
            <button type="button" className="discard-pile" onClick={() => setViewing("discard")} aria-label={`Discard pile: ${p.discard.length} card(s)`}>
              <img src={imageUrl(topDiscard.image)} alt="" />
              <span className="badge">{p.discard.length}</span>
            </button>
          ) : <Slot label="Discard pile" tone="discard" />}
          {you && (
            <button type="button" className="end-turn" disabled={!onEndTurn} onClick={() => onEndTurn?.()}
              title={onEndTurn ? "End your Action Step and go to Clean-up" : "Available during your Action Step"}>
              End Turn
            </button>
          )}
        </div>
      </div>

      {/* Hand (item 14). The Bot has none (REQ-SOLO-34). */}
      {!p.bot && <div className="hand" aria-label={you ? "Your hand" : `${p.name}'s hand`}>
        {p.hand
          ? p.hand.map((c, i) => {
              const mid = (p.hand!.length - 1) / 2;
              return <Card key={c.uid} card={c} style={{ transform: `rotate(${(i - mid) * 4}deg) translateY(${Math.abs(i - mid) * 4}px)` }} />;
            })
          : Array.from({ length: p.hand_count }, (_, i) => <div key={i} className="card-back small" aria-hidden />)}
        <span className="muted hand-size">Hand {p.hand_count} / {p.hand_size}</span>
      </div>}

      {viewing && <PileViewer title={piles[viewing][0]} cards={[...piles[viewing][1]]} onClose={() => setViewing(null)} />}
    </section>
  );
}
