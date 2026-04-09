def _admin_token(client):
    client.post("/api/auth/register", json={
        "nome": "Admin", "email": "admin@test.com", "senha": "password", "nivel": "admin"
    })
    return client.post("/api/auth/login", data={
        "username": "admin@test.com", "password": "password"
    }).json()["access_token"]


def test_create_category(client):
    token = _admin_token(client)
    res = client.post("/api/categorias/", json={
        "nome": "Redes", "descricao": "Problemas de Rede"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert res.json()["nome"] == "Redes"


def test_create_duplicate_category_fails(client):
    token = _admin_token(client)
    payload = {"nome": "Hardware"}
    client.post("/api/categorias/", json=payload, headers={"Authorization": f"Bearer {token}"})
    res = client.post("/api/categorias/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400


def test_list_categories(client):
    token = _admin_token(client)
    client.post("/api/categorias/", json={"nome": "Software"}, headers={"Authorization": f"Bearer {token}"})
    res = client.get("/api/categorias/")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_category_by_id(client):
    token = _admin_token(client)
    created = client.post("/api/categorias/", json={"nome": "BD"}, headers={"Authorization": f"Bearer {token}"}).json()
    res = client.get(f"/api/categorias/{created['id']}")
    assert res.status_code == 200


def test_delete_category(client):
    token = _admin_token(client)
    created = client.post("/api/categorias/", json={"nome": "Temp"}, headers={"Authorization": f"Bearer {token}"}).json()
    res = client.delete(f"/api/categorias/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 204


def test_create_category_as_tecnico_fails(client):
    client.post("/api/auth/register", json={
        "nome": "Tec", "email": "tec@test.com", "senha": "pwd123", "nivel": "tecnico"
    })
    token = client.post("/api/auth/login", data={
        "username": "tec@test.com", "password": "pwd123"
    }).json()["access_token"]
    res = client.post("/api/categorias/", json={"nome": "Negado"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
