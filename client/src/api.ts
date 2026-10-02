export class AuthError extends Error {}

export type GameMode = "two_player" | "solo" | "cadet";
export type BoardSide = "basic" | "advanced";

export interface Deck {
  id: string;
  captain: string;
  faction: string;
  complexity: number;
  set: string;
  summary: string;
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
  expansions: string[];
  promos: boolean;
  status: string;
  seats: Seat[];
  open_seats: number;
  your_seat?: number | null;
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
  if (res.status === 401 && !path.startsWith("/api/auth/login")) throw new AuthError("Not signed in");
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
}

export interface OptionView {
  id: string;
  label: string;
  irreversible: boolean;
  reason: string | null;
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
  away_pool: number;
  mission_tokens: number;
  missions_completed: string[];
}

export interface GameStateView {
  mode: GameMode;
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
  decision: { seat: number; kind: string; prompt: string; options?: OptionView[] } | null;
  log: string[];
  result: { reason: string; winners: number[]; rating?: string; scores?: { seat: number; name: string; total: number; parts: Record<string, number> }[] } | null;
  can_undo: boolean;
}

export interface CardText {
  name: string;
  suit: string;
  operations: { kind: string; text: string | null; action_cost: boolean; attack: boolean; requires: string | null }[];
}

function seatHeaders(id: string): Record<string, string> {
  const token = loadSeatToken(id);
  return token ? { "X-Seat-Token": token } : {};
}

export const api = {
  checkSession: () => request<null>("/api/auth/session").then(() => true),
  login: (password: string) =>
    request<void>("/api/auth/login", { method: "POST", body: JSON.stringify({ password }) }),
  logout: () => request<void>("/api/auth/logout", { method: "POST" }),
  decks: () => request<Deck[]>("/api/content/decks"),
  expansions: () => request<Record<string, string>>("/api/content/expansions"),
  games: () => request<Game[]>("/api/games"),
  game: (id: string) => {
    const token = loadSeatToken(id);
    return request<Game>(`/api/games/${id}`, { headers: token ? { "X-Seat-Token": token } : {} });
  },
  createGame: (body: SeatChoice & { mode: GameMode; expansions: string[]; promos: boolean }) =>
    request<SeatGrant>("/api/games", { method: "POST", body: JSON.stringify(body) }),
  cardText: () => request<Record<string, CardText>>("/api/content/cards"),
  state: (id: string) => request<GameStateView>(`/api/games/${id}/state`, { headers: seatHeaders(id) }),
  command: (id: string, option: string) =>
    request<GameStateView>(`/api/games/${id}/commands`, { method: "POST", body: JSON.stringify({ option }), headers: seatHeaders(id) }),
  undo: (id: string) => request<GameStateView>(`/api/games/${id}/undo`, { method: "POST", headers: seatHeaders(id) }),
  deleteGame: (id: string) => request<null>(`/api/games/${id}`, { method: "DELETE", headers: seatHeaders(id) }),
  joinGame: (id: string, body: SeatChoice) =>
    request<SeatGrant>(`/api/games/${id}/join`, { method: "POST", body: JSON.stringify(body) }),
};

export const MODE_LABELS: Record<GameMode, string> = {
  two_player: "Two players",
  solo: "Solo vs Bot",
  cadet: "Cadet Training",
};
