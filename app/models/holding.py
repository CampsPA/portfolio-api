from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False) #"Cascade = deletes all portfolio if user is deleted "
    ticker = Column(String, nullable=False) # value must be provided
    num_shares = Column(Numeric(precision=12, scale=4), nullable=False) # value must be provided
    average_cost = Column(Numeric, nullable=False)# value most be provided
    created_at = Column(DateTime(timezone=True), server_default=func.now())# returns a function NOW() to return the current time stamp
    purchase_date = Column(DateTime(timezone=True), server_default=func.now()) # SAdded this to practice migrations


    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")