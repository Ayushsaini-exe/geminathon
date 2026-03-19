/**
 * AgroFix API client — thin fetch wrapper with JWT auth headers.
 */

const API_BASE = window.location.origin;

async function request(path, options = {}) {
  const token = localStorage.getItem('agrofix_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    localStorage.removeItem('agrofix_token');
    localStorage.removeItem('agrofix_user');
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Something went wrong' }));
    throw new Error(err.detail || `Error ${res.status}`);
  }

  return res.json();
}

const api = {
  get:  (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put:  (path, body) => request(path, { method: 'PUT',  body: JSON.stringify(body) }),
};

export default api;
