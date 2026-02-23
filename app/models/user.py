from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True) # added this via Alembic to practice migrations
    last_name = Column(String, nullable=True) # added this via Alembic to practice migrations
    email = Column(String, nullable = False, unique= True, index=True)
    hashed_password = Column(String, nullable= False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

   
    # Relationship -> describes the relatioship between the portfolio model and its owner
    portfolios= relationship("Portfolio", back_populates="owner", cascade="all, delete-orphan")
