# run auth test: python -m pytest tests/test_auth.py
# run portfolio test = python -m pytest tests/test_portfolios.py

from app.main import app
from fastapi.testclient import TestClient
from app.database import Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from app.config import settings
import pytest
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.oauth2 import create_access_token
# Import to test analysis
from unittest.mock import patch
import pandas as pd
import numpy as np


# Database connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name_test}"

test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.drop_all(bind=test_engine) # This runs once test starts to give a clean schema
Base.metadata.create_all(bind=test_engine)



# creates a session to perform tests then  clear the database after ech test is completed
@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection) 
    yield session

    session.close()
    transaction.rollback()
    connection.close()



# Client fixture
# This is a basic test client with no authentication - use in endpoints that require no login
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


#  Create a fixture that creates a user in the database and returns it
# This will be use it in tests that need a user to already exist — like testing login
# Not a client, it does not make HTTP requests
@pytest.fixture
def test_creating_user(db_session):
    user_data = UserCreate(email="user1@example.com", password="pass123", first_name="John", last_name="Doe") # creates a pydantic schema object with this inputs
    new_user = create_user(db_session, user_data) # call the crud function, saves to the database
    yield new_user # gives this database user to any test that needs it.
 


# This creates a default user that will be passed to any test that needs an authenticated user
@pytest.fixture
def authenticated_client(db_session, test_creating_user):
    user_token = create_access_token({"sub": test_creating_user.email})

    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, headers={"Authorization": f"Bearer {user_token}"})

    yield client

    app.dependency_overrides.clear()



# Creates a second user so we can use the first client's credentials
# to try to login the second client portfolio
@pytest.fixture
def test_creating_user_2(db_session):
    user_data = UserCreate(email="user2@example.com", password="pass12345", first_name="Joe", last_name="Donald") 
    new_user = create_user(db_session, user_data) 
    yield new_user 


# Create a second authenticated client so we can use the first client's credentials
# to try to login the second client portfolio
@ pytest.fixture
def authenticated_client_2(db_session, test_creating_user_2):
    user_token = create_access_token({"sub": test_creating_user_2.email})

    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, headers={"Authorization": f"Bearer {user_token}"})

    yield client

    app.dependency_overrides.clear()




# Create a fixture test to test run analysis

@pytest.fixture
def run_analysis(authenticated_client):
    # Create fake data
    dates = pd.date_range("2024-01-01", periods=252)  # 252 trading days
    fake_data = pd.DataFrame({
    ("Adj Close", "AAPL"): np.random.uniform(150, 160, 252),
    ("Adj Close", "GOOGL"): np.random.uniform(100, 110, 252)
})
    fake_data.index = dates
    fake_data.columns = pd.MultiIndex.from_tuples(fake_data.columns)

    # Run the test: 
    # create a portfolio, adding a hold with average_cost included, 
    # return fake data, call analysis endpoint, assert response

    # Create a portfolio
    create_response = authenticated_client.post(
        "/portfolios", json= {
            "name": "AI Portfolio",
            "description": "Artificial Intelligence Stocks"
        }
    )
    portfolio_id = create_response.json()["id"]


    # add holdings 
    response = authenticated_client.post(f"/portfolios/{portfolio_id}/holdings",
        json={
            "ticker": "AAPL", "num_shares": 150, "average_cost": 160,
        }
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code} : {response.json()}"


    # Mock yf.download to return your fake data
    with patch("app.services.analysis_service.yf.download") as mock_download:
        mock_download.return_value = fake_data
        response = authenticated_client.post(f"/portfolios/{portfolio_id}/analyze") # analyze here referst to the endpoint creating an analysis

        assert response.status_code == 201, f"Expected 201, got {response.status_code} : {response.json()}"

        yield portfolio_id






