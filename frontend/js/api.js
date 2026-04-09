/**
 * api.js — Camada de acesso à API REST.
 * Centraliza todas as chamadas fetch. Nunca chame fetch() direto nas páginas.
 */

const API_BASE =
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : '';   // mesmo domínio em produção (Render/Railway servindo frontend junto)

// ─── Helpers ─────────────────────────────────────────────────────────────────

function _getToken() {
    return localStorage.getItem('token');
}

function _headers(json = true) {
    const h = {};
    if (json) h['Content-Type'] = 'application/json';
    const token = _getToken();
    if (token) h['Authorization'] = `Bearer ${token}`;
    return h;
}

async function _handle(response) {
    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        window.location.href = '/login.html';
    }
    const text = await response.text();
    const data = text ? JSON.parse(text) : {};
    if (!response.ok) {
        const msg = data?.detail || response.statusText || 'Erro desconhecido';
        throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return data;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

const API = {

    login: async (email, senha) => {
        const body = new URLSearchParams({ username: email, password: senha });
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body,
        });
        return _handle(res);
    },

    register: async ({ nome, email, senha, nivel = 'tecnico' }) => {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: _headers(),
            body: JSON.stringify({ nome, email, senha, nivel }),
        });
        return _handle(res);
    },

    getMe: async () => {
        const res = await fetch(`${API_BASE}/api/auth/me`, { headers: _headers() });
        return _handle(res);
    },

    // ─── Artigos ───────────────────────────────────────────────────────────

    getArtigos: async (params = {}) => {
        const qs = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/artigos/${qs ? '?' + qs : ''}`, {
            headers: _headers(),
        });
        return _handle(res);
    },

    getArtigo: async (id) => {
        const res = await fetch(`${API_BASE}/api/artigos/${id}`, { headers: _headers() });
        return _handle(res);
    },

    getPopulares: async () => {
        const res = await fetch(`${API_BASE}/api/artigos/populares`, { headers: _headers() });
        return _handle(res);
    },

    getRecentes: async () => {
        const res = await fetch(`${API_BASE}/api/artigos/recentes`, { headers: _headers() });
        return _handle(res);
    },

    buscar: async (q) => {
        const res = await fetch(
            `${API_BASE}/api/artigos/busca?q=${encodeURIComponent(q)}`,
            { headers: _headers() }
        );
        return _handle(res);
    },

    createArtigo: async (data) => {
        const res = await fetch(`${API_BASE}/api/artigos/`, {
            method: 'POST',
            headers: _headers(),
            body: JSON.stringify(data),
        });
        return _handle(res);
    },

    updateArtigo: async (id, data) => {
        const res = await fetch(`${API_BASE}/api/artigos/${id}`, {
            method: 'PUT',
            headers: _headers(),
            body: JSON.stringify(data),
        });
        return _handle(res);
    },

    deleteArtigo: async (id) => {
        const res = await fetch(`${API_BASE}/api/artigos/${id}`, {
            method: 'DELETE',
            headers: _headers(),
        });
        if (res.status === 204) return {};
        return _handle(res);
    },

    visualizar: async (id) => {
        const res = await fetch(`${API_BASE}/api/artigos/${id}/visualizar`, {
            method: 'POST',
            headers: _headers(),
        });
        return _handle(res);
    },

    // ─── Categorias ────────────────────────────────────────────────────────

    getCategorias: async () => {
        const res = await fetch(`${API_BASE}/api/categorias/`, { headers: _headers() });
        return _handle(res);
    },
};

window.API = API;
