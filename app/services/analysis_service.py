import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import minimize
import logging
import requests
from ..config import settings
import time


# Get a logger instance
logger = logging.getLogger("app.services.analysis_service")


def fetch_historical_prices(tickers, start_date, end_date):
    api_key = settings.alpha_vantage_api_key
    frames = {}
    for ticker in tickers:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=compact&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        series = data.get("Time Series (Daily)", {})
        if not series:
            logger.error(f"Alpha Vantage response for {ticker}: {data}")
            raise ValueError(f"No data returned for {ticker}: {data}")
        df_ticker = pd.DataFrame.from_dict(series, orient="index")
        df_ticker.index = pd.to_datetime(df_ticker.index)
        df_ticker = df_ticker.sort_index()
        df_ticker = df_ticker[(df_ticker.index >= pd.Timestamp(start_date)) & (df_ticker.index <= pd.Timestamp(end_date))]
        frames[ticker] = df_ticker["4. close"].astype(float)
        time.sleep(1)
    return pd.DataFrame(frames)


# Fetches risk free rate from FRED Api
def get_risk_free_rate():
    risk_free_rate = 0.03  # temporary hardcoded value
    logger.info("Risk free rate successfully retrieved.")
    return risk_free_rate


# Run analysis
def run_portfolio_analysis(holdings):
    # Call the risk free rate function
    risk_free_rate = get_risk_free_rate()

    # Extract tickers from holdings
    tickers = [holding.ticker for holding in holdings]
    logger.info("Tickers successfully retrieved.")

    # Fetch price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    prices = fetch_historical_prices(tickers, start_date, end_date)
    logger.info("Ticker data successfully retrieved.")

    if prices.empty:
        logger.error("Could not fetch price data for tickers")
        raise ValueError("Could not fetch price data for tickers")

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
    sharpe_ratio = (annualized_returns - risk_free_rate) / annualized_volatility

    # Max Drawdown
    running_max = cumulative_returns.cummax()
    drawdown = (running_max - cumulative_returns) / running_max
    max_drawdown = drawdown.max()

    
    # Covariance matrix
    covariance = daily_returns.cov() * 252

    # Get last prices for each ticker from the prices DataFrame
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

    # Portfolio level metrics (averages)
    analysis_data = {
        "total_value": float(total_value),
        "total_cost": float(total_cost),
        "unrealized_profit_loss": float(unrealized_profit_loss),
        "annualized_return": float(annualized_returns.mean()),
        "annualized_volatility": float(annualized_volatility.mean()),
        "sharpe_ratio": float(sharpe_ratio.mean()),
        "max_drawdown": float(max_drawdown.mean())
    }

    # Ticker level metrics (individual values)
    ticker_metrics = []
    for holding in holdings:
        position_value = float(holding.num_shares) * float(current_prices[holding.ticker])
        metric = {
            "ticker": holding.ticker,
            "current_price": float(current_prices[holding.ticker]),
            "position_value": float(position_value),
            "weight": float(position_value / total_value),
            "annualized_return": float(annualized_returns[holding.ticker]),
            "annualized_volatility": float(annualized_volatility[holding.ticker]),
            "sharpe_ratio": float(sharpe_ratio[holding.ticker]),
            "max_drawdown": float(max_drawdown[holding.ticker])
        }
        ticker_metrics.append(metric)

    allocations = []
    logger.info(f"Holdings count: {len(holdings)}, Optimized weights count: {len(optimized_weights)}")
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


def optimize_sharpe(annualized_returns, covariance, risk_free_rate):
    num_assets = len(annualized_returns)

    def neg_sharpe(weights):
        portfolio_return = np.dot(weights, annualized_returns)
        portfolio_vol = np.sqrt(weights.T @ covariance @ weights)
        return -(portfolio_return - risk_free_rate) / portfolio_vol

    initial_weights = np.ones(num_assets) / num_assets
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

    result = minimize(neg_sharpe, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        logger.info(f"Sharpe ratio optimization successful: {result.message}")
    else:
        logger.error(f"Sharpe ratio optimization failed: {result.message}")
        raise ValueError(f"Sharpe ratio optimization failed: {result.message}")

    return result.x


def optimize_min_volatility(annualized_returns, covariance):
    num_assets = len(annualized_returns)

    def portfolio_volatility(weights):
        return np.sqrt(weights.T @ covariance @ weights)

    initial_weights = np.ones(num_assets) / num_assets
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

    result = minimize(portfolio_volatility, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        logger.info(f"Portfolio volatility optimization successful: {result.message}")
    else:
        logger.error(f"Portfolio volatility optimization failed: {result.message}")
        raise ValueError(f"Portfolio volatility optimization failed: {result.message}")

    return result.x