# Support Knowledge Hub

Base de conhecimento técnico para equipes de suporte. Permite cadastrar, buscar e compartilhar soluções para problemas recorrentes em sistemas como GLPI, Colmeia e Infraestrutura.

> **API em produção:** https://support-hub-api-14z3.onrender.com  
> **Documentação interativa (Swagger):** https://support-hub-api-14z3.onrender.com/docs

---

## Integrantes

| Nome |
|---|
| André Soares |
| Jullyanne Roberta |
| Rebeka Natália |
| Nayara G. |

---

## Tecnologias

| Camada | Stack |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy · Pydantic v2 |
| Banco relacional | PostgreSQL (produção) · SQLite (dev) |
| Autenticação | JWT · bcrypt · python-jose |
| Frontend | HTML5 · Bootstrap 5 · Vanilla JS |
| Testes | Pytest · httpx |
| Deploy | Render · Docker |

---

## Padrões de Projeto

### 1AV — Padrões da Unidade 1

#### Singleton — `frontend/js/auth.js`

A classe `SessionManager` garante que existe **uma única instância** de controle de sessão por aba do navegador. Isso evita que o token JWT seja lido ou sobrescrito por múltiplas instâncias concorrentes.

```js
// frontend/js/auth.js
class SessionManager {
  static #instance = null;

  static getInstance() {
    if (!SessionManager.#instance) {
      SessionManager.#instance = new SessionManager();
    }
    return SessionManager.#instance;
  }
  // ...
}
```

**Por que Singleton?** O estado de autenticação (token, dados do usuário) precisa ser consistente em toda a aplicação. Criar múltiplas instâncias poderia causar dessincronização entre páginas ou componentes que leem o localStorage.

---

#### Facade — `frontend/js/api.js`

O objeto `API` funciona como uma **fachada** sobre a API fetch nativa do navegador. Todo o frontend chama métodos simples como `API.get()` ou `API.post()` — sem precisar conhecer headers, tratamento de erros HTTP ou lógica de token.

```js
// frontend/js/api.js
const API = {
  async get(endpoint) {
    const res = await fetch(BASE_URL + endpoint, {
      headers: { Authorization: `Bearer ${SessionManager.getInstance().getToken()}` }
    });
    if (!res.ok) throw await res.json();
    return res.json();
  },
  async post(endpoint, body) { /* ... */ },
  async put(endpoint, body)  { /* ... */ },
  async delete(endpoint)     { /* ... */ },
};
```

**Por que Facade?** O frontend tem múltiplas páginas (artigos, login, perfil, dashboard). Sem a fachada, cada página precisaria reimplementar a lógica de autenticação, tratamento de erros e serialização. A fachada centraliza isso em um único lugar.

---

## Estrutura do Projeto

```
support-knowledge-hub/
├── backend/
│   ├── main.py                  # Entrypoint FastAPI
│   ├── database.py              # Conexão SQLAlchemy
│   ├── models/                  # ORM SQLAlchemy
│   │   ├── usuario.py
│   │   ├── categoria.py
│   │   ├── artigo.py
│   │   └── visualizacao.py
│   ├── schemas/                 # Pydantic v2
│   │   ├── usuario.py
│   │   ├── categoria.py
│   │   ├── artigo.py
│   │   └── visualizacao.py
│   ├── routers/                 # Rotas REST
│   │   ├── auth.py              → /api/auth
│   │   ├── artigos.py           → /api/artigos
│   │   ├── categorias.py        → /api/categorias
│   │   └── usuarios.py          → /api/usuarios
│   ├── services/
│   │   ├── auth_service.py      # bcrypt + JWT
│   │   └── artigo_service.py    # lógica de negócio
│   ├── middleware/
│   │   └── auth_middleware.py   # Verificação JWT
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_artigos.py
│   │   ├── test_categorias.py
│   │   └── test_usuarios.py
│   └── .env.example
├── frontend/
│   ├── index.html               # Dashboard
│   ├── artigos.html             # Lista + filtros
│   ├── artigo-detalhe.html      # Detalhe do artigo
│   ├── criar-artigo.html        # Formulário de criação
│   ├── login.html
│   ├── registro.html
│   ├── perfil.html
│   ├── css/style.css
│   └── js/
│       ├── api.js               # Facade — camada HTTP centralizada
│       ├── auth.js              # Singleton — SessionManager
│       └── app.js               # Lógica por página
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── requirements.txt
└── .gitignore
```

