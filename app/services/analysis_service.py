import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import minimize
import numpy as np
import logging


# Get a logger instance
logger = logging.getLogger("app.services.analysis_service")

# Fetches risk free rate form FRED Api
def get_risk_free_rate():
    risk_free_rate = 0.03 # we do this temporarily
    logger.info("Risk free rate successfully retrieved.")
    return risk_free_rate

# Run analysis
def run_portfolio_analysis(holdings):
    # Call the risk free rate function
    risk_free_rate = get_risk_free_rate()
    

    # Extract tickers from holdings
    tickers = [holding.ticker for holding in holdings]
    logger.info("Tickers successfully retrieved.")

    # fetch price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    df = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False, progress=False)
    logger.info("Ticker data successfuly retieved.")

    if df.empty:
        logger.error("Could not fetch price data for tickers")
        raise ValueError("Could not fetch price data for tickers")

    # Handle muti-ticker vs single ticker
    if isinstance(df.columns, pd.MultiIndex):
        prices = df['Adj Close']
    else:
        prices = df[["Adj Close"]]

    # Drop missing data 
    prices = prices.dropna(how="all")
    logger.info("Missing data prices successfully dropped.")


    # Calculate metrics

    # Daily returns
    daily_returns = prices.pct_change().dropna()
    
        
    # Cumulative returns
    cumulative_returns = (1 + daily_returns).cumprod().dropna()
    

    # Annualized volatility
    std_daily_returns = daily_returns.std()
    annualized_volatility = std_daily_returns * np.sqrt(252)
    

    # Annualized return
    average_daily_returns = daily_returns.mean()
    annualized_returns = average_daily_returns * 252
    

    # Sharpe Ratio
    sharpe_ratio = (annualized_returns - risk_free_rate ) / annualized_volatility
    

    # Maxdrawdown
    running_max = cumulative_returns.cummax()
    drawdown = (running_max - cumulative_returns ) / running_max
    max_drawdown = drawdown.max()
    

    # Calculate correlation between assets
    correlation_matrix = daily_returns.corr()
    
    
    # calculate covariance between assets
    covariance = daily_returns.cov() * 252
    

    # Get last prices for each ticker from the prices DF
    current_prices = prices.iloc[-1]
    

    # Calculate total cost
    total_cost = sum(float(holding.num_shares) * float(holding.average_cost) for holding in holdings)
    

    # Calculate total value
    total_value = sum(float(holding.num_shares) * float(current_prices[holding.ticker]) for holding in holdings)
    

    # Calculate unrealized profit/loss
    unrealized_profit_loss = total_value - total_cost
    

    # Call the optimizer functions
    optimized_weights = optimize_sharpe(annualized_returns, covariance, risk_free_rate)
    min_vol_weights = optimize_min_volatility(annualized_returns, covariance)


    logger.info("Portfolio metrics successfully calculated.")

    # Create return dictionaries 

    # this is portfolio level metrics so I for any series of values I need to provide
    # the average for that metric
    analysis_data = {
    "total_value": float(total_value),
    "total_cost": float(total_cost),
    "unrealized_profit_loss": float(unrealized_profit_loss),
    "annualized_return": float(annualized_returns.mean()),  # average of the returns
    "annualized_volatility": float(annualized_volatility.mean()), # average of the volatility
    "sharpe_ratio": float(sharpe_ratio.mean()), # average sharpe ration
    "max_drawdown": float(max_drawdown.mean()) # average maxdrawdown
}
    
    # This is ticker level so we provide individual values (no averages)
    # current_prices[holding.ticker] - this syntax means to get the current price
    # of the ticker that is in holding
    ticker_metrics = []
    for holding in holdings:
        position_value = float(holding.num_shares) * float(current_prices[holding.ticker])

        metric = {
            "ticker": holding.ticker,  
            "current_price" : float(current_prices[holding.ticker]),
            "position_value": float(position_value), 
            "weight": float(position_value / total_value), 
            "annualized_return": float(annualized_returns[holding.ticker]), 
            "annualized_volatility": float(annualized_volatility[holding.ticker]), 
            "sharpe_ratio" :float(sharpe_ratio[holding.ticker]), 
            "max_drawdown": float(max_drawdown[holding.ticker]) 
    }
        ticker_metrics.append(metric)


    allocations = []
    # Placeholder for the weights
    #equal_weight = 1/len(holdings) no longer needed
    for i, holding in enumerate(holdings):
        position_value = float(holding.num_shares) * float(current_prices[holding.ticker])
        allocation = {
            "ticker": holding.ticker, 
            "current_weight": float(position_value / total_value),
            "optimized_weight": float(optimized_weights[i]),
            "min_vol_weight": float(min_vol_weights[i])
    }
        allocations.append(allocation)

    return analysis_data, ticker_metrics, allocations


# These weights will be used to complete allocations above 
def optimize_sharpe(annualized_returns, covariance, risk_free_rate):
    num_assets = len(annualized_returns)
    def neg_sharpe(weights):
        # Calculate portfolio returns
        portfolio_return = np.dot(weights, annualized_returns)
        # Calculate portfolio volatility
        portfolio_vol = np.sqrt(weights.T @ covariance @ weights) 
        return -(portfolio_return - risk_free_rate) / portfolio_vol
    
    # Set up optimizer
    initial_weights = np.ones(num_assets) / num_assets # 33%,33%,33%
    # Set bounds - one bound pair of values from 0-1 for each asset
    bounds = tuple((0, 1) for _ in range(num_assets))
    # Set constraints - all weights must sum to 1 (fully invested portfolio)
    constraints = {'type':'eq', 'fun': lambda w: np.sum(w) -1}

    # Run optimization
    result = minimize(neg_sharpe, initial_weights, method='SLSQP', bounds= bounds, constraints=constraints)
    
    if result.success:
        logger.info(f"Sharpe ratio optimization successful: {result.message}")
        
    else:
        logger.error(f"Sharpe ratio optimization failed: {result.message}")
        raise ValueError(f"Sharpe ratio optimization failed: {result.message}")
    
    return result.x


def optimize_min_volatility(annualized_returns, covariance):
    num_assets = len(annualized_returns)
    def portfolio_volatility(weights):
        # Calculate portfolio volatility
        portfolio_vol = np.sqrt(weights.T @ covariance @ weights) 
        return portfolio_vol
    
    # Set up optimizer
    initial_weights = np.ones(num_assets) / num_assets # 33%,33%,33%
    # Set bounds - one bound pair of values from 0-1 for each asset
    bounds = tuple((0, 1) for _ in range(num_assets))
    # Set constraints - all weights must sum to 1 (fully invested portfolio)
    constraints = {'type':'eq', 'fun': lambda w: np.sum(w) -1}

    # Run optimization
    result = minimize(portfolio_volatility, initial_weights, method='SLSQP', bounds= bounds, constraints=constraints)
    
    if result.success:
        logger.info(f"Portfolio volatility optimization successful: {result.message}")
        
    else:
        logger.error(f"Portfolio volatility optimization failed: {result.message}")
        raise ValueError(f"Portfolio volatility optimization failed: {result.message}")
    
    return result.x








    
