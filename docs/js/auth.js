/**
 * auth.js — Singleton de sessão + helpers de navbar.
 * Carregue ANTES de qualquer outro script nas páginas protegidas.
 */

class SessionManager {
    static #instance = null;

    static getInstance() {
        if (!SessionManager.#instance) {
            SessionManager.#instance = new SessionManager();
        }
        return SessionManager.#instance;
    }

    constructor() {
        this.token   = localStorage.getItem('token')   || null;
        this.usuario = JSON.parse(localStorage.getItem('usuario') || 'null');
    }

    login(usuario, token) {
        this.token   = token;
        this.usuario = usuario;
        localStorage.setItem('token',   token);
        localStorage.setItem('usuario', JSON.stringify(usuario));
    }

    logout() {
        this.token   = null;
        this.usuario = null;
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        window.location.href = '/login.html';
    }

    isAuthenticated() { return !!this.token; }
    isAdmin()         { return this.usuario?.nivel === 'admin'; }
    getNome()         { return this.usuario?.nome || 'Usuário'; }
}

// Função global usada pelo atributo onclick="logout()"
function logout() { SessionManager.getInstance().logout(); }

// Atualiza navbar com nome do usuário logado
document.addEventListener('DOMContentLoaded', () => {
    const session = SessionManager.getInstance();
    const dropdown = document.getElementById('usuarioDropdown');
    if (!dropdown) return;

    if (session.isAuthenticated()) {
        const firstName = session.getNome().split(' ')[0];
        dropdown.innerHTML = `<i class="bi bi-person-circle"></i> ${firstName}`;

        // Exibe botões de admin quando aplicável
        if (session.isAdmin()) {
            document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('d-none'));
        }
    } else {
        dropdown.innerHTML = `<a href="login.html" class="nav-link"><i class="bi bi-box-arrow-in-right"></i> Entrar</a>`;
    }
});
