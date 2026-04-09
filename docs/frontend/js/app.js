/**
 * app.js — Orquestrador de páginas.
 * Depende de: api.js, auth.js (carregados antes).
 */

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.endsWith('index.html') || path === '/' || path === '') {
        initDashboard();
    } else if (path.includes('artigos.html')) {
        initListaArtigos();
    } else if (path.includes('artigo-detalhe.html')) {
        initDetalheArtigo();
    } else if (path.includes('criar-artigo.html')) {
        initCriarArtigo();
    }
});

// ─── Helpers de renderização ──────────────────────────────────────────────────

const BADGE_COR = {
    GLPI:           'primary',
    Colmeia:        'warning text-dark',
    Infraestrutura: 'info text-dark',
    Redes:          'danger',
    MV:             'dark',
    Windows:        'secondary',
};

const BADGE_ICONE = {
    GLPI:           '<i class="bi bi-ticket-detailed"></i>',
    Colmeia:        '<i class="bi bi-shop"></i>',
    Infraestrutura: '<i class="bi bi-pc-display"></i>',
    Redes:          '<i class="bi bi-router"></i>',
    MV:             '<i class="bi bi-hospital"></i>',
    Windows:        '<i class="bi bi-windows"></i>',
};

function badgeCor(sistema)   { return BADGE_COR[sistema]   || 'secondary'; }
function badgeIcone(sistema) { return BADGE_ICONE[sistema] || '<i class="bi bi-file-text"></i>'; }

function formatarData(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('pt-BR');
}

function cardArtigo(a) {
    return `
    <div class="col-md-4 mb-4">
      <div class="card h-100 shadow-sm article-card">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="badge bg-${badgeCor(a.sistema)}">
              ${badgeIcone(a.sistema)} ${a.sistema || 'Geral'}
            </span>
            <small class="text-muted"><i class="bi bi-eye"></i> ${a.total_visualizacoes}</small>
          </div>
          <h5 class="card-title fw-bold">${a.titulo}</h5>
          <p class="card-text text-muted small mb-3">
            ${(a.problema || '').substring(0, 90)}${(a.problema || '').length > 90 ? '…' : ''}
          </p>
          <a href="artigo-detalhe.html?id=${a.id}" class="btn btn-outline-primary btn-sm stretched-link">
            Ler Solução <i class="bi bi-arrow-right"></i>
          </a>
        </div>
        <div class="card-footer bg-white border-top-0 pt-0">
          <small class="text-muted">
            Por ${a.autor?.nome || 'Sistema'} em ${formatarData(a.data_criacao)}
          </small>
        </div>
      </div>
    </div>`;
}

// ─── Dashboard (index.html) ───────────────────────────────────────────────────

async function initDashboard() {
    // Busca por termo no submit do form
    const formBusca = document.getElementById('form-busca');
    if (formBusca) {
        formBusca.addEventListener('submit', (e) => {
            e.preventDefault();
            const termo = document.getElementById('busca-input').value.trim();
            if (termo) window.location.href = `artigos.html?busca=${encodeURIComponent(termo)}`;
        });
    }

    // Mais acessados
    try {
        const populares = await API.getPopulares();
        const cont = document.getElementById('acessados-container');
        if (cont) {
            cont.innerHTML = populares.length
                ? populares.map(cardArtigo).join('')
                : '<p class="text-muted">Nenhum artigo encontrado.</p>';
        }
    } catch (_) {}

    // Recentes
    try {
        const recentes = await API.getRecentes();
        const cont = document.getElementById('recentes-container');
        if (cont) {
            cont.innerHTML = recentes.length
                ? recentes.map(cardArtigo).join('')
                : '<p class="text-muted">Nenhum artigo encontrado.</p>';
        }
    } catch (_) {}
}

// ─── Lista de artigos (artigos.html) ─────────────────────────────────────────

