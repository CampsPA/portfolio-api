# run: uvicorn app.main:app --reload

from fastapi import FastAPI
from . database import engine, Base

# Create database tables 
Base.metadata.create_all(bind=engine)

# Initialize the App
app = FastAPI(
    title="Portfolio Analyzer API",
    description="Analyze and optimize stock portfolios",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message" : "Portfolio Analyzer API"}

# link routes