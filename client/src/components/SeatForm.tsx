import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
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
      {selected && <TutorialHint deck={selected} />}
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

/** "New to Khan? Try the tutorial" beside a Captain that has one (plans/tutorials-roadmap.md F5). */
function TutorialHint({ deck }: { deck: Deck }) {
  const tutorials = useQuery({ queryKey: ["tutorials"], queryFn: api.tutorials });
  const navigate = useNavigate();
  const start = useMutation({
    mutationFn: (id: string) => api.startTutorial(id),
    onSuccess: (grant) => navigate(`/games/${grant.game.id}`),
  });
  const tutorial = tutorials.data?.find((t) => t.captain === deck.id);
  if (!tutorial) return null;
  return (
    <p className="muted">
      New to {deck.captain}?{" "}
      <button type="button" className="link" disabled={start.isPending} onClick={() => start.mutate(tutorial.id)}>
        Try the tutorial
      </button>
    </p>
  );
}
