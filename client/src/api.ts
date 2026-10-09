export class AuthError extends Error {}

export type GameMode = "two_player" | "solo" | "cadet";
export type BoardSide = "basic" | "advanced";
export type Difficulty = "ensign" | "lieutenant" | "commander" | "captain" | "admiral";
export const DIFFICULTIES: Difficulty[] = ["ensign", "lieutenant", "commander", "captain", "admiral"];

/** Solo mode: the Bot to play against. */
export interface BotChoice {
  deck_id: string;
  difficulty: Difficulty;
  ticking_clock: boolean;
  /** The Core Box Ticking Clock card, instead of or with the other (REQ-SOLO-133). */
  conspiracy?: boolean;
}

/** The box a game is played with (REQ-CORE-10). */
export type Box = "core" | "to_boldly_go" | "both";
/** Each box's name and the sets whose Crew decks it allows. */
export type Boxes = Record<Box, { name: string; sets: string[] }>;
export const DEFAULT_BOX: Box = "to_boldly_go";
/** The sets whose Crew decks a game allows: its box's sets and its expansions. */
export function setsFor(boxes: Boxes | undefined, box: Box, expansions: string[]): string[] {
  return [...(boxes?.[box]?.sets ?? ["to_boldly_go"]), ...expansions];
}
/** "Picard (Starfleet) – complexity 1/10". */
export function deckLabel(d: Deck): string {
  return `${d.captain} (${d.faction})${d.complexity == null ? "" : ` – complexity ${d.complexity}/10`}`;
}
/** Easiest first; Crews without a complexity come last, by name. */
export function byComplexity(a: Deck, b: Deck): number {
  return (a.complexity ?? 99) - (b.complexity ?? 99) || a.captain.localeCompare(b.captain);
}

export interface Deck {
  id: string;
  captain: string;
  faction: string;
  complexity: number | null;
  set: string;
  summary: string;
  bot?: boolean; // can be the solo-mode Bot
}

export interface Seat {
  index: number;
  display_name: string;
  deck_id: string;
  board_side: BoardSide;
}

export interface Game {
  id: string;
  created_at: string;
  mode: GameMode;
  box: Box;
  expansions: string[];
  promos: boolean;
  status: string;
  seats: Seat[];
  open_seats: number;
  your_seat?: number | null;
  bot?: BotChoice | null;
  campaign_id?: string | null;
}

// ------------------------------------------------------------------ Five-Year Mission campaigns

export type CampaignMode = "set_phasers_to_stun" | "yellow_alert" | "gates_of_sto_vo_kor" | "kobayashi_maru";
export const CAMPAIGN_MODES: [CampaignMode, string][] = [
  ["set_phasers_to_stun", "Set Phasers to Stun (easiest)"],
  ["yellow_alert", "Yellow Alert"],
  ["gates_of_sto_vo_kor", "Gates of Sto'Vo'Kor"],
  ["kobayashi_maru", "The Kobayashi Maru (hardest)"],
];

export interface CampaignCard {
  id: string;
  name: string;
  suit: string;
  image: string;
}

export interface Assignment {
  number: number;
  game_id: string;
  date: string;
  rank: string;
  bot: string;
  bot_captain: string;
  difficulty: string;
  board_side: BoardSide;
  outcome: "win" | "loss" | null;
  scores: Record<string, number> | null;
  upgrade: { option: "A" | "B" | "none"; card?: string; bonus?: string; text?: string; cards?: string[] } | null;
}

export interface Challenge {
  id: string;
  name: string;
  rule: string;
}

export interface CampaignBonus {
  key: string;
  text: string;
  kind: "boost" | "reinforce";
  each?: boolean; // REINFORCE "X and/or Y": at most one card from each pool
  pools?: CampaignCard[][];
}

