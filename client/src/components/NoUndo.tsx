import { OptionView } from "../api";

/** The marker on an option that cannot be undone (REQ-UNDO-81). Words, not a padlock: a padlock read as "locked",
 *  as if the option could not be chosen. The reason (REQ-UNDO-10) is its tooltip and is read out by screen readers. */
export function NoUndoTag({ option }: { option: Pick<OptionView, "irreversible" | "reason"> | undefined | null }) {
  if (!option?.irreversible) return null;
  const why = option.reason ? `Can't be undone: ${option.reason}` : "Can't be undone";
  return <span className="no-undo" title={why} aria-label={why}>Can't undo</span>;
}

/** One line under a list of answers that has a marked one, saying what the marker means (REQ-UNDO-81). */
export function NoUndoNote({ options }: { options: Pick<OptionView, "irreversible">[] }) {
  if (!options.some((o) => o.irreversible)) return null;
  return (
    <p className="no-undo-note muted">
      <span className="no-undo">Can't undo</span> A move tagged like this reveals a card, uses chance or hands a
      choice to your opponent, so it can't be taken back. You can still choose it; you'll be asked to confirm.
    </p>
  );
}
