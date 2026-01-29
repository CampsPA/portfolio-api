
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Database connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# Create an engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session (replaces cursor + conn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Create a database session (connection) for each request, then automatically closes it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()