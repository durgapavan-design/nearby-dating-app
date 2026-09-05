const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function clearToken() {
  localStorage.removeItem("access_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> | undefined),
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore body parse failure
    }
    throw new Error(detail);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export interface OtpRequestResponse {
  message: string;
  debug_code: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  is_new_user: boolean;
  profile_completed: boolean;
}

export interface Photo {
  id: string;
  url: string;
  position: number;
  is_primary: boolean;
}

export interface Interest {
  id: string;
  name: string;
  category: string;
}

export interface Me {
  id: string;
  phone_number: string;
  name: string | null;
  birthdate: string | null;
  gender: string | null;
  show_me: string | null;
  bio: string | null;
  city: string | null;
  location_source: string;
  profile_completed: boolean;
  photos: Photo[];
  interests: Interest[];
}

export interface DiscoveryProfile {
  id: string;
  name: string | null;
  age: number | null;
  bio: string | null;
  city: string | null;
  photos: Photo[];
  interests: Interest[];
  shared_interest_count: number;
}

export interface SwipeResult {
  matched: boolean;
  match_id: string | null;
}

export interface MatchSummary {
  match_id: string;
  user_id: string;
  name: string | null;
  primary_photo: Photo | null;
  created_at: string;
  last_message: string | null;
  last_message_at: string | null;
}

export interface LikedMe {
  user_id: string;
  name: string | null;
  primary_photo: Photo | null;
  liked_at: string;
}

export interface ChatMessage {
  id: string;
  match_id: string;
  sender_id: string;
  content: string;
  created_at: string;
  read_at: string | null;
}

export const api = {
  requestOtp: (phone_number: string) =>
    request<OtpRequestResponse>("/auth/otp/request", { method: "POST", body: JSON.stringify({ phone_number }) }),
  verifyOtp: (phone_number: string, code: string) =>
    request<TokenResponse>("/auth/otp/verify", { method: "POST", body: JSON.stringify({ phone_number, code }) }),

  getMe: () => request<Me>("/me"),
  updateMe: (payload: Partial<Pick<Me, "name" | "birthdate" | "gender" | "show_me" | "bio" | "city">>) =>
    request<Me>("/me", { method: "PUT", body: JSON.stringify(payload) }),
  updateMyInterests: (interest_ids: string[]) =>
    request<Me>("/me/interests", { method: "PUT", body: JSON.stringify({ interest_ids }) }),
  uploadPhoto: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Photo>("/me/photos", { method: "POST", body: form });
  },
  deletePhoto: (photoId: string) => request<void>(`/me/photos/${photoId}`, { method: "DELETE" }),

  listCities: () => request<string[]>("/meta/cities"),
  listInterests: () => request<Interest[]>("/interests"),

  getFeed: () => request<DiscoveryProfile[]>("/discovery/feed"),
  swipe: (target_id: string, action: "like" | "pass") =>
    request<SwipeResult>("/discovery/swipe", { method: "POST", body: JSON.stringify({ target_id, action }) }),

  listMatches: () => request<MatchSummary[]>("/matches"),
  listLikedMe: () => request<LikedMe[]>("/matches/liked-me"),

  getMessages: (matchId: string) => request<ChatMessage[]>(`/matches/${matchId}/messages`),
  sendMessage: (matchId: string, content: string) =>
    request<ChatMessage>(`/matches/${matchId}/messages`, { method: "POST", body: JSON.stringify({ content }) }),
};

export function mediaUrl(path: string): string {
  return `${API_URL}${path}`;
}

export function wsUrl(matchId: string): string {
  const base = API_URL.replace(/^http/, "ws");
  return `${base}/ws/chat/${matchId}?token=${encodeURIComponent(getToken() || "")}`;
}
