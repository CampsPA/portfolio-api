from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable = False, unique= True), index=True
    hashed_password = Column(String, nullable= False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Since the User can have more tha one portfolio I define the relationship with the variable postfolios
    portfolios = relationship("Portfolio", back_populates="owner") # one user - many portfolios -> one to many
    # This allows me to user user.portfolios to access Postfolio objects
    # The relationship is created with the ForeignKey
    # back_populates = creates the connects the relationships

    # I'm creating a relationship between the User and Posrtfolio, and the name of this relationship is owner
    # since a User can have many portfolios I'll name this variable 'posrfolios'