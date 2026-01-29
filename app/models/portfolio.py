from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(str, nullable=False) # value must be provided
    description = Column(str, nullable=True) # value not needed
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) #"Cascade = deletes all portfolio if user is deleted "
    created_at = Column(DateTime(timezone=True), server_default=func.now())# returns a function NOW() to return the current time stamp

    # Note:
    # The foreignkey creates the relationships, back_populates= connects the relationships
    # now I can call portfolio.owner to get access to the User object that owns this podtfolio
    # the same is true with holdings and analyses
    # Since the owner is an individual, define the variable as 'owner'
    # Since the owner can have many holdings, define the variable as 'holdings'
    owner = relationship("User", back_populates="portfolios") 
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan") # one portfolio -> many holdings
    analyses = relationship("AnalysisResult", back_populates="portfolio", cascade="all, delete-orphan")
    