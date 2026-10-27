import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CardView, OptionView, PlayerView } from "../api";

export type Preview = {
  image: string;
  beamed?: CardView[];
  wide?: boolean;
  /** A Ship's token, shown with the Ship's name underneath. */
  token?: string;
  tokenName?: string;
  /** Show only the token, large (hovering the token itself). */
  tokenOnly?: boolean;
  x: number;
  y: number;
} | null;
export const PreviewContext = createContext<(p: Preview) => void>(() => {});

/** A card or image opened full screen by pressing and holding it, for touch screens (REQ-CLI-31). */
export type Inspect = {
  image: string;
  name: string;
  beamed?: CardView[];
  /** A Ship's token, shown with its name. */
  token?: string;
  /** Resource tokens on the card, e.g. "2 Glory". */
  resources?: string;
  /** A Crew board or other landscape image. */
  wide?: boolean;
} | null;
export const InspectContext = createContext<(i: Inspect) => void>(() => {});

const HOLD_MS = 450; // how long a press must last to open the viewer
const MOVE_PX = 10; // moving further than this is a scroll, not a press

/** Press-and-hold handlers for touch and pen (REQ-CLI-31). A mouse has hover instead, so it is ignored. The click
 *  that follows a press that opened the viewer is swallowed, so the press does not also select or answer. */
export function useLongPress(onLong: () => void) {
  const timer = useRef<number | undefined>(undefined);
  const start = useRef<{ x: number; y: number } | null>(null);
  const fired = useRef(false);
  useEffect(() => () => window.clearTimeout(timer.current), []);
  const cancel = () => {
    window.clearTimeout(timer.current);
    start.current = null;
  };
  return {
    onPointerDown: (e: React.PointerEvent) => {
      if (e.pointerType === "mouse") return;
      fired.current = false;
      start.current = { x: e.clientX, y: e.clientY };
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => {
        fired.current = true;
        start.current = null;
        onLong();
      }, HOLD_MS);
    },
    onPointerMove: (e: React.PointerEvent) => {
      const s = start.current;
      if (s && Math.hypot(e.clientX - s.x, e.clientY - s.y) > MOVE_PX) cancel();
    },
    onPointerUp: cancel,
    onPointerCancel: cancel,
    // The phone's own long-press menu (save image, share) would open over the viewer.
    onContextMenu: (e: React.MouseEvent) => {
      if (fired.current || start.current) e.preventDefault();
    },
    onClickCapture: (e: React.MouseEvent) => {
      if (!fired.current) return;
      fired.current = false;
      e.preventDefault();
      e.stopPropagation();
    },
  };
}

/** Full-screen view of a pressed card: the card, its tokens and resources, and the cards beamed to it, each of which
 *  can be opened in turn. A tap anywhere else closes it. */
export function CardViewer({ shown, onShow }: { shown: Inspect; onShow: (i: Inspect) => void }) {
  const opened = useRef(0);
  useEffect(() => {
    opened.current = Date.now();
  }, [shown]);
  if (!shown) return null;
  // The tap that ends the press can land on the viewer itself; it must not close it at once.
  const close = () => Date.now() - opened.current > 400 && onShow(null);
  return (
    <div className="modal-backdrop card-viewer" role="dialog" aria-label={shown.name} onClick={close}
      onContextMenu={(e) => e.preventDefault()}
      onKeyDown={(e) => e.key === "Escape" && onShow(null)}>
      <figure className={shown.wide ? "wide" : ""}>
        <img src={imageUrl(shown.image)} alt={shown.name} draggable={false} />
        {(shown.resources || shown.token) && (
          <figcaption>
            {shown.token && <img className="viewer-token" src={imageUrl(shown.token)} alt="" />}
            {shown.resources}
          </figcaption>
        )}
      </figure>
      {shown.beamed && shown.beamed.length > 0 && (
        <div className="viewer-beamed">
          <span>Beamed here:</span>
          {shown.beamed.map((b) => (
            <button key={b.uid} type="button" onClick={(e) => { e.stopPropagation(); onShow(inspectOf(b)); }}
              aria-label={`Show ${b.name}`}>
              <img src={imageUrl(b.image)} alt={b.name} />
            </button>
          ))}
        </div>
      )}
      <p className="viewer-hint">Tap anywhere to close</p>
    </div>
  );
}

