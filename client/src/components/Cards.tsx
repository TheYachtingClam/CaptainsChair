import { createContext, useContext, useLayoutEffect, useRef, useState } from "react";
import { CardView } from "../api";

export type Preview = { image: string; beamed?: CardView[]; wide?: boolean; x: number; y: number } | null;
export const PreviewContext = createContext<(p: Preview) => void>(() => {});

const GAP = 18; // distance between the cursor and the preview
const MARGIN = 8; // keep this far from the window edges

export const imageUrl = (image: string) => `/api/content/images/${image}`;

/** Large version of the hovered or focused card, placed next to the cursor and kept on screen. */
export function CardPreview({ preview }: { preview: Preview }) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!preview || !el) return;
    const { width, height } = el.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    let left = preview.x + GAP;
    if (left + width > vw - MARGIN) left = preview.x - GAP - width;
    left = Math.max(MARGIN, Math.min(left, vw - width - MARGIN));
    const top = Math.max(MARGIN, Math.min(preview.y - height / 2, vh - height - MARGIN));
    setPos({ left, top });
  }, [preview]);

  if (!preview) return null;
  return (
    <div ref={ref} className={`card-preview ${preview.wide ? "wide" : ""}`} aria-hidden
      style={pos ? { left: pos.left, top: pos.top } : { left: -9999, top: 0 }}>
      <img src={imageUrl(preview.image)} alt="" />
      {preview.beamed && preview.beamed.length > 0 && (
        <div className="preview-beamed">
          <span className="muted">Beamed here:</span>
          {preview.beamed.map((b) => <img key={b.uid} src={imageUrl(b.image)} alt="" />)}
        </div>
      )}
    </div>
  );
}

/** A faceup card on the table. Hover or focus shows the large preview. */
export function Card({ card, badges, style }: { card: CardView; badges?: React.ReactNode; style?: React.CSSProperties }) {
  const setPreview = useContext(PreviewContext);
  const glory = card.resources?.glory;
  const show = (x: number, y: number) => setPreview({ image: card.image, beamed: card.beamed, x, y });
  return (
    <div
      className={`gcard ${card.exhausted ? "exhausted" : ""}`}
      style={style}
      title={card.name}
      tabIndex={0}
      onMouseEnter={(e) => show(e.clientX, e.clientY)}
      onMouseMove={(e) => show(e.clientX, e.clientY)}
      onMouseLeave={() => setPreview(null)}
      onFocus={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        show(r.right, r.top + r.height / 2);
      }}
      onBlur={() => setPreview(null)}
    >
      <img src={imageUrl(card.image)} alt={card.name} loading="lazy" />
      {glory ? <span className="badge">{glory} Glory</span> : null}
      {card.away_teams && Object.keys(card.away_teams).length > 0 && (
        <span className="badge left">
          {Object.entries(card.away_teams).map(([seat, n]) => `P${Number(seat) + 1}:${n}`).join(" ")}
        </span>
      )}
      {card.beamed && card.beamed.length > 0 && <span className="badge bottom-left">+{card.beamed.length} beamed</span>}
      {badges}
    </div>
  );
}

/** Hover and focus handlers that show any image in the large preview. */
export function usePreviewHandlers(image: string, wide = false) {
  const setPreview = useContext(PreviewContext);
  const show = (x: number, y: number) => setPreview({ image, wide, x, y });
  return {
    tabIndex: 0,
    onMouseEnter: (e: React.MouseEvent) => show(e.clientX, e.clientY),
    onMouseMove: (e: React.MouseEvent) => show(e.clientX, e.clientY),
    onMouseLeave: () => setPreview(null),
    onFocus: (e: React.FocusEvent<HTMLElement>) => {
      const r = e.currentTarget.getBoundingClientRect();
      show(r.right, r.top + r.height / 2);
    },
    onBlur: () => setPreview(null),
  };
}

/** A facedown deck: card back with its label and count. */
export function CardBack({ label, count, onClick }: { label: string; count: number; onClick?: () => void }) {
  return (
    <button type="button" className={`card-back ${count === 0 ? "empty" : ""}`} onClick={onClick} disabled={!onClick}
      aria-label={`${label}: ${count} card(s)`}>
      <span className="card-back-label">{label}</span>
      <span className="card-back-count">{count}</span>
    </button>
  );
}

/** An empty table space, drawn as a dashed placeholder like the rulebook's play-area diagram. */
export function Slot({ label, tone }: { label: string; tone: "duty" | "status" | "location" | "fleet" | "discard" }) {
  return <div className={`slot slot-${tone}`}><span>{label}</span></div>;
}
