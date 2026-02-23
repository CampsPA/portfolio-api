# Create tests for portfolios

# run portfolio test = python -m pytest tests/test_portfolios.py


# 1- Create a test to make sure a portfolio was created
def test_portfolios(authenticated_client):
    response = authenticated_client.post(
        "/portfolios", json= {
            "name": "Tech Portfolio",
            "description": "Technology Stocks"
        }
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"

# 2- Create a test to list all the portfolios
def test_get_all_portfolios(authenticated_client):
    response = authenticated_client.get(
        "/portfolios")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"


# 3- Create a test to list a single portfolio
# Remember that we need to create a portfolio first since each test is independent of the other
def test_get_portfolio_by_id(authenticated_client):
    # First create the portfolio
    create_response = authenticated_client.post(
        "/portfolios", json= {
            "name": "Test Portfolio",
            "description": "Test"
        }
    )
    portfolio_id = create_response.json()["id"]

    # Get portfolio by id
    response = authenticated_client.get(f"/portfolios/{portfolio_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

    

# 4- Test accessing another user's portolio 
# authenticated_client created a portfolio
# authenticated_client_2 tris to access that portfolio
def test_get_another_user_portfolio( authenticated_client,authenticated_client_2):
    # First create the portfolio
    create_response = authenticated_client.post(
        "/portfolios", json= {
            "name": "Test Portfolio 2",
            "description": "Test_2"
        }
    )
    portfolio_id = create_response.json()["id"]

    # Try accessing the first user's portfolio
    response = authenticated_client_2.get(
        f"/portfolios/{portfolio_id}")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.json()}"