export interface CampaignView {
  id: string;
  display_name: string;
  deck_id: string;
  captain: string;
  mode: CampaignMode;
  mode_name: string;
  box: Box;
  expansions: string[];
  rank: string;
  phase: "start" | "playing" | "upgrade" | "finished";
  assignments: Assignment[];
  assignments_left: number;
  reinforcement: CampaignCard[];
  next_difficulty: string | null;
  opponents: { deck_id: string; captain: string }[];
  game_id?: string;
  upgrade?: { won: boolean; restriction: string | null; options: CampaignCard[]; bonuses: CampaignBonus[] };
  challenges: Challenge[];
  boosts: string[];
  next_notes: string[];
  choose_resource: boolean;
  evaluation?: string;
}

const campaignKey = (id: string) => `cc.campaign.${id}`;

export function saveCampaignToken(id: string, token: string): void {
  try {
    localStorage.setItem(campaignKey(id), token);
  } catch {
    /* storage unavailable: keep the link */
  }
}

export function loadCampaignToken(id: string): string | null {
  try {
    return localStorage.getItem(campaignKey(id));
  } catch {
    return null;
  }
}

/** Campaigns this browser knows the link of. */
export function knownCampaigns(): string[] {
  try {
    return Object.keys(localStorage).filter((k) => k.startsWith("cc.campaign.")).map((k) => k.slice("cc.campaign.".length));
  } catch {
    return [];
  }
}

function campaignHeaders(id: string): Record<string, string> {
  const token = loadCampaignToken(id);
  return token ? { "X-Campaign-Token": token } : {};
}

export interface SeatGrant {
  game: Game;
  seat_index: number;
  seat_token: string;
}

