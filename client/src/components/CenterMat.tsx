import { useState } from "react";
import { CardView, GameStateView } from "../api";
import { Card, CardBack, LocationTokens, PileViewer, imageUrl } from "./Cards";

const SUITS = ["Person", "Cargo", "Ship", "Ally"] as const;

/** The shared table between the players, laid out like the rulebook's central setup (p. 5). */
export function CenterMat({ view }: { view: GameStateView }) {
  const [viewingJunk, setViewingJunk] = useState(false);
  const topJunk = view.junk[view.junk.length - 1];

  const shipsAt = (uid: string, seat: number) =>
    view.players[seat].fleet.filter((s) => s.at === uid).length;

  return (
    <section className="mat center-mat" aria-label="Central play area">
      {/* Encounter deck and Reward pile (item 4) */}
      <div className="center-top">
        <div className="labelled">
          <span className="suit-tag encounter">Encounter</span>
          <CardBack label="Encounter" count={view.encounter_count} />
        </div>
        {view.reward_count > 0 && (
          <div className="labelled">
            <span className="suit-tag reward">Rewards</span>
            <CardBack label="Reward pile" count={view.reward_count} />
          </div>
        )}
      </div>

      {/* Junk space, Market (items 1, 2, 3, 6, 7) and Incident deck (item 5) */}
      <div className="market-row">
        <button type="button" className="junk-space" onClick={() => setViewingJunk(true)}
          aria-label={`Junk pile: ${view.junk.length} card(s)`}>
          {topJunk ? (
            <>
              <img src={imageUrl(topJunk.image)} alt="" />
              <span className="badge">{view.junk.length}</span>
            </>
          ) : <span className="junk-label">Junk space</span>}
        </button>

        <div className="market">
          {SUITS.map((suit) => (
            <div key={suit} className="market-col">
              <CardBack label={suit} count={view.market_deck_counts?.[suit] ?? 0} />
              <span className={`suit-tag ${suit.toLowerCase()}`}>{suit}</span>
              {view.market[suit] ? <Card card={view.market[suit] as CardView} /> : <div className="market-empty">Empty</div>}
            </div>
          ))}
        </div>

        <div className="labelled incident">
          <span className="suit-tag incident">Incident</span>
          <CardBack label="Incident" count={view.incident_count} />
        </div>
      </div>

      {/* Stardate pile (items 11, 13) and Location deck (items 8, 9) */}
      <div className="center-middle">
        <div className="stardate">
          {view.stardate.top ? <Card card={view.stardate.top} /> : <div className="market-empty">No Stardate</div>}
          <div className="stardate-info">
            <span className="glory-token" title="Glory on the Stardate card">{view.stardate.glory}</span>
            <span className="muted">{view.stardate.remaining} Stardate card(s)</span>
            {view.resolution && <span className="pill">Resolution: last turn {view.last_turn}</span>}
          </div>
        </div>
        <div className="labelled">
          <span className="suit-tag location">Location deck</span>
          <CardBack label="Locations" count={view.location_deck_count} />
        </div>
      </div>

      {/* Neutral Zone 1-3 (item 10) */}
      <div className="neutral-zone">
        {view.neutral_zone.map((loc, i) => (
          <div key={loc.uid} className="nz-slot">
            <span className="nz-label">Neutral Zone {i + 1}</span>
            <Card card={loc} tokens={false} />
            <ul className="nz-tokens">
              {view.players.map((p) => {
                const teams = loc.away_teams?.[String(p.seat)] ?? 0;
                const ships = shipsAt(loc.uid, p.seat);
                return (
                  <li key={p.seat} className={loc.secured_by?.includes(p.seat) ? "secured" : ""}>
                    <strong>{p.name}</strong>{" "}
                    {teams || ships ? <LocationTokens loc={loc} seat={p.seat} /> : <span className="muted">no tokens</span>}
                    {loc.secured_by?.includes(p.seat) && <span className="secured-tag">secured</span>}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      {viewingJunk && <PileViewer title="Junk pile" cards={view.junk} onClose={() => setViewingJunk(false)} />}
    </section>
  );
}
