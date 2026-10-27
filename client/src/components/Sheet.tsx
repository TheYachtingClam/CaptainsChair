import { useEffect, useState } from "react";

/** Narrower than this is a phone (requirements/19-technical-architecture.md §4.4). Matches the CSS. */
const PHONE_QUERY = "(max-width: 700px)";

/** Whether the screen is phone-sized, following rotation and window resizes. */
export function usePhone(): boolean {
  const [phone, setPhone] = useState(() => window.matchMedia(PHONE_QUERY).matches);
  useEffect(() => {
    const query = window.matchMedia(PHONE_QUERY);
    const update = () => setPhone(query.matches);
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  return phone;
}

/**
 * A panel that floats on a laptop and, on a phone, sits in the sheet at the bottom of the screen (REQ-CLI-34). Its
 * handle collapses it to one line that still says what it is about; it opens again when `openOn` changes, such as a
 * new question (by default, when the summary changes).
 */
export function Sheet({ summary, openOn, className, label, role, live, innerRef, style, children }: {
  summary: string;
  openOn?: string | number;
  /** Announce changes to screen readers. */
  live?: boolean;
  className: string;
  label: string;
  role: string;
  innerRef?: React.Ref<HTMLDivElement>;
  style?: React.CSSProperties;
  children: React.ReactNode;
}) {
  const phone = usePhone();
  const [collapsed, setCollapsed] = useState(false);
  const key = openOn ?? summary;
  useEffect(() => setCollapsed(false), [key]);
  const ariaLive = live ? "polite" : undefined;
  if (!phone) {
    return (
      <div ref={innerRef} className={className} role={role} aria-label={label} aria-live={ariaLive} style={style}>
        {children}
      </div>
    );
  }
  return (
    <div ref={innerRef} className={`${className} sheet ${collapsed ? "collapsed" : ""}`} role={role} aria-label={label}
      aria-live={ariaLive}>
      <button type="button" className="sheet-handle" aria-expanded={!collapsed} onClick={() => setCollapsed((c) => !c)}>
        <span className="sheet-summary">{summary}</span>
        <span className="sheet-toggle">{collapsed ? "Show" : "Hide"}</span>
      </button>
      {!collapsed && <div className="sheet-body">{children}</div>}
    </div>
  );
}
