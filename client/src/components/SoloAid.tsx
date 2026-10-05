import { useEffect, useRef } from "react";

const TERMS: [string, string][] = [
  ["Gain", "Card to the Bot Discard pile. From the Market, it prefers the most valuable."],
  ["Take", "Card to the top of the Bot deck. From the Market, it prefers the most valuable."],
  ["Deploy", "Move to the Control Area, keeping deployment order."],
  ["Dismiss, Discard, Recall", "Card to the Bot Discard pile. If the Duty Officer went, flip the SUITS card. When choosing a Ship, the most recently deployed."],
  ["Promote", "Move the Person to the Control Area. Flip SUITS if there was no Duty Officer before."],
  ["Log", "Move under the Captain. If the Duty Officer was logged, flip SUITS."],
  ["Explore", "Warp to the neutral Location with the fewest total tokens. Ties: most valuable."],
  ["Engage", "Warp to the neutral Location with the most human tokens. Ties: most valuable."],
  ["Send Away Team", "To the neutral Location with the most Bot tokens. Ties: most valuable. Never where you have more Ships."],
  ["Junk", "The Market card most valuable to you, ignoring cards with resource tokens."],
  ["Continue resolution", "Stop the current row and resolve the next matching row."],
];

/** The solo player aid (requirements/22-solo-mode.md §15): the Bot's turn, the value rules, and its terms. */
export function SoloAid({ onClose }: { onClose: () => void }) {
  const close = useRef<HTMLButtonElement>(null);
  useEffect(() => close.current?.focus(), []);
  return (
    <div className="modal-backdrop" onClick={onClose} onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="card modal solo-aid" role="dialog" aria-labelledby="solo-aid-title" onClick={(e) => e.stopPropagation()}>
        <div className="row between">
          <h2 id="solo-aid-title">Playing against the Bot</h2>
          <button ref={close} className="secondary" onClick={onClose}>Close</button>
        </div>

        <h3>The Bot's turn</h3>
        <ol>
          <li><strong>No Resupply.</strong></li>
          <li><strong>Control:</strong> if it has secured a Location, it takes control of the most valuable one and resolves it.</li>
          <li><strong>Actions:</strong> it draws as many cards as the Bot actions on the Stardate card, facedown, then flips and resolves them one at a time.</li>
          <li><strong>Clean-up:</strong> it resolves a Stardate card it holds, discards its Staging Area, and places 1 Glory on the Market card least valuable to you.</li>
        </ol>
        <p>
          To resolve a card it ignores the card's text: a Surprise card uses its SURPRISE operation; otherwise the first
          TRAITS row with one of the card's traits matches, or else the card's suit row on the SUITS side that is face
          up. When its deck runs out, it shuffles its Discard pile and puts the top Supplement card on top.
        </p>

        <h3>Value of a card</h3>
        <p>
          The VP it would score if the game ended now: printed VP, plus the current multiplier for each Focus icon, plus
          5 for an ENDGAME, plus 1 per Glory on it. Ties: more resource tokens, then the leftmost card.
        </p>

        <h3>Terms</h3>
        <dl className="aid-terms">
          {TERMS.map(([term, meaning]) => (
            <div key={term}>
              <dt>{term}</dt>
              <dd>{meaning}</dd>
            </div>
          ))}
        </dl>

        <h3>Attacks and your cards</h3>
        <ul>
          <li>Bold red text on its cards is an attack on you: your "when attacked" Reactions work, and you make its choices.</li>
          <li>The Bot has no hand. An attack on its hand does nothing: you say whether it succeeded, and may move its top discard onto its deck.</li>
          <li>A draw for the Bot discards its top card instead. It never returns Incidents. Steals come from the supply.</li>
          <li>You win only with more VP than the Bot. A tie, or the Burn, is a loss.</li>
        </ul>
      </div>
    </div>
  );
}
