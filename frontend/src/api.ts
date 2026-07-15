const API_BASE_URL = "http://localhost:8000";

export class ApiError extends Error {}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };

  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    // FastAPI sends errors as { "detail": "..." } — read that specifically
    // so error messages shown in the UI are actually meaningful.
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail || `Request failed (${response.status})`);
  }

  if (response.status === 204) return undefined as T; // delete has no body
  return response.json();
}

export interface User {
  id: number;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function signup(email: string, password: string): Promise<User> {
  return request<User>("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  // /auth/login expects OAuth2's standard form-encoded shape, not JSON —
  // the same "username"/"password" fields Swagger's Authorize button used.
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: form,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

export function getMe(token: string): Promise<User> {
  return request<User>("/auth/me", {}, token);
}

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string | null;
}

export function listNotes(token: string): Promise<Note[]> {
  return request<Note[]>("/notes", {}, token);
}

export function createNote(token: string, title: string, content: string): Promise<Note> {
  return request<Note>("/notes", { method: "POST", body: JSON.stringify({ title, content }) }, token);
}

export function updateNote(
  token: string,
  id: number,
  data: { title?: string; content?: string }
): Promise<Note> {
  return request<Note>(`/notes/${id}`, { method: "PUT", body: JSON.stringify(data) }, token);
}

export function deleteNote(token: string, id: number): Promise<void> {
  return request<void>(`/notes/${id}`, { method: "DELETE" }, token);
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export interface ChatHistoryItem {
  role: "user" | "assistant";
  content: string;
}

export function sendChatMessage(
  token: string,
  question: string,
  history: ChatHistoryItem[]
): Promise<ChatResponse> {
  return request<ChatResponse>(
    "/chat",
    { method: "POST", body: JSON.stringify({ question, history }) },
    token
  );
}