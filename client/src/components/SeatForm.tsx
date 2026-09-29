import { useQuery } from "@tanstack/react-query";
import { BoardSide, Deck, SeatChoice, api } from "../api";

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
    .sort((a, b) => a.complexity - b.complexity);
  const selected = available.find((d) => d.id === value.deck_id);

  return (
    <div className="stack">
      <label>
        Your name
        <input
          maxLength={40}
          value={value.display_name}
          onChange={(e) => onChange({ ...value, display_name: e.target.value })}
        />
      </label>
      <label>
        Crew deck
        <select value={value.deck_id} onChange={(e) => onChange({ ...value, deck_id: e.target.value })}>
          <option value="">Choose a captain…</option>
          {available.map((d) => (
            <option key={d.id} value={d.id}>
              {d.captain} ({d.faction}) – complexity {d.complexity}/10
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
