# Test holdings

# run auth test: python -m pytest tests/test_holdings.py

# 1- Create a test to ensure holding was created sucessfully
# First create a portfolio to add the holdings
def test_holdings(authenticated_client):
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
            "ticker": "JNJ", "num_shares": 7, "average_cost": 55.00
        }
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code} : {response.json()}"


# 2- Create a test to list holdings by portfolio
# First create a portfolio
def test_get_holdings_by_id(authenticated_client):
# Create a portfolio
    create_response = authenticated_client.post(
        "/portfolios", json= {
            "name": "Industrial Portfolio",
            "description": "Industrial Stocks"
        }
    )
    portfolio_id = create_response.json()["id"]

    # Get all holdings in a portfolio
    response = authenticated_client.get(f"/portfolios/{portfolio_id}/holdings")
    assert response.status_code == 200, f"Expected 200, got {response.status_code} : {response.json()}"

