import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { GameStateView, OptionView, api } from "../api";
import { Selection, imageUrl } from "./Cards";

const GAP = 14;
const MARGIN = 8;

type Item = { index: number; kind: string; text: string; option?: OptionView; reason?: string };

/** Why an operation of this card cannot be used right now. */
function unavailableReason(kind: string, actionCost: boolean, card: Selection, view: GameStateView): string {
  const me = view.you;
  const player = me == null ? undefined : view.players[me];
  const uid = card!.card.uid;
  const inHand = !!player?.hand?.some((c) => c.uid === uid);
  const onTable = !!player && [player.captain, ...player.status, ...player.fleet, ...player.locations, ...player.duty].some((c) => c.uid === uid);
  if (kind !== "PLAY" && kind !== "ACTIVATION") {
    return kind === "PASSIVE" || kind === "ENDGAME" ? `${kind} applies automatically` : `${kind} happens at its own timing`;
  }
  if (!player) return "You are watching this game";
  if (kind === "PLAY" && !inHand) return "Only from your hand";
  if (kind === "ACTIVATION" && !onTable) return "Only from your play area";
  if (view.decision?.seat !== me) return "Not your decision right now";
  if (view.decision?.kind !== "action") return "Only during your Action Step";
  if (card!.card.exhausted) return "This card is exhausted";
  if (actionCost && player.actions === 0) return "No actions left";
  return "Not available now";
}

export function CardPanel({ selection, view, onChoose, onClose }: {
  selection: NonNullable<Selection>;
  view: GameStateView;
  onChoose: (o: OptionView) => void;
  onClose: () => void;
}) {
  const cards = useQuery({ queryKey: ["card-text"], queryFn: api.cardText, staleTime: Infinity });
  const ref = useRef<HTMLDivElement>(null);
  const close = useRef<HTMLButtonElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const { width, height } = el.getBoundingClientRect();
    const r = selection.rect;
    let left = r.right + GAP;
    if (left + width > window.innerWidth - MARGIN) left = r.left - GAP - width;
    left = Math.max(MARGIN, Math.min(left, window.innerWidth - width - MARGIN));
    const centre = (r.top + r.bottom) / 2;
    const top = Math.max(MARGIN, Math.min(centre - height / 2, window.innerHeight - height - MARGIN));
    setPos({ left, top });
  }, [selection, cards.data]);

  const card = selection.card;
  const data = cards.data?.[card.id];
  const options = view.decision?.seat === view.you ? view.decision?.options ?? [] : [];
  const items: Item[] = (data?.operations ?? []).map((op, index) => {
    const option = options.find((o) => o.id === `play:${card.uid}:${index}` || o.id === `activate:${card.uid}:${index}`);
    return {
      index,
      kind: op.kind,
      text: [op.action_cost ? "[Action]" : "", op.attack ? "ATTACK" : "", op.text ?? ""].filter(Boolean).join(" "),
      option,
      reason: option ? undefined : unavailableReason(op.kind, op.action_cost, selection, view),
    };
  });

  return (
    <div
      ref={ref}
      className="card-panel"
      role="dialog"
      aria-label={card.name}
      style={pos ? { left: pos.left, top: pos.top } : { left: -9999, top: 0 }}
    >
      <img className="card-panel-image" src={imageUrl(card.image)} alt={card.name} />
      <div className="card-panel-menu">
        <div className="row between">
          <h2>{card.name}</h2>
          <button ref={close} className="icon-button" onClick={onClose} aria-label="Deselect card">✕</button>
        </div>
        <p className="muted">{data?.suit}</p>
        {!data && <p className="muted">Loading…</p>}
        {data && items.length === 0 && <p className="muted">This card has no operations.</p>}
        <ul className="op-list">
          {items.map((item) => (
            <li key={item.index}>
              <button
                className="op"
                disabled={!item.option}
                onClick={() => item.option && onChoose(item.option)}
                title={item.reason}
              >
                <span className="op-kind">
                  {item.kind}
                  {item.option?.irreversible && <span title="Cannot be undone"> 🔒</span>}
                </span>
                <span className="op-text">{item.text}</span>
                {item.reason && <span className="op-reason">{item.reason}</span>}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
