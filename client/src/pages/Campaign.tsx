import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { BoardSide, CampaignBonus, CampaignCard, CampaignView, campaignApi, loadCampaignToken, saveCampaignToken, saveSeatToken } from "../api";
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
  const [drop, setDrop] = useState<"dilithium" | "latinum">("dilithium");
  const [copied, setCopied] = useState(false);

  const start = useMutation({
    mutationFn: () => campaignApi.start(campaignId, { bot_deck_id: bot || null, board_side: side, drop: campaign.data?.choose_resource ? drop : null }),
    onSuccess: (r) => {
      saveSeatToken(r.game_id, r.seat_token);
      navigate(`/games/${r.game_id}`);
    },
  });
  const upgrade = useMutation({
    mutationFn: (choice: { card_id?: string; bonus?: string; cards?: string[] }) => campaignApi.upgrade(campaignId, choice),
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
      {(c.challenges.length > 0 || c.boosts.length > 0) && (
        <section className="card">
          {c.challenges.length > 0 && (
            <>
              <h2>Challenges</h2>
              <ul className="list">{c.challenges.map((ch) => <li key={ch.id}><strong>{ch.name}</strong>: {ch.rule}</li>)}</ul>
            </>
          )}
          {c.boosts.length > 0 && (
            <>
              <h2>Boosts</h2>
              <p className="muted">These resolve at the start of every game in this campaign.</p>
              <ul className="list">{c.boosts.map((b, i) => <li key={i}>{b}</li>)}</ul>
            </>
          )}
        </section>
      )}
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
          {c.choose_resource && (
            <fieldset>
              <legend>Live Long and Prosper: start this game without</legend>
              {(["dilithium", "latinum"] as const).map((r) => (
                <label key={r} className="inline">
                  <input type="radio" name="drop" checked={drop === r} onChange={() => setDrop(r)} />
                  {title(r)}
                </label>
              ))}
            </fieldset>
          )}
          {c.next_notes.length > 0 && (
            <ul className="list muted">{c.next_notes.filter((n) => !(c.choose_resource && n.includes("you choose"))).map((n) => <li key={n}>{n}</li>)}</ul>
          )}
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
        <UpgradeChoice c={c} pending={upgrade.isPending} error={upgrade.error?.message}
          onChoose={(choice) => upgrade.mutate(choice)} />
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
                  <td>{upgradeLabel(c, a.upgrade)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

const cardName = (c: CampaignView, id: string) => c.reinforcement.find((r) => r.id === id)?.name ?? id;

function upgradeLabel(c: CampaignView, u: CampaignView["assignments"][number]["upgrade"]): string {
  if (!u) return "";
  if (u.option === "A" && u.card) return cardName(c, u.card);
  if (u.option === "B" && u.cards?.length) return `Reinforce: ${u.cards.map((id) => cardName(c, id)).join(", ")}`;
  if (u.option === "B") return (u.text ?? "").replace(/^BOOST: /, "Boost: ");
  return "—";
}

type Choice = { card_id?: string; bonus?: string; cards?: string[] };

/** REQ-CAMP-25: option A (a matching Market card you had) or option B (one of the Bot's bonuses). */
function UpgradeChoice({ c, pending, error, onChoose }: {
  c: CampaignView; pending: boolean; error?: string; onChoose: (choice: Choice) => void;
}) {
  const up = c.upgrade!;
  const [picking, setPicking] = useState<CampaignBonus | null>(null);
  const [picked, setPicked] = useState<string[]>([]);
  const nothing = up.options.length === 0 && up.bonuses.every((b) => b.kind === "reinforce" && !b.pools?.some((p) => p.length));

  function toggle(bonus: CampaignBonus, pool: number, id: string) {
    setPicked((now) => {
      if (now.includes(id)) return now.filter((x) => x !== id);
      if (!bonus.each) return [id];
      const others = bonus.pools![pool].map((card) => card.id);
      return [...now.filter((x) => !others.includes(x)), id]; // one from each pool at most
    });
  }

  return (
    <section className="card stack">
      <h2>{up.won ? "Success! You are promoted." : "Assignment failed."} Choose one upgrade</h2>
      <h3>A: Reinforce a Market card you had</h3>
      <p>Allowed after facing this Bot: <strong>{up.restriction ?? "nothing"}</strong>.</p>
      {up.options.length > 0 ? (
        <div className="campaign-cards">
          {up.options.map((card) => (
            <CardTile key={card.id} card={card} disabled={pending} onPick={() => onChoose({ card_id: card.id })} />
          ))}
        </div>
      ) : <p className="muted">You had no matching card.</p>}
      <h3>B: An alternative bonus</h3>
      {up.bonuses.length === 0 ? (
        <p className="muted">{up.won && c.challenges.some((ch) => ch.id === "rules_of_acquisition")
          ? "Rules of Acquisition: no alternative bonus after a success." : "No bonus is available."}</p>
      ) : (
        <ul className="bonus-list">
          {up.bonuses.map((b) => (
            <li key={b.key}>
              <span>{b.text}</span>
              {b.kind === "boost" ? (
                <button disabled={pending} onClick={() => onChoose({ bonus: b.key })}>Take this Boost</button>
              ) : b.pools?.some((p) => p.length) ? (
                <button className="secondary" disabled={pending} onClick={() => { setPicking(b); setPicked([]); }}>
                  Choose cards…
                </button>
              ) : <span className="muted">(no card qualifies)</span>}
            </li>
          ))}
        </ul>
      )}
      {picking && (
        <div className="stack">
          <p>
            {picking.each ? "Choose up to one card from each group." : "Choose one card."} It moves from your deck to your
            Reinforcement pile for every later game.
          </p>
          {picking.pools!.map((pool, i) => (
            <div key={i}>
              {picking.pools!.length > 1 && <h4>{i === 0 ? "Available cards" : "Reserve deck"}</h4>}
              <div className="campaign-cards">
                {pool.map((card) => (
                  <button type="button" key={card.id} className={`campaign-card pickable ${picked.includes(card.id) ? "picked" : ""}`}
                    aria-pressed={picked.includes(card.id)} onClick={() => toggle(picking, i, card.id)}>
                    <img src={imageUrl(card.image)} alt={card.name} />
                    <span>{card.name}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
          <div className="row">
            <button disabled={pending || picked.length === 0} onClick={() => onChoose({ bonus: picking.key, cards: picked })}>
              Reinforce {picked.length} card(s)
            </button>
            <button className="secondary" onClick={() => setPicking(null)}>Cancel</button>
          </div>
        </div>
      )}
      {nothing && (
        <>
          <p className="muted">Nothing can be chosen this time, so there is no upgrade.</p>
          <button disabled={pending} onClick={() => onChoose({})}>Continue</button>
        </>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