async function initListaArtigos() {
    // Carrega categorias no select
    try {
        const cats = await API.getCategorias();
        const sel = document.getElementById('filtro-categoria');
        if (sel) {
            cats.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.nome}</option>`;
            });
        }
    } catch (_) {}

    // Verifica se veio com ?busca= na URL
    const params = new URLSearchParams(window.location.search);
    const termoBusca = params.get('busca');
    if (termoBusca) {
        const input = document.getElementById('filtro-termo');
        if (input) input.value = termoBusca;
        await carregarArtigos({ q: termoBusca });
    } else {
        await carregarArtigos();
    }

    // Submit do form de filtros
    const form = document.getElementById('form-filtro');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const filtros = {};
            const termo      = document.getElementById('filtro-termo').value.trim();
            const sistema    = document.getElementById('filtro-sistema').value;
            const categoriaId = document.getElementById('filtro-categoria').value;
            if (termo)       filtros.q           = termo;
            if (sistema)     filtros.sistema      = sistema;
            if (categoriaId) filtros.categoria_id = categoriaId;
            await carregarArtigos(filtros);
        });

        form.addEventListener('reset', () => {
            setTimeout(() => carregarArtigos(), 50);
        });
    }
}

async function carregarArtigos(filtros = {}) {
    const lista = document.getElementById('artigos-lista');
    if (!lista) return;
    lista.innerHTML = '<div class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>';
    try {
        const artigos = await API.getArtigos(filtros);
        lista.innerHTML = artigos.length
            ? artigos.map(cardArtigo).join('')
            : '<div class="col-12"><p class="text-muted text-center py-4">Nenhum artigo encontrado.</p></div>';
    } catch (err) {
        lista.innerHTML = `<div class="col-12"><div class="alert alert-danger">Erro ao carregar artigos: ${err.message}</div></div>`;
    }
}

// ─── Detalhe do artigo (artigo-detalhe.html) ─────────────────────────────────

async function initDetalheArtigo() {
    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) { _erroDetalhe('ID do artigo não informado.'); return; }

    try {
        const a = await API.getArtigo(id);

        // Breadcrumb
        const bc = document.getElementById('breadcrumb-titulo');
        if (bc) bc.textContent = a.titulo;

        // Header
        document.getElementById('artigo-titulo').textContent  = a.titulo;
        document.getElementById('info-autor').textContent     = a.autor?.nome || 'Sistema';
        document.getElementById('info-data').textContent      = formatarData(a.data_criacao);
        document.getElementById('info-views').textContent     = a.total_visualizacoes;

        // Badges
        const badgeSis = document.getElementById('badge-sistema');
        if (badgeSis) {
            badgeSis.className = `badge bg-${badgeCor(a.sistema)} fs-6 me-1`;
            badgeSis.innerHTML = `${badgeIcone(a.sistema)} ${a.sistema || 'Geral'}`;
        }
        const badgeCat = document.getElementById('badge-categoria');
        if (badgeCat) badgeCat.textContent = a.categoria?.nome || 'Sem categoria';

        // Conteúdo
        document.getElementById('artigo-problema').textContent = a.problema;
        document.getElementById('artigo-solucao').textContent  = a.solucao;

        // Botões de admin
        const session = SessionManager.getInstance();
        if (session.isAdmin()) {
            const actionsAdmin = document.getElementById('acoes-admin');
            if (actionsAdmin) {
                actionsAdmin.classList.remove('d-none');
                actionsAdmin.querySelector('[data-action="delete"]')
                    ?.addEventListener('click', async () => {
                        if (!confirm('Excluir este artigo?')) return;
                        try {
                            await API.deleteArtigo(a.id);
                            window.location.href = 'artigos.html';
                        } catch (err) {
                            alert('Erro ao excluir: ' + err.message);
                        }
                    });
            }
        }

        // Registra visualização (fire-and-forget, só se autenticado)
        if (session.isAuthenticated()) {
            API.visualizar(id).catch(() => {});
        }

    } catch (err) {
        _erroDetalhe('Artigo não encontrado ou erro de conexão.');
    }
}

function _erroDetalhe(msg) {
    const cont = document.getElementById('artigo-conteudo');
    if (cont) cont.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
}

// ─── Criar artigo (criar-artigo.html) ────────────────────────────────────────

async function initCriarArtigo() {
    // Redireciona se não autenticado
    if (!SessionManager.getInstance().isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    // Carrega categorias
    try {
        const cats = await API.getCategorias();
        const sel = document.getElementById('categoria_id');
        if (sel) {
            cats.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.nome}</option>`;
            });
        }
    } catch (_) {}

    const form = document.getElementById('form-artigo');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!form.checkValidity()) { form.classList.add('was-validated'); return; }

        const payload = {
            titulo:       document.getElementById('titulo').value.trim(),
            sistema:      document.getElementById('sistema').value,
            categoria_id: parseInt(document.getElementById('categoria_id').value) || null,
            problema:     document.getElementById('problema').value.trim(),
            solucao:      document.getElementById('solucao').value.trim(),
        };

        const btnSalvar = form.querySelector('[type="submit"]');
        btnSalvar.disabled = true;
        btnSalvar.textContent = 'Salvando…';

        try {
            const criado = await API.createArtigo(payload);
            document.getElementById('mensagem-sucesso').classList.remove('d-none');
            setTimeout(() => window.location.href = `artigo-detalhe.html?id=${criado.id}`, 1500);
        } catch (err) {
            alert('Erro ao salvar: ' + err.message);
            btnSalvar.disabled = false;
            btnSalvar.innerHTML = '<i class="bi bi-save me-2"></i>Salvar e Publicar';
        }
    });
}
