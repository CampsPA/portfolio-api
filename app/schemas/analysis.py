from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TickerMetricResponse(BaseModel):
    id : int 
    ticker : str
    current_price : float 
    position_value : float
    weight : float
    annualized_return : float
    annualized_volatility : float
    sharpe_ratio : float
    max_drawdown : float

    model_config = ConfigDict(from_attributes=True)


class OptimizedAllocationResponse(BaseModel):
    id : int
    ticker : str
    current_weight : float
    optimized_weight : float
    min_vol_weight : float

    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    id : int
    portfolio_id : int
    calculated_at : datetime
    total_value : float
    total_cost : float
    unrealized_profit_loss : float
    annualized_return : float
    annualized_volatility : float
    sharpe_ratio : float
    max_drawdown : float
    ticker_metrics : list[TickerMetricResponse]
    optimized_allocations : list[OptimizedAllocationResponse]

    model_config = ConfigDict(from_attributes=True)