import { createContext, useContext, useLayoutEffect, useRef, useState } from "react";
import { CardView, OptionView } from "../api";

export type Preview = { image: string; beamed?: CardView[]; wide?: boolean; x: number; y: number } | null;
export const PreviewContext = createContext<(p: Preview) => void>(() => {});
/** The selected card, and a toggle to select or deselect a card at a position on screen. */
export type Selection = { card: CardView; rect: { left: number; right: number; top: number; bottom: number } } | null;
export const SelectContext = createContext<{ selected: string | null; toggle: (s: Selection) => void }>({
  selected: null,
  toggle: () => {},
});

/** Uids of cards the viewing player can play or activate right now. */
export const PlayableContext = createContext<Set<string>>(new Set());

/** Cards that answer the current question (e.g. where to warp), and how to answer with one. */
export const TargetContext = createContext<{ targets: Map<string, OptionView>; answer: (o: OptionView) => void }>({
  targets: new Map(),
  answer: () => {},
});

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
  const playable = useContext(PlayableContext).has(card.uid);
  const { selected, toggle } = useContext(SelectContext);
  const { targets, answer } = useContext(TargetContext);
  const target = targets.get(card.uid);
  const isSelected = selected === card.uid;
  const select = (el: HTMLElement) => {
    if (target) {
      setPreview(null);
      answer(target);
      return;
    }
    const r = el.getBoundingClientRect();
    setPreview(null);
    toggle({ card, rect: { left: r.left, right: r.right, top: r.top, bottom: r.bottom } });
  };
  // Resource tokens on the card: Glory on Market cards, Dilithium on Kaelon II or the Talvath, and so on.
  const resourceText = Object.entries(card.resources ?? {})
    .filter(([, n]) => n > 0)
    .map(([kind, n]) => `${n} ${kind[0].toUpperCase()}${kind.slice(1)}`)
    .join(" · ");
  const show = (x: number, y: number) => {
    if (!isSelected) setPreview({ image: card.image, beamed: card.beamed, x, y });
  };
  return (
    <div
      className={`gcard ${card.exhausted ? "exhausted" : ""} ${playable ? "playable" : ""} ${isSelected ? "selected" : ""} ${target ? "target" : ""}`}
      role="button"
      data-uid={card.uid}
      aria-pressed={isSelected}
      onClick={(e) => select(e.currentTarget)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          select(e.currentTarget);
        }
      }}
      style={style}
      title={target ? `Choose ${target.label}` : card.name}
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
      {resourceText ? <span className="badge">{resourceText}</span> : null}
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

/** Modal listing every card in a public pile. */
export function PileViewer({ title, cards, onClose }: { title: string; cards: CardView[]; onClose: () => void }) {
  return (
    <div className="modal-backdrop" onClick={onClose} onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="card modal wide" role="dialog" aria-label={title} onClick={(e) => e.stopPropagation()}>
        <div className="row between">
          <h2>{title} ({cards.length})</h2>
          <button className="secondary" onClick={onClose} autoFocus>Close</button>
        </div>
        <div className="cards">{cards.length ? cards.map((c) => <Card key={c.uid} card={c} />) : <span className="muted">Empty</span>}</div>
      </div>
    </div>
  );
}

