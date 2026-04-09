# Support Knowledge Hub

Base de conhecimento técnico para equipes de suporte. Permite cadastrar, buscar e compartilhar soluções para problemas recorrentes em sistemas como GLPI, Colmeia e Infraestrutura.

---

## Tecnologias

| Camada | Stack |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy · Pydantic v2 |
| Banco relacional | PostgreSQL (produção) · SQLite (dev) |
| Banco NoSQL | MongoDB via Motor (logs de busca) |
| Autenticação | JWT · passlib bcrypt · python-jose |
| Frontend | HTML5 · Bootstrap 5 · Vanilla JS |
| Testes | Pytest · httpx |
| Deploy | Railway / Render · Docker |

---

## Estrutura do Projeto

```
support-knowledge-hub/
├── backend/
│   ├── main.py                  # Entrypoint FastAPI
│   ├── database.py              # Conexão SQLAlchemy + MongoDB
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
│   │   └── artigo_service.py    # log MongoDB
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
│       ├── api.js               # Todas as chamadas HTTP
│       ├── auth.js              # SessionManager (Singleton)
│       └── app.js               # Lógica por página
├── Dockerfile
├── docker-compose.yml
├── Procfile                     # Railway/Render
├── requirements.txt
└── .gitignore
```

---

## Rodando Localmente (sem Docker)

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/seu-usuario/support-knowledge-hub.git
cd support-knowledge-hub

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

```bash
cp backend/.env.example backend/.env
# Edite backend/.env se quiser usar PostgreSQL em vez de SQLite
```

### 3. Inicie a API

```bash
uvicorn backend.main:app --reload
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

### 4. Frontend

Abra qualquer arquivo HTML de `frontend/` diretamente no navegador, ou sirva com:

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
| MongoDB | localhost:27017 |

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL de conexão PostgreSQL ou SQLite | `sqlite:///./support_hub.db` |
| `MONGODB_URL` | URL MongoDB (opcional) | `mongodb://localhost:27017` |
| `MONGO_DB_NAME` | Nome do banco MongoDB | `support_hub_logs` |
| `SECRET_KEY` | Chave para assinar JWT | *(obrigatório em produção)* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token JWT | `1440` (24h) |

---

## Endpoints da API

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
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"João","email":"joao@example.com","senha":"minhasenha"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=joao@example.com&password=minhasenha"
```

**Criar artigo (com token):**
```bash
curl -X POST http://localhost:8000/api/artigos/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Erro GLPI","problema":"Tela branca","solucao":"Reiniciar Apache","sistema":"GLPI"}'
```

---

## Testes

```bash
# Na raiz do projeto
pytest backend/tests/ -v
```

---

## Deploy (Railway / Render)

1. Conecte o repositório ao Railway ou Render
2. Configure as variáveis de ambiente no painel da plataforma
3. O `Procfile` já define o comando de inicialização:
   ```
   web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
4. Para o banco, use Supabase (PostgreSQL gratuito) e defina `DATABASE_URL`

---

## Padrões de Projeto (Frontend)

| Padrão | Onde | Descrição |
|---|---|---|
| **Singleton** | `auth.js` · `SessionManager` | Única instância de sessão por aba |
| **Facade** | `app.js` · funções `init*` | Interface simples sobre chamadas de API complexas |
| **Module** | `api.js` · objeto `API` | Encapsula toda camada HTTP |

---

## Licença

MIT