---

## Banco de Dados

O projeto usa **PostgreSQL** com 4 tabelas relacionais:

| Tabela | Descrição |
|---|---|
| `usuarios` | Cadastro e autenticação de usuários |
| `categorias` | Categorias dos artigos (ex: GLPI, Infraestrutura) |
| `artigos` | Base de conhecimento — problema, solução, sistema |
| `visualizacoes` | Histórico de leituras por usuário |

---

## Endpoints da API

Documentação completa e interativa disponível em:  
**https://support-hub-api-14z3.onrender.com/docs**

### Auth — `/api/auth`

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Cadastrar usuário | Não |
| POST | `/api/auth/login` | Login, retorna JWT | Não |
| GET | `/api/auth/me` | Dados do usuário logado | Sim |

### Artigos — `/api/artigos`

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/artigos/` | Listar artigos (com filtros) | Não |
| GET | `/api/artigos/populares` | Top 5 mais visualizados | Não |
| GET | `/api/artigos/recentes` | Últimos 5 criados | Não |
| GET | `/api/artigos/busca?q=termo` | Busca full-text | Não |
| GET | `/api/artigos/{id}` | Detalhe de um artigo | Não |
| POST | `/api/artigos/` | Criar artigo | Sim |
| PUT | `/api/artigos/{id}` | Editar artigo | Sim (autor ou admin) |
| DELETE | `/api/artigos/{id}` | Excluir artigo | Sim (admin) |
| POST | `/api/artigos/{id}/visualizar` | Registrar visualização | Sim |

**Query params de filtragem:** `?sistema=GLPI&categoria_id=1&autor_id=2&q=erro&page=1&limit=10`

### Categorias — `/api/categorias`

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/categorias/` | Listar categorias | Não |
| GET | `/api/categorias/{id}` | Detalhe | Não |
| POST | `/api/categorias/` | Criar | Sim (admin) |
| PUT | `/api/categorias/{id}` | Editar | Sim (admin) |
| DELETE | `/api/categorias/{id}` | Excluir | Sim (admin) |

### Usuários — `/api/usuarios`

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET | `/api/usuarios/` | Listar usuários | Sim (admin) |
| GET | `/api/usuarios/{id}` | Ver perfil | Sim |
| PUT | `/api/usuarios/{id}` | Editar | Sim (dono ou admin) |
| DELETE | `/api/usuarios/{id}` | Excluir | Sim (admin) |

---

## Exemplos de Requisição

**Registrar usuário:**
```bash
curl -X POST https://support-hub-api-14z3.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"João","email":"joao@example.com","senha":"minhasenha"}'
```

**Login:**
```bash
curl -X POST https://support-hub-api-14z3.onrender.com/api/auth/login \
  -d "username=joao@example.com&password=minhasenha"
```

**Criar artigo (com token):**
```bash
curl -X POST https://support-hub-api-14z3.onrender.com/api/artigos/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Erro GLPI","problema":"Tela branca","solucao":"Reiniciar Apache","sistema":"GLPI"}'
```

---

## Rodando Localmente

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/Ssoares06/Support-Knowledge-Hub.git
cd Support-Knowledge-Hub

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

```bash
cp backend/.env.example backend/.env
# Por padrão usa SQLite — não precisa de PostgreSQL para rodar localmente
```

### 3. Inicie a API

```bash
uvicorn backend.main:app --reload
```

API disponível em `http://localhost:8000`  
Swagger em `http://localhost:8000/docs`

### 4. Frontend

```bash
cd frontend
python -m http.server 3000
# Acesse http://localhost:3000
```

---

## Rodando com Docker

```bash
docker-compose up --build
```

| Serviço | URL |
|---|---|
| API FastAPI | http://localhost:8000 |
| Docs Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

---

## Testes

```bash
pytest backend/tests/ -v
# 26 testes — 0 falhas
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL ou SQLite | `sqlite:///./support_hub.db` |
| `SECRET_KEY` | Chave para assinar JWT | *(obrigatório em produção)* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token | `1440` (24h) |

---

## Licença

MIT