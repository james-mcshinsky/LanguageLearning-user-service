export const API_BASE = (window as any).API_BASE || '';
export function apiFetch(path: string, options?: RequestInit) {
  return fetch(`${API_BASE}${path}`, options);
}
