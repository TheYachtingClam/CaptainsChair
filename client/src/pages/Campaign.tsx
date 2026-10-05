import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { BoardSide, CampaignCard, campaignApi, loadCampaignToken, saveCampaignToken, saveSeatToken } from "../api";
import { imageUrl } from "../components/Cards";

const title = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

function CardTile({ card, onPick, disabled }: { card: CampaignCard; onPick?: () => void; disabled?: boolean }) {
  const body = (
    <>
      <img src={imageUrl(card.image)} alt={card.name} />
      <span>{card.name}</span>
    </>
  );
  return onPick
    ? <button type="button" className="campaign-card pickable" onClick={onPick} disabled={disabled}>{body}</button>
    : <div className="campaign-card">{body}</div>;
}

/** A Five-Year Mission: the log, rank, Reinforcement pile, the next assignment, upgrades and the final review
 * (REQ-CAMP-53). Reached by its secret link (`?key=`), which this browser then remembers. */
export function Campaign() {
  const { campaignId = "" } = useParams();
  const [search] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const key = search.get("key");
  if (key && loadCampaignToken(campaignId) !== key) saveCampaignToken(campaignId, key);
  const campaign = useQuery({ queryKey: ["campaign", campaignId], queryFn: () => campaignApi.get(campaignId), retry: false });
  const [bot, setBot] = useState("");
  const [side, setSide] = useState<BoardSide>("basic");
  const [copied, setCopied] = useState(false);

  const start = useMutation({
    mutationFn: () => campaignApi.start(campaignId, { bot_deck_id: bot || null, board_side: side }),
    onSuccess: (r) => {
      saveSeatToken(r.game_id, r.seat_token);
      navigate(`/games/${r.game_id}`);
    },
  });
  const upgrade = useMutation({
    mutationFn: (cardId: string | null) => campaignApi.upgrade(campaignId, cardId),
    onSuccess: (view) => queryClient.setQueryData(["campaign", campaignId], view),
  });
  useEffect(() => setBot(""), [campaign.data?.assignments.length]);

  if (campaign.isPending) return <main className="page">Loading the campaign…</main>;
  if (campaign.isError) {
    return (
      <main className="page">
        <p className="error">{campaign.error.message}</p>
        <p className="muted">A campaign opens only from its own link. <Link to="/">Back to the lobby</Link></p>
      </main>
    );
  }
  const c = campaign.data;
  const token = loadCampaignToken(campaignId);
  const link = `${window.location.origin}/campaigns/${c.id}?key=${encodeURIComponent(token ?? "")}`;

  return (
    <main className="page stack">
      <div className="row between">
        <h1>Five-Year Mission: {c.display_name}</h1>
        <Link to="/">Lobby</Link>
      </div>
      <p>
        <strong>{title(c.rank)}</strong> · {c.captain}'s crew · {c.mode_name} · {c.assignments.length} of 10 assignments
        {c.next_difficulty && c.phase === "start" && ` · next Bot: ${title(c.next_difficulty)}`}
      </p>
      <p className="muted">
        This campaign's link is its key. Bookmark it to continue from another browser.{" "}
        <button className="link" onClick={() => { navigator.clipboard?.writeText(link); setCopied(true); }}>
          {copied ? "Copied" : "Copy the link"}
        </button>
      </p>

      {c.phase === "finished" && (
        <section className="card">
          <h2>Performance review</h2>
          <p>Final rank: <strong>{title(c.rank)}</strong> after {c.assignments.length} assignments.</p>
          <p className="evaluation">{c.evaluation}</p>
        </section>
      )}

      {c.phase === "start" && (
        <section className="card stack">
          <h2>Assignment {c.assignments.length + 1}</h2>
          <label>
            Opponent
            <select value={bot} onChange={(e) => setBot(e.target.value)}>
              <option value="">Pick one at random</option>
              {c.opponents.map((o) => <option key={o.deck_id} value={o.deck_id}>{o.captain} Bot</option>)}
            </select>
          </label>
          <fieldset>
            <legend>Your Crew board side</legend>
            {(["basic", "advanced"] as BoardSide[]).map((s) => (
              <label key={s} className="inline">
                <input type="radio" name="side" checked={side === s} onChange={() => setSide(s)} />
                {title(s)}
              </label>
            ))}
          </fieldset>
          {start.error && <p className="error">{start.error.message}</p>}
          <button disabled={start.isPending} onClick={() => start.mutate()}>Start the assignment</button>
        </section>
      )}

      {c.phase === "playing" && (
        <section className="card">
          <h2>Assignment {c.assignments.length} in progress</h2>
          <Link className="button" to={`/games/${c.game_id}`}>Continue the game</Link>
        </section>
      )}

      {c.phase === "upgrade" && c.upgrade && (
        <section className="card stack">
          <h2>{c.upgrade.won ? "Success! You are promoted." : "Assignment failed."} Choose an upgrade</h2>
          <p>
            Add a card you had in that game to your Reinforcement pile
            {c.upgrade.restriction && <> (this Bot allows: <strong>{c.upgrade.restriction}</strong>)</>}.
          </p>
          {c.upgrade.options.length > 0 ? (
            <div className="campaign-cards">
              {c.upgrade.options.map((card) => (
                <CardTile key={card.id} card={card} disabled={upgrade.isPending} onPick={() => upgrade.mutate(card.id)} />
              ))}
            </div>
          ) : (
            <>
              <p className="muted">
                You had no matching card. The alternative bonuses (option B) are not available yet, so this upgrade is
                skipped.
              </p>
              <button disabled={upgrade.isPending} onClick={() => upgrade.mutate(null)}>Continue</button>
            </>
          )}
          {upgrade.error && <p className="error">{upgrade.error.message}</p>}
        </section>
      )}

      <section className="card">
        <h2>Reinforcement pile</h2>
        {c.reinforcement.length === 0 ? (
          <p className="muted">Empty. Cards added here come back in every later game through the Reinforce card.</p>
        ) : (
          <div className="campaign-cards">{c.reinforcement.map((card, i) => <CardTile key={`${card.id}-${i}`} card={card} />)}</div>
        )}
      </section>

      <section className="card">
        <h2>Campaign log</h2>
        {c.assignments.length === 0 ? <p className="muted">No assignments yet.</p> : (
          <table className="campaign-log">
            <thead>
              <tr><th>#</th><th>Date</th><th>Your rank</th><th>Bot</th><th>Difficulty</th><th>Scores</th><th>Result</th><th>Upgrade</th></tr>
            </thead>
            <tbody>
              {c.assignments.map((a) => (
                <tr key={a.number}>
                  <td>{a.number}</td>
                  <td>{a.date}</td>
                  <td>{title(a.rank)}</td>
                  <td>{a.bot_captain}</td>
                  <td>{title(a.difficulty)}</td>
                  <td>{a.scores ? Object.entries(a.scores).map(([n, v]) => `${n} ${v}`).join(" · ") : "—"}</td>
                  <td>{a.outcome === "win" ? "Success" : a.outcome === "loss" ? "Failure" : <Link to={`/games/${a.game_id}`}>In progress</Link>}</td>
                  <td>{a.upgrade?.card ? c.reinforcement.find((r) => r.id === a.upgrade?.card)?.name ?? a.upgrade.card : a.upgrade ? "—" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
