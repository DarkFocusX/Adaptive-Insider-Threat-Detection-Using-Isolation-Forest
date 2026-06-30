def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_register_and_login(client):
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "9876543210",
            "password": "secret12",
            "confirm_password": "secret12",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "secret12"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"Welcome" in response.data
