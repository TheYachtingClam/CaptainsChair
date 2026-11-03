import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Game, SeatChoice, api, setsFor } from "../api";
import { SeatForm } from "./SeatForm";

/**
 * Choose a Crew and take a game's open seat: an open game's Join, or a challenge's Accept (REQ-USER-51), which can
 * also be declined (REQ-USER-53). Both go to the game afterwards.
 */
export function JoinForm({ game, onCancel }: { game: Game; onCancel?: () => void }) {
  const boxes = useQuery({ queryKey: ["boxes"], queryFn: api.boxes });
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [seat, setSeat] = useState<SeatChoice>({ deck_id: "", board_side: "basic" });
  const challenge = !!game.challenge;
  const done = () => {
    queryClient.invalidateQueries({ queryKey: ["games"] });
    queryClient.invalidateQueries({ queryKey: ["my-games"] });
    queryClient.invalidateQueries({ queryKey: ["game", game.id] });
  };
  const join = useMutation({
    mutationFn: () => api.joinGame(game.id, seat),
    onSuccess: () => {
      done();
      navigate(`/games/${game.id}`);
    },
  });
  const decline = useMutation({
    mutationFn: () => api.declineGame(game.id),
    onSuccess: () => {
      done();
      navigate("/", { replace: true });
    },
  });
  const error = join.error ?? decline.error;
  const busy = join.isPending || decline.isPending;

  return (
    <div className="stack">
      <SeatForm
        value={seat}
        onChange={setSeat}
        sets={setsFor(boxes.data, game.box, game.expansions)}
        takenDecks={game.seats.map((s) => s.deck_id)}
      />
      {error && <p className="error" role="alert">{error.message}</p>}
      <div className="row">
        <button disabled={busy || !seat.deck_id} onClick={() => join.mutate()}>
          {challenge ? "Accept and start" : "Take the seat"}
        </button>
        {challenge && <button className="secondary" disabled={busy} onClick={() => decline.mutate()}>Decline</button>}
        {onCancel && <button className="link" onClick={onCancel}>Cancel</button>}
      </div>
    </div>
  );
}
