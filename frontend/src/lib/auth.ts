export type Role = "administrator" | "teacher" | "student";

export interface AuthSession {
  accessToken: string;
  refreshToken: string;
  tokenType: "bearer";
  role: Role;
  userId: number;
  orgId?: number;
  expiresAt?: string;
}

type JwtPayload = {
  sub?: string;
  exp?: number;
  role?: Role;
  org_id?: number;
};

const STORAGE_KEY = "aalp.auth";
let memorySession: AuthSession | null = null;

function readStoredSession(): string | null {
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredSession(raw: string): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, raw);
  } catch {
    memorySession = JSON.parse(raw) as AuthSession;
  }
}

function removeStoredSession(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    memorySession = null;
  }
}

function decodeBase64Url(input: string): string {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), "=");
  return atob(padded);
}

export function decodeJwt(token: string): JwtPayload | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) {
      return null;
    }
    return JSON.parse(decodeBase64Url(payload)) as JwtPayload;
  } catch {
    return null;
  }
}

export function getAuthSession(): AuthSession | null {
  if (memorySession) {
    return memorySession;
  }

  const raw = readStoredSession();
  if (!raw) {
    return null;
  }
  try {
    memorySession = JSON.parse(raw) as AuthSession;
    return memorySession;
  } catch {
    return null;
  }
}

export function getAccessToken(): string | null {
  return getAuthSession()?.accessToken ?? null;
}

export function getRefreshToken(): string | null {
  return getAuthSession()?.refreshToken ?? null;
}

export function getCurrentRole(): Role | null {
  return getAuthSession()?.role ?? null;
}

export function saveAuthSession(session: AuthSession): void {
  memorySession = session;
  writeStoredSession(JSON.stringify(session));
  window.dispatchEvent(new Event("aalp-auth-changed"));
}

export function clearAuthSession(): void {
  memorySession = null;
  removeStoredSession();
  window.dispatchEvent(new Event("aalp-auth-changed"));
}

export function createSessionFromTokens(accessToken: string, refreshToken: string): AuthSession {
  const payload = decodeJwt(accessToken);
  const userId = Number(payload?.sub ?? 0);
  const expiresAt = payload?.exp ? new Date(payload.exp * 1000).toISOString() : undefined;
  const role = payload?.role ?? "student";

  return {
    accessToken,
    refreshToken,
    tokenType: "bearer",
    role,
    userId,
    orgId: payload?.org_id,
    expiresAt,
  };
}

export function getDashboardPath(role: Role | null | undefined): string {
  switch (role) {
    case "administrator":
      return "/admin/dashboard";
    case "teacher":
      return "/teacher/dashboard";
    case "student":
      return "/student/dashboard";
    default:
      return "/login";
  }
}
