import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { CAMPAIGN_MODES, CampaignMode, Deck, api, campaignApi, saveCampaignToken } from "../api";

/** Start a Five-Year Mission (REQ-CAMP-02): your Crew deck and a campaign mode. You start as an Ensign. */
export function NewCampaign() {
  const navigate = useNavigate();
  const decks = useQuery({ queryKey: ["decks"], queryFn: api.decks });
  const expansions = useQuery({ queryKey: ["expansions"], queryFn: api.expansions });
  const [name, setName] = useState("");
  const [deck, setDeck] = useState("");
  const [mode, setMode] = useState<CampaignMode>("set_phasers_to_stun");
  const [chosen, setChosen] = useState<string[]>([]);
  const [promos, setPromos] = useState(false);
  const [challenges, setChallenges] = useState<string[]>([]);
  // REQ-CAMP-41: only the challenges this Crew deck can take are shown.
  const available = useQuery({ queryKey: ["challenges", deck], queryFn: () => campaignApi.challenges(deck), enabled: !!deck });
  const sets = ["to_boldly_go", ...chosen];
  const crews = (decks.data ?? []).filter((d: Deck) => sets.includes(d.set)).sort((a, b) => a.complexity - b.complexity);

  const create = useMutation({
    mutationFn: () => campaignApi.create({
      display_name: name.trim(), deck_id: deck, mode, expansions: chosen, promos,
      challenges: challenges.filter((c) => available.data?.some((a) => a.id === c)),
    }),
    onSuccess: ({ campaign, token }) => {
      saveCampaignToken(campaign.id, token);
      navigate(`/campaigns/${campaign.id}?key=${encodeURIComponent(token)}`);
    },
  });

  function submit(e: FormEvent) {
    e.preventDefault();
    create.mutate();
  }

  return (
    <main className="page">
      <h1>New Five-Year Mission</h1>
      <p className="muted">
        A campaign of up to 10 solo games against the Bots. Each win promotes you; after every assignment you earn an
        upgrade for your Crew deck. Reach Admiral to win.
      </p>
      <form className="card stack" onSubmit={submit}>
        <label>
          Your name
          <input maxLength={40} value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <fieldset>
          <legend>Expansions</legend>
          {Object.entries(expansions.data ?? {}).map(([id, label]) => (
            <label key={id} className="inline">
              <input type="checkbox" checked={chosen.includes(id)}
                onChange={() => { setChosen((c) => (c.includes(id) ? c.filter((x) => x !== id) : [...c, id])); setDeck(""); }} />
              {label}
            </label>
          ))}
          <label className="inline">
            <input type="checkbox" checked={promos} onChange={(e) => setPromos(e.target.checked)} />
            Promo cards
          </label>
        </fieldset>
        <label>
          Your Crew deck
          <select value={deck} onChange={(e) => setDeck(e.target.value)}>
            <option value="">Choose a captain…</option>
            {crews.map((d) => (
              <option key={d.id} value={d.id}>{d.captain} ({d.faction}) – complexity {d.complexity}/10</option>
            ))}
          </select>
        </label>
        <fieldset>
          <legend>Campaign mode</legend>
          {CAMPAIGN_MODES.map(([id, label]) => (
            <label key={id} className="inline">
              <input type="radio" name="mode" checked={mode === id} onChange={() => setMode(id)} />
              {label}
            </label>
          ))}
        </fieldset>
        {deck && (
          <fieldset>
            <legend>Challenges (optional)</legend>
            {(available.data ?? []).map((c) => (
              <label key={c.id} className="inline challenge">
                <input type="checkbox" checked={challenges.includes(c.id)}
                  onChange={() => setChallenges((cs) => (cs.includes(c.id) ? cs.filter((x) => x !== c.id) : [...cs, c.id]))} />
                <span><strong>{c.name}</strong> <span className="muted">{c.rule}</span></span>
              </label>
            ))}
          </fieldset>
        )}
        {create.error && <p className="error" role="alert">{create.error.message}</p>}
        <button type="submit" disabled={create.isPending || !name.trim() || !deck}>Start the campaign</button>
      </form>
    </main>
  );
}
