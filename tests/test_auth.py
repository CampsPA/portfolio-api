# Tests for authentication

# run auth test: python -m pytest tests/test_auth.py

# 1- Create a test to register user
def test_register(client):
    response = client.post(
        "/auth/register",
        json= {
    "email": "user1@example.com",
    "password": "pass123",
    "first_name" : "John",
    "last_name": "Doe"
}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"



# 2- Create a test to test user registration with duplicate email
def test_duplicated_email(client):
    # Register the user 
    response = client.post(
        "/auth/register",
        json= {
    "email": "user1@example.com",
    "password": "pass123",
    "first_name" : "John",
    "last_name": "Doe"
}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

    # Register another user with the same email as user1 to trigger an error
    response = client.post(
        "/auth/register",
        json= {
    "email": "user1@example.com",
    "password": "pass456",
    "first_name" : "Joe",
    "last_name": "Doe"
}
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.json()}"


# 3- Create a test for login success
def test_login_success(client, test_creating_user): # it needs a user to exist for testing
    response = client.post(
        "/auth/login",
        # login uses form data, not json 
        data = {
            "username": "user1@example.com",
            "password" : "pass123"
        }

    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"



# 4- Create a test to reject login with wrong password
def test_login_wrong_password(client, test_creating_user): # it needs a user to exist for testing
    response = client.post(
        "/auth/login",
        # login uses form data, not json
        data = {
            "username": "user1@example.com",
            "password" : "pass123"
        }

    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

    # Same user, different password to trigger error
    response = client.post(
        "/auth/login",
        # login uses form data, not json
        data = {
            "username": "user1@example.com",
            "password" : "pass333"
        }

    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.json()}"


# 5- Createa test to reject loging in with the wrong email
def test_login_wrong_email(client, test_creating_user):
    response = client.post(
        "/auth/login",
        # login uses form data, not json
        data = {
            "username": "different_user@example.com",
            "password" : "pass123"
        }

    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.json()}"
    





