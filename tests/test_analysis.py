# Test analysis

# run auth test: python -m pytest tests/test_analysis.py

# We will use "Mocking" to replace a API call with fake data

# Create a test to test run analysis
# pass the run_analysis fixture as the argument
def test_run_analysis(run_analysis):
    portfolio_id = run_analysis
    assert portfolio_id is not None
    

# Create a test to get latest analysis results
def test_get_latest_analysis(run_analysis, authenticated_client):
    portfolio_id = run_analysis
    response = authenticated_client.get(f"/portfolios/{portfolio_id}/analysis") # analysis endpoint here refers to retrieving an analysis
    assert response.status_code == 200, f"Expected 200, got {response.status_code} : {response.json()}"


# Create a test to list all the analysis history
def test_get_analysis_history(run_analysis, authenticated_client):
    portfolio_id = run_analysis
    response = authenticated_client.get(f"/portfolios/{portfolio_id}/analysis/history")
    assert response.status_code == 200, f"Expected 200, got {response.status_code} : {response.json()}"