import { useQuery } from "@tanstack/react-query";
import { useAccount } from "../account";
import { BoardSide, Deck, SeatChoice, api, byComplexity, deckLabel } from "../api";

interface Props {
  value: SeatChoice;
  onChange: (value: SeatChoice) => void;
  /** Sets whose decks may be chosen. */
  sets: string[];
  /** Decks already taken by another player. */
  takenDecks?: string[];
}

export function SeatForm({ value, onChange, sets, takenDecks = [] }: Props) {
  const decks = useQuery({ queryKey: ["decks"], queryFn: api.decks });
  const available = (decks.data ?? [])
    .filter((d: Deck) => sets.includes(d.set) && !takenDecks.includes(d.id))
    .sort(byComplexity);
  const selected = available.find((d) => d.id === value.deck_id);
  // The seat takes the account's display name (REQ-USER-40).
  const account = useAccount();

  return (
    <div className="stack">
      {account && <p className="muted">Playing as <strong>{account.display_name}</strong></p>}
      <label>
        Crew deck
        <select value={value.deck_id} onChange={(e) => onChange({ ...value, deck_id: e.target.value })}>
          <option value="">Choose a captain…</option>
          {available.map((d) => (
            <option key={d.id} value={d.id}>
              {deckLabel(d)}
            </option>
          ))}
        </select>
      </label>
      {selected && <p className="muted">{selected.summary}</p>}
      <fieldset>
        <legend>Crew board side</legend>
        {(["basic", "advanced"] as BoardSide[]).map((side) => (
          <label key={side} className="inline">
            <input
              type="radio"
              name="board_side"
              checked={value.board_side === side}
              onChange={() => onChange({ ...value, board_side: side })}
            />
            {side === "basic" ? "Basic (recommended for new players)" : "Advanced"}
          </label>
        ))}
      </fieldset>
    </div>
  );
}
