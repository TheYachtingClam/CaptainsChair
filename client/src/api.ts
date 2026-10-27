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

export interface SeatGrant {
  game: Game;
  seat_index: number;
}

/** The player's name comes from their account (REQ-USER-40). */
export interface SeatChoice {
  deck_id: string;
  board_side: BoardSide;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    credentials: "same-origin",
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
  });
  // A wrong password is an ordinary error; any other 401 means the session has ended.
  if (res.status === 401 && !path.startsWith("/api/auth/login")) {
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
  /** Two-player games: the other player's latest turn, played back like a Bot turn (REQ-CLI-19). */
  opponent_turn?: BotTurnView | null;
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

export const campaignApi = {
  challenges: (deckId: string) => request<Challenge[]>(`/api/campaigns/challenges/${deckId}`),
  create: (body: { deck_id: string; mode: CampaignMode; box: Box; expansions: string[];
    promos: boolean; challenges: string[] }) =>
    request<{ campaign: CampaignView }>("/api/campaigns", { method: "POST", body: JSON.stringify(body) }),
  get: (id: string) => request<CampaignView>(`/api/campaigns/${id}`),
  start: (id: string, body: { bot_deck_id: string | null; board_side: BoardSide; drop: "dilithium" | "latinum" | null }) =>
    request<{ game_id: string; seat_index: number; campaign: CampaignView }>(`/api/campaigns/${id}/assignments`,
      { method: "POST", body: JSON.stringify(body) }),
  upgrade: (id: string, choice: { card_id?: string; bonus?: string; cards?: string[] }) =>
    request<CampaignView>(`/api/campaigns/${id}/upgrade`,
      { method: "POST", body: JSON.stringify(choice) }),
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

/** The signed-in account (REQ-USER-01). */
export interface Account {
  id: string;
  email: string;
  display_name: string;
  is_admin: boolean;
}

/** An account as the Admin page lists it (REQ-USER-31). */
export interface AdminUser extends Account {
  disabled: boolean;
  created_at: string | null;
  last_seen_at: string | null;
}

/** An open invitation (REQ-USER-30). `link` is only there right after it is made. */
export interface AdminInvite {
  id: string;
  email: string;
  is_admin: boolean;
  created_at: string | null;
  expires_at: string | null;
  link?: string;
  /** How the invitation email went, right after it is made. */
  mail?: MailOutcome;
}

/** "sent"; "logged": email is not set up on the server; "failed": the email could not be sent. */
export type MailOutcome = "sent" | "logged" | "failed";

export interface AdminCampaign {
  id: string;
  display_name: string;
  deck_id: string;
  rank: string;
  assignments: number;
  status: string;
  created_at: string | null;
}

/** A player's bug report as the Admin page lists it (REQ-BUG-05). */
export interface AdminBug {
  id: string;
  created_at: string | null;
  game_id: string;
  reporter: string;
  seat: number;
  description: string;
  status: "open" | "resolved";
  /** A bug report, or a request for a feature; both keep the game (REQ-BUG-09). */
  kind: "bug" | "feature";
  mode: GameMode;
  box: Box;
  players: string[];
  bot: string | null;
  turn: number;
  step: string;
  moves: number;
}

/** A playable copy of a reported game: a new game in which the admin holds every seat (REQ-BUG-07). */
export interface RecreatedGame {
  game_id: string;
  reporter_seat: number;
}

export const adminApi = {
  bugs: () => request<AdminBug[]>("/api/admin/bugs"),
  bug: (id: string) => request<AdminBug & { bundle: unknown }>(`/api/admin/bugs/${id}`),
  setBugStatus: (id: string, status: AdminBug["status"]) =>
    request<AdminBug>(`/api/admin/bugs/${id}/status`, { method: "POST", body: JSON.stringify({ status }) }),
  deleteBug: (id: string) => request<null>(`/api/admin/bugs/${id}`, { method: "DELETE" }),
  recreateBug: (id: string, moves?: number) =>
    request<RecreatedGame>(`/api/admin/bugs/${id}/recreate`, { method: "POST", body: JSON.stringify(moves == null ? {} : { moves }) }),
  status: () => request<{ admin: boolean }>("/api/admin/status"),
  users: () => request<AdminUser[]>("/api/admin/users"),
  changeUser: (id: string, change: { disabled?: boolean; is_admin?: boolean }) =>
    request<AdminUser>(`/api/admin/users/${id}`, { method: "PATCH", body: JSON.stringify(change) }),
  resetUser: (id: string) => request<{ link: string; mail: MailOutcome }>(`/api/admin/users/${id}/reset`, { method: "POST" }),
  invites: () => request<AdminInvite[]>("/api/admin/invites"),
  invite: (email: string, admin = false) =>
    request<AdminInvite>("/api/admin/invites", { method: "POST", body: JSON.stringify({ email, admin }) }),
  cancelInvite: (id: string) => request<null>(`/api/admin/invites/${id}`, { method: "DELETE" }),
  games: () => request<AdminGame[]>("/api/admin/games"),
  deleteGame: (id: string) => request<null>(`/api/admin/games/${id}`, { method: "DELETE" }),
  /** Take over a seat in a real game: its player is locked out (REQ-ADMIN-06). */
  takeSeat: (id: string, seat: number) =>
    request<{ game_id: string; seat_index: number; display_name: string }>(
      `/api/admin/games/${id}/seats/${seat}/take`, { method: "POST" }),
  campaigns: () => request<AdminCampaign[]>("/api/admin/campaigns"),
  deleteCampaign: (id: string) => request<null>(`/api/admin/campaigns/${id}`, { method: "DELETE" }),
};

export const api = {
  checkSession: () => request<null>("/api/auth/session").then(() => true),
  /** Sign in to an account (REQ-USER-10). */
  login: (email: string, password: string) =>
    request<void>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request<Account>("/api/auth/me"),
  /** The signed-in account's games and campaigns, on any device (REQ-USER-40). */
  myGames: () => request<(Game & { your_seat: number })[]>("/api/me/games"),
  myCampaigns: () => request<{ id: string }[]>("/api/me/campaigns"),
  invitation: (code: string) => request<{ email: string }>(`/api/auth/invite/${encodeURIComponent(code)}`),
  signUp: (code: string, display_name: string, password: string) =>
    request<Account>("/api/auth/signup", { method: "POST", body: JSON.stringify({ code, display_name, password }) }),
  forgot: (email: string) =>
    request<{ detail: string }>("/api/auth/forgot", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (code: string, password: string) =>
    request<Account>("/api/auth/reset", { method: "POST", body: JSON.stringify({ code, password }) }),
  logout: () => request<void>("/api/auth/logout", { method: "POST" }),
  decks: () => request<Deck[]>("/api/content/decks"),
  expansions: () => request<Record<string, string>>("/api/content/expansions"),
  boxes: () => request<Boxes>("/api/content/boxes"),
  games: () => request<Game[]>("/api/games"),
  game: (id: string) => request<Game>(`/api/games/${id}`),
  createGame: (body: SeatChoice & { mode: GameMode; box: Box; expansions: string[]; promos: boolean; bot?: BotChoice }) =>
    request<SeatGrant>("/api/games", { method: "POST", body: JSON.stringify(body) }),
  cardText: () => request<Record<string, CardText>>("/api/content/cards"),
  state: (id: string) => request<GameStateView>(`/api/games/${id}/state`),
  command: (id: string, option: string) =>
    request<GameStateView>(`/api/games/${id}/commands`, { method: "POST", body: JSON.stringify({ option }) }),
  undo: (id: string) => request<GameStateView>(`/api/games/${id}/undo`, { method: "POST" }),
  /** Report a bug: the server keeps the description with the game's setup, seed and moves (REQ-BUG-01). */
  reportBug: (id: string, description: string, kind: "bug" | "feature" = "bug") =>
    request<{ id: string }>(`/api/games/${id}/bugs`, { method: "POST", body: JSON.stringify({ description, kind }) }),
  dev: (id: string, body: DevCommand) =>
    request<GameStateView>(`/api/games/${id}/dev`, { method: "POST", body: JSON.stringify(body) }),
  deleteGame: (id: string) => request<null>(`/api/games/${id}`, { method: "DELETE" }),
  joinGame: (id: string, body: SeatChoice) =>
    request<SeatGrant>(`/api/games/${id}/join`, { method: "POST", body: JSON.stringify(body) }),
};

export const MODE_LABELS: Record<GameMode, string> = {
  two_player: "Two players",
  solo: "Solo vs Bot",
  cadet: "Cadet Training",
};
