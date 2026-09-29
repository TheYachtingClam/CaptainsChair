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

export function loadSeatToken(gameId: string): string | null {
  try {
    return localStorage.getItem(seatKey(gameId));
  } catch {
    return null;
  }
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
  createGame: (body: SeatChoice & { mode: GameMode; expansions: string[] }) =>
    request<SeatGrant>("/api/games", { method: "POST", body: JSON.stringify(body) }),
  joinGame: (id: string, body: SeatChoice) =>
    request<SeatGrant>(`/api/games/${id}/join`, { method: "POST", body: JSON.stringify(body) }),
};

export const MODE_LABELS: Record<GameMode, string> = {
  two_player: "Two players",
  solo: "Solo vs Bot",
  cadet: "Cadet Training",
};
