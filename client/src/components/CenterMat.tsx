import { useState } from "react";
import { CardView, GameStateView } from "../api";
import { Card, CardBack, LocationTokens, PileViewer, awayTokenImage, imageUrl } from "./Cards";
import { usePhone } from "./Sheet";

const SUITS = ["Person", "Cargo", "Ship", "Ally"] as const;

/** The shared table between the players, laid out like the rulebook's central setup (p. 5). */
export function CenterMat({ view }: { view: GameStateView }) {
  const [viewingJunk, setViewingJunk] = useState(false);
  const topJunk = view.junk[view.junk.length - 1];

  const phone = usePhone();

  if (phone) return <PhoneCentre view={view} />;

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

        <div className="market" data-tutorial="market">
          {SUITS.map((suit) => (
            <div key={suit} className="market-col" data-tutorial={`market:${suit}`}>
              <CardBack label={suit} count={view.market_deck_counts?.[suit] ?? 0} />
              <span className={`suit-tag ${suit.toLowerCase()}`}>{suit}</span>
              {view.market[suit] ? <Card card={view.market[suit] as CardView} /> : <div className="market-empty">Empty</div>}
            </div>
          ))}
        </div>

        <div className="labelled incident" data-tutorial="incident">
          <span className="suit-tag incident">Incident</span>
          <CardBack label="Incident" count={view.incident_count} />
        </div>
      </div>

      {/* Stardate pile (items 11, 13) and Location deck (items 8, 9) */}
      <div className="center-middle">
        <div className="stardate" data-tutorial="stardate">
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
      <NeutralZone view={view} compact={phone} />

      {viewingJunk && <PileViewer title="Junk pile" cards={view.junk} onClose={() => setViewingJunk(false)} />}
    </section>
  );
}

/** The three neutral Locations with each player's tokens there. `compact` is the phone's form (REQ-CLI-32): the three
 *  side by side, each player's tokens as icons without their name, and a secured Location's line in green. It is
 *  shown on the You tab too, for planning your turn. In Cadet Training the practice opponent's Away Team, always one
 *  at every neutral Location (REQ-CTM-12), is shown too, since securing has to beat it. */
const VIRTUAL_TEAM = "The practice opponent always has 1 Away Team at every neutral Location. "
  + "To secure one you need 3+ tokens there, 2 more than its 1.";

export function NeutralZone({ view, compact = false }: { view: GameStateView; compact?: boolean }) {
  const shipsAt = (uid: string, seat: number) => view.players[seat].fleet.filter((s) => s.at === uid).length;
  return (
    <div className={`neutral-zone ${compact ? "compact" : ""}`} data-tutorial="neutral">
      {view.neutral_zone.map((loc, i) => (
        <div key={loc.uid} className="nz-slot">
          <span className="nz-label">{compact ? `NZ ${i + 1}` : `Neutral Zone ${i + 1}`}</span>
          <Card card={loc} tokens={false} />
          <ul className="nz-tokens">
            {view.players.map((p) => {
              const teams = loc.away_teams?.[String(p.seat)] ?? 0;
              const ships = shipsAt(loc.uid, p.seat);
              const secured = loc.secured_by?.includes(p.seat);
              return (
                <li key={p.seat} className={secured ? "secured" : ""} title={`${p.name}${secured ? ": secured" : ""}`}>
                  {!compact && <><strong>{p.name}</strong>{" "}</>}
                  {teams || ships ? <LocationTokens loc={loc} seat={p.seat} compact={compact} />
                    : <span className="muted">{compact ? "–" : "no tokens"}</span>}
                  {secured && <span className="secured-tag">{compact ? "✓" : "secured"}</span>}
                </li>
              );
            })}
            {view.mode === "cadet" && (
              <li className="virtual" title={VIRTUAL_TEAM}>
                {!compact && <><strong>Practice opponent</strong> <span className="muted">always</span>{" "}</>}
                <span className={`tokens ${compact ? "compact" : ""}`}><span className="away-token">
                  <img src={imageUrl(awayTokenImage(1))} alt="The practice opponent's Away Team" />
                </span></span>
              </li>
            )}
          </ul>
        </div>
      ))}
      {view.mode === "cadet" && <p className="nz-virtual muted">{VIRTUAL_TEAM}</p>}
    </div>
  );
}

/** A deck shown only by its count, on a phone (REQ-CLI-38). */
function DeckCount({ kind, label, count }: { kind: string; label: string; count: number }) {
  return (
    <div className={`deck-count ${kind}`} aria-label={`${label}: ${count} card(s)`}>
      <span>{label}</span>
      <strong>{count}</strong>
    </div>
  );
}

/** The centre on a phone (REQ-CLI-38): the Encounter, Incident and Location decks as counts in one row; the Market
 *  four across, each suit's deck count above its face-up card, as on the table; then the Junk and the Stardate side by
 *  side, and the Neutral Zone. */
function PhoneCentre({ view }: { view: GameStateView }) {
  const [viewingJunk, setViewingJunk] = useState(false);
  const topJunk = view.junk[view.junk.length - 1];
  return (
    <section className="mat center-mat phone-centre" aria-label="Central play area">
      <div className="deck-counts">
        <DeckCount kind="encounter" label="Encounter" count={view.encounter_count} />
        <div data-tutorial="incident"><DeckCount kind="incident" label="Incident" count={view.incident_count} /></div>
        <DeckCount kind="location" label="Locations" count={view.location_deck_count} />
        {view.reward_count > 0 && <DeckCount kind="reward" label="Rewards" count={view.reward_count} />}
      </div>

      <div className="market phone-market" data-tutorial="market">
        {SUITS.map((suit) => (
          <div key={suit} className="market-col" data-tutorial={`market:${suit}`}>
            <DeckCount kind={suit.toLowerCase()} label={suit} count={view.market_deck_counts?.[suit] ?? 0} />
            {view.market[suit] ? <Card card={view.market[suit] as CardView} /> : <div className="market-empty">Empty</div>}
          </div>
        ))}
      </div>

      <div className="phone-centre-row">
        <button type="button" className="junk-space" onClick={() => setViewingJunk(true)}
          aria-label={`Junk pile: ${view.junk.length} card(s)`}>
          {topJunk ? (
            <>
              <img src={imageUrl(topJunk.image)} alt="" />
              <span className="badge">{view.junk.length}</span>
            </>
          ) : <span className="junk-label">Junk space</span>}
        </button>
        <div className="stardate" data-tutorial="stardate">
          {view.stardate.top ? <Card card={view.stardate.top} /> : <div className="market-empty">No Stardate</div>}
          <div className="stardate-info">
            <span className="glory-token" title="Glory on the Stardate card">{view.stardate.glory}</span>
            <span className="muted">{view.stardate.remaining} Stardate card(s)</span>
            {view.resolution && <span className="pill">Resolution: last turn {view.last_turn}</span>}
          </div>
        </div>
      </div>

      <NeutralZone view={view} compact />

      {viewingJunk && <PileViewer title="Junk pile" cards={view.junk} onClose={() => setViewingJunk(false)} />}
    </section>
  );
}
