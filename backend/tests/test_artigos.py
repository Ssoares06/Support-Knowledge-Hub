def _register_and_login(client, email, nivel="tecnico"):
    client.post("/api/auth/register", json={
        "nome": "User", "email": email, "senha": "pwd123", "nivel": nivel
    })
    return client.post("/api/auth/login", data={
        "username": email, "password": "pwd123"
    }).json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_article_authenticated(client):
    token = _register_and_login(client, "tec@test.com")
    res = client.post("/api/artigos/", json={
        "titulo": "Erro XPTO", "problema": "Não liga", "solucao": "Reiniciar"
    }, headers=_auth(token))
    assert res.status_code == 201
    assert res.json()["titulo"] == "Erro XPTO"


def test_create_article_unauthenticated_fails(client):
    res = client.post("/api/artigos/", json={
        "titulo": "Erro", "problema": "A", "solucao": "B"
    })
    assert res.status_code == 401


def test_get_all_articles(client):
    token = _register_and_login(client, "tec@test.com")
    client.post("/api/artigos/", json={
        "titulo": "Artigo 1", "problema": "P", "solucao": "S"
    }, headers=_auth(token))
    res = client.get("/api/artigos/")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_article_by_id(client):
    token = _register_and_login(client, "tec@test.com")
    created = client.post("/api/artigos/", json={
        "titulo": "Artigo ID", "problema": "P", "solucao": "S"
    }, headers=_auth(token)).json()
    res = client.get(f"/api/artigos/{created['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_get_article_not_found(client):
    res = client.get("/api/artigos/9999")
    assert res.status_code == 404


def test_update_article(client):
    token = _register_and_login(client, "tec@test.com")
    created = client.post("/api/artigos/", json={
        "titulo": "Original", "problema": "P", "solucao": "S"
    }, headers=_auth(token)).json()
    res = client.put(f"/api/artigos/{created['id']}", json={
        "titulo": "Atualizado"
    }, headers=_auth(token))
    assert res.status_code == 200
    assert res.json()["titulo"] == "Atualizado"


def test_delete_article_as_admin(client):
    tec_token = _register_and_login(client, "tec@test.com")
    adm_token = _register_and_login(client, "adm@test.com", nivel="admin")
    created = client.post("/api/artigos/", json={
        "titulo": "Para Deletar", "problema": "P", "solucao": "S"
    }, headers=_auth(tec_token)).json()
    res = client.delete(f"/api/artigos/{created['id']}", headers=_auth(adm_token))
    assert res.status_code == 204


def test_delete_article_as_tecnico_fails(client):
    token = _register_and_login(client, "tec@test.com")
    created = client.post("/api/artigos/", json={
        "titulo": "Protegido", "problema": "P", "solucao": "S"
    }, headers=_auth(token)).json()
    res = client.delete(f"/api/artigos/{created['id']}", headers=_auth(token))
    assert res.status_code == 403


def test_search_articles_by_query(client):
    token = _register_and_login(client, "tec@test.com")
    client.post("/api/artigos/", json={
        "titulo": "Impressora offline", "problema": "Impressora sem sinal", "solucao": "Reiniciar spooler"
    }, headers=_auth(token))
    res = client.get("/api/artigos/busca?q=impressora")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_populares(client):
    res = client.get("/api/artigos/populares")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_recentes(client):
    res = client.get("/api/artigos/recentes")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