/** Resource tokens on a card as text: Glory on Market cards, Dilithium on Kaelon II or the Talvath, and so on. */
function resourcesOf(card: CardView): string {
  return Object.entries(card.resources ?? {})
    .filter(([, n]) => n > 0)
    .map(([kind, n]) => `${n} ${kind[0].toUpperCase()}${kind.slice(1)}`)
    .join(" · ");
}

export function inspectOf(card: CardView): Inspect {
  return { image: card.image, name: card.name, beamed: card.beamed, token: card.token, resources: resourcesOf(card) || undefined };
}

/** Every player, so a Location can show the Ship tokens warped to it. */
export const PlayersContext = createContext<PlayerView[]>([]);

/** The Away Team token of a seat: blue for the first player, pink for the second player or the Bot. */
export const awayTokenImage = (seat: number) => (seat === 0 ? "away-team-p1" : "away-team-p2");

/** The tokens at a Location, by player: Away Teams (token and count) and each Ship warped there. */
export function LocationTokens({ loc, seat, compact = false }: { loc: CardView; seat?: number; compact?: boolean }) {
  const players = useContext(PlayersContext);
  const groups = players
    .filter((p) => seat === undefined || p.seat === seat)
    .map((p) => ({
      p,
      teams: loc.away_teams?.[String(p.seat)] ?? 0,
      ships: p.fleet.filter((s) => s.at === loc.uid),
    }))
    .filter((g) => seat !== undefined || g.teams > 0 || g.ships.length > 0);
  if (!groups.length) return null;
  return (
    <span className={`tokens ${compact ? "compact" : ""}`}>
      {groups.map(({ p, teams, ships }) => (
        <span key={p.seat} className="token-group" title={`${p.name}: ${teams} Away Team(s), ${ships.length} Ship(s)`}>
          {teams > 0 && (
            <span className="away-token">
              <img src={imageUrl(awayTokenImage(p.seat))} alt={`${p.name}'s Away Team`} />
              {teams > 1 && <span className="token-count">×{teams}</span>}
            </span>
          )}
          {ships.map((s) => <ShipToken key={s.uid} ship={s} />)}
        </span>
      ))}
    </span>
  );
}
/** A Ship's token at a Location: hover shows it large; pressing and holding opens the Ship (REQ-CLI-30, -31). */
function ShipToken({ ship }: { ship: CardView }) {
  const setPreview = useContext(PreviewContext);
  const inspect = useContext(InspectContext);
  const held = useLongPress(() => inspect(inspectOf(ship)));
  // A press on the token opens the Ship, not the Location card it sits on.
  const press = { ...held, onPointerDown: (e: React.PointerEvent) => { e.stopPropagation(); held.onPointerDown(e); } };
  const hover = (e: React.MouseEvent) =>
    ship.token && setPreview({ image: ship.token, token: ship.token, tokenName: ship.name, tokenOnly: true, x: e.clientX, y: e.clientY });
  return (
    <img className="ship-token" src={imageUrl(ship.token ?? ship.image)} alt={ship.name} {...press}
      onMouseEnter={hover} onMouseMove={hover} onMouseLeave={() => setPreview(null)} />
  );
}

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
    <div ref={ref} className={`card-preview ${preview.wide ? "wide" : ""} ${preview.tokenOnly ? "token-only" : ""}`} aria-hidden
      style={pos ? { left: pos.left, top: pos.top } : { left: -9999, top: 0 }}>
      {!preview.tokenOnly && <img src={imageUrl(preview.image)} alt="" />}
      {preview.token && (
        <div className="preview-token">
          <figure><img src={imageUrl(preview.token)} alt="" /><figcaption>{preview.tokenName}</figcaption></figure>
        </div>
      )}
      {preview.beamed && preview.beamed.length > 0 && (
        <div className="preview-beamed">
          <span className="muted">Beamed here:</span>
          {preview.beamed.map((b) => <img key={b.uid} src={imageUrl(b.image)} alt="" />)}
        </div>
      )}
    </div>
  );
}