export interface SeatChoice {
  display_name: string;
  deck_id: string;
  board_side: BoardSide;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    credentials: "same-origin",
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
  });
  // A wrong password (site or admin) is an ordinary error; any other 401 means the site session has ended.
  if (res.status === 401 && !path.startsWith("/api/auth/login") && !path.startsWith("/api/admin/login")) {
    throw new AuthError("Not signed in");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`;
    throw new Error(detail);
  }
  // Queries must never resolve to undefined (TanStack Query treats that as an error), so 204 becomes null.
  return res.status === 204 ? (null as T) : ((await res.json()) as T);
}

// Seat tokens let a player rejoin their seat after a refresh (REQ-SRV-30).
const seatKey = (gameId: string) => `cc.seat.${gameId}`;

export function saveSeatToken(gameId: string, token: string): void {
  try {
    localStorage.setItem(seatKey(gameId), token);
  } catch {
    /* storage unavailable: the seat lasts only for this page */
  }
}

export function forgetSeatToken(gameId: string): void {
  try {
    localStorage.removeItem(seatKey(gameId));
  } catch {
    /* storage unavailable: nothing stored */
  }
}

export function loadSeatToken(gameId: string): string | null {
  try {
    return localStorage.getItem(seatKey(gameId));
  } catch {
    return null;
  }
}

export interface CardView {
  uid: string;
  id: string;
  name: string;
  suit: string;
  image: string;
  exhausted: boolean;
  at?: string;
  resources?: Record<string, number>;
  beamed?: CardView[];
  away_teams?: Record<string, number>;
  secured_by?: number[];
  token?: string; // a Ship's token image, shown where the Ship is warped
  facedown?: boolean; // a Bot card drawn this turn and not yet flipped; only uid is set
}

export interface OptionView {
  id: string;
  label: string;
  irreversible: boolean;
  reason: string | null;
}

/** One trait slot on Khan's Crew board: its token image changes when it is marked. */
export interface TraitSlot {
  slot: string;
  label: string;
  marked: boolean;
  trait: string | null;
  image: string;
}

export interface PlayerView {
  seat: number;
  name: string;
  deck: string;
  board: string;
  captain: CardView;
  status: CardView[];
  hand: CardView[] | null;
  hand_count: number;
  hand_size: number;
  draw_count: number;
  draw: CardView[] | null; // set while the Draw deck is face-up (Gluonic Distortion), top card first
  reserve_count: number;
  discard: CardView[];
  development: CardView[];
  staging: CardView[];
  fleet: CardView[];
  locations: CardView[];
  duty: CardView[];
  log: CardView[];
  resources: { dilithium: number; latinum: number; glory: number };
  actions: number;
  tracks: Record<string, number>;
  /** Khan only: the 12 trait slots of his Crew board, in board order (REQ-CD-KHN-06). */
  traits?: TraitSlot[] | null;
  away_pool: number;
  reserve?: CardView[] | null; // your own Reserve deck's contents, sorted by name; never its order (REQ-INF-05)
  // Five-Year Mission games only
  reinforcement?: CardView[];
  boosts?: string[];
  only_ship?: string | null;
  teams_aside?: number;
  mission_tokens: number;
  missions_completed: string[];
  bot: BotView | null; // the solo-mode Bot
}

export interface CommandRowView {
  number: number;
  matches: string[];
  text: string;
  attack: boolean;
}

/** The Bot's Automated Command cards as they lie, and its settings. */
export interface BotView {
  crew: string;
  difficulty: Difficulty;
  ticking_clock: boolean;
  conspiracy?: boolean;
  suits_side: "no_duty_officer" | "with_duty_officer";
  /** The Khan Bot only: it is still on its KHAN IN EXILE card (REQ-CD-KHN-11). */
  exile: boolean;
  special_rule: string | null;
  command: { side: string; image: string | null; up: boolean; rows: CommandRowView[] }[];
}

/** A row of an Automated Command card: which side, and its number on that side. */
export interface RowRef {
  side: string;
  number: number;
}

/** One line of a Bot turn, for watching it step by step. */
export interface BotStep {
  text: string;
  card?: { id: string; name: string; image: string };
  row?: RowRef;
}

/** The latest Bot turn. `start` identifies it; `finished` is false while it waits for your answer. */
export interface BotTurnView {
  start: number;
  finished: boolean;
  steps: BotStep[];
}

export interface GameStateView {
  mode: GameMode;
  difficulty: Difficulty | null;
  turn: number;
  active: number;
  first_seat: number;
  step: string;
  you: number | null;
  players: PlayerView[];
  market: Record<string, CardView | null>;
  neutral_zone: CardView[];
  junk: CardView[];
  market_deck_counts: Record<string, number>;
  reward_count: number;
  location_deck_count: number;
  encounter_count: number;
  incident_count: number;
  stardate: { top: CardView | null; glory: number; remaining: number };
  resolution: boolean;
  last_turn: number | null;
  decision: { seat: number; kind: string; prompt: string; options?: OptionView[]; cards?: CardView[] } | null;
  log: string[];
  bot_turn: BotTurnView | null;
  result: { reason: string; winners: number[]; rating?: string; scores?: { seat: number; name: string; total: number; parts: Record<string, number> }[] } | null;
  can_undo: boolean;
  dev_tools?: boolean;
}

/** Developer panel command (server engine/dev.py). */
export type DevCommand =
  | { kind: "card"; card: string; zone: string }
  | { kind: "resource"; resource: "dilithium" | "latinum" | "glory" | "actions"; amount: number }
  | { kind: "track"; track: "research" | "influence" | "military"; amount: number }
  | { kind: "mark"; amount: number };

export interface CardText {
  name: string;
  suit: string;
  set?: string;
  operations: { kind: string; text: string | null; action_cost: boolean; attack: boolean; requires: string | null }[];
}

function seatHeaders(id: string): Record<string, string> {
  const token = loadSeatToken(id);
  return token ? { "X-Seat-Token": token } : {};
}

export const campaignApi = {
  challenges: (deckId: string) => request<Challenge[]>(`/api/campaigns/challenges/${deckId}`),
  create: (body: { display_name: string; deck_id: string; mode: CampaignMode; box: Box; expansions: string[];
    promos: boolean; challenges: string[] }) =>
    request<{ campaign: CampaignView; token: string }>("/api/campaigns", { method: "POST", body: JSON.stringify(body) }),
  get: (id: string) => request<CampaignView>(`/api/campaigns/${id}`, { headers: campaignHeaders(id) }),
  start: (id: string, body: { bot_deck_id: string | null; board_side: BoardSide; drop: "dilithium" | "latinum" | null }) =>
    request<{ game_id: string; seat_token: string; campaign: CampaignView }>(`/api/campaigns/${id}/assignments`,
      { method: "POST", body: JSON.stringify(body), headers: campaignHeaders(id) }),
  upgrade: (id: string, choice: { card_id?: string; bonus?: string; cards?: string[] }) =>
    request<CampaignView>(`/api/campaigns/${id}/upgrade`,
      { method: "POST", body: JSON.stringify(choice), headers: campaignHeaders(id) }),
};

// ------------------------------------------------------------------ admin (REQ-ADMIN-01 to -05)

export interface AdminGame {
  id: string;
  mode: GameMode;
  status: string;
  created_at: string | null;
  players: string[];
  bot: string | null;
  campaign_id: string | null;
  moves: number;
}

export interface AdminCampaign {
  id: string;
  display_name: string;
  deck_id: string;
  rank: string;
  assignments: number;
  status: string;
  created_at: string | null;
}

export const adminApi = {
  status: () => request<{ enabled: boolean; admin: boolean }>("/api/admin/status"),
  login: (password: string) => request<null>("/api/admin/login", { method: "POST", body: JSON.stringify({ password }) }),
  logout: () => request<null>("/api/admin/logout", { method: "POST" }),
  games: () => request<AdminGame[]>("/api/admin/games"),
  deleteGame: (id: string) => request<null>(`/api/admin/games/${id}`, { method: "DELETE" }),
  campaigns: () => request<AdminCampaign[]>("/api/admin/campaigns"),
  deleteCampaign: (id: string) => request<null>(`/api/admin/campaigns/${id}`, { method: "DELETE" }),
};

export const api = {
  checkSession: () => request<null>("/api/auth/session").then(() => true),
  login: (password: string) =>
    request<void>("/api/auth/login", { method: "POST", body: JSON.stringify({ password }) }),
  logout: () => request<void>("/api/auth/logout", { method: "POST" }),
  decks: () => request<Deck[]>("/api/content/decks"),
  expansions: () => request<Record<string, string>>("/api/content/expansions"),
  boxes: () => request<Boxes>("/api/content/boxes"),
  games: () => request<Game[]>("/api/games"),
  game: (id: string) => {
    const token = loadSeatToken(id);
    return request<Game>(`/api/games/${id}`, { headers: token ? { "X-Seat-Token": token } : {} });
  },
  createGame: (body: SeatChoice & { mode: GameMode; box: Box; expansions: string[]; promos: boolean; bot?: BotChoice }) =>
    request<SeatGrant>("/api/games", { method: "POST", body: JSON.stringify(body) }),
  cardText: () => request<Record<string, CardText>>("/api/content/cards"),
  state: (id: string) => request<GameStateView>(`/api/games/${id}/state`, { headers: seatHeaders(id) }),
  command: (id: string, option: string) =>
    request<GameStateView>(`/api/games/${id}/commands`, { method: "POST", body: JSON.stringify({ option }), headers: seatHeaders(id) }),
  undo: (id: string) => request<GameStateView>(`/api/games/${id}/undo`, { method: "POST", headers: seatHeaders(id) }),
  dev: (id: string, body: DevCommand) =>
    request<GameStateView>(`/api/games/${id}/dev`, { method: "POST", body: JSON.stringify(body), headers: seatHeaders(id) }),
  deleteGame: (id: string) => request<null>(`/api/games/${id}`, { method: "DELETE", headers: seatHeaders(id) }),
  joinGame: (id: string, body: SeatChoice) =>
    request<SeatGrant>(`/api/games/${id}/join`, { method: "POST", body: JSON.stringify(body) }),
};

export const MODE_LABELS: Record<GameMode, string> = {
  two_player: "Two players",
  solo: "Solo vs Bot",
  cadet: "Cadet Training",
};
