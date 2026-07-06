"""Baseline API tests for the current mini-blog behavior."""


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def register_user(client, username="alice", password="secret"):
    """Register a user and return the registration payload."""
    response = client.post(
        "/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def get_auth_headers(client, username="alice", password="secret"):
    """Return bearer auth headers for a registered user."""
    token_response = client.post(
        "/token",
        data={"username": username, "password": password},
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login_return_bearer_tokens(client):
    registration = register_user(client, username="alice")
    assert registration["token_type"] == "bearer"
    assert isinstance(registration["access_token"], str)
    assert registration["access_token"]

    login_response = client.post(
        "/token",
        data={"username": "alice", "password": "secret"},
    )
    login_payload = login_response.json()

    assert login_response.status_code == 200
    assert login_payload["token_type"] == "bearer"
    assert isinstance(login_payload["access_token"], str)
    assert login_payload["access_token"]


def test_post_requires_authentication(client):
    response = client.post("/post", json={"body": "Hello"})

    assert response.status_code == 401


def test_authenticated_post_creation_works(client):
    register_user(client, username="alice")
    headers = get_auth_headers(client, username="alice")

    response = client.post("/post", json={"body": "Hello world"}, headers=headers)
    payload = response.json()

    assert response.status_code == 201
    assert payload["body"] == "Hello world"


def test_authenticated_comment_creation_works_for_existing_post(client):
    register_user(client, username="alice")
    headers = get_auth_headers(client, username="alice")

    post_response = client.post("/post", json={"body": "Hello world"}, headers=headers)
    post_payload = post_response.json()
    post_id = post_payload["id"]

    comment_response = client.post(
        "/comment",
        json={"body": "Nice post", "post_id": post_id},
        headers=headers,
    )
    comment_payload = comment_response.json()

    assert comment_response.status_code == 201
    assert comment_payload["body"] == "Nice post"
    assert comment_payload["post_id"] == post_id


def test_get_posts_detail_returns_post_with_comments(client):
    register_user(client, username="alice")
    headers = get_auth_headers(client, username="alice")

    post_response = client.post("/post", json={"body": "Hello world"}, headers=headers)
    post_payload = post_response.json()
    post_id = post_payload["id"]

    client.post(
        "/comment",
        json={"body": "Nice post", "post_id": post_id},
        headers=headers,
    )

    response = client.get(f"/posts/{post_id}")
    payload = response.json()

    assert response.status_code == 200
    assert payload["body"] == "Hello world"
    assert len(payload["comments"]) == 1
    assert payload["comments"][0]["body"] == "Nice post"


def test_comment_on_missing_post_returns_404(client):
    register_user(client, username="alice")
    headers = get_auth_headers(client, username="alice")

    response = client.post(
        "/comment",
        json={"body": "Oops", "post_id": 999},
        headers=headers,
    )
    payload = response.json()

    assert response.status_code == 404
    assert payload["detail"] == "Post not found"