/** A faceup card on the table. Hover or focus shows the large preview. Cards beamed to it are shown tucked under
 *  it as small cards of their own, each with its own preview and click (REQ-CLI-12). */
export function Card({ card, badges, style, tokens = true, mini = false }: {
  card: CardView;
  badges?: React.ReactNode;
  style?: React.CSSProperties;
  /** A Location shows the tokens at it, unless they are listed elsewhere (the Neutral Zone). */
  tokens?: boolean;
  /** A card beamed to another card: drawn small under its host. */
  mini?: boolean;
}) {
  const setPreview = useContext(PreviewContext);
  const inspect = useContext(InspectContext);
  const press = useLongPress(() => {
    setPreview(null);
    inspect(inspectOf(card));
  });
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
  const resourceText = resourcesOf(card);
  const show = (x: number, y: number) => {
    if (!isSelected) setPreview({ image: card.image, beamed: card.beamed, token: mini ? undefined : card.token, tokenName: card.name, x, y });
  };
  const beamed = card.beamed ?? [];
  const body = (
    <div
      className={`gcard ${mini ? "mini" : ""} ${card.exhausted && !mini ? "exhausted" : ""} ${playable ? "playable" : ""} ${isSelected ? "selected" : ""} ${target ? "target" : ""}`}
      role="button"
      data-uid={card.uid}
      aria-pressed={isSelected}
      {...press}
      onClick={(e) => select(e.currentTarget)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          select(e.currentTarget);
        }
      }}
      style={style}
      title={target ? `Choose ${target.label}` : mini ? `${card.name} (beamed)` : card.name}
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
      {resourceText && !mini ? <span className="badge">{resourceText}</span> : null}
      {card.suit === "Location" && tokens && !mini && <LocationTokens loc={card} compact />}
      {badges}
    </div>
  );
  if (beamed.length === 0) return body;
  // The host's hover preview shows only the host; each beamed card below has its own.
  return (
    <div className={`gcard-stack ${mini ? "mini" : ""}`}>
      {body}
      <div className="beamed-strip" role="group" aria-label={`Cards beamed to ${card.name}`}>
        {beamed.map((b) => <Card key={b.uid} card={b} mini />)}
      </div>
    </div>
  );
}

/** Hover and focus handlers that show any image in the large preview, and press and hold to open it full screen. */
export function usePreviewHandlers(image: string, wide = false, name = "") {
  const setPreview = useContext(PreviewContext);
  const inspect = useContext(InspectContext);
  const press = useLongPress(() => {
    setPreview(null);
    inspect({ image, name, wide });
  });
  const show = (x: number, y: number) => setPreview({ image, wide, x, y });
  return {
    ...press,
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
export function CardBack({ label, count, onClick, title }: { label: string; count: number; onClick?: () => void; title?: string }) {
  return (
    <button type="button" className={`card-back ${count === 0 ? "empty" : ""}`} onClick={onClick} disabled={!onClick}
      aria-label={`${label}: ${count} card(s)`} title={title}>
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
export function PileViewer({ title, cards, onClose, note }: {
  title: string;
  cards: CardView[];
  onClose: () => void;
  /** A line under the title, e.g. that a deck's order is not shown. */
  note?: string;
}) {
  return (
    <div className="modal-backdrop" onClick={onClose} onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="card modal wide" role="dialog" aria-label={title} onClick={(e) => e.stopPropagation()}>
        <div className="row between">
          <h2>{title} ({cards.length})</h2>
          <button className="secondary" onClick={onClose} autoFocus>Close</button>
        </div>
        {note && <p className="pile-note">{note}</p>}
        <div className="cards">{cards.length ? cards.map((c) => <Card key={c.uid} card={c} />) : <span className="muted">Empty</span>}</div>
      </div>
    </div>
  );
}

