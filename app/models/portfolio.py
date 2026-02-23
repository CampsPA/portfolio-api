from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # value must be provided
    description = Column(String, nullable=True) # value not needed
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) #"Cascade = deletes all portfolio if user is deleted "
    created_at = Column(DateTime(timezone=True), server_default=func.now())# returns a function NOW() to return the current time stamp

    
    # Relationships
    owner = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio",cascade="all, delete-orphan")
    analysis_result = relationship("AnalysisResult", back_populates="portfolio", cascade="all, delete-orphan")