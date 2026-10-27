import { Link } from "react-router-dom";
import { TutorialView } from "../api";
import { Sheet } from "./Sheet";

/** The coach's text: plain sentences with **bold** for card and game terms. */
function Say({ text }: { text: string }) {
  const parts = text.replace(/\s*\n\s*/g, " ").split(/\*\*(.+?)\*\*/g);
  return <p className="coach-say">{parts.map((p, i) => (i % 2 ? <strong key={i}>{p}</strong> : p))}</p>;
}

/**
 * A tutorial's coach (requirements/24-tutorials.md REQ-TUT-40): what to do or learn now, with Next for explanations,
 * Back (an ordinary undo), Let me play and Leave. A floating panel on a laptop, the top block of the sheet on a phone.
 */
export function Coach({ tutorial, canUndo, busy, onNext, onBack, onFree }: {
  tutorial: TutorialView;
  canUndo: boolean;
  busy: boolean;
  onNext: () => void;
  onBack: () => void;
  onFree: () => void;
}) {
  const step = tutorial.step;
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
      <div className="coach-buttons">
        {canUndo && <button className="secondary" disabled={busy} onClick={onBack}>Back</button>}
        {step.next && <button disabled={busy} onClick={onNext} autoFocus>Next</button>}
        <span className="coach-spacer" />
        <button className="link" disabled={busy} onClick={onFree}>Let me play</button>
        <Link className="link" to="/">Leave tutorial</Link>
      </div>
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
  if (show === "question") return document.querySelector<HTMLElement>(".decision-dock");
  return null;
}
