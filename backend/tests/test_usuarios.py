def test_get_usuarios_admin(client):
    client.post("/api/auth/register", json={
        "nome": "Admin", "email": "adm@test.com", "senha": "pwd", "nivel": "admin"
    })
    token = client.post("/api/auth/login", data={
        "username": "adm@test.com", "password": "pwd"
    }).json()["access_token"]
    res = client.get("/api/usuarios/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_usuarios_tecnico_fails(client):
    client.post("/api/auth/register", json={
        "nome": "Tec", "email": "tec@test.com", "senha": "pwd", "nivel": "tecnico"
    })
    token = client.post("/api/auth/login", data={
        "username": "tec@test.com", "password": "pwd"
    }).json()["access_token"]
    res = client.get("/api/usuarios/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_get_own_profile(client):
    client.post("/api/auth/register", json={
        "nome": "Tec", "email": "tec@test.com", "senha": "pwd"
    })
    login = client.post("/api/auth/login", data={
        "username": "tec@test.com", "password": "pwd"
    }).json()
    token = login["access_token"]
    # get own id via /me
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    res = client.get(f"/api/usuarios/{me['id']}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
