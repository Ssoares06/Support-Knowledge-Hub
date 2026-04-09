def test_register_user(client):
    res = client.post("/api/auth/register", json={
        "nome": "Test User",
        "email": "test@test.com",
        "senha": "password123",
    })
    assert res.status_code == 201
    assert res.json()["email"] == "test@test.com"


def test_register_duplicate_email_fails(client):
    payload = {"nome": "User", "email": "dup@test.com", "senha": "password123"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400


def test_login_returns_token(client):
    client.post("/api/auth/register", json={
        "nome": "Test User", "email": "test@test.com", "senha": "password123"
    })
    res = client.post("/api/auth/login", data={
        "username": "test@test.com", "password": "password123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={
        "nome": "Test User", "email": "test@test.com", "senha": "password123"
    })
    res = client.post("/api/auth/login", data={
        "username": "test@test.com", "password": "wrong"
    })
    assert res.status_code == 401


def test_protected_route_without_token_fails(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_get_me_authenticated(client):
    client.post("/api/auth/register", json={
        "nome": "Test User", "email": "test@test.com", "senha": "password123"
    })
    token = client.post("/api/auth/login", data={
        "username": "test@test.com", "password": "password123"
    }).json()["access_token"]

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "test@test.com"
