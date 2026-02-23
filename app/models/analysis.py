from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE") , nullable=False)
    calculated_at = Column(DateTime(timezone=True),server_default=func.now())
    total_value = Column(Numeric, nullable=False)
    total_cost = Column(Numeric, nullable=False)
    unrealized_profit_loss = Column(Numeric, nullable=False)
    annualized_return = Column(Numeric, nullable=False)
    annualized_volatility = Column(Numeric, nullable=False)
    sharpe_ratio = Column(Numeric, nullable=False)
    max_drawdown = Column(Numeric, nullable=False)

    # Relationship
    portfolio = relationship("Portfolio", back_populates="analysis_result")
    ticker_metrics = relationship("TickerMetric", back_populates="analysis_result", cascade="all, delete-orphan")
    optimized_allocations = relationship("OptimizedAllocation",back_populates="analysis_result", cascade="all, delete-orphan")

class TickerMetric(Base):
    __tablename__ = "ticker_metrics"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="CASCADE") , nullable=False)
    ticker = Column(String, nullable=False)
    current_price = Column(Numeric, nullable=False)
    position_value = Column(Numeric, nullable=False)
    weight = Column(Numeric(precision=12, scale=4), nullable=False)
    annualized_return = Column(Numeric, nullable=False)
    annualized_volatility = Column(Numeric, nullable=False)
    sharpe_ratio = Column(Numeric, nullable=False)
    max_drawdown = Column(Numeric, nullable=False)

    
    # Relationship
    analysis_result = relationship("AnalysisResult", back_populates="ticker_metrics")
    


class OptimizedAllocation(Base):
    __tablename__ = "optimized_allocations"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="CASCADE") , nullable=False)
    ticker = Column(String, nullable=False)
    current_weight = Column(Numeric(precision=12, scale=4), nullable=False)
    optimized_weight = Column(Numeric(precision=12, scale=4), nullable=False)
    min_vol_weight = Column(Numeric(precision=12, scale=4), nullable=False)



    # Relationship
    analysis_result = relationship("AnalysisResult", back_populates="optimized_allocations")





