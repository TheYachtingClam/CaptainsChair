import { Fragment, ReactNode } from "react";

/** The icons cropped from the rulebook (scripts/crop_icons.py), by the name card text writes in brackets. */
const ICONS: Record<string, string> = {
  Action: "action",
  "Away Team": "away-team",
  Dilithium: "dilithium",
  Latinum: "latinum",
  Glory: "glory",
  Research: "research",
  Influence: "influence",
  Military: "military",
};

const BRACKETS = new RegExp(`\\[(${Object.keys(ICONS).join("|")})\\]`, "g");

export function Icon({ name }: { name: string }) {
  return <img className="icon-inline" src={`/icons/${ICONS[name]}.webp`} alt={name} title={name} />;
}

/** Text with "[Dilithium]" and the other known icon names drawn as icons; unknown brackets stay as written. */
export function IconText({ text }: { text: string }) {
  const parts = text.split(BRACKETS);
  return <>{parts.map((p, i) => (i % 2 ? <Icon key={i} name={p} /> : <Fragment key={i}>{p}</Fragment>))}</>;
}

/** The coach's text: sentences with **bold** game terms and bracketed icons. */
export function RichText({ text }: { text: string }): ReactNode {
  const parts = text.replace(/\s*\n\s*/g, " ").split(/\*\*(.+?)\*\*/g);
  return parts.map((p, i) => (i % 2 ? <strong key={i}><IconText text={p} /></strong> : <IconText key={i} text={p} />));
}
