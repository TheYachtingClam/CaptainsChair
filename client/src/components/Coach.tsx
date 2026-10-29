import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createPortal } from "react-dom";
import { Link } from "react-router-dom";
import { api, TutorialView } from "../api";
import { IconText, RichText } from "./Icons";
import { Sheet } from "./Sheet";

/** The coach's text: plain sentences with **bold** for card and game terms, and icons. */
function Say({ text, className = "coach-say" }: { text: string; className?: string }) {
  return <p className={className}><RichText text={text} /></p>;
}

/** The How cards work sheet behind the coach's "?" (REQ-TUT-43): where cards are, where abilities work, icons, words. */
function GuideSheet({ onClose }: { onClose: () => void }) {
  const guide = useQuery({ queryKey: ["guide", "how-cards-work"], queryFn: () => api.guide("how-cards-work"),
    staleTime: Infinity });
  const close = useRef<HTMLButtonElement>(null);
  useEffect(() => close.current?.focus(), []);
  return (
    <div className="modal-backdrop guide-backdrop" onClick={onClose} onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="card modal guide" role="dialog" aria-labelledby="guide-title" onClick={(e) => e.stopPropagation()}>
        <div className="row between">
          <h2 id="guide-title">{guide.data?.title ?? "How cards work"}</h2>
          <button ref={close} className="secondary" onClick={onClose}>Close</button>
        </div>
        {!guide.data && <p className="muted">Loading…</p>}
        {guide.data?.sections.map((s) => (
          <section key={s.heading}>
            <h3>{s.heading}</h3>
            <dl className="guide-rows">
              {s.rows.map((r) => (
                <div key={r.term}><dt><IconText text={r.term} /></dt><dd><IconText text={r.means} /></dd></div>
              ))}
            </dl>
            {s.note && <p className="muted">{s.note}</p>}
          </section>
        ))}
      </div>
    </div>
  );
}

/**
 * A tutorial's coach (requirements/24-tutorials.md REQ-TUT-40): what to do or learn now, with Next for explanations,
 * Back (an ordinary undo), Let me play and Leave. A floating panel on a laptop, the top block of the sheet on a phone.
 */
export function Coach({ tutorial, canUndo, busy, onNext, onBack, onFree, onTip }: {
  tutorial: TutorialView;
  canUndo: boolean;
  busy: boolean;
  onNext: () => void;
  onBack: () => void;
  onFree: () => void;
  onTip: () => void;
}) {
  const step = tutorial.step;
  const tip = tutorial.tip;
  const [more, setMore] = useState(false);
  const [guide, setGuide] = useState(false);
  useEffect(() => setMore(false), [step?.id]);
  const help = (
    <button className="icon-button coach-help" onClick={() => setGuide(true)} aria-label="How cards work"
      title="How cards work">?</button>
  );
  const sheet = guide && createPortal(<GuideSheet onClose={() => setGuide(false)} />, document.body);
  if (!step && tip) {
    return (
      <Sheet className="coach card" role="region" label="Tutorial tip" live openOn={tip.id} summary="Tutorial tip">
        <div className="coach-head"><strong>Tip</strong><span className="muted">{tutorial.title}</span></div>
        <Say text={tip.say} />
        <div className="coach-buttons">
          {tip.link && <Link className="button" to={tip.link.to}>{tip.link.label}</Link>}
          <span className="coach-spacer" />
          {help}
          <button className={tip.link ? "secondary" : undefined} disabled={busy} onClick={onTip}>Got it</button>
        </div>
        {sheet}
      </Sheet>
    );
  }
  if (!step) return null;
  const done = Math.round((tutorial.index / tutorial.total) * 100);
  return (
    <Sheet className="coach card" role="region" label={tutorial.title} live openOn={step.id}
      summary={`Tutorial · step ${tutorial.index + 1} of ${tutorial.total}`}>
      <div className="coach-head">
        <strong>{tutorial.title}</strong>
        <span className="muted">Step {tutorial.index + 1} of {tutorial.total}</span>
      </div>
      <div className="coach-progress" aria-hidden><span style={{ width: `${done}%` }} /></div>
      <Say text={step.say} />
      {step.more && more && <Say className="coach-say coach-more" text={step.more} />}
      <div className="coach-buttons">
        {step.more && (
          <button className="link" onClick={() => setMore(!more)} aria-expanded={more}>{more ? "Less" : "More"}</button>
        )}
        {canUndo && <button className="secondary" disabled={busy} onClick={onBack}>Back</button>}
        {step.next && <button disabled={busy} onClick={onNext} autoFocus>Next</button>}
        <span className="coach-spacer" />
        {help}
        <button className="link" disabled={busy} onClick={onFree}>Let me play</button>
        <Link className="link" to="/">Leave tutorial</Link>
      </div>
      {sheet}
    </Sheet>
  );
}

/** The element a step points at (REQ-TUT-21): your own mat first, then the rest of the table. */
export function coachTarget(show: string | null): HTMLElement | null {
  if (!show) return null;
  const [kind, ...rest] = show.split(":");
  const name = rest.join(":");
  const first = (selector: string) =>
    document.querySelector<HTMLElement>(`.mat.mine ${selector}`) ?? document.querySelector<HTMLElement>(selector);
  if (kind === "card") return first(`.gcard[data-card-id="${name}"]`);
  if (kind === "zone") return first(`[data-tutorial="${name === "log" ? "captain" : name}"]`);
  if (kind === "button") return first(`[data-tutorial="${name}"]`);
  if (kind === "bot") return document.querySelector<HTMLElement>(`.mat:not(.mine) [data-tutorial="${name}"]`);
  if (show === "question") return document.querySelector<HTMLElement>(".decision-dock");
  if (show === "bot-panel") return document.querySelector<HTMLElement>(".bot-playback");
  if (show === "bot-row") return document.querySelector<HTMLElement>(".matched-row") ?? document.querySelector(".bot-playback");
  return null;
}
